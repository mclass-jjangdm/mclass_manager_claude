from django import forms
from .models import Room, Maintenance
from datetime import datetime


class MonthYearWidget(forms.widgets.Widget):
    template_name = 'maintenance/month_year_widget.html'
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if value:
            if isinstance(value, datetime.date):
                value = value.strftime('%Y-%m')
            context['widget']['value'] = value
        return context


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['number', 'contract_start_date', 'contract_end_date', 'is_active']
        widgets = {
            'number': forms.NumberInput(attrs={
                'min': '1',
                'class': 'form-control'
            }),
            'contract_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'contract_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class MaintenanceForm(forms.Form):
    date = forms.CharField(
        label='부과년월',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'month',
            'style': 'width: 150px;'
        })
    )
    
    def clean_date(self):
        date_str = self.cleaned_data.get('date')
        try:
            return datetime.strptime(date_str + '-01', '%Y-%m-%d').date()
            # 또는 별칭을 사용한 경우: return dt.strptime(date_str + '-01', '%Y-%m-%d').date()
        except ValueError:
            raise forms.ValidationError('올바른 년월을 입력해주세요.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rooms = Room.objects.all().order_by('number')
        
        for room in rooms:
            self.fields[f'charge_{room.id}'] = forms.DecimalField(
                label=f'{room.number}호 부과금액',
                required=False,
                min_value=0,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control charge-input',
                    'style': 'width: 100%;'
                })
            )
            self.fields[f'date_paid_{room.id}'] = forms.DateField(
                label=f'{room.number}호 납부일자',
                required=False,
                widget=forms.DateInput(attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'style': 'width: 100%;'
                })
            )
            self.fields[f'memo_{room.id}'] = forms.CharField(
                label=f'{room.number}호 메모',
                required=False,
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'style': 'width: 100%;'
                })
            )


class MaintenanceUpdateForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ['charge', 'date_paid', 'memo']
        widgets = {
            'charge': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '0'
            }),
            'date_paid': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'memo': forms.TextInput(attrs={
                'class': 'form-input'
            })
        }