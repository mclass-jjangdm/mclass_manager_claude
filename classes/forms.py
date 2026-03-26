from django import forms
from teachers.models import Teacher
from .models import Lesson, Enrollment, TuitionPayment


class LessonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True).order_by('name')
        self.fields['teacher'].label = '담당 선생님'

    class Meta:
        model = Lesson
        fields = [
            'name', 'subject', 'teacher', 'books',
            'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
            'start_time', 'end_time',
            'base_tuition', 'memo', 'is_active',
        ]
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
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
