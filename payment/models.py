from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from students.models import Student
from bookstore.models import BookStock, BookDistribution
from django.db.models import Sum, F

class Payment(models.Model):
    """결제 정보 기본 모델"""
    PAYMENT_STATUS = [
        ('pending', '미납'),
        ('partial', '부분납부'),
        ('completed', '완납'),
        ('refunded', '환불됨'),
    ]

    PAYMENT_METHOD = [
        ('cash', '현금'),
        ('card', '카드'),
        ('transfer', '계좌이체'),
        ('other', '기타'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name='학생'
    )
    paid_amount = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='납부 금액',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='pending',
        verbose_name='납부 상태',
        blank=True,
        null=True
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD,
        verbose_name='결제 수단',
        blank=True,
        null=True
    )
    payment_date = models.DateField(
        default=timezone.now,
        verbose_name='결제일',
        blank=True,
        null=True
    )
    memo = models.TextField(
        blank=True,
        null=True,
        verbose_name='메모'
    )

    @property
    def total_amount(self):
        """'bookstore' 앱의 정보를 기반으로 총 금액 계산"""
        total = BookDistribution.objects.filter(student=self.student).aggregate(
            total_amount=Sum(F('book_stock__selling_price') * F('quantity'))
        )['total_amount'] or 0
        return total

    class Meta:
        verbose_name = '결제'
        verbose_name_plural = '결제 내역'
        ordering = ['-payment_date', 'student__name']

    def __str__(self):
        return f"{self.student.name} - 총액: {self.total_amount}원"

    def save(self, *args, **kwargs):
        """결제 상태 자동 업데이트"""
        if self.paid_amount >= self.total_amount:
            self.status = 'completed'
        elif self.paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'pending'
        super().save(*args, **kwargs)


class BookPayment(models.Model):
    """교재 결제 정보"""
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        verbose_name='결제'
    )
    book_distribution = models.OneToOneField(
        BookDistribution,
        on_delete=models.CASCADE,
        verbose_name='교재 판매'
    )
    original_price = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='원래 가격'
    )
    discounted_price = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='할인된 가격'
    )
    
    class Meta:
        verbose_name = '교재 결제'
        verbose_name_plural = '교재 결제 목록'

    def __str__(self):
        return f"{self.payment.student.name} - {self.book_distribution.book_stock.book.name}"

    def save(self, *args, **kwargs):
        """최초 저장 시 Payment 레코드 생성"""
        if not self.pk and not hasattr(self, 'payment'):
            payment = Payment.objects.create(
                student=self.book_distribution.student,
                total_amount=self.discounted_price,
                due_date=timezone.now() + timezone.timedelta(days=30)  # 기본 30일 납부 기한
            )
            self.payment = payment
        super().save(*args, **kwargs)


class PaymentHistory(models.Model):
    """결제 이력"""
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='histories',
        verbose_name='결제'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='결제 금액'
    )
    payment_method = models.CharField(
        max_length=10,
        choices=Payment.PAYMENT_METHOD,
        verbose_name='결제 수단'
    )
    paid_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='결제 시각'
    )
    receipt_no = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='영수증 번호'
    )

    class Meta:
        verbose_name = '결제 이력'
        verbose_name_plural = '결제 이력 목록'
        ordering = ['-paid_at']

    def __str__(self):
        return f"{self.payment.student.name} - {self.amount}원 ({self.get_payment_method_display()})"

    def save(self, *args, **kwargs):
        """결제 이력 저장 시 Payment의 paid_amount 업데이트"""
        super().save(*args, **kwargs)
        payment = self.payment
        total_paid = payment.histories.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        payment.paid_amount = total_paid
        payment.save()