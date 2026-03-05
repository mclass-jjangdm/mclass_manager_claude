"""
mclass.shop → mclass.co.kr 교재 판매 데이터 마이그레이션 명령어

사용법:
    # 미리 보기 (DB 변경 없음)
    python manage.py import_shop_sales data.csv --mapping-file compare_title.csv --dry-run

    # 실제 적용
    python manage.py import_shop_sales data.csv --mapping-file compare_title.csv

교재 매칭 규칙:
    - compare_title.csv 에 있는 shop 교재명  → co.kr 교재명으로 치환하여 DB 검색
    - compare_title.csv 에 없는 shop 교재명  → co.kr에 없는 별개 교재 → placeholder 생성

납부 처리:
    납부완료 → is_paid=True,  payment_date=납부일
    미납     → is_paid=False, payment_date=None
"""

import csv
import hashlib
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from bookstore.models import Book, BookSale
from students.models import Student


REQUIRED_COLUMNS = {'학생명', '학생코드', '교재명', '가격', '지급일', '납부여부', '납부일'}
DATE_FORMATS = ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d']


# ── 헬퍼 함수 ────────────────────────────────────────────────────────────────

def parse_date(value):
    if not value or not str(value).strip():
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    return None


def make_placeholder_isbn(title):
    h = hashlib.md5(title.encode('utf-8')).hexdigest()[:12]
    return f'SHOP-{h}'


def load_csv(filepath):
    """UTF-8-SIG → CP949 → UTF-8 순으로 인코딩 자동 감지."""
    for encoding in ('utf-8-sig', 'cp949', 'utf-8'):
        try:
            with open(filepath, 'r', encoding=encoding, newline='') as f:
                rows = list(csv.DictReader(f))
                return rows, encoding
        except (UnicodeDecodeError, LookupError):
            continue
    raise CommandError(f'파일 인코딩을 감지할 수 없습니다: {filepath}')


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


# ── 커맨드 ────────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = (
        'mclass.shop 교재 판매 내역 CSV를 mclass.co.kr로 마이그레이션합니다.\n'
        '--mapping-file 로 shop↔co.kr 교재명 대응표를 지정하세요.\n'
        '대응표에 없는 shop 교재명은 co.kr에 없는 별개 교재로 처리합니다.'
    )

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='판매 내역 CSV 파일 경로')
        parser.add_argument(
            '--mapping-file', type=str, default='', metavar='PATH',
            help='교재명 매핑 CSV 경로 (shop명,co.kr명 형식)',
        )
        parser.add_argument(
            '--dry-run', action='store_true', default=False,
            help='DB를 변경하지 않고 결과만 미리 확인합니다.',
        )

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        mapping_path = options['mapping_file']
        dry_run = options['dry_run']

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
            self.stdout.write('교재명 매핑 파일: 사용 안 함 (모든 교재가 신규로 처리됩니다)')

        # ── CSV 읽기 ────────────────────────────────────────────────────────
        rows, encoding = load_csv(csv_path)
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
        self.stdout.write(
            f'납부완료: {paid_count}행 / 미납: {len(rows) - paid_count}행 / 합계: {len(rows)}행\n'
        )

        # ── DB 교재 캐시 (제목으로 빠른 조회) ──────────────────────────────
        # co.kr 제목 → Book 객체
        book_by_title: dict = {}
        for book in Book.objects.all():
            book_by_title[book.title] = book
        self.stdout.write(f'교재 DB 캐시 로드: {len(book_by_title)}종\n')

        # ── 캐시 & 통계 초기화 ──────────────────────────────────────────────
        book_result_cache: dict = {}  # {shop_title → Book}
        student_cache: dict = {}
        unique_student_results: dict = {}
        student_id_updated: set = set()

        stats = {
            'total_rows': len(rows),
            'book_mapped': 0,       # 매핑 파일로 co.kr DB 교재와 연결됨
            'book_created': 0,      # 매핑 파일 없음 → 신규 placeholder 생성
            'book_map_not_found': 0,# 매핑 파일에 있으나 DB에서 못 찾음 → placeholder
            'sale_created_paid': 0,
            'sale_created_unpaid': 0,
            'sale_skipped_duplicate': 0,
            'sale_skipped_no_student': 0,
            'row_error': 0,
        }

        skipped_student_details = []
        mapped_books_log = []       # 매핑 성공 내역
        map_not_found_log = []      # 매핑 파일에 있으나 DB에서 못 찾음
        new_books_log = []          # 신규 생성 교재 (매핑 파일에 없음)

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

                    # 필수값 검사
                    if not student_name or not shop_student_id or not book_title:
                        self.stdout.write(self.style.WARNING(
                            f'  {row_num}행: 필수값 누락 → 건너뜀'
                        ))
                        stats['row_error'] += 1
                        continue

                    # 날짜 파싱
                    sale_date = parse_date(sale_date_raw)
                    if not sale_date:
                        self.stdout.write(self.style.WARNING(
                            f'  {row_num}행 [{student_name}]: 지급일 형식 오류 "{sale_date_raw}" → 건너뜀'
                        ))
                        stats['row_error'] += 1
                        continue

                    # 납부완료만 납부일 사용, 미납은 None
                    payment_date = parse_date(payment_date_raw) if is_paid else None

                    # 금액 파싱
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
                                    reason = (
                                        f'student_id 충돌: {shop_student_id} → '
                                        f'{conflict.name} 사용 중'
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

                    cached_student = student_cache[student_name]
                    if cached_student in ('not_found', 'duplicate', 'conflict'):
                        stats['sale_skipped_no_student'] += 1
                        continue
                    student = cached_student

                    # ── Phase 3: 교재 매칭 ───────────────────────────────────
                    if book_title not in book_result_cache:

                        co_kr_title = title_mapping.get(book_title)

                        if co_kr_title:
                            # 매핑 파일에 있음 → co.kr 제목으로 DB 조회
                            db_book = book_by_title.get(co_kr_title)
                            if db_book:
                                # 매핑 성공
                                book_result_cache[book_title] = db_book
                                stats['book_mapped'] += 1
                                mapped_books_log.append({
                                    'shop_title': book_title,
                                    'co_kr_title': co_kr_title,
                                    'book_pk': db_book.pk,
                                })
                            else:
                                # 매핑 파일에는 있으나 DB에 해당 제목 없음
                                stats['book_map_not_found'] += 1
                                map_not_found_log.append({
                                    'shop_title': book_title,
                                    'co_kr_title': co_kr_title,
                                })
                                # placeholder 생성
                                placeholder_isbn = make_placeholder_isbn(book_title)
                                if not dry_run:
                                    db_book, created = Book.objects.get_or_create(
                                        isbn=placeholder_isbn,
                                        defaults={
                                            'title': book_title,
                                            'price': price,
                                            'original_price': 0,
                                            'cost_price': 0,
                                            'stock': 0,
                                            'memo': 'imported from mclass.shop (매핑 DB 불일치)',
                                        }
                                    )
                                else:
                                    db_book = Book(
                                        title=book_title,
                                        isbn=placeholder_isbn,
                                        price=price,
                                    )
                                book_result_cache[book_title] = db_book

                        else:
                            # 매핑 파일에 없음 → co.kr에 없는 별개 교재 → placeholder
                            placeholder_isbn = make_placeholder_isbn(book_title)
                            if not dry_run:
                                db_book, created = Book.objects.get_or_create(
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
                                    new_books_log.append(book_title)
                            else:
                                db_book = Book(
                                    title=book_title,
                                    isbn=placeholder_isbn,
                                    price=price,
                                )
                                stats['book_created'] += 1
                                new_books_log.append(book_title)
                            book_result_cache[book_title] = db_book

                    book = book_result_cache[book_title]

                    # ── Phase 4: BookSale 생성 ──────────────────────────────
                    # memo에 원래 shop 교재명 저장 → 재실행 시에도 정확한 중복 감지
                    memo_key = f'shop:{book_title}'

                    if not dry_run and book.pk:
                        # 중복 체크 1: 학생이 이미 해당 교재를 보유 (날짜 무관)
                        # → 기존 수동 입력 데이터와 날짜가 달라도 같은 교재 중복 방지
                        already_has_book = BookSale.objects.filter(
                            student=student, book=book
                        ).exists()
                        # 중복 체크 2: 이전 실행에서 같은 shop 교재명으로 이미 입력됨
                        # → 매핑 파일 수정 후 재실행 시 Book FK가 달라도 중복 방지
                        already_imported = BookSale.objects.filter(
                            student=student, memo=memo_key
                        ).exists()

                        if already_has_book or already_imported:
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
                            memo=memo_key,
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
        self.stdout.write(self.style.SUCCESS(
            f'  매핑 파일로 co.kr DB 연결:  {stats["book_mapped"]}건'
        ))
        self.stdout.write(self.style.WARNING(
            f'  매핑 있으나 DB 불일치 (신규): {stats["book_map_not_found"]}건'
        ))
        self.stdout.write(
            f'  매핑 없음 → 신규 교재 생성:  {stats["book_created"]}건'
        )
        self.stdout.write('')

        self.stdout.write('[ 판매 내역 (BookSale) ]')
        self.stdout.write(self.style.SUCCESS(f'  생성 합계: {total_created}건'))
        self.stdout.write(f'    납부완료 (is_paid=True):  {stats["sale_created_paid"]}건')
        self.stdout.write(f'    미납 (is_paid=False):     {stats["sale_created_unpaid"]}건')
        self.stdout.write(f'  중복 건너뜀: {stats["sale_skipped_duplicate"]}건')
        self.stdout.write(f'  학생 미매칭 건너뜀: {stats["sale_skipped_no_student"]}건')
        self.stdout.write(f'  행 오류: {stats["row_error"]}건')

        # 매핑 성공 목록
        if mapped_books_log:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('[ 매핑 성공 교재 목록 ]'))
            self.stdout.write(
                f'  {"shop 교재명":<40} {"→ co.kr DB 교재명":<40} {"PK":>5}'
            )
            self.stdout.write('  ' + '-' * 88)
            seen = set()
            for e in mapped_books_log:
                if e['shop_title'] in seen:
                    continue
                seen.add(e['shop_title'])
                self.stdout.write(
                    f'  {e["shop_title"][:38]:<40} {e["co_kr_title"][:38]:<40} {e["book_pk"]:>5}'
                )

        # 매핑 파일에 있으나 DB에서 못 찾은 경우 (경고)
        if map_not_found_log:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('[ 매핑 DB 불일치 - compare_title.csv 확인 필요 ]'))
            self.stdout.write('  매핑 파일에는 있으나 co.kr DB에서 해당 제목을 찾지 못했습니다.')
            for e in map_not_found_log:
                self.stdout.write(self.style.ERROR(
                    f'  shop:   {e["shop_title"]}\n'
                    f'  co.kr:  {e["co_kr_title"]}  ← DB에 없음'
                ))

        # 신규 생성 교재 목록
        if new_books_log:
            self.stdout.write('')
            self.stdout.write('[ 신규 생성 교재 목록 (매핑 파일에 없는 교재) ]')
            seen = set()
            for title in new_books_log:
                if title in seen:
                    continue
                seen.add(title)
                self.stdout.write(f'  + {title}')

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
