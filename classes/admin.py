from django.contrib import admin
from django.contrib import messages
from .models import Lesson, LessonSchedule, Enrollment, TuitionPayment, MonthlyEnrollment


class LessonScheduleInline(admin.TabularInline):
    model = LessonSchedule
    extra = 0
    fields = ['day', 'start_time', 'end_time']


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = ['student', 'enrollment_date', 'tuition_adjustment', 'is_active']
    readonly_fields = ['created_at']
    can_delete = False  # 인라인 삭제 비활성화 (고아 MonthlyEnrollment 방지)


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


def _cancel_monthly_enrollments_and_delete(modeladmin, request, enrollment):
    """Enrollment 삭제 전 납부 기록 확인 및 MonthlyEnrollment 정리"""
    if enrollment.payments.exists():
        modeladmin.message_user(
            request,
            f'[{enrollment.student.name} / {enrollment.lesson.name}] 납부 기록이 있어 삭제할 수 없습니다.',
            level=messages.ERROR,
        )
        return False
    MonthlyEnrollment.objects.filter(
        student=enrollment.student,
        lesson=enrollment.lesson,
    ).update(status='cancelled')
    return True


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'enrollment_date', 'tuition_adjustment', 'is_active']
    list_filter = ['is_active', 'lesson']
    search_fields = ['student__name', 'lesson__name']
    inlines = [TuitionPaymentInline]

    def delete_model(self, request, obj):
        if not _cancel_monthly_enrollments_and_delete(self, request, obj):
            return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        blocked = []
        for enrollment in queryset.prefetch_related('payments'):
            if enrollment.payments.exists():
                blocked.append(f'{enrollment.student.name} / {enrollment.lesson.name}')
            else:
                MonthlyEnrollment.objects.filter(
                    student=enrollment.student,
                    lesson=enrollment.lesson,
                ).update(status='cancelled')

        if blocked:
            self.message_user(
                request,
                f'납부 기록이 있어 삭제할 수 없는 수강: {", ".join(blocked)}',
                level=messages.ERROR,
            )
            return

        queryset.delete()


@admin.register(TuitionPayment)
class TuitionPaymentAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'year', 'month', 'amount', 'payment_date', 'payment_method']
    list_filter = ['year', 'month', 'payment_method']


@admin.register(MonthlyEnrollment)
class MonthlyEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'year', 'month', 'status', 'tuition_fee', 'tuition_adjustment']
    list_filter = ['year', 'month', 'status', 'lesson']
    search_fields = ['student__name', 'lesson__name']
    ordering = ['-year', '-month', 'lesson__name', 'student__name']
