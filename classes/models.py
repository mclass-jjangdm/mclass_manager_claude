from django.db import models


PAYMENT_METHOD_CHOICES = [
    ('cash', '현금'),
    ('card', '카드'),
    ('transfer', '계좌이체'),
    ('other', '기타'),
]

MONTH_CHOICES = [(i, f'{i}월') for i in range(1, 13)]

DAY_CHOICES = [
    ('mon', '월'),
    ('tue', '화'),
    ('wed', '수'),
    ('thu', '목'),
    ('fri', '금'),
    ('sat', '토'),
    ('sun', '일'),
]

DAY_ORDER = {d: i for i, (d, _) in enumerate(DAY_CHOICES)}


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
        verbose_name='담당 선생님',
    )
    books = models.ManyToManyField(
        'bookstore.Book',
        blank=True,
        verbose_name='교재',
    )

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
        """'월수금' 형태로 반환"""
        schedules = sorted(self.schedules.all(), key=lambda s: DAY_ORDER.get(s.day, 99))
        day_labels = dict(DAY_CHOICES)
        return ''.join(day_labels[s.day] for s in schedules) or '-'

    @property
    def schedule_display(self):
        """'월 20:00~22:00 · 금 20:00~22:00 · 토 14:00~18:00' 형태로 반환"""
        schedules = sorted(self.schedules.all(), key=lambda s: DAY_ORDER.get(s.day, 99))
        day_labels = dict(DAY_CHOICES)
        parts = [
            f"{day_labels[s.day]} {s.start_time.strftime('%H:%M')}~{s.end_time.strftime('%H:%M')}"
            for s in schedules
        ]
        return ' · '.join(parts) or '-'

    @property
    def active_enrollment_count(self):
        return self.enrollments.filter(is_active=True).count()


class LessonSchedule(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='수업',
    )
    day = models.CharField(max_length=3, choices=DAY_CHOICES, verbose_name='요일')
    start_time = models.TimeField(verbose_name='시작 시간')
    end_time = models.TimeField(verbose_name='종료 시간')

    class Meta:
        unique_together = ['lesson', 'day']
        verbose_name = '수업 일정'
        verbose_name_plural = '수업 일정 목록'

    def __str__(self):
        day_label = dict(DAY_CHOICES).get(self.day, self.day)
        return (
            f"{self.lesson.name} {day_label} "
            f"{self.start_time.strftime('%H:%M')}~{self.end_time.strftime('%H:%M')}"
        )


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
