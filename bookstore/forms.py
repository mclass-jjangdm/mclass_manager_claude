from django import forms
from django.utils import timezone
from .models import BookStock, BookIssue
from students.models import Student

class StockCreateForm(forms.ModelForm):
    class Meta:
        model = BookStock
        fields = ['received_date', 'book', 'quantity', 'list_price', 'unit_price', 'selling_price', 'memo']

class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = BookStock
        fields = ['received_date', 'book', 'quantity', 'list_price', 'unit_price', 'selling_price', 'memo']

class BookIssueForm(forms.ModelForm):
    class Meta:
        model = BookIssue
        fields = ['book_stock', 'student', 'quantity', 'issued_date', 'memo']
        widgets = {
            'issued_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 활성 학생만 필터링 (is_active=True)
        self.fields['student'].queryset = Student.objects.filter(is_active=True)
        self.fields['quantity'].initial = 1
        self.fields['issued_date'].initial = timezone.now().date()
