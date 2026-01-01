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
    code_number 구조 (19자리):
    - 4자리: 과목 코드 (Subject.subject_code와 일치)
    - 2자리: 대단원 (01-99)
    - 2자리: 중단원 (01-99)
    - 2자리: 소단원 (01-99)
    - 3자리: 유형 (001-999)
    - 4자리: 문제 번호 (0001-9999)
    - 2자리: 난도 (01-10)
    예: 5001020310035139203
    """
    code_number = models.CharField(
        max_length=19,
        unique=True,
        verbose_name="코드 번호",
        validators=[
            RegexValidator(
                regex=r'^\d{19}$',
                message="코드 번호는 정확히 19자리 숫자여야 합니다."
            )
        ],
        help_text="형식: [과목코드4자리][대단원2자리][중단원2자리][소단원2자리][유형3자리][문제번호4자리][난도2자리]"
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
        if self.code_number and len(self.code_number) == 19:
            subject_code = self.code_number[:4]
            difficulty = int(self.code_number[17:19])

            # 과목 코드 존재 확인
            if not Subject.objects.filter(subject_code=subject_code).exists():
                raise ValidationError({
                    'code_number': f"과목 코드 '{subject_code}'가 존재하지 않습니다."
                })

            # 난도 범위 확인
            if difficulty < 1 or difficulty > 10:
                raise ValidationError({
                    'code_number': f"난도는 01~10 사이여야 합니다. (현재: {difficulty:02d})"
                })

    @property
    def subject_code(self):
        """과목 코드 (4자리)"""
        return self.code_number[:4] if self.code_number else None

    @property
    def major_unit(self):
        """대단원 (2자리)"""
        return self.code_number[4:6] if self.code_number else None

    @property
    def medium_unit(self):
        """중단원 (2자리)"""
        return self.code_number[6:8] if self.code_number else None

    @property
    def minor_unit(self):
        """소단원 (2자리)"""
        return self.code_number[8:10] if self.code_number else None

    @property
    def problem_type_code(self):
        """유형 (3자리)"""
        return self.code_number[10:13] if self.code_number else None

    @property
    def problem_number(self):
        """문제 번호 (4자리)"""
        return self.code_number[13:17] if self.code_number else None

    @property
    def difficulty(self):
        """난도 (2자리, 01-10)"""
        return self.code_number[17:19] if self.code_number else None

    @property
    def subject(self):
        """연결된 과목 객체"""
        if self.subject_code:
            return Subject.objects.filter(subject_code=self.subject_code).first()
        return None


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
