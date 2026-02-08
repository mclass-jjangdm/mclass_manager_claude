# progress/models.py

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from bookstore.models import Book, BookSale
from students.models import Student
from teachers.models import Teacher
from subjects.models import Subject


class ProblemType(models.Model):
    """
    문제 유형표
    code_number 구조 (20자리):
    - 7자리: 교재코드 (Book.book_code)
    - 2자리: 대단원 (01-99)
    - 2자리: 중단원 (01-99)
    - 2자리: 소단원 (01-99)
    - 3자리: 유형 (001-999)
    - 4자리: 문제 번호 (0001-9999)
    예: 12345670102030010001
    난도는 별도 필드로 관리
    """
    code_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="코드 번호",
        validators=[
            RegexValidator(
                regex=r'^\d{20}$',
                message="코드 번호는 정확히 20자리 숫자여야 합니다."
            )
        ],
        help_text="형식: [교재코드7자리][대단원2자리][중단원2자리][소단원2자리][유형3자리][문제번호4자리]"
    )
    difficulty = models.PositiveIntegerField(
        verbose_name="난도",
        validators=[
            MinValueValidator(1, message="난도는 1 이상이어야 합니다."),
            MaxValueValidator(10, message="난도는 10 이하여야 합니다.")
        ],
        default=5,
        help_text="1(쉬움) ~ 10(어려움)"
    )
    title = models.CharField(max_length=200, verbose_name="제목")
    memo = models.TextField(blank=True, verbose_name="메모")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "문제 유형"
        verbose_name_plural = "문제 유형 목록"
        ordering = ['code_number']

    def __str__(self):
        return f"[{self.code_number}] {self.title}"

    def clean(self):
        """코드 번호 유효성 검사"""
        super().clean()
        if self.code_number and len(self.code_number) == 20:
            book_code = self.code_number[:7]

            # 교재 코드 존재 확인
            if not Book.objects.filter(book_code=book_code).exists():
                raise ValidationError({
                    'code_number': f"교재 코드 '{book_code}'가 존재하지 않습니다."
                })

    def get_book_code(self):
        """교재 코드 (7자리)"""
        return self.code_number[:7] if self.code_number else None

    @property
    def book(self):
        """연결된 교재 객체"""
        book_code = self.get_book_code()
        if book_code:
            return Book.objects.filter(book_code=book_code).first()
        return None

    @property
    def subject(self):
        """연결된 과목 객체 (교재를 통해)"""
        book = self.book
        if book:
            return book.subject
        return None

    @property
    def major_unit(self):
        """대단원 (2자리)"""
        return self.code_number[7:9] if self.code_number else None

    @property
    def medium_unit(self):
        """중단원 (2자리)"""
        return self.code_number[9:11] if self.code_number else None

    @property
    def minor_unit(self):
        """소단원 (2자리)"""
        return self.code_number[11:13] if self.code_number else None

    @property
    def problem_type_code(self):
        """유형 (3자리)"""
        return self.code_number[13:16] if self.code_number else None

    @property
    def problem_number(self):
        """문제 번호 (4자리)"""
        return self.code_number[16:20] if self.code_number else None


class BookProblem(models.Model):
    """교재의 문제 정보 (ProblemType과 연결)"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='problems', verbose_name="교재")
    problem_type = models.ForeignKey(
        ProblemType,
        on_delete=models.CASCADE,
        related_name='book_problems',
        verbose_name="문제 유형"
    )
    page = models.PositiveIntegerField(blank=True, null=True, verbose_name="페이지")
    order = models.PositiveIntegerField(default=0, verbose_name="순서")
    memo = models.CharField(max_length=255, blank=True, verbose_name="비고")

    class Meta:
        verbose_name = "교재 문제"
        verbose_name_plural = "교재 문제 목록"
        ordering = ['book', 'order']
        unique_together = ['book', 'problem_type']

    def __str__(self):
        return f"{self.book.title} - {self.problem_type.code_number}"


class StudentProgress(models.Model):
    """학생에게 교재 지급 시 생성되는 진도표 헤더"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress_sheets', verbose_name="학생")
    book_sale = models.OneToOneField(BookSale, on_delete=models.CASCADE, related_name='progress', verbose_name="교재 판매 내역")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='student_progress', verbose_name="교재")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    memo = models.TextField(blank=True, verbose_name="메모")

    class Meta:
        verbose_name = "학생 진도표"
        verbose_name_plural = "학생 진도표 목록"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.book.title}"

    def get_completion_rate(self):
        """진도율 계산"""
        total = self.entries.count()
        if total == 0:
            return 0
        completed = self.entries.filter(study_date__isnull=False).count()
        return round((completed / total) * 100, 1)


class ProgressEntry(models.Model):
    """진도표의 각 문제별 학습 기록"""
    UNDERSTANDING_CHOICES = [
        (1, '매우 부족'),
        (2, '부족'),
        (3, '보통'),
        (4, '양호'),
        (5, '완벽'),
    ]

    progress = models.ForeignKey(StudentProgress, on_delete=models.CASCADE, related_name='entries', verbose_name="진도표")
    book_problem = models.ForeignKey(BookProblem, on_delete=models.CASCADE, verbose_name="문제")

    is_assigned = models.BooleanField(default=False, verbose_name="과제 체크")
    study_date = models.DateField(blank=True, null=True, verbose_name="학습 날짜")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="담당 선생님")
    understanding = models.PositiveIntegerField(choices=UNDERSTANDING_CHOICES, blank=True, null=True, verbose_name="이해 정도")
    homework = models.CharField(max_length=255, blank=True, verbose_name="과제")
    memo = models.CharField(max_length=255, blank=True, verbose_name="비고")

    class Meta:
        verbose_name = "진도 항목"
        verbose_name_plural = "진도 항목 목록"
        ordering = ['progress', 'book_problem__order']
        unique_together = ['progress', 'book_problem']

    def __str__(self):
        return f"{self.progress.student.name} - {self.book_problem.problem_type.code_number}"


class StudentActivity(models.Model):
    """
    교재 외 수업 활동 기록 (프린트, 학습지, 강의 등)
    교재 진도(StudentBookProgress)와 독립적으로 관리
    """
    ACTIVITY_TYPE_CHOICES = [
        ('quiz', '퀴즈'),
        ('practice', '추가 연습 문제'),
        ('booklet', '제본 교재'),
        ('other', '기타'),
    ]

    ACHIEVEMENT_CHOICES = [
        ('A', '매우 우수'),
        ('B', '우수'),
        ('C', '보통'),
        ('D', '미흡'),
        ('F', '매우 미흡'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name="학생"
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_activities',
        verbose_name="담당 교사"
    )
    date = models.DateField(verbose_name="활동 날짜")
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES,
        default='print',
        verbose_name="활동 유형"
    )
    title = models.CharField(max_length=200, verbose_name="활동명")
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="과목"
    )

    # 평가 정보 (선택적)
    achievement = models.CharField(
        max_length=1,
        choices=ACHIEVEMENT_CHOICES,
        blank=True,
        verbose_name="성취도"
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="점수"
    )
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="만점"
    )
    needs_review = models.BooleanField(
        default=False,
        verbose_name="보완 필요"
    )
    homework_checked = models.BooleanField(
        default=False,
        verbose_name="과제 확인"
    )

    memo = models.TextField(blank=True, verbose_name="메모")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "수업 활동"
        verbose_name_plural = "수업 활동 목록"
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.get_activity_type_display()} - {self.title}"

    @property
    def score_display(self):
        """점수 표시 (예: 85/100)"""
        if self.score is not None and self.total_score is not None:
            return f"{self.score}/{self.total_score}"
        elif self.score is not None:
            return str(self.score)
        return None


class LearningRecord(models.Model):
    """
    통합 학습 기록 모델
    교재 진도(StudentBookProgress)와 수업 활동(StudentActivity)을 하나로 통합
    통계 및 관리를 단순화하기 위한 구조
    """
    RECORD_TYPE_CHOICES = [
        ('textbook', '교재 진도'),      # 기존 StudentBookProgress
        ('quiz', '퀴즈'),               # 수업 활동
        ('practice', '추가 연습 문제'),  # 수업 활동
        ('booklet', '제본 교재'),        # 수업 활동
        ('other', '기타'),              # 수업 활동
    ]

    ACHIEVEMENT_CHOICES = [
        ('', '-'),
        ('A', 'A (우수)'),
        ('B', 'B (양호)'),
        ('C', 'C (보통)'),
        ('D', 'D (미흡)'),
        ('F', 'F (재학습)'),
    ]

    # 기본 정보 (필수)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='learning_records',
        verbose_name="학생"
    )
    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPE_CHOICES,
        default='textbook',
        verbose_name="기록 유형"
    )
    date = models.DateField(null=True, blank=True, verbose_name="학습 날짜")
    title = models.CharField(max_length=200, verbose_name="학습 내용")

    # 교재 진도인 경우만 사용 (record_type='textbook')
    book_sale = models.ForeignKey(
        'bookstore.BookSale',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='learning_records',
        verbose_name="교재 지급"
    )
    book_content = models.ForeignKey(
        'bookstore.BookContent',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='learning_records',
        verbose_name="목차 항목"
    )

    # 과목 (선택)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="과목"
    )

    # 평가 정보
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='learning_records',
        verbose_name="담당 교사"
    )
    achievement = models.CharField(
        max_length=1,
        choices=ACHIEVEMENT_CHOICES,
        blank=True,
        default='',
        verbose_name="성취도"
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="점수"
    )
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="만점"
    )

    # 체크 항목 (공통)
    homework_checked = models.BooleanField(default=False, verbose_name="과제 확인")
    needs_review = models.BooleanField(default=False, verbose_name="보완 필요")

    # 메모 및 메타 정보
    memo = models.TextField(blank=True, verbose_name="메모")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "학습 기록"
        verbose_name_plural = "학습 기록 목록"
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['record_type']),
            models.Index(fields=['book_sale']),
        ]
        # 교재 진도의 경우 중복 방지
        constraints = [
            models.UniqueConstraint(
                fields=['book_sale', 'book_content'],
                condition=models.Q(record_type='textbook'),
                name='unique_textbook_progress'
            )
        ]

    def __str__(self):
        return f"{self.student.name} - {self.get_record_type_display()} - {self.title}"

    @property
    def is_textbook_record(self):
        """교재 진도 기록인지 여부"""
        return self.record_type == 'textbook'

    @property
    def is_activity_record(self):
        """수업 활동 기록인지 여부"""
        return self.record_type != 'textbook'

    @property
    def is_completed(self):
        """학습 완료 여부 (학습 날짜가 있고 성취도가 입력된 경우)"""
        return bool(self.date and self.achievement)

    @property
    def is_pending(self):
        """미완료 항목인지 여부"""
        return not self.is_completed

    @property
    def book(self):
        """연결된 교재"""
        if self.book_sale:
            return self.book_sale.book
        return None

    @property
    def score_display(self):
        """점수 표시 (예: 85/100)"""
        if self.score is not None and self.total_score is not None:
            return f"{self.score}/{self.total_score}"
        elif self.score is not None:
            return str(self.score)
        return None

    def clean(self):
        """유효성 검사"""
        super().clean()
        # 교재 진도인 경우 book_sale과 book_content 필수
        if self.record_type == 'textbook':
            if not self.book_sale or not self.book_content:
                raise ValidationError(
                    "교재 진도 기록에는 교재 지급 정보와 목차 항목이 필요합니다."
                )
        # 수업 활동인 경우 title 필수
        else:
            if not self.title:
                raise ValidationError(
                    "수업 활동 기록에는 활동명이 필요합니다."
                )
