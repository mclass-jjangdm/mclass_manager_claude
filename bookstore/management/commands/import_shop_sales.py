"""
mclass.shop → mclass.co.kr 교재 판매 데이터 마이그레이션 명령어

사용법:
    # 미리 보기 (DB 변경 없음)
    python manage.py import_shop_sales C:/path/to/file.csv --dry-run

    # 실제 적용
    python manage.py import_shop_sales C:/path/to/file.csv

CSV 컬럼 (mclass.shop 내보내기 형식):
    학생명, 학생코드, 교재명, 가격, 지급일, 납부여부, 납부일

처리 대상:
    납부완료 → is_paid=True, payment_date=납부일
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


# mclass.shop CSV 컬럼명
REQUIRED_COLUMNS = {'학생명', '학생코드', '교재명', '가격', '지급일', '납부여부', '납부일'}

DATE_FORMATS = ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d']


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
        '학생 고유번호(student_id)를 shop 기준으로 통일합니다.'
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

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        dry_run = options['dry_run']

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
        self.stdout.write(f'파일 읽기 완료: {os.path.basename(csv_path)} (인코딩: {encoding}, 전체 {len(rows)}행)\n')

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
        unpaid_rows = [r for r in rows if str(r.get('납부여부', '') or '').strip() != '납부완료']
        self.stdout.write(
            f'납부완료: {len(paid_rows)}행 / 미납: {len(unpaid_rows)}행 / 합계: {len(rows)}행\n'
        )

        # ── 캐시: 반복 DB 조회 방지 ──────────────────────────────────────────
        # {학생명: student_object or 'not_found'/'duplicate'/'conflict'}
        student_cache = {}
        # {교재명: book_object}
        book_cache = {}
        # 학생 관련 통계 (고유 학생 기준)
        unique_student_results = {}  # {학생명: 결과}
        student_id_updated = set()   # student_id가 실제 업데이트된 고유 학생명 집합

        # ── 통계 카운터 ───────────────────────────────────────────────────────
        stats = {
            'total_rows': len(rows),
            'book_existing': 0,
            'book_created': 0,
            'sale_created_paid': 0,
            'sale_created_unpaid': 0,
            'sale_skipped_duplicate': 0,
            'sale_skipped_no_student': 0,
            'row_error': 0,
        }

        skipped_student_details = []  # [(학생명, 사유)] 건너뛴 학생 상세
        created_books = []            # 새로 생성된 교재 목록

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
                            self.style.WARNING(f'  {row_num}행 [{student_name}]: 지급일 형식 오류 "{sale_date_raw}" → 건너뜀')
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
                            self.style.WARNING(f'  {row_num}행 [{student_name}]: 가격 형식 오류 "{price_raw}" → 건너뜀')
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

                            # student_id 업데이트 필요 여부 확인
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
                                    # student_id 업데이트
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

                    student = cached  # 실제 Student 객체

                    # ── Phase 3: 교재 매칭 및 자동 생성 ─────────────────────
                    if book_title not in book_cache:
                        try:
                            book = Book.objects.get(title=book_title)
                            book_cache[book_title] = book
                            stats['book_existing'] += 1
                        except Book.DoesNotExist:
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
                                    stats['book_existing'] += 1
                            else:
                                book = Book(title=book_title, isbn=placeholder_isbn, price=price)
                                stats['book_created'] += 1
                                created_books.append(book_title)
                            book_cache[book_title] = book
                        except Book.MultipleObjectsReturned:
                            book = Book.objects.filter(title=book_title).first()
                            book_cache[book_title] = book
                            stats['book_existing'] += 1
                    else:
                        book = book_cache[book_title]

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

                # dry-run이면 롤백
                if dry_run:
                    transaction.set_rollback(True)

        except CommandError:
            raise
        except Exception as e:
            raise CommandError(f'마이그레이션 중 오류 발생: {e}')

        # ── Phase 5: 요약 보고서 출력 ──────────────────────────────────────────
        matched_count = sum(1 for v in unique_student_results.values() if v == 'matched')
        not_found_count = sum(1 for v in unique_student_results.values() if v == 'not_found')
        duplicate_count = sum(1 for v in unique_student_results.values() if v == 'duplicate')
        conflict_count = sum(1 for v in unique_student_results.values() if v == 'conflict')

        total_created = stats['sale_created_paid'] + stats['sale_created_unpaid']

        self.stdout.write('\n' + '=' * 55)
        self.stdout.write(self.style.SUCCESS('=== 마이그레이션 결과 ==='))
        self.stdout.write('=' * 55)
        self.stdout.write(f'전체 처리 행: {stats["total_rows"]}행')
        self.stdout.write('')
        self.stdout.write('[ 학생 ] (고유 학생 기준)')
        self.stdout.write(self.style.SUCCESS(f'  매칭 성공: {matched_count}명'))
        self.stdout.write(f'  → student_id 업데이트: {len(student_id_updated)}명')
        self.stdout.write(self.style.WARNING(f'  이름 없음 (건너뜀): {not_found_count}명'))
        self.stdout.write(self.style.WARNING(f'  동명이인 (건너뜀): {duplicate_count}명'))
        self.stdout.write(self.style.WARNING(f'  student_id 충돌 (건너뜀): {conflict_count}명'))
        self.stdout.write('')
        self.stdout.write('[ 교재 ]')
        self.stdout.write(f'  기존 교재 매칭 (제목 일치): {stats["book_existing"]}건')
        self.stdout.write(f'  신규 교재 생성 (placeholder ISBN): {stats["book_created"]}종')
        self.stdout.write('')
        self.stdout.write('[ 판매 내역 (BookSale) ]')
        self.stdout.write(self.style.SUCCESS(f'  생성 합계: {total_created}건'))
        self.stdout.write(f'    납부완료(is_paid=True):  {stats["sale_created_paid"]}건')
        self.stdout.write(f'    미납(is_paid=False):     {stats["sale_created_unpaid"]}건')
        self.stdout.write(f'  중복으로 건너뜀: {stats["sale_skipped_duplicate"]}건')
        self.stdout.write(f'  학생 미매칭으로 건너뜀: {stats["sale_skipped_no_student"]}건')
        self.stdout.write(f'  행 오류: {stats["row_error"]}건')

        if skipped_student_details:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('[ 건너뛴 학생 목록 ]'))
            seen = set()
            for name, reason in skipped_student_details:
                key = (name, reason)
                if key not in seen:
                    seen.add(key)
                    self.stdout.write(self.style.WARNING(f'  - {name}: {reason}'))

        if student_id_updated:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('[ student_id 업데이트된 학생 ]'))
            for name in sorted(student_id_updated):
                self.stdout.write(f'  - {name}')

        if created_books:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('[ 새로 생성된 교재 목록 ]'))
            for title in created_books:
                placeholder = make_placeholder_isbn(title)
                self.stdout.write(f'  + {title}  (ISBN: {placeholder})')

        self.stdout.write('=' * 55)

        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                '[DRY RUN] 위 내용은 미리보기입니다. DB는 변경되지 않았습니다.\n'
                '실제 적용하려면 --dry-run 옵션을 제거하고 다시 실행하세요.'
            ))
        else:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('마이그레이션이 완료되었습니다.'))
