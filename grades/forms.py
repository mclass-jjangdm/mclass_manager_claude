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
            ('체육', '체육'), ('음악/미술', '음악/미술'), ('교양', '교양'),
            ('기술/가정', '기술/가정'), ('제2외국어', '제2외국어'),
            ('한문', '한문'), ('기타', '기타')
        ],
        widget=forms.Select(attrs={'class': 'category-select'})
    )

    class Meta:
        model = Grade
        fields = [
            'subject', 'year', 'semester', 'credits',
            'score', 'subject_average', 'subject_stddev', 'grade_rank',
            'is_elective', 'achievement_level', 'distribution_a', 'distribution_b', 'distribution_c'
        ]
        widgets = {
            'year': forms.Select(choices=[(i, f'{i}학년') for i in range(1, 4)]),
            'semester': forms.RadioSelect(),
            'grade_rank': forms.Select(),
            'is_elective': forms.CheckboxInput(attrs={'class': 'elective-checkbox'}),
            'achievement_level': forms.Select(attrs={'class': 'elective-field'}),
            'distribution_a': forms.NumberInput(attrs={'class': 'elective-field', 'step': '0.01', 'placeholder': 'A 비율'}),
            'distribution_b': forms.NumberInput(attrs={'class': 'elective-field', 'step': '0.01', 'placeholder': 'B 비율'}),
            'distribution_c': forms.NumberInput(attrs={'class': 'elective-field', 'step': '0.01', 'placeholder': 'C 비율'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # grade_type을 내신으로 고정
        self.instance.grade_type = 'internal'

        # 활성화된 과목만 선택 가능
        self.fields['subject'].queryset = Subject.objects.filter(is_active=True).order_by('subject_code')

        # 진로선택 과목 필드는 선택적으로 표시
        self.fields['subject_stddev'].required = False
        self.fields['grade_rank'].required = False
        self.fields['achievement_level'].required = False
        self.fields['distribution_a'].required = False
        self.fields['distribution_b'].required = False
        self.fields['distribution_c'].required = False

        # 수정 시 현재 과목의 카테고리를 초기값으로 설정
        if self.instance.pk and self.instance.subject:
            self.fields['category'].initial = self.instance.subject.category

    def clean(self):
        cleaned_data = super().clean()
        is_elective = cleaned_data.get('is_elective', False)

        if is_elective:
            # 진로선택 과목: 성취도, 분포비율 필수
            if not cleaned_data.get('achievement_level'):
                self.add_error('achievement_level', '진로선택 과목은 성취도가 필수입니다.')
            if cleaned_data.get('distribution_a') is None:
                self.add_error('distribution_a', '진로선택 과목은 성취도 A 비율이 필수입니다.')
            if cleaned_data.get('distribution_b') is None:
                self.add_error('distribution_b', '진로선택 과목은 성취도 B 비율이 필수입니다.')
            if cleaned_data.get('distribution_c') is None:
                self.add_error('distribution_c', '진로선택 과목은 성취도 C 비율이 필수입니다.')
            # 진로선택일 경우 등급/표준편차 초기화
            cleaned_data['grade_rank'] = None
            cleaned_data['subject_stddev'] = None
        else:
            # 일반 과목: 등급, 표준편차 필수
            if cleaned_data.get('grade_rank') is None:
                self.add_error('grade_rank', '일반 과목은 등급이 필수입니다.')
            if cleaned_data.get('subject_stddev') is None:
                self.add_error('subject_stddev', '일반 과목은 표준편차가 필수입니다.')
            # 일반 과목일 경우 진로선택 필드 초기화
            cleaned_data['achievement_level'] = None
            cleaned_data['distribution_a'] = None
            cleaned_data['distribution_b'] = None
            cleaned_data['distribution_c'] = None

        # category 필드는 모델에 저장되지 않으므로 제거
        cleaned_data.pop('category', None)
        return cleaned_data

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
            ('체육', '체육'), ('음악/미술', '음악/미술'), ('교양', '교양'),
            ('기술/가정', '기술/가정'), ('제2외국어', '제2외국어'),
            ('한문', '한문'), ('기타', '기타')
        ],
        widget=forms.Select(attrs={'class': 'category-select'})
    )

    class Meta:
        model = Grade
        fields = [
            'subject', 'year', 'exam_year', 'exam_month', 'exam_name',
            'score', 'subject_average', 'subject_stddev', 'grade_rank', 'percentile'
        ]
        widgets = {
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

        # 수정 시 현재 과목의 카테고리를 초기값으로 설정
        if self.instance.pk and self.instance.subject:
            self.fields['category'].initial = self.instance.subject.category

    def clean(self):
        cleaned_data = super().clean()
        # category 필드는 모델에 저장되지 않으므로 제거
        cleaned_data.pop('category', None)
        return cleaned_data

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
