from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime


phone_number_validator = RegexValidator(
    regex=r'^\d{9,11}$',
    message="전화번호는 9-11자리 숫자로 입력해주세요. (예: 01012345678, 0212345678)"
)


class Teacher(models.Model):
    GENDER_CHOICES = [
        ('M', '남'),
        ('F', '여'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='이름')
    phone_number = models.CharField(
        max_length=11,  # 일시적으로 11자로 설정
        validators=[phone_number_validator],
        blank=True,
        null=True,
        verbose_name='전화번호'
    )
    email = models.EmailField(blank=True, null=True, verbose_name='이메일')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='성별')
    hire_date = models.DateField(blank=True, null=True, verbose_name='입사일')
    resignation_date = models.DateField(null=True, blank=True, verbose_name='퇴사일')
    bank = models.ForeignKey('common.Bank', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='거래은행')
    account_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='급여계좌')
    base_salary = models.IntegerField(blank=True, null=True, verbose_name='급여기준', default=15000)
    other_info = models.TextField(blank=True, null=True, verbose_name='기타')
    is_active = models.BooleanField(default=True, verbose_name="재직 중")
    extra_field1 = models.CharField(max_length=100, blank=True, null=True, verbose_name='예비1')
    extra_field2 = models.CharField(max_length=100, blank=True, null=True, verbose_name='예비2')
    extra_field3 = models.CharField(max_length=100, blank=True, null=True, verbose_name='예비3')
    extra_field4 = models.CharField(max_length=100, blank=True, null=True, verbose_name='예비4')

    def __str__(self):
        return self.name

    def get_formatted_phone_number(self):
        """전화번호를 하이픈이 포함된 형태로 반환"""
        if not self.phone_number:
            return ''
        
        phone = self.phone_number
        
        # 11자리 휴대폰 번호 (010-xxxx-xxxx)
        if len(phone) == 11 and phone.startswith('010'):
            return f'{phone[:3]}-{phone[3:7]}-{phone[7:]}'
        # 10자리 지역번호
        elif len(phone) == 10:
            if phone.startswith('02'):
                # 서울 지역번호 (02-xxxx-xxxx)
                return f'{phone[:2]}-{phone[2:6]}-{phone[6:]}'
            else:
                # 기타 지역번호 (031-xxx-xxxx)
                return f'{phone[:3]}-{phone[3:6]}-{phone[6:]}'
        # 9자리 서울 지역번호 (02-xxx-xxxx)
        elif len(phone) == 9 and phone.startswith('02'):
            return f'{phone[:2]}-{phone[2:5]}-{phone[5:]}'
        
        return phone

    class Meta:
        verbose_name = '교사'
        verbose_name_plural = '교사'

    def save(self, *args, **kwargs):
        # 퇴사일이 있고 오늘 날짜보다 이전이면 비활성
        if self.resignation_date and self.resignation_date <= timezone.now().date():
            self.is_active = False
        # 퇴사일이 없거나 미래 날짜면 활성
        else:
            self.is_active = True
        super().save(*args, **kwargs)


class Attendance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='교사')
    date = models.DateField(default=timezone.now, verbose_name='날짜')
    is_present = models.BooleanField(default=True, verbose_name='출근')
    start_time = models.TimeField(null=True, blank=True, verbose_name='근무 시작 시간')
    end_time = models.TimeField(null=True, blank=True, verbose_name='근무 종료 시간')

    class Meta:
        unique_together = ['teacher', 'date']
        verbose_name = '출근기록'
        verbose_name_plural = '출근기록'

    def __str__(self):
        return f"{self.teacher.name} - {self.date}"


class Salary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='교사')
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        default=timezone.now().year,
        verbose_name='년도'
    )
    month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        default=timezone.now().month,
        verbose_name='월'
    )
    work_days = models.PositiveIntegerField(verbose_name='근무일수')
    base_amount = models.PositiveIntegerField(verbose_name='기본급', default=15000)
    additional_amount = models.PositiveIntegerField(verbose_name='추가급', default=0)
    total_amount = models.PositiveIntegerField(verbose_name='총액')

    class Meta:
        verbose_name = '급여'
        verbose_name_plural = '급여'
        unique_together = ['teacher', 'year', 'month']

    def __str__(self):
        return f"{self.teacher.name} - {self.year}년 {self.month}월"

    def clean(self):
        super().clean()
        if self.month < 1 or self.month > 12:
            raise ValidationError({'month': _('월은 1부터 12 사이의 값이어야 합니다.')})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class TeacherUnavailability(models.Model):
    """교사 출근 불가 날짜 관리"""
    REASON_CHOICES = [
        ('personal', '개인 사유'),
        ('sick', '병가'),
        ('vacation', '휴가'),
        ('other', '기타'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='교사')
    date = models.DateField(verbose_name='날짜')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='personal', verbose_name='사유')
    memo = models.TextField(blank=True, null=True, verbose_name='메모')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일시')

    class Meta:
        unique_together = ['teacher', 'date']
        verbose_name = '출근 불가 일정'
        verbose_name_plural = '출근 불가 일정'
        ordering = ['date', 'teacher__name']

    def __str__(self):
        return f"{self.teacher.name} - {self.date} ({self.get_reason_display()})"


class TeacherStudentAssignment(models.Model):
    """날짜별 교사-학생 배정"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='교사')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, verbose_name='학생')
    date = models.DateField(verbose_name='날짜')
    memo = models.TextField(blank=True, null=True, verbose_name='메모')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일시')

    class Meta:
        unique_together = ['student', 'date']  # 학생은 하루에 한 교사에게만 배정
        verbose_name = '교사-학생 배정'
        verbose_name_plural = '교사-학생 배정'
        ordering = ['date', 'teacher__name', 'student__name']

    def __str__(self):
        return f"{self.date} - {self.teacher.name} → {self.student.name}"
