# progress/admin.py

from django.contrib import admin
from .models import ProblemType, BookProblem, StudentProgress, ProgressEntry, StudentActivity, LearningRecord


@admin.register(ProblemType)
class ProblemTypeAdmin(admin.ModelAdmin):
    list_display = ('code_number', 'title', 'difficulty', 'get_book', 'created_at')
    list_filter = ('difficulty', 'created_at')
    search_fields = ('code_number', 'title', 'memo')
    ordering = ['code_number']
    readonly_fields = ('created_at', 'updated_at')

    def get_book(self, obj):
        return obj.book.title if obj.book else '-'
    get_book.short_description = "교재"


@admin.register(BookProblem)
class BookProblemAdmin(admin.ModelAdmin):
    list_display = ('book', 'get_code_number', 'get_title', 'page', 'order')
    list_filter = ('book',)
    search_fields = ('book__title', 'problem_type__code_number', 'problem_type__title')
    ordering = ['book', 'order']
    raw_id_fields = ['problem_type']

    def get_code_number(self, obj):
        return obj.problem_type.code_number
    get_code_number.short_description = "코드 번호"

    def get_title(self, obj):
        return obj.problem_type.title
    get_title.short_description = "유형 제목"


class ProgressEntryInline(admin.TabularInline):
    model = ProgressEntry
    extra = 0
    fields = ['book_problem', 'is_assigned', 'study_date', 'teacher', 'understanding', 'homework', 'memo']
    raw_id_fields = ['book_problem']


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'get_completion_rate', 'created_at')
    list_filter = ('book', 'created_at')
    search_fields = ('student__name', 'book__title')
    inlines = [ProgressEntryInline]
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def get_completion_rate(self, obj):
        return f"{obj.get_completion_rate()}%"
    get_completion_rate.short_description = "진도율"


@admin.register(ProgressEntry)
class ProgressEntryAdmin(admin.ModelAdmin):
    list_display = ('get_student', 'get_code_number', 'is_assigned', 'study_date', 'teacher', 'understanding')
    list_filter = ('is_assigned', 'understanding', 'teacher')
    search_fields = ('progress__student__name', 'book_problem__problem_type__code_number')
    raw_id_fields = ['book_problem']

    def get_student(self, obj):
        return obj.progress.student.name
    get_student.short_description = "학생"

    def get_code_number(self, obj):
        return obj.book_problem.problem_type.code_number
    get_code_number.short_description = "코드 번호"


@admin.register(StudentActivity)
class StudentActivityAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'activity_type', 'title', 'teacher', 'achievement', 'needs_review', 'homework_checked')
    list_filter = ('activity_type', 'achievement', 'needs_review', 'homework_checked', 'date', 'teacher')
    search_fields = ('student__name', 'title', 'memo')
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('기본 정보', {
            'fields': ('student', 'teacher', 'date', 'activity_type', 'title', 'subject')
        }),
        ('평가', {
            'fields': ('achievement', 'score', 'total_score', 'needs_review', 'homework_checked')
        }),
        ('메모', {
            'fields': ('memo',)
        }),
        ('시스템', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LearningRecord)
class LearningRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'record_type', 'title', 'teacher', 'achievement', 'needs_review', 'homework_checked')
    list_filter = ('record_type', 'achievement', 'needs_review', 'homework_checked', 'date', 'teacher')
    search_fields = ('student__name', 'title', 'memo')
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('기본 정보', {
            'fields': ('student', 'teacher', 'date', 'record_type', 'title', 'subject')
        }),
        ('교재 진도 (record_type=textbook인 경우)', {
            'fields': ('book_sale', 'book_content'),
            'classes': ('collapse',)
        }),
        ('평가', {
            'fields': ('achievement', 'score', 'total_score', 'needs_review', 'homework_checked')
        }),
        ('메모', {
            'fields': ('memo',)
        }),
        ('시스템', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
