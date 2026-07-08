# forms.py
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import Student, School
from common.utils import validate_uploaded_file, validate_file_size


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class StudentEmailForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        label='제목',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '이메일 제목을 입력하세요'
        })
    )
    message = forms.CharField(
        label='내용',
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 10,
            'placeholder': '이메일 내용을 입력하세요'
        })
    )
    attachments = MultipleFileField(
        label='첨부파일',
        required=False,
        help_text='여러 파일을 선택할 수 있습니다.'
    )


class StudentSMSForm(forms.Form):
    message = forms.CharField(
        label='문자 내용',
        max_length=2000,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 6,
            'placeholder': '문자 내용을 입력하세요 (최대 2000자)',
            'maxlength': '2000'
        }),
        help_text='SMS: 90바이트(한글 45자) / LMS: 2000바이트(한글 1000자)'
    )


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        exclude = (
            'student_id',
            'is_active',  # 퇴원 처리 여부
            'extra1',     # 예비1
            'extra2',     # 예비2
            'extra3',     # 예비3
            'extra4',     # 예비4
            'extra5',     # 예비5
        )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 필수가 아닌 필드들 설정
        self.fields['school'].required = False
        self.fields['grade'].required = False
        self.fields['email'].required = False
        self.fields['gender'].required = False
        self.fields['parent_phone'].required = False
        self.fields['receipt_number'].required = False
        self.fields['interview_date'].required = False
        self.fields['interview_info'].required = False
        self.fields['first_class_date'].required = False
        self.fields['quit_date'].required = False
        self.fields['etc'].required = False
        self.fields['personal_file'].required = False

        # widgets를 유지합니다.
        self.fields['name'].widget = forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '이름을 입력하세요'
        })
        self.fields['phone_number'].widget = forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '010-0000-0000',
            'maxlength': '13',
            'oninput': 'formatPhoneInput(this)'
        })
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': '이메일을 입력하세요'
        })
        self.fields['parent_phone'].widget = forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '010-0000-0000',
            'maxlength': '13',
            'oninput': 'formatPhoneInput(this)'
        })
        self.fields['receipt_number'].widget = forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '현금영수증용 번호를 입력하세요'
        })
        self.fields['interview_date'].widget = forms.TextInput(attrs={
            'class': 'form-input mclass-datepicker',
            'readonly': 'readonly'
        })
        self.fields['interview_score'].widget = forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '인터뷰 평가를 입력하세요',
            'min': 1,
            'max': 10
        })
        self.fields['interview_info'].widget = forms.Textarea(attrs={
            'class': 'form-input',  # form-textarea에서 form-input으로 변경
            'placeholder': '인터뷰 정보를 입력하세요',
            'style': 'height: 100px; width: 100%;'  # width 추가
        })
        self.fields['first_class_date'].widget = forms.TextInput(attrs={
            'class': 'form-input mclass-datepicker',
            'readonly': 'readonly'
        })
        self.fields['quit_date'].widget = forms.TextInput(attrs={
            'class': 'form-input mclass-datepicker',
            'readonly': 'readonly'
        })
        self.fields['etc'].widget = forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '기타 정보를 입력하세요'
        })
        self.fields['personal_file'].widget = forms.FileInput(attrs={
            'class': 'form-input'
        })
        self.fields['director_memo'].widget = forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': '학생 특징 및 요구사항을 입력하세요 (선생님에게 표시됨)',
            'rows': 3
        })
        self.fields['director_memo'].required = False


class StudentImportForm(forms.Form):
    file = forms.FileField(
        label='파일 업로드',
        help_text='허용된 확장자: .xlsx, .xls, .csv (최대 5MB)',
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1].lower()

        # 확장자 검증
        if ext not in ['xlsx', 'xls', 'csv']:
            raise forms.ValidationError('엑셀 파일(.xlsx, .xls) 또는 CSV 파일(.csv)만 업로드 가능합니다.')

        # 파일 크기 검증 (5MB)
        max_size = getattr(settings, 'MAX_IMPORT_FILE_SIZE', 5 * 1024 * 1024)
        if file.size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise forms.ValidationError(f'파일 크기가 너무 큽니다. (최대 {max_mb:.0f}MB)')

        return file


class StudentFileUploadForm(forms.Form):
    """학생 파일 업로드 폼 (보안 강화)"""
    file = forms.FileField(
        label='파일',
        help_text='허용된 파일 형식: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG 등 (최대 10MB)',
    )
    description = forms.CharField(
        label='설명',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '파일 설명 (선택사항)'
        })
    )

    def clean_file(self):
        file = self.cleaned_data['file']

        # 종합 파일 검증
        try:
            validate_uploaded_file(file)
        except ValidationError as e:
            raise forms.ValidationError(str(e))

        return file


class ParentStudentUpdateForm(forms.ModelForm):
    """부모님용 학생 정보 수정 폼 (제한된 필드만 수정 가능)"""
    class Meta:
        model = Student
        fields = ['phone_number', 'email', 'parent_phone', 'receipt_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].widget = forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': '010-0000-0000'
        })
        self.fields['phone_number'].required = False
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'example@email.com'
        })
        self.fields['email'].required = False
        self.fields['parent_phone'].widget = forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': '010-0000-0000'
        })
        self.fields['parent_phone'].required = False
        self.fields['receipt_number'].widget = forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': '현금영수증 발급용 번호'
        })
        self.fields['receipt_number'].required = False


class BulkSMSForm(forms.Form):
    TARGET_CHOICES = [
        ('student', '학생'),
        ('parent', '학부모'),
        ('both', '학생 + 학부모'),
    ]

    student_ids = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
    )

    target = forms.ChoiceField(
        choices=TARGET_CHOICES,
        initial='student',
        label='발송 대상',
        widget=forms.RadioSelect,
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': '전송할 메시지를 입력하세요',
            'rows': 5,
            'maxlength': 2000,
        }),
        label='메시지',
        max_length=2000,
    )

    def clean_student_ids(self):
        student_ids = self.cleaned_data.get('student_ids', '')
        if not student_ids:
            raise forms.ValidationError('발송 대상 학생을 선택해주세요.')

        # 콤마로 구분된 ID를 리스트로 변환
        try:
            id_list = [int(id.strip()) for id in student_ids.split(',') if id.strip()]
            if not id_list:
                raise ValueError
            return id_list
        except (ValueError, AttributeError):
            raise forms.ValidationError('잘못된 학생 ID 형식입니다.')

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if not message:
            raise forms.ValidationError('메시지를 입력해주세요.')
        return message