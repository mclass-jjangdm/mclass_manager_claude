"""
mclass.shop → mclass.co.kr 교재 판매 데이터 마이그레이션 명령어

사용법:
    # 미리 보기 (DB 변경 없음)
    python manage.py import_shop_sales data.csv --mapping-file compare_title.csv --dry-run

    # 실제 적용
    python manage.py import_shop_sales data.csv --mapping-file compare_title.csv

교재 매칭 순서:
    1. 매핑 파일  — shop 교재명 → co.kr 교재명으로 치환 후 DB 검색 (최우선)
    2. 정확 일치  — 제목이 완전히 같음
    3. 정규화 일치 — 공백·괄호·연도 표기 차이 무시
    4. 퍼지 유사도 — difflib 유사도 >= threshold (기본 85%)
    5. 날짜 추론  — 같은 학생·같은 날짜에 기존 BookSale 1건이면 해당 교재로 추론
    최종 실패    — placeholder ISBN으로 신규 교재 생성

납부 처리:
    납부완료 → is_paid=True,  payment_date=납부일
    미납     → is_paid=False, payment_date=None

날짜 추론 주의: 날짜가 같아도 다른 교재일 수 있으므로 보고서를 반드시 검토하세요.
"""

import csv
import difflib
import hashlib
import os
import re
import unicodedata
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from bookstore.models import Book, BookSale
from students.models import Student


REQUIRED_COLUMNS = {'학생명', '학생코드', '교재명', '가격', '지급일', '납부여부', '납부일'}
DATE_FORMATS = ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d']

_GRADE_REPLACEMENTS = [
    ('중학교', '중'), ('고등학교', '고'), ('초등학교', '초'),
    ('중학', '중'), ('고학교', '고'), ('초학교', '초'),
    ('중등', '중'), ('고등', '고'), ('초등', '초'),
]


# ── 헬퍼 함수 ────────────────────────────────────────────────────────────────

def parse_date(value):
    if not value or not str(value).strip():
        return None
    value = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def make_placeholder_isbn(title):
    h = hashlib.md5(title.encode('utf-8')).hexdigest()[:12]
    return f'SHOP-{h}'


def normalize_title(title: str) -> str:
    """공백·괄호·연도·학교급 표기 차이를 제거한 정규화 문자열 반환."""
    if not title:
        return ''
    t = unicodedata.normalize('NFC', title.strip())
    t = re.sub(r'[\s\u3000]+', '', t)
    t = re.sub(r'[()（）\[\]【】{}<>《》「」]', '', t)
    t = re.sub(r'(\d{2,4})년용', r'\1', t)
    t = re.sub(r'(\d{2,4})년', r'\1', t)
    for old, new in _GRADE_REPLACEMENTS:
        t = t.replace(old, new)
    t = t.replace('·', '-').replace('‐', '-').replace('－', '-')
    return t.lower()


def find_book(search_title: str, book_by_exact: dict, book_by_norm: dict,
              all_norm_pairs: list, threshold: float = 0.85):
    """
    3단계 교재 매칭.
    반환: (tier, book_or_None, score, ambig_or_None)
    tier: 'exact' | 'normalized' | 'normalized_ambig' | 'fuzzy' | 'fuzzy_ambig' | 'no_match'
    """
    # Tier 1: 정확 일치
    if search_title in book_by_exact:
        return ('exact', book_by_exact[search_title], 1.0, None)

    # Tier 2: 정규화 일치
    norm = normalize_title(search_title)
    if norm in book_by_norm:
        cands = book_by_norm[norm]
        if len(cands) == 1:
            return ('normalized', cands[0], 1.0, None)
        return ('normalized_ambig', None, 1.0, cands)

    # Tier 3: 퍼지 유사도 (4자 미만이면 오매칭 방지를 위해 생략)
    if len(norm) < 4:
        return ('no_match', None, 0.0, None)

    best_score, best_books = 0.0, []
    for db_norm, book in all_norm_pairs:
        score = difflib.SequenceMatcher(False, norm, db_norm).ratio()
        if score > best_score + 1e-9:
            best_score, best_books = score, [book]
        elif abs(score - best_score) < 1e-9:
            best_books.append(book)

    if best_score >= threshold:
        if len(best_books) == 1:
            return ('fuzzy', best_books[0], best_score, None)
        return ('fuzzy_ambig', None, best_score, best_books)

    return ('no_match', None, best_score, None)


def load_mapping_file(filepath: str) -> dict:
    """
    교재명 매핑 CSV 로드.
    형식: mclass.shop 교재명, mclass.co.kr 교재명 (첫 줄 헤더)
    반환: {shop_title: co_kr_title}
    """
    if not filepath:
        return {}
    if not os.path.exists(filepath):
        raise CommandError(f'매핑 파일을 찾을 수 없습니다: {filepath}')
    for encoding in ('utf-8-sig', 'cp949', 'utf-8'):
        try:
            with open(filepath, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f)
                next(reader, None)  # 헤더 스킵
                mapping = {}
                for row in reader:
                    if len(row) >= 2:
                        shop = row[0].strip()
                        co_kr = row[1].strip()
                        if shop and co_kr:
                            mapping[shop] = co_kr
            return mapping
        except (UnicodeDecodeError, LookupError):
            continue
    raise CommandError(f'매핑 파일 인코딩을 감지할 수 없습니다: {filepath}')


def read_csv(filepath):
    for encoding in ('utf-8-sig', 'cp949', 'utf-8'):
        try:
            with open(filepath, 'r', encoding=encoding, newline='') as f:
                rows = list(csv.DictReader(f))
                return rows, encoding
        except (UnicodeDecodeError, LookupError):
            continue
    raise CommandError(f'CSV 파일 인코딩을 감지할 수 없습니다: {filepath}')


# ── 커맨드 ────────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = (
        'mclass.shop 교재 판매 내역 CSV를 mclass.co.kr로 마이그레이션합니다.\n'
        '--mapping-file 로 교재명 대응표를 지정하면 이름이 많이 달라도 정확하게 매칭됩니다.'
    )

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='판매 내역 CSV 파일 경로')
        parser.add_argument(
            '--mapping-file', type=str, default='', metavar='PATH',
            help='교재명 매핑 CSV 경로 (shop명,co.kr명 형식). 권장 사용.',
        )
        parser.add_argument(
            '--dry-run', action='store_true', default=False,
            help='DB를 변경하지 않고 결과만 미리 확인합니다.',
        )
        parser.add_argument(
            '--similarity-threshold', type=float, default=0.85, metavar='FLOAT',
            help='퍼지 매칭 최소 유사도 (기본값: 0.85)',
        )

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        mapping_path = options['mapping_file']
        dry_run = options['dry_run']
        threshold = options['similarity_threshold']

        if not (0.0 < threshold <= 1.0):
            raise CommandError('--similarity-threshold는 0.0 초과 1.0 이하여야 합니다.')

        # 상대경로 → 프로젝트 루트 기준 절대경로
        from django.conf import settings
        if not os.path.isabs(csv_path):
            csv_path = os.path.join(settings.BASE_DIR, csv_path)
        if mapping_path and not os.path.isabs(mapping_path):
            mapping_path = os.path.join(settings.BASE_DIR, mapping_path)

        if not os.path.exists(csv_path):
            raise CommandError(f'CSV 파일을 찾을 수 없습니다: {csv_path}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN 모드] DB가 변경되지 않습니다.\n'))

        # ── 매핑 파일 로드 ──────────────────────────────────────────────────
        title_mapping = load_mapping_file(mapping_path)
        if title_mapping:
            self.stdout.write(f'교재명 매핑 파일 로드: {len(title_mapping)}건')
        else:
            self.stdout.write('교재명 매핑 파일: 사용 안 함')

        # ── CSV 읽기 ────────────────────────────────────────────────────────
        rows, encoding = read_csv(csv_path)
        self.stdout.write(
            f'파일 읽기 완료: {os.path.basename(csv_path)} '
            f'(인코딩: {encoding}, 전체 {len(rows)}행)\n'
        )

        if not rows:
            self.stdout.write(self.style.WARNING('CSV 파일이 비어있습니다.'))
            return

        missing = REQUIRED_COLUMNS - set(rows[0].keys())
        if missing:
            raise CommandError(
                f'필수 컬럼이 없습니다: {", ".join(sorted(missing))}\n'
                f'현재 컬럼: {", ".join(sorted(rows[0].keys()))}'
            )

        paid_count = sum(1 for r in rows if str(r.get('납부여부', '') or '').strip() == '납부완료')
        self.stdout.write(f'납부완료: {paid_count}행 / 미납: {len(rows) - paid_count}행 / 합계: {len(rows)}행\n')

        # ── DB 교재 캐시 (루프 전 일괄 로드) ───────────────────────────────
        _book_by_exact, _book_by_norm, _all_norm_pairs = {}, {}, []
        for book in Book.objects.all():
            _book_by_exact[book.title] = book
            nk = normalize_title(book.title)
            _book_by_norm.setdefault(nk, []).append(book)
            _all_norm_pairs.append((nk, book))
        self.stdout.write(f'교재 DB 캐시 로드: {len(_book_by_exact)}종')

        # ── 기존 BookSale 스냅샷 (날짜 추론용, 마이그레이션 전 상태) ─────
        existing_sales_snapshot = {}  # {(student_pk, sale_date): [BookSale...]}
        for bs in BookSale.objects.select_related('book').all():
            key = (bs.student_id, bs.sale_date)
            existing_sales_snapshot.setdefault(key, []).append(bs)
        total_existing = sum(len(v) for v in existing_sales_snapshot.values())
        self.stdout.write(f'기존 판매 내역 스냅샷: {total_existing}건\n')

        # ── 캐시 & 통계 초기화 ──────────────────────────────────────────────
        book_result_cache = {}   # {shop_title → Book} (매핑/정확/정규화/퍼지 결과만 캐시)
        student_cache = {}
        unique_student_results = {}
        student_id_updated = set()

        stats = {
            'total_rows': len(rows),
            'book_mapped': 0,         # 매핑 파일로 매칭
            'book_exact': 0,          # 정확 일치
            'book_normalized': 0,     # 정규화 일치
            'book_fuzzy': 0,          # 퍼지 유사도
            'book_date_inferred': 0,  # 날짜 추론
            'book_ambiguous': 0,      # 모호 → placeholder 생성
            'book_created': 0,        # 신규 placeholder
            'sale_created_paid': 0,
            'sale_created_unpaid': 0,
            'sale_skipped_duplicate': 0,
            'sale_skipped_no_student': 0,
            'row_error': 0,
        }

        skipped_student_details = []
        created_books = []
        fuzzy_match_log = []      # 퍼지 매칭 내역
        date_inferred_log = []    # 날짜 추론 내역 (검토 필요)
        ambiguous_match_log = []  # 모호 매칭 내역
        mapping_fail_log = []     # 매핑 파일 적용 후 DB에서 못 찾은 케이스

        try:
            with transaction.atomic():
                for row_num, row in enumerate(rows, start=1):

                    is_paid = str(row.get('납부여부', '') or '').strip() == '납부완료'
                    student_name = str(row.get('학생명', '') or '').strip()
                    shop_student_id = str(row.get('학생코드', '') or '').strip()
                    book_title = str(row.get('교재명', '') or '').strip()
                    price_raw = str(row.get('가격', '') or '').strip()
                    sale_date_raw = str(row.get('지급일', '') or '').strip()
                    payment_date_raw = str(row.get('납부일', '') or '').strip()

                    if not student_name or not shop_student_id or not book_title:
                        self.stdout.write(self.style.WARNING(
                            f'  {row_num}행: 필수값 누락 → 건너뜀'
                        ))
                        stats['row_error'] += 1
                        continue

                    sale_date = parse_date(sale_date_raw)
                    if not sale_date:
                        self.stdout.write(self.style.WARNING(
                            f'  {row_num}행 [{student_name}]: 지급일 형식 오류 "{sale_date_raw}" → 건너뜀'
                        ))
                        stats['row_error'] += 1
                        continue

                    payment_date = parse_date(payment_date_raw) if is_paid else None

                    try:
                        price = int(str(price_raw).replace(',', '').strip())
                    except (ValueError, TypeError):
                        self.stdout.write(self.style.WARNING(
                            f'  {row_num}행 [{student_name}]: 가격 형식 오류 "{price_raw}" → 건너뜀'
                        ))
                        stats['row_error'] += 1
                        continue

                    # ── Phase 2: 학생 매칭 ───────────────────────────────────
                    if student_name not in student_cache:
                        qs = Student.objects.filter(name=student_name)
                        count = qs.count()
                        if count == 0:
                            student_cache[student_name] = 'not_found'
                            skipped_student_details.append((student_name, '이름 없음'))
                            unique_student_results[student_name] = 'not_found'
                        elif count > 1:
                            student_cache[student_name] = 'duplicate'
                            skipped_student_details.append((student_name, f'동명이인 {count}명'))
                            unique_student_results[student_name] = 'duplicate'
                        else:
                            student = qs.first()
                            if student.student_id != shop_student_id:
                                conflict = Student.objects.filter(
                                    student_id=shop_student_id
                                ).exclude(pk=student.pk).first()
                                if conflict:
                                    reason = f'student_id 충돌: {shop_student_id} → {conflict.name} 사용 중'
                                    student_cache[student_name] = 'conflict'
                                    skipped_student_details.append((student_name, reason))
                                    unique_student_results[student_name] = 'conflict'
                                else:
                                    if not dry_run:
                                        student.student_id = shop_student_id
                                        student.save(update_fields=['student_id'])
                                    student_id_updated.add(student_name)
                                    student_cache[student_name] = student
                                    unique_student_results[student_name] = 'matched'
                            else:
                                student_cache[student_name] = student
                                unique_student_results[student_name] = 'matched'

                    cached_student = student_cache[student_name]
                    if cached_student in ('not_found', 'duplicate', 'conflict'):
                        stats['sale_skipped_no_student'] += 1
                        continue
                    student = cached_student

                    # ── Phase 3: 교재 매칭 ───────────────────────────────────
                    book = None

                    # 3-a. 캐시 확인 (이전 행에서 동일 shop 제목 이미 처리한 경우)
                    if book_title in book_result_cache:
                        book = book_result_cache[book_title]

                    else:
                        # 3-b. 매핑 파일: shop 제목 → co.kr 제목으로 치환
                        mapped_co_kr = title_mapping.get(book_title)
                        search_title = mapped_co_kr if mapped_co_kr else book_title

                        tier, matched_book, score, ambig = find_book(
                            search_title, _book_by_exact, _book_by_norm,
                            _all_norm_pairs, threshold
                        )

                        if matched_book is not None:
                            # 매칭 성공
                            book = matched_book
                            if mapped_co_kr:
                                stats['book_mapped'] += 1
                            elif tier == 'exact':
                                stats['book_exact'] += 1
                            elif tier == 'normalized':
                                stats['book_normalized'] += 1
                            elif tier == 'fuzzy':
                                stats['book_fuzzy'] += 1
                                fuzzy_match_log.append({
                                    'csv_title': book_title,
                                    'db_title': matched_book.title,
                                    'score': score,
                                    'book_pk': matched_book.pk,
                                })
                            book_result_cache[book_title] = book

                        else:
                            # 매칭 실패 처리
                            if mapped_co_kr:
                                # 매핑 파일에 있었지만 DB에서 못 찾음 → 경고
                                mapping_fail_log.append({
                                    'csv_title': book_title,
                                    'mapped_to': mapped_co_kr,
                                })

                            if tier in ('normalized_ambig', 'fuzzy_ambig'):
                                stats['book_ambiguous'] += 1
                                ambiguous_match_log.append({
                                    'csv_title': book_title,
                                    'tier': tier,
                                    'score': score,
                                    'candidates': [{'pk': b.pk, 'title': b.title} for b in ambig],
                                })

                            # 3-c. 날짜 추론: 같은 학생 + 같은 날짜에 기존 BookSale 1건이면 추론
                            date_key = (student.pk, sale_date)
                            existing_on_date = existing_sales_snapshot.get(date_key, [])
                            if len(existing_on_date) == 1:
                                inferred = existing_on_date[0].book
                                book = inferred
                                stats['book_date_inferred'] += 1
                                date_inferred_log.append({
                                    'csv_title': book_title,
                                    'db_title': inferred.title,
                                    'student': student_name,
                                    'date': sale_date,
                                    'book_pk': inferred.pk,
                                })
                                # 날짜 추론 결과는 title별 캐시에 저장하지 않음
                                # (다른 학생·날짜에서 다른 책이 추론될 수 있음)

                            # 3-d. 최종 실패 → placeholder 교재 생성
                            if book is None:
                                placeholder_isbn = make_placeholder_isbn(book_title)
                                if not dry_run:
                                    book, created = Book.objects.get_or_create(
                                        isbn=placeholder_isbn,
                                        defaults={
                                            'title': book_title,
                                            'price': price,
                                            'original_price': 0,
                                            'cost_price': 0,
                                            'stock': 0,
                                            'memo': 'imported from mclass.shop',
                                        }
                                    )
                                    if created:
                                        stats['book_created'] += 1
                                        created_books.append(book_title)
                                else:
                                    book = Book(
                                        title=book_title,
                                        isbn=placeholder_isbn,
                                        price=price,
                                    )
                                    stats['book_created'] += 1
                                    created_books.append(book_title)
                                book_result_cache[book_title] = book

                    # ── Phase 4: BookSale 생성 ──────────────────────────────
                    if not dry_run and book.pk:
                        if BookSale.objects.filter(
                            student=student, book=book, sale_date=sale_date
                        ).exists():
                            stats['sale_skipped_duplicate'] += 1
                            continue

                        BookSale.objects.create(
                            student=student,
                            book=book,
                            sale_date=sale_date,
                            price=price,
                            quantity=1,
                            is_paid=is_paid,
                            payment_date=payment_date,
                            memo='imported from mclass.shop',
                        )

                    if is_paid:
                        stats['sale_created_paid'] += 1
                    else:
                        stats['sale_created_unpaid'] += 1

                if dry_run:
                    transaction.set_rollback(True)

        except CommandError:
            raise
        except Exception as e:
            raise CommandError(f'마이그레이션 중 오류 발생: {e}')

        # ── 요약 보고서 ──────────────────────────────────────────────────────
        matched_count = sum(1 for v in unique_student_results.values() if v == 'matched')
        not_found_count = sum(1 for v in unique_student_results.values() if v == 'not_found')
        duplicate_count = sum(1 for v in unique_student_results.values() if v == 'duplicate')
        conflict_count = sum(1 for v in unique_student_results.values() if v == 'conflict')
        total_book_matched = (stats['book_mapped'] + stats['book_exact'] +
                              stats['book_normalized'] + stats['book_fuzzy'] +
                              stats['book_date_inferred'])
        total_created = stats['sale_created_paid'] + stats['sale_created_unpaid']

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('=== 마이그레이션 결과 ==='))
        self.stdout.write('=' * 60)
        self.stdout.write(f'전체 처리 행: {stats["total_rows"]}행')
        self.stdout.write('')

        self.stdout.write('[ 학생 ] (고유 학생 기준)')
        self.stdout.write(self.style.SUCCESS(f'  매칭 성공: {matched_count}명'))
        self.stdout.write(f'  → student_id 업데이트: {len(student_id_updated)}명')
        self.stdout.write(self.style.WARNING(f'  이름 없음 (건너뜀): {not_found_count}명'))
        self.stdout.write(self.style.WARNING(f'  동명이인 (건너뜀): {duplicate_count}명'))
        self.stdout.write(self.style.WARNING(f'  student_id 충돌 (건너뜀): {conflict_count}명'))
        self.stdout.write('')

        self.stdout.write('[ 교재 ] (고유 교재명 기준)')
        self.stdout.write(self.style.SUCCESS(f'  매칭 합계: {total_book_matched}건'))
        self.stdout.write(f'    매핑 파일 (수동 지정):       {stats["book_mapped"]}건')
        self.stdout.write(f'    정확 일치:                   {stats["book_exact"]}건')
        self.stdout.write(f'    정규화 일치 (공백/괄호):      {stats["book_normalized"]}건')
        self.stdout.write(f'    퍼지 유사도 (≥{threshold:.0%}):        {stats["book_fuzzy"]}건')
        self.stdout.write(self.style.WARNING(
            f'    날짜 추론 (검토 필요):        {stats["book_date_inferred"]}건'
        ))
        self.stdout.write(self.style.WARNING(
            f'  모호 매칭 (신규 생성됨):       {stats["book_ambiguous"]}건'
        ))
        self.stdout.write(f'  신규 생성 (placeholder):       {stats["book_created"]}종')
        self.stdout.write('')

        self.stdout.write('[ 판매 내역 (BookSale) ]')
        self.stdout.write(self.style.SUCCESS(f'  생성 합계: {total_created}건'))
        self.stdout.write(f'    납부완료 (is_paid=True):   {stats["sale_created_paid"]}건')
        self.stdout.write(f'    미납 (is_paid=False):      {stats["sale_created_unpaid"]}건')
        self.stdout.write(f'  중복 건너뜀: {stats["sale_skipped_duplicate"]}건')
        self.stdout.write(f'  학생 미매칭 건너뜀: {stats["sale_skipped_no_student"]}건')
        self.stdout.write(f'  행 오류: {stats["row_error"]}건')

        # 매핑 파일 적용 실패 경고
        if mapping_fail_log:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('[ 매핑 파일 적용 실패 - DB에서 못 찾음 ]'))
            seen = set()
            for e in mapping_fail_log:
                if e['csv_title'] not in seen:
                    seen.add(e['csv_title'])
                    self.stdout.write(self.style.ERROR(
                        f'  CSV:    {e["csv_title"]}\n'
                        f'  매핑→   {e["mapped_to"]}'
                    ))

        # 날짜 추론 내역 (반드시 검토)
        if date_inferred_log:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('[ 날짜 추론 매칭 - 반드시 검토 필요 ]'))
            self.stdout.write('  같은 학생·같은 날짜에 기존 판매 내역이 1건 있어 추론한 교재입니다.')
            self.stdout.write('  날짜가 같아도 다른 교재일 수 있으니 아래 내역을 반드시 확인하세요.\n')
            self.stdout.write(
                f'  {"학생":<12} {"날짜":<12} {"CSV 교재명(shop)":<34} {"→ DB 교재명":<34} {"PK":>5}'
            )
            self.stdout.write('  ' + '-' * 101)
            for e in date_inferred_log:
                self.stdout.write(
                    f'  {e["student"]:<12} {str(e["date"]):<12} '
                    f'{e["csv_title"][:32]:<34} {e["db_title"][:32]:<34} {e["book_pk"]:>5}'
                )

        # 퍼지 매칭 내역 (검토 권장)
        if fuzzy_match_log:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('[ 퍼지 매칭 교재 목록 - 검토 권장 ]'))
            self.stdout.write(
                f'  {"CSV 교재명(shop)":<38} {"DB 교재명":<38} {"유사도":>6}  {"PK":>5}'
            )
            self.stdout.write('  ' + '-' * 92)
            seen_csv = set()
            for e in fuzzy_match_log:
                if e['csv_title'] in seen_csv:
                    continue
                seen_csv.add(e['csv_title'])
                self.stdout.write(
                    f'  {e["csv_title"][:36]:<38} {e["db_title"][:36]:<38} '
                    f'{e["score"]:.1%}  {e["book_pk"]:>5}'
                )

        # 모호 매칭
        if ambiguous_match_log:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('[ 모호 매칭 교재 - 수동 처리 필요 (신규 생성됨) ]'))
            seen_ambig = set()
            for e in ambiguous_match_log:
                if e['csv_title'] in seen_ambig:
                    continue
                seen_ambig.add(e['csv_title'])
                self.stdout.write(self.style.ERROR(
                    f'  CSV: {e["csv_title"]}  (유사도={e["score"]:.1%})'
                ))
                for c in e['candidates']:
                    self.stdout.write(f'      후보: pk={c["pk"]}  {c["title"]}')

        # 건너뛴 학생
        if skipped_student_details:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('[ 건너뛴 학생 목록 ]'))
            seen = set()
            for name, reason in skipped_student_details:
                if (name, reason) not in seen:
                    seen.add((name, reason))
                    self.stdout.write(self.style.WARNING(f'  - {name}: {reason}'))

        # student_id 업데이트
        if student_id_updated:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('[ student_id 업데이트된 학생 ]'))
            for name in sorted(student_id_updated):
                self.stdout.write(f'  - {name}')

        # 신규 교재 목록
        if created_books:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('[ 신규 생성 교재 (매핑 파일에 추가 권장) ]'))
            for title in created_books:
                self.stdout.write(f'  + {title}  (ISBN: {make_placeholder_isbn(title)})')

        self.stdout.write('=' * 60)

        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                '[DRY RUN] 위 내용은 미리보기입니다. DB는 변경되지 않았습니다.\n'
                '실제 적용하려면 --dry-run 옵션을 제거하고 다시 실행하세요.'
            ))
        else:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('마이그레이션이 완료되었습니다.'))
