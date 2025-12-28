from django import forms
from django.forms import modelformset_factory
from .models import Grade
from subjects.models import Subject


class InternalGradeForm(forms.ModelForm):
    """내신 성적 입력 폼"""

    # 교과 선택을 위한 필드 추가 (모델 필드 아님)
    category = forms.ChoiceField(
        label='교과',
        required=False,
        choices=[('', '--- 교과 선택 ---')] + [
            ('국어', '국어'), ('수학', '수학'), ('영어', '영어'),
            ('사회', '사회'), ('과학', '과학'), ('한국사', '한국사'),
            ('기술/가정/정보', '기술/가정/정보'), ('제2외국어', '제2외국어'),
            ('한문', '한문'), ('기타', '기타')
        ],
        widget=forms.Select(attrs={'class': 'category-select'})
    )

    class Meta:
        model = Grade
        fields = [
            'student', 'subject', 'year', 'semester', 'credits',
            'score', 'subject_average', 'subject_stddev', 'grade_rank',
            'is_elective'
        ]
        widgets = {
            'student': forms.HiddenInput(),
            'year': forms.Select(choices=[(i, f'{i}학년') for i in range(1, 4)]),
            'semester': forms.RadioSelect(),
            'grade_rank': forms.Select(),
            'is_elective': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # grade_type을 내신으로 고정
        self.instance.grade_type = 'internal'

        # 활성화된 과목만 선택 가능
        self.fields['subject'].queryset = Subject.objects.filter(is_active=True).order_by('subject_code')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.grade_type = 'internal'
        if commit:
            instance.save()
        return instance


class MockExamGradeForm(forms.ModelForm):
    """모의고사 성적 입력 폼"""

    # 교과 선택을 위한 필드 추가 (모델 필드 아님)
    category = forms.ChoiceField(
        label='교과',
        required=False,
        choices=[('', '--- 교과 선택 ---')] + [
            ('국어', '국어'), ('수학', '수학'), ('영어', '영어'),
            ('사회', '사회'), ('과학', '과학'), ('한국사', '한국사'),
            ('기술/가정/정보', '기술/가정/정보'), ('제2외국어', '제2외국어'),
            ('한문', '한문'), ('기타', '기타')
        ],
        widget=forms.Select(attrs={'class': 'category-select'})
    )

    class Meta:
        model = Grade
        fields = [
            'student', 'subject', 'year', 'exam_year', 'exam_month', 'exam_name',
            'score', 'subject_average', 'subject_stddev', 'grade_rank', 'percentile'
        ]
        widgets = {
            'student': forms.HiddenInput(),
            'year': forms.Select(choices=[(i, f'{i}학년') for i in range(1, 4)]),
            'exam_month': forms.Select(choices=[(i, f'{i}월') for i in range(1, 13)]),
            'grade_rank': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # grade_type을 모의고사로 고정
        self.instance.grade_type = 'mock'

        # 활성화된 과목만 선택 가능
        self.fields['subject'].queryset = Subject.objects.filter(is_active=True).order_by('subject_code')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.grade_type = 'mock'
        if commit:
            instance.save()
        return instance


class GradeImportForm(forms.Form):
    """성적 CSV/Excel 파일 업로드 폼"""

    GRADE_TYPE_CHOICES = [
        ('internal', '내신'),
        ('mock', '모의고사'),
    ]

    grade_type = forms.ChoiceField(
        choices=GRADE_TYPE_CHOICES,
        label='성적 유형',
        widget=forms.RadioSelect()
    )
    file = forms.FileField(
        label='파일 선택',
        help_text='CSV 또는 Excel 파일을 업로드하세요',
        widget=forms.FileInput(attrs={'accept': '.csv,.xlsx,.xls'})
    )


# 한 학기 성적을 한 번에 입력하기 위한 Formset
InternalGradeBulkFormSet = modelformset_factory(
    Grade,
    form=InternalGradeForm,
    extra=10,  # 기본 10개 과목 입력 폼 제공
    can_delete=True
)
