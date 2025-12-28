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
        """과목 카테고리 반환 (코드 첫 자리 기준)"""
        code_prefix = self.subject_code[0] if self.subject_code else ''
        categories = {
            '1': '국어',
            '2': '수학',
            '3': '영어',
            '4': '사회',
            '5': '과학',
            '6': '한국사',
            '7': '기술/가정/정보',
            '8': '제2외국어',
            '9': '한문',
        }
        return categories.get(code_prefix, '기타')
