"""
mclass.shop 마이그레이션 후 생긴 중복 BookSale 정리 명령어

동작:
    - SHOP- placeholder Book이 붙은 BookSale 중,
      같은 학생이 동일 제목의 정식 교재 BookSale도 갖고 있는 경우
      → placeholder BookSale을 DB에서 직접 삭제 (재고 변동 없음)
      → placeholder Book이 더 이상 BookSale이 없으면 Book도 삭제

사용법:
    # 미리 보기 (DB 변경 없음)
    python manage.py clean_shop_imports --dry-run

    # 실제 적용
    python manage.py clean_shop_imports
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from bookstore.models import Book, BookSale


class Command(BaseCommand):
    help = 'SHOP- placeholder로 중복 생성된 BookSale/Book을 안전하게 정리합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true', default=False,
            help='DB를 변경하지 않고 결과만 미리 확인합니다.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] DB가 변경되지 않습니다.\n'))

        # placeholder BookSale 전체 조회
        placeholder_sales = BookSale.objects.filter(
            book__isbn__startswith='SHOP-'
        ).select_related('student', 'book').order_by('student__name', 'book__title')

        total_ph = placeholder_sales.count()
        self.stdout.write(f'SHOP- placeholder BookSale 총 {total_ph}건 검색 중...\n')

        to_delete = []   # (placeholder_sale, real_sale) — 삭제 대상
        orphans = []     # placeholder_sale — 정식 교재 없음, 유지

        for sale in placeholder_sales:
            student = sale.student
            ph_title = sale.book.title

            # 같은 학생 + 동일 제목 + 정식 교재(비-placeholder)
            real_sale = BookSale.objects.filter(
                student=student,
                book__title=ph_title,
            ).exclude(
                book__isbn__startswith='SHOP-'
            ).select_related('book').first()

            if real_sale:
                to_delete.append((sale, real_sale))
            else:
                orphans.append(sale)

        # ── 결과 출력 ─────────────────────────────────────────────────────
        self.stdout.write(f'삭제 대상 (중복): {len(to_delete)}건')
        self.stdout.write(f'유지 (정식 교재 없음): {len(orphans)}건\n')

        if to_delete:
            self.stdout.write(self.style.SUCCESS('[ 삭제할 중복 placeholder BookSale ]'))
            for ph_sale, real_sale in to_delete:
                self.stdout.write(
                    f'  학생: {ph_sale.student.name:<12} | '
                    f'교재: {ph_sale.book.title[:40]:<40} | '
                    f'placeholder BookSale pk={ph_sale.pk} → 정식 BookSale pk={real_sale.pk}'
                )

        if orphans:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('[ 유지할 단독 placeholder BookSale (정식 교재 없음) ]'))
            for ph_sale in orphans:
                self.stdout.write(
                    f'  학생: {ph_sale.student.name:<12} | '
                    f'교재: {ph_sale.book.title[:40]}'
                )

        if not to_delete:
            self.stdout.write(self.style.SUCCESS('\n삭제할 중복 항목이 없습니다.'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\n[DRY RUN] 위 내용은 미리보기입니다. '
                '실제 적용하려면 --dry-run 없이 다시 실행하세요.'
            ))
            return

        # ── 실제 삭제 ─────────────────────────────────────────────────────
        try:
            with transaction.atomic():
                deleted_sale_count = 0
                placeholder_book_pks = set()

                for ph_sale, _ in to_delete:
                    ph_book_pk = ph_sale.book.pk
                    # BookSale을 ORM으로 직접 삭제 → 뷰 레벨 재고 로직 우회
                    BookSale.objects.filter(pk=ph_sale.pk).delete()
                    deleted_sale_count += 1
                    placeholder_book_pks.add(ph_book_pk)

                # BookSale이 남지 않은 placeholder Book 삭제
                deleted_book_count = 0
                for book_pk in placeholder_book_pks:
                    try:
                        book = Book.objects.get(pk=book_pk)
                        remaining_sales = BookSale.objects.filter(book=book).count()
                        if remaining_sales == 0:
                            self.stdout.write(
                                f'  placeholder Book 삭제: {book.title} (pk={book.pk})'
                            )
                            book.delete()
                            deleted_book_count += 1
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  placeholder Book 유지 (다른 학생의 BookSale {remaining_sales}건 남음): '
                                    f'{book.title} (pk={book.pk})'
                                )
                            )
                    except Book.DoesNotExist:
                        pass

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n오류 발생 (롤백됨): {e}'))
            raise

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'정리 완료: BookSale {deleted_sale_count}건 삭제, '
            f'placeholder Book {deleted_book_count}종 삭제'
        ))
        self.stdout.write(self.style.SUCCESS(
            '재고(stock)는 변경되지 않았습니다.'
        ))
