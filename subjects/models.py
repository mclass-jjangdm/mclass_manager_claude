from django.db import models


class Subject(models.Model):
    """교과 과목 모델"""

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
        # category_code가 있으면 그것 사용
        if self.category_code:
            # 2자리 교과코드 매핑 (91, 92, 93 등 특수 코드용)
            categories_2digit = {
                '91': '체육',
                '92': '음악/미술',
                '93': '교양',
            }
            if self.category_code in categories_2digit:
                return categories_2digit[self.category_code]

        # 과목코드 앞 1자리로 교과 구분
        if not self.subject_code:
            return '기타'

        first_digit = self.subject_code[0] if len(self.subject_code) >= 1 else None

        if not first_digit:
            return '기타'

        # 앞 1자리 교과코드 매핑
        categories = {
            '1': '국어',
            '2': '수학',
            '3': '영어',
            '4': '사회',
            '5': '과학',
            '6': '한국사',
            '7': '기술/가정',
            '8': '제2외국어',
            '9': '기타(9xxx)',  # 9로 시작하는 건 별도 처리 필요
        }

        # 9로 시작하는 경우 앞 2자리로 세분화
        if first_digit == '9' and len(self.subject_code) >= 2:
            two_digits = self.subject_code[:2]
            categories_9xxx = {
                '90': '한문',
                '91': '체육',
                '92': '음악/미술',
                '93': '교양',
            }
            return categories_9xxx.get(two_digits, '기타(9xxx)')

        return categories.get(first_digit, '기타')
