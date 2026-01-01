from django.db import models
from django.core.validators import MinValueValidator
from students.models import Student
from subjects.models import Subject


class Grade(models.Model):
    """학생 성적 모델 (내신 + 모의고사 통합)"""

    GRADE_TYPE_CHOICES = [
        ('internal', '내신'),
        ('mock', '모의고사'),
    ]

    SEMESTER_CHOICES = [
        (1, '1학기'),
        (2, '2학기'),
    ]

    GRADE_RANK_CHOICES = [
        (1, '1등급'),
        (2, '2등급'),
        (3, '3등급'),
        (4, '4등급'),
        (5, '5등급'),
        (6, '6등급'),
        (7, '7등급'),
        (8, '8등급'),
        (9, '9등급'),
    ]

    # 기본 정보
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='학생'
    )
    grade_type = models.CharField(
        max_length=10,
        choices=GRADE_TYPE_CHOICES,
        verbose_name='성적 유형'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        verbose_name='과목'
    )

    # 공통 필드
    year = models.IntegerField(verbose_name='학년')
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='원점수'
    )
    subject_average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='과목 평균'
    )
    subject_stddev = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='과목 표준편차'
    )
    grade_rank = models.IntegerField(
        choices=GRADE_RANK_CHOICES,
        null=True,
        blank=True,
        verbose_name='등급'
    )

    # 내신 전용 필드
    semester = models.IntegerField(
        choices=SEMESTER_CHOICES,
        null=True,
        blank=True,
        verbose_name='학기'
    )
    credits = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name='단위'
    )
    is_elective = models.BooleanField(
        default=False,
        verbose_name='진로선택 과목 여부'
    )

    # 진로선택 과목 전용 필드
    ACHIEVEMENT_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]
    achievement_level = models.CharField(
        max_length=1,
        choices=ACHIEVEMENT_CHOICES,
        null=True,
        blank=True,
        verbose_name='성취도'
    )
    distribution_a = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='성취도 A 비율'
    )
    distribution_b = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='성취도 B 비율'
    )
    distribution_c = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='성취도 C 비율'
    )

    # 모의고사 전용 필드
    exam_year = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='시험 연도'
    )
    exam_month = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='시험 월'
    )
    exam_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='모의고사 이름'
    )
    percentile = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='백분위'
    )

    # 메타 정보
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='등록일시'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        db_table = 'grades'
        verbose_name = '성적'
        verbose_name_plural = '성적 목록'
        ordering = ['-year', '-semester', '-exam_year', '-exam_month']
        indexes = [
            models.Index(fields=['student', 'grade_type']),
            models.Index(fields=['student', 'year']),
        ]

    def __str__(self):
        if self.grade_type == 'internal':
            return f"{self.student.name} - {self.year}학년 {self.semester}학기 {self.subject.name}"
        else:
            return f"{self.student.name} - {self.exam_year}년 {self.exam_month}월 {self.exam_name} {self.subject.name}"

    @property
    def curriculum(self):
        """교과 카테고리 반환 (Subject의 category 활용)"""
        return self.subject.category if self.subject else None

    def clean(self):
        """유효성 검사"""
        from django.core.exceptions import ValidationError

        if self.grade_type == 'internal':
            # 내신 성적은 학기, 단위 필수
            if not self.semester:
                raise ValidationError({'semester': '내신 성적은 학기가 필수입니다.'})
            if not self.credits:
                raise ValidationError({'credits': '내신 성적은 단위가 필수입니다.'})

            # 진로선택 과목 여부에 따른 필수 필드 검사
            if self.is_elective:
                # 진로선택 과목: 성취도, 분포비율 필수
                if not self.achievement_level:
                    raise ValidationError({'achievement_level': '진로선택 과목은 성취도가 필수입니다.'})
                if self.distribution_a is None:
                    raise ValidationError({'distribution_a': '진로선택 과목은 성취도 A 비율이 필수입니다.'})
                if self.distribution_b is None:
                    raise ValidationError({'distribution_b': '진로선택 과목은 성취도 B 비율이 필수입니다.'})
                if self.distribution_c is None:
                    raise ValidationError({'distribution_c': '진로선택 과목은 성취도 C 비율이 필수입니다.'})
            else:
                # 일반 과목: 등급, 표준편차 필수
                if self.grade_rank is None:
                    raise ValidationError({'grade_rank': '일반 과목은 등급이 필수입니다.'})
                if self.subject_stddev is None:
                    raise ValidationError({'subject_stddev': '일반 과목은 표준편차가 필수입니다.'})

        elif self.grade_type == 'mock':
            # 모의고사 성적은 시험 연도, 월, 이름, 백분위 필수
            if not self.exam_year:
                raise ValidationError({'exam_year': '모의고사 성적은 시험 연도가 필수입니다.'})
            if not self.exam_month:
                raise ValidationError({'exam_month': '모의고사 성적은 시험 월이 필수입니다.'})
            if not self.exam_name:
                raise ValidationError({'exam_name': '모의고사 성적은 시험 이름이 필수입니다.'})
            if self.percentile is None:
                raise ValidationError({'percentile': '모의고사 성적은 백분위가 필수입니다.'})
            if self.grade_rank is None:
                raise ValidationError({'grade_rank': '모의고사 성적은 등급이 필수입니다.'})
