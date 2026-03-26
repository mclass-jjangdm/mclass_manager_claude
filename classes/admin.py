from django.contrib import admin
from .models import Lesson, LessonSchedule, Enrollment, TuitionPayment


class LessonScheduleInline(admin.TabularInline):
    model = LessonSchedule
    extra = 0
    fields = ['day', 'start_time', 'end_time']


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = ['student', 'enrollment_date', 'tuition_adjustment', 'is_active']
    readonly_fields = ['created_at']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'teacher', 'days_display', 'base_tuition', 'is_active']
    list_filter = ['is_active', 'teacher']
    search_fields = ['name']
    inlines = [LessonScheduleInline, EnrollmentInline]


@admin.register(LessonSchedule)
class LessonScheduleAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'day', 'start_time', 'end_time']
    list_filter = ['day']


class TuitionPaymentInline(admin.TabularInline):
    model = TuitionPayment
    extra = 0
    fields = ['year', 'month', 'amount', 'payment_date', 'payment_method']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'enrollment_date', 'tuition_adjustment', 'is_active']
    list_filter = ['is_active', 'lesson']
    search_fields = ['student__name', 'lesson__name']
    inlines = [TuitionPaymentInline]


@admin.register(TuitionPayment)
class TuitionPaymentAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'year', 'month', 'amount', 'payment_date', 'payment_method']
    list_filter = ['year', 'month', 'payment_method']
