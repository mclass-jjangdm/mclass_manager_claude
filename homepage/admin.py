from django.contrib import admin
from .models import Notice, Column, ExamNews, SchoolIntro, VisitorStat, ConsultationRequest


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_published', 'created_at']
    list_filter = ['is_published']
    search_fields = ['title', 'content']


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_published', 'created_at']
    list_filter = ['is_published']
    search_fields = ['title', 'content']


@admin.register(ExamNews)
class ExamNewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_name', 'is_published', 'created_at']
    list_filter = ['is_published']
    search_fields = ['title', 'content', 'source_name']


@admin.register(SchoolIntro)
class SchoolIntroAdmin(admin.ModelAdmin):
    list_display = ['academy_name', 'phone', 'email', 'updated_at']


@admin.register(VisitorStat)
class VisitorStatAdmin(admin.ModelAdmin):
    list_display = ['date', 'count']
    ordering = ['-date']
    readonly_fields = ['date', 'count']


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'grade', 'phone_number', 'status', 'created_at']
    list_filter = ['status', 'grade', 'gender']
    search_fields = ['name', 'phone_number', 'school', 'parent_phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
