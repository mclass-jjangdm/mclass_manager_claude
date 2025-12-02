from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'isbn',
        'name', 
        'subject', 
        'publisher', 
        'difficulty_level',
        'unique_code',
    ]
    list_filter = ['subject', 'publisher', 'difficulty_level']
    readonly_fields = ['barcode', 'qr_code', 'unique_code']
    search_fields = ['name', 'isbn']
    fieldsets = [
        ('기본 정보', {
            'fields': ['name', 'subject', 'isbn', 'publisher']
        }),
        ('추가 정보', {
            'fields': ['difficulty_level', 'memo']
        }),
        ('예비 필드', {
            'fields': ['spare1', 'spare2', 'spare3'],
            'classes': ['collapse']
        })
    ]