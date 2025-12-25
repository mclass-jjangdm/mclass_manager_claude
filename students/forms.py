# forms.py
from django import forms
from .models import Student, School


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
            'placeholder': '학생 전화번호를 입력하세요'
        })
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': '이메일을 입력하세요'
        })
        self.fields['parent_phone'].widget = forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '부모님 전화번호를 입력하세요'
        })
        self.fields['receipt_number'].widget = forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '현금영수증용 번호를 입력하세요'
        })
        self.fields['interview_date'].widget = forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
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
        self.fields['first_class_date'].widget = forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
        self.fields['quit_date'].widget = forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
        self.fields['etc'].widget = forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '기타 정보를 입력하세요'
        })
        self.fields['personal_file'].widget = forms.FileInput(attrs={
            'class': 'form-input'
        })


class StudentImportForm(forms.Form):
    file = forms.FileField(
        label='파일 업로드',
        help_text='허용된 확장자: .xlsx, .xls, .csv',
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1].lower()

        if ext not in ['xlsx', 'xls', 'csv']:
            raise forms.ValidationError('엑셀 파일(.xlsx, .xls) 또는 CSV 파일(.csv)만 업로드 가능합니다.')

        return file


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