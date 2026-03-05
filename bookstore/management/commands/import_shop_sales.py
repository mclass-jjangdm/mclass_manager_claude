"""
mclass.shop → mclass.co.kr 교재 판매 데이터 마이그레이션 명령어

사용법:
    # 미리 보기 (DB 변경 없음)
    python manage.py import_shop_sales shop_sales.csv --dry-run

    # 실제 적용
    python manage.py import_shop_sales shop_sales.csv

CSV 컬럼 (순서 무관, 헤더명 정확히 일치):
    student_name, student_id, book_title, book_isbn,
    sale_date, price, quantity, payment_date
"""

import csv
import os
from datetime import datetime, date

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from bookstore.models import Book, BookSale
from students.models import Student


REQUIRED_COLUMNS = {
    'student_name', 'student_id', 'book_title', 'book_isbn',
    'sale_date', 'price', 'quantity', 'payment_date',
}

DATE_FORMATS = ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d']


def parse_date(value):
    """날짜 문자열을 date 객체로 변환. 실패 시 None 반환."""
    if not value or not str(value).strip():
        return None
    value = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def read_csv(filepath):
    """UTF-8-SIG → CP949 순서로 인코딩 자동 감지하여 CSV 읽기."""
    for encoding in ('utf-8-sig', 'cp949', 'utf-8'):
        try:
            with open(filepath, 'r', encoding=encoding, newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if rows:
                    return rows, encoding
                return rows, encoding
        except (UnicodeDecodeError, LookupError):
            continue
    raise CommandError(f'CSV 파일 인코딩을 감지할 수 없습니다: {filepath}')


class Command(BaseCommand):
    help = 'mclass.shop의 결제 완료 교재 판매 내역을 mclass.co.kr로 마이그레이션합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='CSV 파일 경로 (절대경로 또는 Django 프로젝트 루트 기준 상대경로)',
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
        try:
            rows, encoding = read_csv(csv_path)
        except CommandError as e:
            raise e

        self.stdout.write(f'파일 읽기 완료: {csv_path} (인코딩: {encoding}, {len(rows)}행)')

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

        # 통계 카운터
        stats = {
            'total_rows': len(rows),
            'student_matched': 0,
            'student_id_updated': 0,
            'student_not_found': 0,
            'student_id_conflict': 0,
            'student_name_duplicate': 0,
            'book_existing': 0,
            'book_created': 0,
            'sale_created': 0,
            'sale_skipped_duplicate': 0,
            'sale_skipped_no_student': 0,
            'row_error': 0,
        }

        skipped_students = []   # (이름, 사유)
        created_books = []      # 새로 생성된 교재 목록
        skipped_students_set = set()  # 건너뛴 학생 이름 집합

        try:
            with transaction.atomic():
                for row_num, row in enumerate(rows, start=2):  # 헤더가 1행이므로 데이터는 2행부터
                    # 값 추출 및 정리
                    student_name = str(row.get('student_name', '') or '').strip()
                    shop_student_id = str(row.get('student_id', '') or '').strip()
                    book_title = str(row.get('book_title', '') or '').strip()
                    book_isbn = str(row.get('book_isbn', '') or '').strip()
                    sale_date_raw = str(row.get('sale_date', '') or '').strip()
                    price_raw = str(row.get('price', '') or '').strip()
                    quantity_raw = str(row.get('quantity', '') or '').strip()
                    payment_date_raw = str(row.get('payment_date', '') or '').strip()

                    # 필수값 검사
                    if not student_name or not shop_student_id or not book_isbn:
                        self.stdout.write(
                            self.style.WARNING(f'  {row_num}행: 필수값 누락 (학생명/고유번호/ISBN) → 건너뜀')
                        )
                        stats['row_error'] += 1
                        continue

                    # 날짜 파싱
                    sale_date = parse_date(sale_date_raw)
                    payment_date = parse_date(payment_date_raw)
                    if not sale_date:
                        self.stdout.write(
                            self.style.WARNING(f'  {row_num}행: 판매일 형식 오류 "{sale_date_raw}" → 건너뜀')
                        )
                        stats['row_error'] += 1
                        continue

                    # 금액/수량 파싱
                    try:
                        price = int(str(price_raw).replace(',', '').strip())
                        quantity = int(str(quantity_raw).replace(',', '').strip())
                    except (ValueError, TypeError):
                        self.stdout.write(
                            self.style.WARNING(f'  {row_num}행: 금액/수량 형식 오류 → 건너뜀')
                        )
                        stats['row_error'] += 1
                        continue

                    # ── Phase 2: 학생 매칭 ──────────────────────────────────────
                    if student_name in skipped_students_set:
                        # 이미 건너뛰기로 결정된 학생
                        stats['sale_skipped_no_student'] += 1
                        continue

                    students_qs = Student.objects.filter(name=student_name)
                    student_count = students_qs.count()

                    if student_count == 0:
                        # 이름 없음
                        skipped_students.append((student_name, '이름 없음'))
                        skipped_students_set.add(student_name)
                        stats['student_not_found'] += 1
                        stats['sale_skipped_no_student'] += 1
                        continue

                    if student_count > 1:
                        # 동명이인
                        skipped_students.append((student_name, f'동명이인 {student_count}명 존재'))
                        skipped_students_set.add(student_name)
                        stats['student_name_duplicate'] += 1
                        stats['sale_skipped_no_student'] += 1
                        continue

                    student = students_qs.first()
                    stats['student_matched'] += 1

                    # student_id 업데이트 필요 여부 확인
                    if student.student_id != shop_student_id:
                        # 충돌 검사: 다른 학생이 해당 student_id를 이미 사용 중?
                        conflict = Student.objects.filter(
                            student_id=shop_student_id
                        ).exclude(pk=student.pk).first()

                        if conflict:
                            reason = f'student_id 충돌 (이미 {conflict.name}이 {shop_student_id} 사용 중)'
                            skipped_students.append((student_name, reason))
                            skipped_students_set.add(student_name)
                            stats['student_id_conflict'] += 1
                            stats['sale_skipped_no_student'] += 1
                            continue

                        # student_id 업데이트
                        if not dry_run:
                            student.student_id = shop_student_id
                            student.save(update_fields=['student_id'])
                        stats['student_id_updated'] += 1

                    # ── Phase 3: 교재 매칭 및 자동 생성 ────────────────────────
                    try:
                        book = Book.objects.get(isbn=book_isbn)
                        stats['book_existing'] += 1
                    except Book.DoesNotExist:
                        # 신규 교재 생성
                        if not dry_run:
                            book = Book.objects.create(
                                title=book_title,
                                isbn=book_isbn,
                                price=price,
                                original_price=0,
                                cost_price=0,
                                stock=0,
                                memo='imported from mclass.shop',
                            )
                        else:
                            # dry-run: 가상 book 객체 (저장 안 함)
                            book = Book(
                                title=book_title,
                                isbn=book_isbn,
                                price=price,
                            )
                        stats['book_created'] += 1
                        created_books.append(f'{book_title} (ISBN: {book_isbn})')

                    # ── Phase 4: BookSale 생성 ───────────────────────────────
                    # dry-run 에서는 book.pk가 없을 수 있으므로 중복 검사 생략
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
                            quantity=quantity,
                            is_paid=True,
                            payment_date=payment_date,
                            memo='imported from mclass.shop',
                        )

                    stats['sale_created'] += 1

                # dry-run이면 롤백
                if dry_run:
                    transaction.set_rollback(True)

        except Exception as e:
            raise CommandError(f'마이그레이션 중 오류 발생: {e}')

        # ── Phase 5: 요약 보고서 출력 ─────────────────────────────────────────
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('=== 마이그레이션 결과 ==='))
        self.stdout.write('=' * 50)
        self.stdout.write(f'전체 처리 행: {stats["total_rows"]}')
        self.stdout.write('')
        self.stdout.write('[ 학생 ]')
        self.stdout.write(f'  매칭 성공: {stats["student_matched"]}명')
        self.stdout.write(f'  student_id 업데이트: {stats["student_id_updated"]}명')
        self.stdout.write(f'  이름 없음 (건너뜀): {stats["student_not_found"]}명')
        self.stdout.write(f'  student_id 충돌 (건너뜀): {stats["student_id_conflict"]}명')
        self.stdout.write(f'  동명이인 (건너뜀): {stats["student_name_duplicate"]}명')
        self.stdout.write('')
        self.stdout.write('[ 교재 ]')
        self.stdout.write(f'  기존 교재 매칭: {stats["book_existing"]}종')
        self.stdout.write(f'  신규 교재 생성: {stats["book_created"]}종')
        self.stdout.write('')
        self.stdout.write('[ BookSale ]')
        self.stdout.write(f'  생성: {stats["sale_created"]}건')
        self.stdout.write(f'  중복 건너뜀: {stats["sale_skipped_duplicate"]}건')
        self.stdout.write(f'  학생 미매칭으로 건너뜀: {stats["sale_skipped_no_student"]}건')
        self.stdout.write(f'  행 오류 건너뜀: {stats["row_error"]}건')

        if skipped_students:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('[ 건너뛴 학생 목록 ]'))
            # 중복 제거하여 출력
            seen = set()
            for name, reason in skipped_students:
                key = (name, reason)
                if key not in seen:
                    seen.add(key)
                    self.stdout.write(self.style.WARNING(f'  - {name}: {reason}'))

        if created_books:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('[ 새로 생성된 교재 목록 ]'))
            for b in created_books:
                self.stdout.write(f'  + {b}')

        self.stdout.write('=' * 50)

        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                '[DRY RUN] 위 내용은 미리보기입니다. 실제로 적용되지 않았습니다.\n'
                '실제 적용하려면 --dry-run 옵션을 제거하고 다시 실행하세요.'
            ))
        else:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('마이그레이션이 완료되었습니다.'))
