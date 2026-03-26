from django.db import models


PAYMENT_METHOD_CHOICES = [
    ('cash', '현금'),
    ('card', '카드'),
    ('transfer', '계좌이체'),
    ('other', '기타'),
]

MONTH_CHOICES = [(i, f'{i}월') for i in range(1, 13)]


class Lesson(models.Model):
    name = models.CharField(max_length=100, verbose_name='수업 이름')
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='과목',
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='담당 교사',
    )
    books = models.ManyToManyField(
        'bookstore.Book',
        blank=True,
        verbose_name='교재',
    )

    # 수업 요일
    mon = models.BooleanField(default=False, verbose_name='월')
    tue = models.BooleanField(default=False, verbose_name='화')
    wed = models.BooleanField(default=False, verbose_name='수')
    thu = models.BooleanField(default=False, verbose_name='목')
    fri = models.BooleanField(default=False, verbose_name='금')
    sat = models.BooleanField(default=False, verbose_name='토')
    sun = models.BooleanField(default=False, verbose_name='일')

    # 수업 시간
    start_time = models.TimeField(verbose_name='시작 시간')
    end_time = models.TimeField(verbose_name='종료 시간')

    # 수강료
    base_tuition = models.PositiveIntegerField(verbose_name='기본 수강료')

    memo = models.TextField(blank=True, verbose_name='기타')
    is_active = models.BooleanField(default=True, verbose_name='활성')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = '수업'
        verbose_name_plural = '수업 목록'

    def __str__(self):
        return self.name

    @property
    def days_display(self):
        day_map = [
            (self.mon, '월'),
            (self.tue, '화'),
            (self.wed, '수'),
            (self.thu, '목'),
            (self.fri, '금'),
            (self.sat, '토'),
            (self.sun, '일'),
        ]
        return ''.join(label for flag, label in day_map if flag) or '-'

    @property
    def active_enrollment_count(self):
        return self.enrollments.filter(is_active=True).count()


class Enrollment(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='학생',
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='수업',
    )
    enrollment_date = models.DateField(verbose_name='수강 시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='수강 종료일')
    tuition_adjustment = models.IntegerField(default=0, verbose_name='수강료 조정액')
    memo = models.TextField(blank=True, verbose_name='메모')
    is_active = models.BooleanField(default=True, verbose_name='활성')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'lesson']
        ordering = ['-enrollment_date']
        verbose_name = '수강 신청'
        verbose_name_plural = '수강 신청 목록'

    def __str__(self):
        return f'{self.student} - {self.lesson}'

    @property
    def adjusted_tuition(self):
        return self.lesson.base_tuition + self.tuition_adjustment


class TuitionPayment(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='수강 신청',
    )
    year = models.IntegerField(verbose_name='납부 연도')
    month = models.IntegerField(choices=MONTH_CHOICES, verbose_name='납부 월')
    amount = models.PositiveIntegerField(verbose_name='납부 금액')
    payment_date = models.DateField(verbose_name='납부일')
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='납부 방법',
    )
    memo = models.TextField(blank=True, verbose_name='메모')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-month']
        verbose_name = '수강료 납부'
        verbose_name_plural = '수강료 납부 목록'

    def __str__(self):
        return f'{self.enrollment} - {self.year}년 {self.month}월'
