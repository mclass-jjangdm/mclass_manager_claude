from django.utils import timezone
from django import forms
from .models import Teacher, TeacherUnavailability, TeacherStudentAssignment


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


class TeacherEmailForm(forms.Form):
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

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'gender', 'phone_number', 'email', 'hire_date', 'resignation_date',
                 'base_salary', 'bank', 'account_number']
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


class TeacherUnavailabilityForm(forms.ModelForm):
    """출근 불가 일정 등록 폼"""
    class Meta:
        model = TeacherUnavailability
        fields = ['teacher', 'date', 'reason', 'memo']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'memo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '상세 사유 (선택사항)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 활성 교사만 표시
        self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True).order_by('name')


class BulkUnavailabilityForm(forms.Form):
    """여러 날짜 일괄 등록 폼"""
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.filter(is_active=True).order_by('name'),
        label='교사',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        label='시작일',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        label='종료일',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    reason = forms.ChoiceField(
        choices=TeacherUnavailability.REASON_CHOICES,
        label='사유',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    memo = forms.CharField(
        required=False,
        label='메모',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '상세 사유 (선택사항)'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('종료일은 시작일 이후여야 합니다.')

        return cleaned_data


class TeacherStudentAssignmentForm(forms.ModelForm):
    """교사-학생 배정 폼"""
    class Meta:
        model = TeacherStudentAssignment
        fields = ['teacher', 'student', 'date', 'memo']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'memo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '메모 (선택사항)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from students.models import Student
        # 활성 교사만 표시
        self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True).order_by('name')
        # 활성 학생만 표시
        self.fields['student'].queryset = Student.objects.filter(is_active=True).order_by('name')
