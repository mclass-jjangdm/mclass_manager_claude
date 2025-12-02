# bookstore/management/commands/migrate_book_issues.py
from django.core.management.base import BaseCommand
from bookstore.models import BookIssue, BookDistribution

class Command(BaseCommand):
    help = '기존 BookIssue 데이터를 BookDistribution으로 마이그레이션'

    def handle(self, *args, **kwargs):
        book_issues = BookIssue.objects.all()
        success_count = 0
        
        for issue in book_issues:
            try:
                # BookIssue 데이터를 BookDistribution으로 변환
                BookDistribution.objects.create(
                    book_stock=issue.book_stock,
                    student=issue.student,
                    sold_date=issue.issued_date,
                    quantity=issue.quantity,
                    notes=issue.memo
                )
                success_count += 1
                self.stdout.write(f"성공: {issue.student.name} - {issue.book_stock.book.name}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"실패: {issue.student.name} - {issue.book_stock.book.name}: {str(e)}"
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f'마이그레이션 완료: 총 {book_issues.count()}건 중 {success_count}건 성공'
        ))