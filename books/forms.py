from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    difficulty_level = forms.IntegerField(
        label='교재 난이도',
        min_value=1,
        max_value=10,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50',
            'placeholder': '1-10 사이의 값을 입력하세요'
        }),
        help_text='1(쉬움) ~ 10(어려움)'
    )

    class Meta:
        model = Book
        exclude = ['barcode', 'qr_code', 'spare1', 'spare2', 'spare3']
        widgets = {
            'memo': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 필수 필드가 아닌 경우 "(선택)" 텍스트 추가
        for field_name, field in self.fields.items():
            if not field.required:
                field.label = f"{field.label} (선택)"
            
            if field_name not in ['difficulty_level']:  # difficulty_level은 이미 위에서 설정됨
                field.widget.attrs.update({
                    'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
                })

    def clean_difficulty_level(self):
        difficulty = self.cleaned_data.get('difficulty_level')
        if difficulty is not None and (difficulty < 1 or difficulty > 10):
            raise forms.ValidationError('난이도는 1부터 10 사이의 값이어야 합니다.')
        return difficulty