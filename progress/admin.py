# progress/admin.py

from django.contrib import admin
from .models import ProblemType, BookProblem, StudentProgress, ProgressEntry


@admin.register(ProblemType)
class ProblemTypeAdmin(admin.ModelAdmin):
    list_display = ('code_number', 'title', 'get_subject_code', 'get_difficulty', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('code_number', 'title', 'memo')
    ordering = ['code_number']

    def get_subject_code(self, obj):
        return obj.subject_code
    get_subject_code.short_description = "과목코드"

    def get_difficulty(self, obj):
        return obj.difficulty
    get_difficulty.short_description = "난도"


class ProgressEntryInline(admin.TabularInline):
    model = ProgressEntry
    extra = 0
    fields = ['book_problem', 'is_assigned', 'study_date', 'teacher', 'understanding', 'homework', 'memo']
    raw_id_fields = ['book_problem']


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
    get_title.short_description = "제목"


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'created_at', 'get_completion_rate')
    list_filter = ('book', 'created_at')
    search_fields = ('student__name', 'book__title')
    inlines = [ProgressEntryInline]
    date_hierarchy = 'created_at'

    def get_completion_rate(self, obj):
        return f"{obj.get_completion_rate()}%"
    get_completion_rate.short_description = "진도율"


@admin.register(ProgressEntry)
class ProgressEntryAdmin(admin.ModelAdmin):
    list_display = ('progress', 'get_code_number', 'is_assigned', 'study_date', 'teacher', 'understanding')
    list_filter = ('is_assigned', 'understanding', 'teacher', 'study_date')
    search_fields = ('progress__student__name', 'book_problem__problem_type__code_number')
    date_hierarchy = 'study_date'

    def get_code_number(self, obj):
        return obj.book_problem.problem_type.code_number
    get_code_number.short_description = "코드 번호"
