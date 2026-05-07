from django import forms
from teachers.models import Teacher
from students.models import Student
from .models import Lesson, Enrollment, TuitionPayment, MonthlyEnrollment, STATUS_CHOICES




class LessonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 재직 중인 선생님만 표시, null(미선택) = 원장으로 취급
        self.fields['teacher'].queryset = Teacher.objects.filter(
            is_active=True
        ).order_by('name')
        self.fields['teacher'].label = '담당 선생님'
        self.fields['teacher'].empty_label = '원장'
        self.fields['teacher'].required = False

    class Meta:
        model = Lesson
        fields = ['name', 'subject', 'teacher', 'books', 'base_tuition', 'memo', 'is_active']
        widgets = {
            'memo': forms.Textarea(attrs={'rows': 3}),
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = [
            'student', 'enrollment_date', 'end_date',
            'tuition_adjustment', 'memo', 'is_active',
        ]
        widgets = {
            'enrollment_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'memo': forms.Textarea(attrs={'rows': 2}),
        }


class MonthlyEnrollmentEditForm(forms.ModelForm):
    lesson = forms.ModelChoiceField(
        queryset=Lesson.objects.filter(is_active=True).order_by('name'),
        label='수업',
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label='상태',
    )

    class Meta:
        model = MonthlyEnrollment
        fields = ['lesson', 'status', 'tuition_adjustment', 'memo']
        widgets = {
            'memo': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'tuition_adjustment': '수강료 조정액',
            'memo': '메모',
        }


class LessonTransferForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(is_active=True).order_by('name'),
        label='학생',
        widget=forms.Select(attrs={'id': 'id_student'}),
    )
    from_lesson = forms.ModelChoiceField(
        queryset=Lesson.objects.filter(is_active=True).order_by('name'),
        label='현재 반',
    )
    to_lesson = forms.ModelChoiceField(
        queryset=Lesson.objects.filter(is_active=True).order_by('name'),
        label='이동할 반',
    )
    transfer_date = forms.DateField(
        label='전반일',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def clean(self):
        cleaned = super().clean()
        student = cleaned.get('student')
        from_lesson = cleaned.get('from_lesson')
        to_lesson = cleaned.get('to_lesson')

        if from_lesson and to_lesson and from_lesson == to_lesson:
            raise forms.ValidationError('현재 반과 이동할 반이 같습니다.')

        if student and from_lesson:
            if not Enrollment.objects.filter(student=student, lesson=from_lesson, is_active=True).exists():
                raise forms.ValidationError(f'{student.name} 학생은 {from_lesson.name} 반에 수강 중이 아닙니다.')

        return cleaned


class TuitionPaymentForm(forms.ModelForm):
    class Meta:
        model = TuitionPayment
        fields = ['year', 'month', 'amount', 'payment_date', 'payment_method', 'memo']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'memo': forms.Textarea(attrs={'rows': 2}),
        }
