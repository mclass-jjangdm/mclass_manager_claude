from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from books.models import Book
from students.models import Student
from django.core.exceptions import ValidationError


class BookStock(models.Model):
    """도서 재고 정보"""
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        verbose_name='도서명'
    )
    quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='수량'
    )
    list_price = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='정가'
    )
    unit_price = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='단가'
    )
    selling_price = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='판매가'
    )
    memo = models.TextField(
        blank=True,
        verbose_name='메모'
    )
    received_date = models.DateField(
        verbose_name='입고일'
    )
    
    @classmethod
    def get_total_quantity(cls, book):
        return cls.objects.filter(book=book).aggregate(
            total_quantity=models.Sum('quantity')
        )['total_quantity'] or 0

    class Meta:
        verbose_name = '도서 재고'
        verbose_name_plural = '도서 재고'
        ordering = ['-received_date', 'book__name']

    def __str__(self):
        return f"{self.book.name} - {self.quantity}권"


class BookDistribution(models.Model):
    """도서 판매 정보"""
    book_stock = models.ForeignKey(
        BookStock,
        on_delete=models.CASCADE,
        verbose_name='도서'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name='학생'
    )
    sold_date = models.DateField(
        default=timezone.now,
        verbose_name='판매일'
    )
    quantity = models.PositiveIntegerField(
        default=1,  # 기본 값을 1로 설정
        validators=[MinValueValidator(1)],
        verbose_name='판매 수량'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='비고'
    )

    def clean(self):
        super().clean()
        if self.book_stock.quantity < self.quantity:
            raise ValidationError(
                {'book_stock': '재고가 부족합니다. 해당 도서의 재고는 {}권입니다.'.format(self.book_stock.quantity)}
            )

    class Meta:
        verbose_name = '도서 판매'
        verbose_name_plural = '도서 판매'
        ordering = ['-sold_date', 'book_stock__book__name']

    def __str__(self):
        return f"{self.student.name} - {self.book_stock.book.name} ({self.quantity}권)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.book_stock.quantity >= self.quantity:  # 잔여 재고가 충분한 경우
            self.book_stock.quantity -= self.quantity
            self.book_stock.save()
        else:
            # 잔여 재고가 부족한 경우 처리
            # 예: 에러 메시지 출력, 판매 취소 등
            pass  # 여기에 잔여 재고 부족 시 수행할 작업을 추가합니다.


class BookIssue(models.Model):
    book_stock = models.ForeignKey(
        'BookStock',
        on_delete=models.CASCADE,
        verbose_name='재고'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name='학생'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='수량'
    )
    issued_date = models.DateField(
        default=timezone.now,
        verbose_name='출고일'
    )
    memo = models.TextField(
        null=True,
        blank=True,
        verbose_name='비고'
    )

    def clean(self):
        super().clean()
        if self.book_stock.quantity < self.quantity:
            raise ValidationError('재고가 부족합니다.')

    def save(self, *args, **kwargs):
        self.book_stock.quantity -= self.quantity
        self.book_stock.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '도서 출고'
        verbose_name_plural = '도서 출고 목록'

    def __str__(self):
        return f"{self.student.name} - {self.book_stock.book.name} ({self.quantity}권)"


class BookReturn(models.Model):
    book_stock = models.ForeignKey(BookStock, on_delete=models.CASCADE, verbose_name='재고')
    quantity = models.PositiveIntegerField(verbose_name='반품 수량')
    return_date = models.DateField(verbose_name='반품 날짜')

    class Meta:
        verbose_name = '도서 반품'
        verbose_name_plural = '도서 반품 목록'

    def __str__(self):
        return f"{self.book_stock.book.name} - {self.quantity}권 반품"
