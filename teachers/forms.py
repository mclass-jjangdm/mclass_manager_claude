from django.utils import timezone
from django import forms
from .models import Teacher

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'gender', 'phone_number', 'email', 'hire_date', 'resignation_date', 
                 'base_salary', 'additional_salary', 'bank', 'account_number']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '이름'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-input',
                'placeholder': '성별',
            }, choices=[('', )] + Teacher.GENDER_CHOICES),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '01012345678 (숫자만 입력)',
                'maxlength': '11'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': '이메일'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'resignation_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'base_salary': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '시급'
            }),
            'additional_salary': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '추가 급여'
            }),
            'bank': forms.Select(attrs={
                'class': 'form-input'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '계좌번호'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 필수가 아닌 필드들 설정
        self.fields['resignation_date'].required = False
        self.fields['additional_salary'].required = False
        self.fields['email'].required = False
        self.fields['bank'].required = False
        self.fields['account_number'].required = False

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # 모든 특수문자 제거 (띄어쓰기, 하이픈 등)
            phone_number = ''.join(filter(str.isdigit, phone_number))
            
            # 길이 검증
            if len(phone_number) == 11 and phone_number.startswith('010'):
                # 휴대폰 번호: 01012345678
                return phone_number
            elif len(phone_number) == 10:
                if phone_number.startswith('02'):
                    # 서울 지역번호: 0212345678
                    return phone_number
                else:
                    # 기타 지역번호: 0311234567
                    return phone_number
            elif len(phone_number) == 9 and phone_number.startswith('02'):
                # 서울 지역번호: 021234567
                return phone_number
            else:
                raise forms.ValidationError('올바른 전화번호 형식이 아닙니다. 9-11자리 숫자로 입력해주세요. (예: 01012345678, 0212345678)')
            
        return phone_number

class AttendanceRecordForm(forms.Form):
    is_present = forms.BooleanField(required=False, initial=True, label='출근')
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        initial=timezone.now().replace(hour=18, minute=0, second=0).time(),
        required=False,
        label='시작 시간'
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        initial=timezone.now().replace(hour=20, minute=0, second=0).time(),
        required=False,
        label='종료 시간'
    )

class BulkAttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=timezone.now)

    def __init__(self, *args, **kwargs):
        teachers = kwargs.pop('teachers', None)
        super().__init__(*args, **kwargs)
        
        if teachers:
            for teacher in teachers:
                self.fields[f'is_present_{teacher.id}'] = forms.BooleanField(required=False, initial=True, label=f'{teacher.name} 출근')
                self.fields[f'start_time_{teacher.id}'] = forms.TimeField(
                    widget=forms.TimeInput(attrs={'type': 'time'}),
                    initial=timezone.now().replace(hour=18, minute=0, second=0).time(),
                    required=False,
                    label=f'{teacher.name} 시작 시간'
                )
                self.fields[f'end_time_{teacher.id}'] = forms.TimeField(
                    widget=forms.TimeInput(attrs={'type': 'time'}),
                    initial=timezone.now().replace(hour=20, minute=0, second=0).time(),
                    required=False,
                    label=f'{teacher.name} 종료 시간'
                )
