"""
mclass.shop → mclass.co.kr 교재 판매 데이터 마이그레이션 명령어

사용법:
    # 미리 보기 (DB 변경 없음)
    python manage.py import_shop_sales C:/path/to/file.csv --dry-run

    # 실제 적용
    python manage.py import_shop_sales C:/path/to/file.csv

    # 퍼지 매칭 임계값 조정 (기본값 0.85)
    python manage.py import_shop_sales C:/path/to/file.csv --similarity-threshold 0.9

CSV 컬럼 (mclass.shop 내보내기 형식):
    학생명, 학생코드, 교재명, 가격, 지급일, 납부여부, 납부일

교재 매칭 3단계:
    1. 정확 일치       - 제목이 완전히 같음
    2. 정규화 일치     - 공백·괄호·연도 표기 차이 무시
    3. 퍼지 유사도     - difflib 유사도 >= threshold (기본 85%)
    위 셋 모두 실패 시 → placeholder ISBN으로 신규 교재 생성

납부 처리:
    납부완료 → is_paid=True, payment_date=납부일
    미납     → is_paid=False, payment_date=None
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


# mclass.shop CSV 컬럼명
REQUIRED_COLUMNS = {'학생명', '학생코드', '교재명', '가격', '지급일', '납부여부', '납부일'}

DATE_FORMATS = ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d']

# 학교급 단어 정규화 맵 (긴 것부터 처리해야 부분 치환 오류 방지)
_GRADE_REPLACEMENTS = [
    ('중학교', '중'),
    ('고등학교', '고'),
    ('초등학교', '초'),
    ('중학', '중'),
    ('고학교', '고'),
    ('초학교', '초'),
    ('중등', '중'),
    ('고등', '고'),
    ('초등', '초'),
]


def parse_date(value):
    """날짜 문자열을 date 객체로 변환. 빈 값 또는 실패 시 None 반환."""
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
    """교재명으로 고유한 placeholder ISBN 생성 (SHOP-xxxx 형식, 최대 18자)."""
    h = hashlib.md5(title.encode('utf-8')).hexdigest()[:12]
    return f'SHOP-{h}'


def normalize_title(title: str) -> str:
    """
    교재명을 정규화하여 표기 차이를 제거한 비교 가능한 문자열로 변환.

    적용 순서:
        1. NFC 유니코드 정규화 (한글 자모 통일)
        2. 모든 공백 제거
        3. 괄호류 제거: ( ) [ ] { } 【 】 （ ） 《 》 「 」 등
        4. 연도 패턴 제거: 2024년용 → 2024, 2024년 → 2024
        5. 학교급 단어 통일: 중등/중학교/중학 → 중, 고등/고학교 → 고
        6. 영소문자 변환 (영문 포함 교재 대응)
    """
    if not title:
        return ''

    t = title.strip()

    # 1. NFC 유니코드 정규화
    t = unicodedata.normalize('NFC', t)

    # 2. 모든 공백·전각 공백 제거
    t = re.sub(r'[\s\u3000]+', '', t)

    # 3. 괄호류 제거
    t = re.sub(r'[()（）\[\]【】{}<>《》「」]', '', t)

    # 4. 연도 패턴 정규화 (괄호 제거 후 처리)
    t = re.sub(r'(\d{2,4})년용', r'\1', t)
    t = re.sub(r'(\d{2,4})년', r'\1', t)

    # 5. 학교급 단어 통일 (긴 것부터)
    for old, new in _GRADE_REPLACEMENTS:
        t = t.replace(old, new)

    # 6. 전각 하이픈·가운뎃점 → 반각 하이픈
    t = t.replace('·', '-').replace('‐', '-').replace('－', '-')

    # 7. 영소문자 변환
    t = t.lower()

    return t


def find_book(
    csv_title: str,
    book_by_exact: dict,
    book_by_norm: dict,
    all_norm_pairs: list,
    threshold: float = 0.85,
):
    """
    3단계 교재 매칭. 4-tuple 반환: (tier, book_or_None, score, ambig_list_or_None)

    tier 값:
        'exact'           - 원본 제목 정확 일치
        'normalized'      - 정규화 후 일치 (단일 후보)
        'normalized_ambig'- 정규화 후 일치하나 복수 DB 교재 존재
        'fuzzy'           - 퍼지 유사도 >= threshold (단일 최고 후보)
        'fuzzy_ambig'     - 퍼지 동점 복수 후보
        'no_match'        - threshold 미달
    """

    # Tier 1: 원본 제목 정확 일치
    if csv_title in book_by_exact:
        return ('exact', book_by_exact[csv_title], 1.0, None)

    # Tier 2: 정규화 후 정확 일치
    csv_norm = normalize_title(csv_title)
    if csv_norm in book_by_norm:
        candidates = book_by_norm[csv_norm]
        if len(candidates) == 1:
            return ('normalized', candidates[0], 1.0, None)
        else:
            return ('normalized_ambig', None, 1.0, candidates)

    # Tier 3: 퍼지 유사도 (정규화 후 4자 미만이면 생략 - 오매칭 방지)
    if len(csv_norm) < 4:
        return ('no_match', None, 0.0, None)

    best_score = 0.0
    best_books = []

    for db_norm, book in all_norm_pairs:
        # autojunk=False: 짧은 제목에서 공통 부분을 junk로 오판하지 않도록
        score = difflib.SequenceMatcher(False, csv_norm, db_norm).ratio()
        if score > best_score + 1e-9:
            best_score = score
            best_books = [book]
        elif abs(score - best_score) < 1e-9:
            best_books.append(book)

    if best_score >= threshold:
        if len(best_books) == 1:
            return ('fuzzy', best_books[0], best_score, None)
        else:
            return ('fuzzy_ambig', None, best_score, best_books)

    return ('no_match', None, best_score, None)


def read_csv(filepath):
    """UTF-8-SIG → CP949 → UTF-8 순서로 인코딩 자동 감지하여 CSV 읽기."""
    for encoding in ('utf-8-sig', 'cp949', 'utf-8'):
        try:
            with open(filepath, 'r', encoding=encoding, newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                return rows, encoding
        except (UnicodeDecodeError, LookupError):
            continue
    raise CommandError(f'CSV 파일 인코딩을 감지할 수 없습니다: {filepath}')


class Command(BaseCommand):
    help = (
        'mclass.shop의 교재 판매 내역 CSV를 mclass.co.kr로 마이그레이션합니다.\n'
        '납부완료(is_paid=True)와 미납(is_paid=False) 모두 가져옵니다.\n'
        '교재명은 정확 일치 → 정규화 → 퍼지 유사도 순으로 매칭합니다.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='CSV 파일 경로 (절대경로 권장)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='DB를 변경하지 않고 결과만 미리 확인합니다.',
        )
        parser.add_argument(
            '--similarity-threshold',
            type=float,
            default=0.85,
            metavar='FLOAT',
            help=(
                '교재명 퍼지 매칭 최소 유사도 (0.0~1.0, 기본값: 0.85). '
                '낮을수록 느슨하게 매칭합니다. 0.7 미만은 오매칭 위험이 높습니다.'
            ),
        )

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        dry_run = options['dry_run']
        similarity_threshold = options['similarity_threshold']

        if not (0.0 < similarity_threshold <= 1.0):
            raise CommandError('--similarity-threshold는 0.0 초과 1.0 이하의 값이어야 합니다.')

        # 파일 경로 해석: 절대경로가 아니면 프로젝트 루트 기준
        if not os.path.isabs(csv_path):
            from django.conf import settings
            csv_path = os.path.join(settings.BASE_DIR, csv_path)

        if not os.path.exists(csv_path):
            raise CommandError(f'CSV 파일을 찾을 수 없습니다: {csv_path}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN 모드] DB가 변경되지 않습니다.\n'))

        # CSV 읽기
        rows, encoding = read_csv(csv_path)
        self.stdout.write(
            f'파일 읽기 완료: {os.path.basename(csv_path)} '
            f'(인코딩: {encoding}, 전체 {len(rows)}행)\n'
        )

        if not rows:
            self.stdout.write(self.style.WARNING('CSV 파일이 비어있습니다.'))
            return

        # 컬럼 유효성 검사
        actual_columns = set(rows[0].keys())
        missing = REQUIRED_COLUMNS - actual_columns
        if missing:
            raise CommandError(
                f'필수 컬럼이 없습니다: {", ".join(sorted(missing))}\n'
                f'현재 컬럼: {", ".join(sorted(actual_columns))}'
            )

        # 납부여부 분류
        paid_rows = [r for r in rows if str(r.get('납부여부', '') or '').strip() == '납부완료']
        unpaid_rows_count = len(rows) - len(paid_rows)
        self.stdout.write(
            f'납부완료: {len(paid_rows)}행 / 미납: {unpaid_rows_count}행 / 합계: {len(rows)}행\n'
        )

        # ── DB 교재 캐시: 루프 시작 전 한 번만 조회 ────────────────────────
        _book_by_exact: dict = {}        # 원본 제목 → Book
        _book_by_norm: dict = {}         # 정규화 제목 → [Book, ...]
        _all_norm_pairs: list = []       # [(정규화 제목, Book), ...]
        book_result_cache: dict = {}     # CSV 교재명 → Book (중복 탐색 방지)

        all_db_books = list(Book.objects.all())
        self.stdout.write(f'교재 DB 캐시 로드: {len(all_db_books)}종\n')

        for book in all_db_books:
            _book_by_exact[book.title] = book
            norm_key = normalize_title(book.title)
            _book_by_norm.setdefault(norm_key, []).append(book)
            _all_norm_pairs.append((norm_key, book))

        # ── 학생 캐시 ─────────────────────────────────────────────────────
        student_cache = {}           # {학생명: Student 객체 or 'not_found'/'duplicate'/'conflict'}
        unique_student_results = {}  # {학생명: 결과 문자열}
        student_id_updated = set()   # student_id가 업데이트된 고유 학생명

        # ── 통계 카운터 ───────────────────────────────────────────────────
        stats = {
            'total_rows': len(rows),
            # 교재 매칭 단계별
            'book_exact': 0,
            'book_normalized': 0,
            'book_fuzzy': 0,
            'book_ambiguous': 0,
            'book_created': 0,
            # 판매 내역
            'sale_created_paid': 0,
            'sale_created_unpaid': 0,
            'sale_skipped_duplicate': 0,
            'sale_skipped_no_student': 0,
            'row_error': 0,
        }

        skipped_student_details = []  # [(학생명, 사유)]
        created_books = []            # 새로 생성된 교재 목록
        fuzzy_match_log = []          # [{csv_title, db_title, score, book_pk}]
        ambiguous_match_log = []      # [{csv_title, tier, score, candidates}]

        try:
            with transaction.atomic():
                for row_num, row in enumerate(rows, start=1):

                    # 납부 여부 판단
                    is_paid_str = str(row.get('납부여부', '') or '').strip()
                    is_paid = (is_paid_str == '납부완료')

                    # 값 추출
                    student_name = str(row.get('학생명', '') or '').strip()
                    shop_student_id = str(row.get('학생코드', '') or '').strip()
                    book_title = str(row.get('교재명', '') or '').strip()
                    price_raw = str(row.get('가격', '') or '').strip()
                    sale_date_raw = str(row.get('지급일', '') or '').strip()
                    payment_date_raw = str(row.get('납부일', '') or '').strip()

                    # 필수값 검사
                    if not student_name or not shop_student_id or not book_title:
                        self.stdout.write(
                            self.style.WARNING(f'  {row_num}행: 필수값 누락 (학생명/학생코드/교재명) → 건너뜀')
                        )
                        stats['row_error'] += 1
                        continue

                    # 날짜 파싱
                    sale_date = parse_date(sale_date_raw)
                    if not sale_date:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  {row_num}행 [{student_name}]: 지급일 형식 오류 "{sale_date_raw}" → 건너뜀'
                            )
                        )
                        stats['row_error'] += 1
                        continue

                    # 납부일: 납부완료인 경우만 사용, 미납이면 None
                    payment_date = parse_date(payment_date_raw) if is_paid else None

                    # 금액 파싱
                    try:
                        price = int(str(price_raw).replace(',', '').strip())
                    except (ValueError, TypeError):
                        self.stdout.write(
                            self.style.WARNING(
                                f'  {row_num}행 [{student_name}]: 가격 형식 오류 "{price_raw}" → 건너뜀'
                            )
                        )
                        stats['row_error'] += 1
                        continue

                    # ── Phase 2: 학생 매칭 ───────────────────────────────────
                    if student_name not in student_cache:
                        students_qs = Student.objects.filter(name=student_name)
                        count = students_qs.count()

                        if count == 0:
                            student_cache[student_name] = 'not_found'
                            skipped_student_details.append((student_name, '이름 없음 (mclass.co.kr에 없는 학생)'))
                            unique_student_results[student_name] = 'not_found'

                        elif count > 1:
                            student_cache[student_name] = 'duplicate'
                            skipped_student_details.append(
                                (student_name, f'동명이인 {count}명 존재 → 수동 처리 필요')
                            )
                            unique_student_results[student_name] = 'duplicate'

                        else:
                            student = students_qs.first()

                            if student.student_id != shop_student_id:
                                conflict = Student.objects.filter(
                                    student_id=shop_student_id
                                ).exclude(pk=student.pk).first()

                                if conflict:
                                    reason = (
                                        f'student_id 충돌: shop의 {shop_student_id}를 '
                                        f'이미 {conflict.name}이(가) 사용 중'
                                    )
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

                    cached = student_cache[student_name]

                    if cached in ('not_found', 'duplicate', 'conflict'):
                        stats['sale_skipped_no_student'] += 1
                        continue

                    student = cached

                    # ── Phase 3: 교재 매칭 (3단계 tiered matching) ───────────
                    if book_title not in book_result_cache:

                        tier, matched_book, score, ambig = find_book(
                            book_title,
                            _book_by_exact,
                            _book_by_norm,
                            _all_norm_pairs,
                            threshold=similarity_threshold,
                        )

                        if tier == 'exact':
                            book_result_cache[book_title] = matched_book
                            stats['book_exact'] += 1

                        elif tier == 'normalized':
                            book_result_cache[book_title] = matched_book
                            stats['book_normalized'] += 1

                        elif tier == 'fuzzy':
                            book_result_cache[book_title] = matched_book
                            stats['book_fuzzy'] += 1
                            fuzzy_match_log.append({
                                'csv_title': book_title,
                                'db_title': matched_book.title,
                                'score': score,
                                'book_pk': matched_book.pk if matched_book.pk else '-',
                            })

                        else:
                            # normalized_ambig / fuzzy_ambig / no_match → 신규 교재 생성
                            if tier in ('normalized_ambig', 'fuzzy_ambig'):
                                stats['book_ambiguous'] += 1
                                ambiguous_match_log.append({
                                    'csv_title': book_title,
                                    'tier': tier,
                                    'score': score,
                                    'candidates': [
                                        {'pk': b.pk, 'title': b.title} for b in ambig
                                    ],
                                })

                            placeholder_isbn = make_placeholder_isbn(book_title)
                            if not dry_run:
                                book_obj, created = Book.objects.get_or_create(
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
                                # 이미 있으면 그대로 사용 (이전 실행분)
                            else:
                                book_obj = Book(
                                    title=book_title,
                                    isbn=placeholder_isbn,
                                    price=price,
                                )
                                stats['book_created'] += 1
                                created_books.append(book_title)

                            book_result_cache[book_title] = book_obj

                    book = book_result_cache[book_title]

                    # ── Phase 4: BookSale 생성 ──────────────────────────────
                    if not dry_run and book.pk:
                        already_exists = BookSale.objects.filter(
                            student=student,
                            book=book,
                            sale_date=sale_date,
                        ).exists()

                        if already_exists:
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

        # ── Phase 5: 요약 보고서 출력 ──────────────────────────────────────
        matched_count = sum(1 for v in unique_student_results.values() if v == 'matched')
        not_found_count = sum(1 for v in unique_student_results.values() if v == 'not_found')
        duplicate_count = sum(1 for v in unique_student_results.values() if v == 'duplicate')
        conflict_count = sum(1 for v in unique_student_results.values() if v == 'conflict')
        total_created = stats['sale_created_paid'] + stats['sale_created_unpaid']
        total_book_matched = stats['book_exact'] + stats['book_normalized'] + stats['book_fuzzy']

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
        self.stdout.write(
            self.style.SUCCESS(f'  기존 교재 매칭 합계: {total_book_matched}건')
        )
        self.stdout.write(f'    정확 일치:                {stats["book_exact"]}건')
        self.stdout.write(f'    정규화 일치 (공백/괄호):   {stats["book_normalized"]}건')
        self.stdout.write(
            f'    퍼지 유사도 (≥{similarity_threshold:.0%}):     {stats["book_fuzzy"]}건'
        )
        self.stdout.write(self.style.WARNING(f'  모호 매칭 (신규 생성됨): {stats["book_ambiguous"]}건'))
        self.stdout.write(f'  신규 생성 (placeholder ISBN): {stats["book_created"]}종')
        self.stdout.write('')

        self.stdout.write('[ 판매 내역 (BookSale) ]')
        self.stdout.write(self.style.SUCCESS(f'  생성 합계: {total_created}건'))
        self.stdout.write(f'    납부완료 (is_paid=True):  {stats["sale_created_paid"]}건')
        self.stdout.write(f'    미납 (is_paid=False):     {stats["sale_created_unpaid"]}건')
        self.stdout.write(f'  중복으로 건너뜀: {stats["sale_skipped_duplicate"]}건')
        self.stdout.write(f'  학생 미매칭으로 건너뜀: {stats["sale_skipped_no_student"]}건')
        self.stdout.write(f'  행 오류: {stats["row_error"]}건')

        # 퍼지 매칭 교재 목록 (중복 제거)
        if fuzzy_match_log:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('[ 퍼지 매칭 교재 목록 - 검토 필요 ]'))
            self.stdout.write(
                f'  {"CSV 교재명":<38} {"DB 교재명":<38} {"유사도":>6}  {"PK":>5}'
            )
            self.stdout.write('  ' + '-' * 92)
            seen_csv = set()
            for entry in fuzzy_match_log:
                if entry['csv_title'] in seen_csv:
                    continue
                seen_csv.add(entry['csv_title'])
                csv_t = entry['csv_title'][:36]
                db_t = entry['db_title'][:36]
                pct = f"{entry['score']:.1%}"
                pk = str(entry['book_pk'])
                self.stdout.write(f'  {csv_t:<38} {db_t:<38} {pct:>6}  {pk:>5}')

        # 모호 매칭 교재 목록
        if ambiguous_match_log:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('[ 모호 매칭 교재 - 수동 처리 필요 (신규 교재로 생성됨) ]'))
            seen_ambig = set()
            for entry in ambiguous_match_log:
                if entry['csv_title'] in seen_ambig:
                    continue
                seen_ambig.add(entry['csv_title'])
                self.stdout.write(self.style.ERROR(
                    f'  CSV: {entry["csv_title"]}  '
                    f'(tier={entry["tier"]}, 유사도={entry["score"]:.1%})'
                ))
                for c in entry['candidates']:
                    self.stdout.write(f'      후보 DB 교재: pk={c["pk"]}  {c["title"]}')

        # 건너뛴 학생 목록
        if skipped_student_details:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('[ 건너뛴 학생 목록 ]'))
            seen = set()
            for name, reason in skipped_student_details:
                key = (name, reason)
                if key not in seen:
                    seen.add(key)
                    self.stdout.write(self.style.WARNING(f'  - {name}: {reason}'))

        # student_id 업데이트 학생 목록
        if student_id_updated:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('[ student_id 업데이트된 학생 ]'))
            for name in sorted(student_id_updated):
                self.stdout.write(f'  - {name}')

        # 신규 생성 교재 목록
        if created_books:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('[ 새로 생성된 교재 목록 ]'))
            for title in created_books:
                placeholder = make_placeholder_isbn(title)
                self.stdout.write(f'  + {title}  (ISBN: {placeholder})')

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
