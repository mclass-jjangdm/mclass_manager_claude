"""
mclass.shop 마이그레이션 현황 진단 명령어

사용법:
    python manage.py diagnose_shop_imports

출력:
    - SHOP- placeholder Book 목록 (제목, pk, BookSale 수)
    - 같은 학생이 동일 제목의 정식 교재도 갖고 있는 중복 케이스
    - 한 학생이 같은 교재를 2건 이상 갖는 전체 현황
"""

from django.core.management.base import BaseCommand

from bookstore.models import Book, BookSale


class Command(BaseCommand):
    help = 'mclass.shop 마이그레이션 후 생긴 placeholder/중복 현황을 진단합니다.'

    def handle(self, *args, **options):

        # ── 1. SHOP- placeholder Book 현황 ─────────────────────────────────
        placeholder_books = Book.objects.filter(
            isbn__startswith='SHOP-'
        ).prefetch_related('booksale_set')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(f'[ SHOP- placeholder Book 현황 ] 총 {placeholder_books.count()}종')
        self.stdout.write('=' * 70)

        for book in placeholder_books.order_by('title'):
            sale_count = book.booksale_set.count()
            students = ', '.join(
                s.student.name for s in book.booksale_set.select_related('student').all()
            )
            self.stdout.write(
                f'  pk={book.pk:>5} | {book.title[:50]:<50} | BookSale {sale_count}건'
                + (f' → {students}' if students else '')
            )

        # ── 2. 중복 케이스: placeholder + 정식 교재 동시 보유 ─────────────
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('[ 중복 케이스: 같은 학생이 placeholder + 정식 교재 동시 보유 ]')
        self.stdout.write('=' * 70)

        placeholder_sales = BookSale.objects.filter(
            book__isbn__startswith='SHOP-'
        ).select_related('student', 'book').order_by('student__name', 'book__title')

        duplicate_count = 0
        orphan_count = 0

        for sale in placeholder_sales:
            student = sale.student
            ph_title = sale.book.title

            # 같은 학생 + 같은 제목의 정식 교재(비-placeholder) BookSale 검색
            real_sales = BookSale.objects.filter(
                student=student,
                book__title=ph_title,
            ).exclude(
                book__isbn__startswith='SHOP-'
            ).select_related('book')

            if real_sales.exists():
                duplicate_count += 1
                real_book = real_sales.first().book
                self.stdout.write(
                    self.style.ERROR(
                        f'  [중복] {student.name} | 교재: {ph_title}\n'
                        f'         → placeholder pk={sale.book.pk} (isbn={sale.book.isbn})\n'
                        f'         → 정식    pk={real_book.pk} (isbn={real_book.isbn or "없음"})\n'
                        f'         → 삭제 대상: placeholder BookSale pk={sale.pk}'
                    )
                )
            else:
                orphan_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'  [단독] {student.name} | 교재: {ph_title} '
                        f'(placeholder pk={sale.book.pk}, BookSale pk={sale.pk}) '
                        f'— 정식 교재 없음, 유지'
                    )
                )

        self.stdout.write(f'\n  중복(삭제 대상): {duplicate_count}건, 단독(유지): {orphan_count}건')

        # ── 3. 전체 BookSale 중 같은 학생이 같은 교재를 2건 이상 보유 ─────
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('[ 동일 학생 + 동일 교재명 2건 이상 보유 전체 현황 ]')
        self.stdout.write('=' * 70)

        from django.db.models import Count

        dupes = (
            BookSale.objects
            .values('student__name', 'book__title')
            .annotate(cnt=Count('pk'))
            .filter(cnt__gte=2)
            .order_by('-cnt', 'student__name')
        )

        if dupes:
            for d in dupes:
                self.stdout.write(
                    self.style.ERROR(
                        f'  {d["student__name"]} | {d["book__title"]} → {d["cnt"]}건'
                    )
                )
            self.stdout.write(f'\n  총 {len(dupes)}개 (학생+교재 조합)')
        else:
            self.stdout.write(self.style.SUCCESS('  중복 없음'))

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('진단 완료. 정리하려면: python manage.py clean_shop_imports --dry-run')
        self.stdout.write('=' * 70 + '\n')
