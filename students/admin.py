from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'school', 'grade', 'interview_date', 'first_class_date')
    list_filter = ('school', 'grade', 'gender')
    search_fields = ('name', 'student_id', 'email')
    readonly_fields = ('student_id',)
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'student_id', 'school', 'grade', 'gender', 'email')
        }),
        ('연락처 정보', {
            'fields': ('phone_number', 'parent_phone', 'receipt_number')
        }),
        ('인터뷰 정보', {
            'fields': ('interview_date', 'interview_score', 'interview_info')
        }),
        ('수업 정보', {
            'fields': ('first_class_date', 'quit_date')
        }),
        ('추가 정보', {
            'fields': ('personal_file', 'etc', 'extra1', 'extra2', 'extra3', 'extra4', 'extra5')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.student_id:
            obj.student_id = obj.generate_student_id()
        super().save_model(request, obj, form, change)