# progress/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import ProblemType, BookProblem, StudentProgress, ProgressEntry
from bookstore.models import Book, BookSale
from teachers.models import Teacher
from subjects.models import Subject


class ProblemTypeForm(forms.ModelForm):
    """문제 유형 등록 폼"""
    # 개별 필드로 분리하여 입력
    book_code = forms.CharField(
        max_length=7,
        label="교재 코드",
        widget=forms.TextInput(attrs={
            'placeholder': '예: 1234567',
            'class': 'form-control',
            'maxlength': '7',
            'pattern': r'\d{7}'
        }),
        help_text="7자리 숫자 (교재 관리에서 확인 가능)"
    )
    major_unit = forms.CharField(
        max_length=2,
        label="대단원",
        widget=forms.TextInput(attrs={
            'placeholder': '01',
            'class': 'form-control',
            'maxlength': '2',
            'pattern': r'\d{2}'
        }),
        help_text="01~99"
    )
    medium_unit = forms.CharField(
        max_length=2,
        label="중단원",
        widget=forms.TextInput(attrs={
            'placeholder': '01',
            'class': 'form-control',
            'maxlength': '2',
            'pattern': r'\d{2}'
        }),
        help_text="01~99"
    )
    minor_unit = forms.CharField(
        max_length=2,
        label="소단원",
        widget=forms.TextInput(attrs={
            'placeholder': '01',
            'class': 'form-control',
            'maxlength': '2',
            'pattern': r'\d{2}'
        }),
        help_text="01~99"
    )
    problem_type_code = forms.CharField(
        max_length=3,
        label="유형",
        widget=forms.TextInput(attrs={
            'placeholder': '001',
            'class': 'form-control',
            'maxlength': '3',
            'pattern': r'\d{3}'
        }),
        help_text="001~999"
    )
    problem_number = forms.CharField(
        max_length=4,
        label="문제 번호",
        widget=forms.TextInput(attrs={
            'placeholder': '0001',
            'class': 'form-control',
            'maxlength': '4',
            'pattern': r'\d{4}'
        }),
        help_text="0001~9999"
    )
    difficulty = forms.IntegerField(
        label="난도",
        min_value=1,
        max_value=10,
        initial=5,
        widget=forms.NumberInput(attrs={
            'placeholder': '5',
            'class': 'form-control',
            'min': '1',
            'max': '10'
        }),
        help_text="1(쉬움) ~ 10(어려움)"
    )

    class Meta:
        model = ProblemType
        fields = ['title', 'memo', 'difficulty']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': '문제 유형 제목',
                'class': 'form-control'
            }),
            'memo': forms.Textarea(attrs={
                'placeholder': '메모',
                'class': 'form-control',
                'rows': 3
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        # 개별 필드에서 code_number 조합
        book_code = cleaned_data.get('book_code', '').zfill(7)
        major_unit = cleaned_data.get('major_unit', '').zfill(2)
        medium_unit = cleaned_data.get('medium_unit', '').zfill(2)
        minor_unit = cleaned_data.get('minor_unit', '').zfill(2)
        problem_type_code = cleaned_data.get('problem_type_code', '').zfill(3)
        problem_number = cleaned_data.get('problem_number', '').zfill(4)
        difficulty = cleaned_data.get('difficulty')

        # 각 필드 유효성 검사
        if not book_code.isdigit() or len(book_code) != 7:
            raise ValidationError({'book_code': '교재 코드는 7자리 숫자여야 합니다.'})

        if not Book.objects.filter(book_code=book_code).exists():
            raise ValidationError({'book_code': f"교재 코드 '{book_code}'가 존재하지 않습니다."})

        if not major_unit.isdigit() or not (1 <= int(major_unit) <= 99):
            raise ValidationError({'major_unit': '대단원은 01~99 사이여야 합니다.'})

        if not medium_unit.isdigit() or not (1 <= int(medium_unit) <= 99):
            raise ValidationError({'medium_unit': '중단원은 01~99 사이여야 합니다.'})

        if not minor_unit.isdigit() or not (1 <= int(minor_unit) <= 99):
            raise ValidationError({'minor_unit': '소단원은 01~99 사이여야 합니다.'})

        if not problem_type_code.isdigit() or not (1 <= int(problem_type_code) <= 999):
            raise ValidationError({'problem_type_code': '유형은 001~999 사이여야 합니다.'})

        if not problem_number.isdigit() or not (1 <= int(problem_number) <= 9999):
            raise ValidationError({'problem_number': '문제 번호는 0001~9999 사이여야 합니다.'})

        if difficulty is None or not (1 <= difficulty <= 10):
            raise ValidationError({'difficulty': '난도는 1~10 사이여야 합니다.'})

        # code_number 조합 (난도 제외, 20자리)
        code_number = f"{book_code}{major_unit}{medium_unit}{minor_unit}{problem_type_code}{problem_number}"
        cleaned_data['code_number'] = code_number

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.code_number = self.cleaned_data['code_number']
        instance.difficulty = self.cleaned_data['difficulty']
        if commit:
            instance.save()
        return instance


class ProblemTypeUploadForm(forms.Form):
    """CSV/Excel 파일로 문제 유형 일괄 업로드 폼"""
    file = forms.FileField(
        label="파일 업로드 (CSV 또는 Excel)",
        help_text="필수 컬럼: code_number, title / 선택 컬럼: memo"
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext not in ['csv', 'xlsx', 'xls']:
                raise forms.ValidationError("CSV 또는 Excel 파일만 업로드 가능합니다.")
        return file


class BookProblemForm(forms.ModelForm):
    """교재-문제 유형 연결 폼"""
    class Meta:
        model = BookProblem
        fields = ['book', 'problem_type', 'page', 'order', 'memo']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'problem_type': forms.Select(attrs={'class': 'form-control'}),
            'page': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'memo': forms.TextInput(attrs={'placeholder': '비고', 'class': 'form-control'}),
        }


class ProgressEntryForm(forms.ModelForm):
    """진도표 항목 수정 폼"""
    class Meta:
        model = ProgressEntry
        fields = ['is_assigned', 'study_date', 'teacher', 'understanding', 'homework', 'memo']
        widgets = {
            'is_assigned': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5'}),
            'study_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'understanding': forms.Select(attrs={'class': 'form-control'}),
            'homework': forms.TextInput(attrs={'placeholder': '과제 내용', 'class': 'form-control'}),
            'memo': forms.TextInput(attrs={'placeholder': '비고', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True).order_by('name')


class StudentProgressCreateForm(forms.Form):
    """학생 진도표 생성 폼 (BookSale 선택)"""
    book_sale = forms.ModelChoiceField(
        queryset=BookSale.objects.none(),
        label="교재 판매 내역 선택",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['book_sale'].queryset = BookSale.objects.filter(
            progress__isnull=True
        ).select_related('student', 'book').order_by('-sale_date')

    def clean_book_sale(self):
        book_sale = self.cleaned_data.get('book_sale')
        if book_sale:
            if not book_sale.book.problems.exists():
                raise forms.ValidationError(
                    f"'{book_sale.book.title}' 교재에 등록된 문제가 없습니다. 먼저 문제를 등록해주세요."
                )
        return book_sale
