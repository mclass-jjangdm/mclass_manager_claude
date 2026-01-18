# bookstore/models.py

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from students.models import Student
from subjects.models import Subject


class BookSupplier(models.Model):
    """도서 구매처(출판사/서점) 정보"""
    name = models.CharField(max_length=100, verbose_name="상호명(법인명)")
    registration_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="사업자 등록번호")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="전화번호")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="주소")

    # 계좌 정보
    bank_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="은행명")
    account_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="계좌번호")
    account_owner = models.CharField(max_length=50, blank=True, null=True, verbose_name="예금주")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "구매처"
        verbose_name_plural = "구매처 목록"


class Book(models.Model):
    """교재(상품) 기본 정보 모델"""
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name='books',
        null=True,
        blank=True,
        verbose_name="과목",
        help_text="이 교재가 속한 과목"
    )
    book_code = models.CharField(
        max_length=7,
        unique=True,
        null=True,
        blank=True,
        verbose_name="교재코드",
        validators=[
            RegexValidator(
                regex=r'^\d{7}$',
                message="교재코드는 정확히 7자리 숫자여야 합니다."
            )
        ],
        help_text="ISBN 뒤 7자리 또는 자동생성 코드 (진도표 코드에 사용)"
    )
    title = models.CharField(max_length=200, verbose_name="교재명")
    isbn = models.CharField(max_length=50, unique=True, verbose_name="바코드(ISBN)")
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name="저자")
    publisher = models.CharField(max_length=100, blank=True, null=True, verbose_name="출판사")
    supplier = models.ForeignKey('BookSupplier', on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name="주거래 구매처")
    original_price = models.PositiveIntegerField(default=0, verbose_name="정상 가격")  # 정가
    cost_price = models.PositiveIntegerField(default=0, verbose_name="입고 가격")  # 원가
    price = models.PositiveIntegerField(default=0, verbose_name="판매 가격")
    stock = models.PositiveIntegerField(default=0, verbose_name="재고 수량")
    memo = models.TextField(blank=True, null=True, verbose_name="비고")

    created_at = models.DateTimeField(default=timezone.now, verbose_name="등록일(입고일)")

    def save(self, *args, **kwargs):
        if not self.book_code:
            self.book_code = self._generate_book_code()
        super().save(*args, **kwargs)

    def _generate_book_code(self):
        """ISBN 뒤 7자리 또는 순차 코드 생성"""
        # ISBN이 있고 7자리 이상인 경우 뒤 7자리 사용
        if self.isbn:
            # ISBN에서 숫자만 추출
            isbn_digits = ''.join(c for c in self.isbn if c.isdigit())
            if len(isbn_digits) >= 7:
                candidate = isbn_digits[-7:]
                # 중복 체크
                if not Book.objects.filter(book_code=candidate).exists():
                    return candidate

        # ISBN이 없거나 중복인 경우 순차 코드 생성
        return self._generate_sequence_code()

    def _generate_sequence_code(self):
        """순차 교재코드 생성 (0000001부터 시작)"""
        # 가장 큰 순차 코드 찾기
        last_book = Book.objects.filter(
            book_code__regex=r'^[0-9]{7}$'
        ).order_by('-book_code').first()

        if last_book:
            try:
                last_num = int(last_book.book_code)
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1

        return str(new_num).zfill(7)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "교재"
        verbose_name_plural = "교재 목록"
        ordering = ['title']


class BookSale(models.Model):
    """교재 판매/분배 내역 모델"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_sales', verbose_name="학생")
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='sales', verbose_name="교재")

    sale_date = models.DateField(default=timezone.now, verbose_name="판매일(지급일)")
    price = models.PositiveIntegerField(verbose_name="판매 당시 가격")  # 가격 변동 대비
    quantity = models.PositiveIntegerField(default=1, verbose_name="수량")

    is_paid = models.BooleanField(default=False, verbose_name="결제 완료 여부")
    payment_date = models.DateField(blank=True, null=True, verbose_name="결제일")

    memo = models.CharField(max_length=255, blank=True, null=True, verbose_name="비고")

    def get_total_price(self):
        return self.price * self.quantity

    def create_progress_records(self):
        """교재의 모든 목차에 대한 진도 레코드 생성"""
        from bookstore.models import StudentBookProgress
        contents = self.book.contents.all()
        created_count = 0
        for content in contents:
            _, created = StudentBookProgress.objects.get_or_create(
                book_sale=self,
                book_content=content
            )
            if created:
                created_count += 1
        return created_count

    def get_progress_stats(self):
        """진도 통계 반환"""
        total = self.progress_records.count()
        completed = self.progress_records.filter(study_date__isnull=False, achievement__gt='').count()
        needs_review = self.progress_records.filter(needs_review=True).count()
        return {
            'total': total,
            'completed': completed,
            'remaining': total - completed,
            'needs_review': needs_review,
            'progress_percent': round(completed / total * 100, 1) if total > 0 else 0
        }

    def __str__(self):
        return f"{self.student.name} - {self.book.title}"

    class Meta:
        verbose_name = "교재 판매 내역"
        verbose_name_plural = "교재 판매 내역"
        ordering = ['-sale_date']


class BookContent(models.Model):
    """교재 세부 목차 정보 (대단원, 중단원, 소단원, 페이지 등)"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='contents', verbose_name="교재")

    # 대단원
    chapter_num = models.PositiveIntegerField(verbose_name="대단원 번호")
    chapter_title = models.CharField(max_length=200, verbose_name="대단원 주제")

    # 중단원
    section_num = models.PositiveIntegerField(verbose_name="중단원 번호")
    section_title = models.CharField(max_length=200, verbose_name="중단원 주제")

    # 소단원
    subsection_num = models.CharField(max_length=10, verbose_name="소단원 번호")  # '01', '90' 등 문자열로
    subsection_title = models.CharField(max_length=200, verbose_name="소단원 주제")

    # 페이지
    page = models.PositiveIntegerField(verbose_name="페이지")

    class Meta:
        verbose_name = "교재 목차"
        verbose_name_plural = "교재 목차"
        ordering = ['book', 'page']
        # 같은 교재의 같은 페이지는 중복 불가
        unique_together = ['book', 'page']

    def __str__(self):
        return f"{self.book.title} - {self.chapter_title} > {self.section_title} > {self.subsection_title} (p.{self.page})"


class StudentBookProgress(models.Model):
    """학생별 교재 진도 평가 기록"""
    ACHIEVEMENT_CHOICES = [
        ('', '-'),
        ('A', 'A (우수)'),
        ('B', 'B (양호)'),
        ('C', 'C (보통)'),
        ('D', 'D (미흡)'),
        ('F', 'F (재학습)'),
    ]

    # 연결 관계
    book_sale = models.ForeignKey(BookSale, on_delete=models.CASCADE, related_name='progress_records', verbose_name="교재 지급")
    book_content = models.ForeignKey(BookContent, on_delete=models.CASCADE, related_name='progress_records', verbose_name="목차 항목")

    # 평가 정보
    study_date = models.DateField(blank=True, null=True, verbose_name="학습 날짜")
    achievement = models.CharField(max_length=1, choices=ACHIEVEMENT_CHOICES, blank=True, default='', verbose_name="성취 수준")
    needs_review = models.BooleanField(default=False, verbose_name="보완 추천 여부")
    homework_done = models.BooleanField(default=False, verbose_name="과제 수행 여부")

    # 담당 교사 (평가 시 자동 기록)
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="담당쌤"
    )

    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "학생 진도 기록"
        verbose_name_plural = "학생 진도 기록"
        ordering = ['book_sale', 'book_content__page']
        # 학생의 특정 교재 지급 건에 대해 각 목차 항목은 하나만 존재
        unique_together = ['book_sale', 'book_content']

    def __str__(self):
        return f"{self.book_sale.student.name} - {self.book_content.subsection_title} (p.{self.book_content.page})"

    @property
    def student(self):
        return self.book_sale.student

    @property
    def book(self):
        return self.book_sale.book

    @property
    def is_completed(self):
        """학습 완료 여부 (학습 날짜가 있고 성취도가 입력된 경우)"""
        return bool(self.study_date and self.achievement)


class BookStockLog(models.Model):
    """교재 입고(재고 추가) 및 반품 기록"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='stock_logs', verbose_name="교재")
    # 구매처 연결(Optional: 기존 데이터 호환성을 위해 null = True)
    supplier = models.ForeignKey(BookSupplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="구매처")
    # PositiveIntegerField -> IntegerField (반품 시 -수량 저장을 위해)
    quantity = models.IntegerField(verbose_name="수량 (입고/반품)")
    cost_price = models.PositiveIntegerField(verbose_name="단가")
    total_payment = models.PositiveIntegerField(default=0, verbose_name="총액")
    payment_date = models.DateField(blank=True, null=True, verbose_name="날짜")  # 지급일 or 반품일
    # auto_now_add=True를 삭제하고 default=timezone.now 로 변경
    created_at = models.DateTimeField(default=timezone.now, verbose_name="입고/반품일")
    memo = models.CharField(max_length=255, blank=True, null=True, verbose_name="비고")
    # 정산(입금) 완료 여부
    is_paid = models.BooleanField(default=False, verbose_name="정산 완료 여부")

    def save(self, *args, **kwargs):
        # 총액 자동 계산 (절대값 사용)
        if not self.total_payment:
            self.total_payment = abs(self.quantity * self.cost_price)

        if not self.pk:
            # 수량만큼 재고 변경 (음수면 재고 감소)
            self.book.stock += self.quantity

            # 입고(양수)일 때만 단가 업데이트
            if self.quantity > 0:
                self.book.cost_price = self.cost_price

            self.book.save()
        super().save(*args, **kwargs)

    def __str__(self):
        action = "입고" if self.quantity > 0 else "반품"
        return f"{self.book.title} ({action} {abs(self.quantity)})"

    class Meta:
        verbose_name = "재고 기록"
        verbose_name_plural = "재고 기록"
        ordering = ['-created_at']
