from django.db import models


CURRICULUM_CHOICES = [(2015, '2015 개정'), (2022, '2022 개정')]

SUBJECT_GROUP_CHOICES = [
    ('01', '국어'),
    ('02', '수학'),
    ('03', '영어'),
    ('04', '사회(역사/도덕 포함)'),
    ('05', '과학'),
    ('06', '기술가정/정보'),
    ('07', '체육'),
    ('08', '예술'),
    ('09', '제2외국어/한문'),
    ('10', '교양'),
]

SUBJECT_TYPE_CHOICES = [
    ('0', '공통과목'),
    ('1', '일반선택'),
    ('2', '진로선택'),
    ('3', '융합선택'),
]


class Subject(models.Model):
    """교과 과목 모델"""

    curriculum_year = models.IntegerField(
        choices=CURRICULUM_CHOICES,
        default=2015,
        verbose_name='교육과정',
        help_text='2015 개정 또는 2022 개정 교육과정'
    )
    category_code = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name='교과코드',
        help_text='교과 분류 코드 (예: 10, 20, 91, 92, 93)'
    )
    subject_code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='과목코드',
        help_text='고유 과목 코드 (예: 1001, 2001)'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='과목명'
    )
    special_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='특수코드',
        help_text='특수 분류 코드'
    )
    memo = models.TextField(
        blank=True,
        null=True,
        verbose_name='메모'
    )
    extra = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='여분',
        help_text='추가 정보'
    )
    prerequisite = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_subjects',
        verbose_name='선수과목',
        help_text='이 과목의 선수과목 (공통과목이 선택과목의 선수과목이 되는 경우)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='사용 여부',
        help_text='현재 교육과정에서 사용 중인 과목'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='등록일시'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        db_table = 'subjects'
        verbose_name = '과목'
        verbose_name_plural = '과목 목록'
        ordering = ['subject_code']

    def __str__(self):
        return f"[{self.subject_code}] {self.name}"

    @property
    def category(self):
        """과목 카테고리 반환 (교과코드 기준)"""
        if not self.subject_code:
            return '기타'

        # 2022 개정 교육과정: 6자리 코드 GG-T-S-NN
        if self.curriculum_year == 2022 and len(self.subject_code) == 6:
            group_code = self.subject_code[:2]
            group_map = dict(SUBJECT_GROUP_CHOICES)
            return group_map.get(group_code, '기타')

        # 2015 교육과정: 기존 코드 처리
        # category_code가 있으면 그것 사용
        if self.category_code:
            categories_2digit = {
                '91': '체육',
                '92': '음악/미술',
                '93': '교양',
            }
            if self.category_code in categories_2digit:
                return categories_2digit[self.category_code]

        first_digit = self.subject_code[0] if len(self.subject_code) >= 1 else None
        if not first_digit:
            return '기타'

        categories = {
            '1': '국어',
            '2': '수학',
            '3': '영어',
            '4': '사회',
            '5': '과학',
            '6': '한국사',
            '7': '기술/가정',
            '8': '제2외국어',
        }

        if first_digit == '9' and len(self.subject_code) >= 2:
            two_digits = self.subject_code[:2]
            categories_9xxx = {
                '90': '한문',
                '91': '체육',
                '92': '음악/미술',
                '93': '교양',
            }
            return categories_9xxx.get(two_digits, '기타')

        return categories.get(first_digit, '기타')

    @property
    def subject_type_display(self):
        """2022 과목 코드에서 과목 유형 반환"""
        if self.curriculum_year == 2022 and len(self.subject_code) == 6:
            type_code = self.subject_code[2]
            type_map = dict(SUBJECT_TYPE_CHOICES)
            return type_map.get(type_code, '')
        return ''

    @property
    def is_csat(self):
        """수능 출제 여부 반환 (2022 과목 코드 기준)"""
        if self.curriculum_year == 2022 and len(self.subject_code) == 6:
            return self.subject_code[3] == '1'
        return False
