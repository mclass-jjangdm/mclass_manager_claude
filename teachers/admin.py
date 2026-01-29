from django.contrib import admin
from django.utils.html import format_html
from .models import Teacher, Attendance, Salary, TeacherUnavailability, TeacherStudentAssignment

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


@admin.register(TeacherUnavailability)
class TeacherUnavailabilityAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'reason', 'status_display', 'created_by_admin', 'reviewed_at', 'created_at')
    list_filter = ('status', 'reason', 'date', 'teacher', 'created_by_admin')
    search_fields = ('teacher__name', 'memo', 'reject_reason')
    date_hierarchy = 'date'
    ordering = ['-date', 'teacher__name']
    readonly_fields = ('created_at', 'reviewed_at')

    def status_display(self, obj):
        colors = {
            'pending': '#f59e0b',  # 노란색
            'approved': '#10b981',  # 녹색
            'rejected': '#ef4444',  # 빨간색
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = '승인 상태'


@admin.register(TeacherStudentAssignment)
class TeacherStudentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('date', 'teacher', 'student', 'memo', 'created_at')
    list_filter = ('date', 'teacher')
    search_fields = ('teacher__name', 'student__name', 'memo')
    date_hierarchy = 'date'
    ordering = ['-date', 'teacher__name', 'student__name']