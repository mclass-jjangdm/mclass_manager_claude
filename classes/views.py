from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import json

from .models import Lesson, LessonSchedule, Enrollment, TuitionPayment, DAY_CHOICES
from .forms import LessonForm, EnrollmentForm, TuitionPaymentForm


def _get_lesson_form_context():
    """수업 폼에 필요한 교과/과목/교재 JSON 데이터 반환"""
    from subjects.models import Subject
    from bookstore.models import Book

    subjects = Subject.objects.filter(is_active=True).order_by('name')
    books = Book.objects.select_related('subject').order_by('title')

    subjects_data = [
        {'id': s.pk, 'name': s.name, 'category': s.category}
        for s in subjects
    ]
    books_data = [
        {'id': b.pk, 'title': b.title,
         'category': b.subject.category if b.subject else '기타'}
        for b in books
    ]

    categories = sorted(set(s['category'] for s in subjects_data))

    return {
        'categories': categories,
        'subjects_json': json.dumps(subjects_data, ensure_ascii=False),
        'books_json': json.dumps(books_data, ensure_ascii=False),
        'day_choices': DAY_CHOICES,
    }


def _get_default_teacher_pk():
    """'원장' 이름의 선생님 pk 반환 (is_active 무관). 없으면 None."""
    from teachers.models import Teacher
    try:
        return Teacher.objects.get(name='원장').pk
    except Teacher.DoesNotExist:
        return None


def _save_schedules(post_data, lesson):
    """POST 데이터에서 요일별 시간 파싱 후 LessonSchedule 저장"""
    lesson.schedules.all().delete()
    for day, _ in DAY_CHOICES:
        if post_data.get(f'sched_{day}'):
            start = post_data.get(f'sched_{day}_start', '').strip()
            end = post_data.get(f'sched_{day}_end', '').strip()
            if start and end:
                LessonSchedule.objects.create(
                    lesson=lesson,
                    day=day,
                    start_time=start,
                    end_time=end,
                )


def _get_existing_schedules(lesson):
    """수업의 기존 일정을 {day: {start, end}} 형태로 반환"""
    result = {}
    for s in lesson.schedules.all():
        result[s.day] = {
            'start': s.start_time.strftime('%H:%M'),
            'end': s.end_time.strftime('%H:%M'),
        }
    return result


# ──────────────────────────────────────────────
# Lesson (수업)
# ──────────────────────────────────────────────

@login_required
def lesson_list(request):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    lessons = Lesson.objects.select_related('subject', 'teacher').prefetch_related('schedules')
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

    lesson = get_object_or_404(
        Lesson.objects.prefetch_related('schedules', 'books'),
        pk=pk,
    )
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
            _save_schedules(request.POST, lesson)
            messages.success(request, f'수업 "{lesson.name}"이 생성되었습니다.')
            return redirect('classes:lesson_detail', pk=lesson.pk)
    else:
        default_teacher_pk = _get_default_teacher_pk()
        initial = {'teacher': default_teacher_pk} if default_teacher_pk else {}
        form = LessonForm(initial=initial)

    ctx = _get_lesson_form_context()
    ctx.update({
        'form': form,
        'action': 'create',
        'existing_schedules_json': '{}',
        'current_category': '',
    })
    return render(request, 'classes/lesson_form.html', ctx)


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
            _save_schedules(request.POST, lesson)
            messages.success(request, f'수업 "{lesson.name}"이 수정되었습니다.')
            return redirect('classes:lesson_detail', pk=lesson.pk)
    else:
        form = LessonForm(instance=lesson)

    existing_schedules = _get_existing_schedules(lesson)
    current_category = lesson.subject.category if lesson.subject else ''

    ctx = _get_lesson_form_context()
    ctx.update({
        'form': form,
        'lesson': lesson,
        'action': 'edit',
        'existing_schedules_json': json.dumps(existing_schedules, ensure_ascii=False),
        'current_category': current_category,
    })
    return render(request, 'classes/lesson_form.html', ctx)


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
