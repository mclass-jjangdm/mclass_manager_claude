from django.contrib import admin
from django.utils.html import format_html
from .models import Teacher, Attendance, Salary

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'gender', 'hire_date', 'resignation_date', 'is_active')
    search_fields = ('name', 'phone_number', 'email')
    list_filter = ('gender', 'hire_date', 'resignation_date', 'is_active')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'is_present')
    list_filter = ('date', 'is_present')
    date_hierarchy = 'date'

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'year', 'month', 'work_days', 'formatted_base_amount', 'formatted_additional_amount', 'formatted_total_amount')
    list_filter = ('year', 'month')
    search_fields = ('teacher__name',)

    def formatted_base_amount(self, obj):
        return format_html('{}원', '{:,}'.format(obj.base_amount))
    formatted_base_amount.short_description = '기본급'

    def formatted_additional_amount(self, obj):
        return format_html('{}원', '{:,}'.format(obj.additional_amount))
    formatted_additional_amount.short_description = '추가급'

    def formatted_total_amount(self, obj):
        return format_html('{}원', '{:,}'.format(obj.total_amount))
    formatted_total_amount.short_description = '총액'