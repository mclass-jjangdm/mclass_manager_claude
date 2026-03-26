from django import forms
from django.db.models import Q, Case, When, Value, IntegerField
from teachers.models import Teacher
from .models import Lesson, Enrollment, TuitionPayment


class LessonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 재직 중인 선생님 + 원장은 항상 포함, 원장을 맨 위에 표시
        self.fields['teacher'].queryset = Teacher.objects.filter(
            Q(is_active=True) | Q(name='원장')
        ).annotate(
            sort_key=Case(
                When(name='원장', then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by('sort_key', 'name')
        self.fields['teacher'].label = '담당 선생님'

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
