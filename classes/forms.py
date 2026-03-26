from django import forms
from teachers.models import Teacher
from .models import Lesson, Enrollment, TuitionPayment


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


class TuitionPaymentForm(forms.ModelForm):
    class Meta:
        model = TuitionPayment
        fields = ['year', 'month', 'amount', 'payment_date', 'payment_method', 'memo']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'memo': forms.Textarea(attrs={'rows': 2}),
        }
