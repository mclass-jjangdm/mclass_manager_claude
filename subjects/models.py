from django.db import models


class Subject(models.Model):
    """교과 과목 모델"""

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
        """과목 카테고리 반환 (코드 앞 두 자리 기준)"""
        if not self.subject_code or len(self.subject_code) < 2:
            return '기타'

        # 과목 코드의 앞 두 자리 추출
        code_prefix = self.subject_code[:2]

        # 두 자리 코드 매핑
        categories = {
            '10': '국어',
            '20': '수학',
            '30': '영어',
            '40': '사회',
            '50': '과학',
            '60': '한국사',
            '70': '기술/가정',
            '80': '제2외국어',
            '90': '한문',
            '91': '체육',
            '92': '음악/미술',
            '93': '교양',
        }
        return categories.get(code_prefix, '기타')
