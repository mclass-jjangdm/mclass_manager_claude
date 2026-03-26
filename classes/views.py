from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Lesson, Enrollment, TuitionPayment
from .forms import LessonForm, EnrollmentForm, TuitionPaymentForm


def _admin_required(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')
    return None


# ──────────────────────────────────────────────
# Lesson (수업)
# ──────────────────────────────────────────────

@login_required
def lesson_list(request):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    lessons = Lesson.objects.select_related('subject', 'teacher')
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', 'active')

    if search:
        lessons = lessons.filter(name__icontains=search)
    if status == 'active':
        lessons = lessons.filter(is_active=True)
    elif status == 'inactive':
        lessons = lessons.filter(is_active=False)

    return render(request, 'classes/lesson_list.html', {
        'lessons': lessons,
        'search': search,
        'status': status,
    })


@login_required
def lesson_detail(request, pk):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    lesson = get_object_or_404(Lesson, pk=pk)
    enrollments = lesson.enrollments.select_related('student').prefetch_related('payments').order_by('-enrollment_date')

    return render(request, 'classes/lesson_detail.html', {
        'lesson': lesson,
        'enrollments': enrollments,
    })


@login_required
def lesson_create(request):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save()
            messages.success(request, f'수업 "{lesson.name}"이 생성되었습니다.')
            return redirect('classes:lesson_detail', pk=lesson.pk)
    else:
        form = LessonForm()

    return render(request, 'classes/lesson_form.html', {
        'form': form,
        'action': 'create',
    })


@login_required
def lesson_edit(request, pk):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    lesson = get_object_or_404(Lesson, pk=pk)

    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f'수업 "{lesson.name}"이 수정되었습니다.')
            return redirect('classes:lesson_detail', pk=lesson.pk)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'classes/lesson_form.html', {
        'form': form,
        'lesson': lesson,
        'action': 'edit',
    })


@login_required
def lesson_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    lesson = get_object_or_404(Lesson, pk=pk)

    if request.method == 'POST':
        name = lesson.name
        lesson.delete()
        messages.success(request, f'수업 "{name}"이 삭제되었습니다.')
        return redirect('classes:lesson_list')

    return render(request, 'classes/lesson_confirm_delete.html', {'lesson': lesson})


# ──────────────────────────────────────────────
# Enrollment (수강 신청)
# ──────────────────────────────────────────────

@login_required
def enrollment_create(request, pk):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    lesson = get_object_or_404(Lesson, pk=pk)

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.lesson = lesson
            try:
                enrollment.save()
                messages.success(request, f'{enrollment.student} 학생의 수강 신청이 완료되었습니다.')
                return redirect('classes:lesson_detail', pk=lesson.pk)
            except Exception:
                messages.error(request, '이미 수강 신청된 학생입니다.')
    else:
        form = EnrollmentForm()

    return render(request, 'classes/enrollment_form.html', {
        'form': form,
        'lesson': lesson,
        'action': 'create',
    })


@login_required
def enrollment_edit(request, pk, enroll_pk):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    lesson = get_object_or_404(Lesson, pk=pk)
    enrollment = get_object_or_404(Enrollment, pk=enroll_pk, lesson=lesson)

    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, '수강 신청 정보가 수정되었습니다.')
            return redirect('classes:lesson_detail', pk=lesson.pk)
    else:
        form = EnrollmentForm(instance=enrollment)

    return render(request, 'classes/enrollment_form.html', {
        'form': form,
        'lesson': lesson,
        'enrollment': enrollment,
        'action': 'edit',
    })


@login_required
def enrollment_delete(request, pk, enroll_pk):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    lesson = get_object_or_404(Lesson, pk=pk)
    enrollment = get_object_or_404(Enrollment, pk=enroll_pk, lesson=lesson)

    if request.method == 'POST':
        student_name = enrollment.student.name
        enrollment.delete()
        messages.success(request, f'{student_name} 학생의 수강이 취소되었습니다.')
        return redirect('classes:lesson_detail', pk=lesson.pk)

    return render(request, 'classes/enrollment_confirm_delete.html', {
        'enrollment': enrollment,
        'lesson': lesson,
    })


# ──────────────────────────────────────────────
# TuitionPayment (수강료 납부)
# ──────────────────────────────────────────────

@login_required
def tuition_payment_create(request, enroll_pk):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    enrollment = get_object_or_404(Enrollment, pk=enroll_pk)
    today = timezone.localdate()

    if request.method == 'POST':
        form = TuitionPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.enrollment = enrollment
            payment.save()
            messages.success(request, f'{payment.year}년 {payment.month}월 수강료가 납부 처리되었습니다.')
            return redirect('classes:lesson_detail', pk=enrollment.lesson.pk)
    else:
        form = TuitionPaymentForm(initial={
            'year': today.year,
            'month': today.month,
            'amount': enrollment.adjusted_tuition,
            'payment_date': today,
        })

    return render(request, 'classes/tuition_payment_form.html', {
        'form': form,
        'enrollment': enrollment,
    })


@login_required
def tuition_payment_delete(request, enroll_pk, pay_pk):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    enrollment = get_object_or_404(Enrollment, pk=enroll_pk)
    payment = get_object_or_404(TuitionPayment, pk=pay_pk, enrollment=enrollment)

    if request.method == 'POST':
        lesson_pk = enrollment.lesson.pk
        payment.delete()
        messages.success(request, '납부 기록이 삭제되었습니다.')
        return redirect('classes:lesson_detail', pk=lesson_pk)

    return render(request, 'classes/tuition_payment_confirm_delete.html', {
        'payment': payment,
        'enrollment': enrollment,
    })
