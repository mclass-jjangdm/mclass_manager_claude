# bookstore/forms.py

from django import forms
from .models import Book, BookStockLog, BookSupplier, BookSale
import re


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['created_at', 'title', 'isbn', 'author', 'publisher', 'supplier', 'original_price',
                  'cost_price', 'price', 'stock', 'memo']
        widgets = {
            'created_at': forms.DateInput(attrs={'type': 'date'}),
            'isbn': forms.TextInput(attrs={
                'placeholder': '바코드를 스캔하세요',
                'autofocus': 'autofocus',
                'class': 'ime-mode-disabled',
                'id': 'id_isbn',
            }),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'original_price': forms.NumberInput(attrs={'step': '100'}),
            'cost_price': forms.NumberInput(attrs={'step': '10'}),
            'price': forms.NumberInput(attrs={'step': '100'}),
            'memo': forms.TextInput(attrs={'placeholder': '비고 (선택 사항)'}),
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn:
            isbn = re.sub(r'[^0-9X]', '', isbn.upper())

            if len(isbn) == 10:
                core = isbn[:9]
                temp_isbn = "978" + core

                total = 0
                for i, digit in enumerate(temp_isbn):
                    total += int(digit) * (1 if i % 2 == 0 else 3)

                check_digit = (10 - (total % 10)) % 10
                isbn = temp_isbn + str(check_digit)

            if len(isbn) != 13:
                raise forms.ValidationError(f"올바르지 않은 바코드 길이입니다. (변환 후 {len(isbn)}자리)")

        return isbn


class BookSupplierForm(forms.ModelForm):
    class Meta:
        model = BookSupplier
        fields = ['name', 'registration_number', 'phone', 'address', 'bank_name', 'account_number', 'account_owner']
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': '주소 입력'}),
        }


class BookStockLogForm(forms.ModelForm):
    class Meta:
        model = BookStockLog
        fields = ['created_at', 'supplier', 'quantity', 'cost_price', 'memo']

        widgets = {
            'created_at': forms.DateInput(attrs={'type': 'date'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'autofocus': 'autofocus'}),
            'cost_price': forms.NumberInput(attrs={'step': 100}),
            'memo': forms.TextInput(attrs={'placeholder': '비고'}),
        }
        labels = {
            'created_at': '입고 날짜',
        }

class BookReturnForm(forms.ModelForm):
    class Meta:
        model = BookStockLog
        fields = ['supplier', 'quantity', 'cost_price', 'total_payment', 'payment_date', 'memo']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'autofocus': 'autofocus'}),
            'cost_price': forms.NumberInput(attrs={'step': 100}),
            'total_payment': forms.NumberInput(attrs={'readonly': 'readonly', 'style': 'background-color: #eee;'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'memo': forms.TextInput(attrs={'placeholder': '반품 사유'}),
        }


class BookSaleForm(forms.ModelForm):
    class Meta:
        model = BookSale
        fields = ['sale_date', 'book', 'quantity', 'price', 'is_paid', 'memo']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'value': 1}),
            'price': forms.NumberInput(attrs={'step': 100}),
            'sale_date': forms.DateInput(attrs={'type': 'date'}),
            'memo': forms.TextInput(attrs={'placeholder': '비고'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['book'].queryset = Book.objects.filter(stock__gt=0).order_by('title')
        self.fields['book'].label = "판매할 교재"
