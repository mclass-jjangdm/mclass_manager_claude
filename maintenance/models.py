from django.db import models
from django.core.validators import MinValueValidator
from django.forms import ValidationError
import datetime


class Room(models.Model):
    number = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='호실',
        unique=True,
        # help_text='양수만 입력 가능합니다.'
    )
    contract_start_date = models.DateField(
        verbose_name='계약 시작일'
    )
    contract_end_date = models.DateField(
        verbose_name='계약 종료일',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='계약 활성 상태'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '호실 정보'
        verbose_name_plural = '호실 목록'
        ordering = ['number']

    def __str__(self):
        return f"{self.number}호"
    

class MonthYearField(models.DateField):
    """Custom field for Month/Year without day"""
    def __init__(self, *args, **kwargs):
        kwargs['help_text'] = '년월을 선택해주세요 (예: 2024년 10월)'
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, datetime.date):
            return datetime.date(value.year, value.month, 1)
        if not value:
            return None
        try:
            if isinstance(value, str):
                # Handle string input in format "YYYY년 MM월"
                if '년' in value and '월' in value:
                    year = int(value.split('년')[0].strip())
                    month = int(value.split('년')[1].split('월')[0].strip())
                    return datetime.date(year, month, 1)
                # Handle string input in format "YYYY-MM"
                year, month = map(int, value.split('-'))
                return datetime.date(year, month, 1)
        except (ValueError, TypeError):
            raise ValidationError('올바른 년월 형식이 아닙니다. (예: 2024년 10월 또는 2024-10)')
        return None


class Maintenance(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        verbose_name='호실'
    )
    date = models.DateField(
        verbose_name='부과년월',
        help_text='년월을 선택해주세요 (예: 2024년 10월)'
    )
    charge = models.IntegerField(
        validators=[MinValueValidator(0, message='금액은 0 이상이어야 합니다.')],
        verbose_name='부과금액',
        help_text='0 이상의 금액을 입력해주세요.'
    )
    date_paid = models.DateField(
        null=True,
        blank=True,
        verbose_name='납부일자'
    )
    memo = models.TextField(
        blank=True,
        verbose_name='메모'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '관리비'
        verbose_name_plural = '관리비 목록'
        ordering = ['-date', 'room']

    def __str__(self):
        return f"{self.room} - {self.date.strftime('%Y년 %m월')} ({self.charge:,}원)"