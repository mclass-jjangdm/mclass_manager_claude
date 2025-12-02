import datetime
from django.contrib import admin
from maintenance.forms import MonthYearWidget
from .models import Maintenance, Room
from django.db.models import Sum
from django import forms


# class MaintenanceAdminForm(forms.ModelForm):
#     date = forms.DateField(
#         label='부과년월',
#         widget=forms.DateInput(
#             attrs={
#                 'type': 'month'
#             }
#         ),
#         input_formats=['%Y-%m'],
#     )

#     class Meta:
#         model = Maintenance
#         fields = '__all__'
#         widgets = {
#             'room': forms.NumberInput(attrs={
#                 'min': '1',
#                 'step': '1',
#             }),
#             'charge': forms.NumberInput(attrs={
#                 'min': '0',
#                 'step': '1',
#             }),
#         }

#     def clean_date(self):
#         date = self.cleaned_data['date']
#         if isinstance(date, str):
#             try:
#                 year, month = map(int, date.split('-'))
#                 date = datetime.date(year, month, 1)
#             except ValueError:
#                 raise forms.ValidationError('올바른 년월 형식이 아닙니다.')
#         return date.replace(day=1)


class MaintenanceAdminForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = '__all__'
        widgets = {
            'room': forms.Select(attrs={
                'style': 'width: 200px;'
            })
        }


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['get_room_number', 'contract_start_date', 'contract_end_date', 'is_active']
    list_filter = ['is_active']
    ordering = ['number']
    search_fields = ['number']

    def get_room_number(self, obj):
        return f"{obj.number}호"
    get_room_number.short_description = '호실'


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    form = MaintenanceAdminForm
    list_display = ['get_room_display', 'formatted_date', 'formatted_charge', 'date_paid', 'payment_status']
    list_filter = ['room', 'date', 'date_paid']
    search_fields = ['room__number', 'memo']
    ordering = ['-date', 'room']
    date_hierarchy = 'date'

    def get_room_display(self, obj):
        return f"{obj.room.number}호"
    get_room_display.short_description = '호실'

    def formatted_date(self, obj):
        return obj.date.strftime('%Y년 %m월')
    formatted_date.short_description = '부과년월'

    def formatted_charge(self, obj):
        return f"{obj.charge:,}"
    formatted_charge.short_description = '부과금액'

    def payment_status(self, obj):
        return '납부완료' if obj.date_paid else '미납'
    payment_status.short_description = '납부상태'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            kwargs["queryset"] = Room.objects.filter(is_active=True).order_by('number')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)