from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models as django_models
import calendar
import datetime
import json

from .models import Lesson, LessonSchedule, Enrollment, TuitionPayment, DAY_CHOICES
from .forms import LessonForm, EnrollmentForm, TuitionPaymentForm


def _assign_timetable_columns(items):
    """같은 요일의 수업 블록에 겹침 처리용 col/total_cols/left_pct/right_pct 할당"""
    if not items:
        return items

    items = sorted(items, key=lambda x: x['top'])
    lanes = []  # 각 lane의 현재 끝 위치(px)

    # 1단계: 그리디 lane 배정
    for item in items:
        start = item['top']
        end   = start + item['height']
        placed = False
        for i, lane_end in enumerate(lanes):
            if lane_end <= start:
                lanes[i] = end
                item['col'] = i
                placed = True
                break
        if not placed:
            item['col'] = len(lanes)
            lanes.append(end)

    # 2단계: 각 아이템이 겹치는 구간의 최대 col → total_cols 결정
    for item in items:
        s, e = item['top'], item['top'] + item['height']
        max_col = max(
            (o['col'] for o in items
             if not (o['top'] + o['height'] <= s or o['top'] >= e)),
            default=0,
        )
        item['total_cols'] = max_col + 1
        item['left_pct']   = item['col'] * 100 / item['total_cols']
        item['right_pct']  = (item['total_cols'] - item['col'] - 1) * 100 / item['total_cols']

    return items


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

    # ── 시간표 데이터 (항상 활성 수업만, 검색 조건 무관) ──────────
    TIMETABLE_COLORS = [
        {'bg': '#e0e7ff', 'text': '#3730a3', 'border': '#c7d2fe'},  # indigo
        {'bg': '#ede9fe', 'text': '#6d28d9', 'border': '#ddd6fe'},  # violet
        {'bg': '#dbeafe', 'text': '#1e40af', 'border': '#bfdbfe'},  # blue
        {'bg': '#e0f2fe', 'text': '#0369a1', 'border': '#bae6fd'},  # sky
        {'bg': '#d1fae5', 'text': '#065f46', 'border': '#a7f3d0'},  # emerald
        {'bg': '#dcfce7', 'text': '#166534', 'border': '#bbf7d0'},  # green
        {'bg': '#fef9c3', 'text': '#854d0e', 'border': '#fde68a'},  # yellow
        {'bg': '#ffedd5', 'text': '#9a3412', 'border': '#fed7aa'},  # orange
        {'bg': '#fee2e2', 'text': '#991b1b', 'border': '#fecaca'},  # rose
        {'bg': '#fce7f3', 'text': '#9d174d', 'border': '#fbcfe8'},  # pink
        {'bg': '#f3e8ff', 'text': '#6b21a8', 'border': '#e9d5ff'},  # purple
        {'bg': '#ccfbf1', 'text': '#134e4a', 'border': '#99f6e4'},  # teal
    ]

    tt_lessons = list(
        Lesson.objects.filter(is_active=True)
        .select_related('subject', 'teacher')
        .prefetch_related('schedules', 'enrollments__student')
        .order_by('pk')
    )

    lesson_color_map = {
        lesson.pk: TIMETABLE_COLORS[i % len(TIMETABLE_COLORS)]
        for i, lesson in enumerate(tt_lessons)
    }
    tt_legend = [
        {'lesson': lesson, 'color': lesson_color_map[lesson.pk]}
        for lesson in tt_lessons
    ]

    # 시간 범위 계산
    all_starts, all_ends = [], []
    for lesson in tt_lessons:
        for s in lesson.schedules.all():
            all_starts.append(s.start_time.hour * 60 + s.start_time.minute)
            all_ends.append(s.end_time.hour * 60 + s.end_time.minute)

    if all_starts:
        base_min = (min(all_starts) // 60) * 60          # 내림하여 정시
        top_min  = ((max(all_ends) + 59) // 60) * 60     # 올림하여 정시
    else:
        base_min, top_min = 13 * 60, 22 * 60

    PX_PER_MIN = 1.2
    table_height = max(round((top_min - base_min) * PX_PER_MIN), 120)

    # 요일별 수업 블록 데이터
    day_map = {d: {'key': d, 'label': lbl, 'items': []} for d, lbl in DAY_CHOICES}
    for lesson in tt_lessons:
        color = lesson_color_map[lesson.pk]
        # 현재 활성 수강생 이름 목록
        students = sorted(
            e.student.name for e in lesson.enrollments.all() if e.is_active
        )
        for s in lesson.schedules.all():
            start_min = s.start_time.hour * 60 + s.start_time.minute
            end_min   = s.end_time.hour * 60 + s.end_time.minute
            day_map[s.day]['items'].append({
                'lesson':   lesson,
                'top':      round((start_min - base_min) * PX_PER_MIN),
                'height':   max(round((end_min - start_min) * PX_PER_MIN), 22),
                'time':     f"{s.start_time.strftime('%H:%M')}~{s.end_time.strftime('%H:%M')}",
                'color':    color,
                'students': students,
            })

    # 요일별 겹침 처리
    for day_data in day_map.values():
        day_data['items'] = _assign_timetable_columns(day_data['items'])

    timetable_days = [day_map[d] for d, _ in DAY_CHOICES]

    hour_labels = []
    h = base_min // 60
    while h * 60 <= top_min:
        hour_labels.append({
            'label': f'{h:02d}:00',
            'top':   round((h * 60 - base_min) * PX_PER_MIN),
        })
        h += 1

    return render(request, 'classes/lesson_list.html', {
        'lessons':        lessons,
        'search':         search,
        'status':         status,
        # timetable
        'timetable_days': timetable_days,
        'hour_labels':    hour_labels,
        'table_height':   table_height,
        'tt_legend':      tt_legend,
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
        form = LessonForm()  # teacher 기본값 null = 원장

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

GRADE_LABELS = {
    'K5': '초5', 'K6': '초6',
    'K7': '중1', 'K8': '중2', 'K9': '중3',
    'K10': '고1', 'K11': '고2', 'K12': '고3',
}
GRADE_ORDER = ['K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11', 'K12']


def _get_grade_groups(lesson):
    """학년별 학생 그룹 리스트와 이미 수강 중인 학생 ID 세트 반환.
    반환: (grade_groups, enrolled_ids)
    grade_groups = [{'key': 'K7', 'label': '중1', 'students': [...]}, ...]
    """
    from students.models import Student
    all_students = list(
        Student.objects.filter(quit_date__isnull=True).order_by('grade', 'name')
    )
    enrolled_ids = set(
        lesson.enrollments.filter(is_active=True).values_list('student_id', flat=True)
    )
    grade_groups = []
    for grade in GRADE_ORDER:
        group = [s for s in all_students if s.grade == grade]
        if group:
            grade_groups.append({
                'key': grade,
                'label': GRADE_LABELS.get(grade, grade),
                'students': group,
            })
    others = [s for s in all_students if s.grade not in GRADE_ORDER]
    if others:
        grade_groups.append({'key': 'other', 'label': '기타', 'students': others})
    return grade_groups, enrolled_ids


@login_required
def enrollment_create(request, pk):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    lesson = get_object_or_404(
        Lesson.objects.prefetch_related('schedules', 'enrollments'), pk=pk
    )

    if request.method == 'POST':
        student_pks = request.POST.getlist('student')
        enrollment_date = request.POST.get('enrollment_date', '').strip()
        end_date = request.POST.get('end_date', '').strip() or None
        tuition_adjustment = request.POST.get('tuition_adjustment', 0)
        memo = request.POST.get('memo', '')
        is_active = 'is_active' in request.POST

        errors = []
        if not student_pks:
            errors.append('학생을 한 명 이상 선택해 주세요.')
        if not enrollment_date:
            errors.append('수강 시작일을 입력해 주세요.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            from students.models import Student
            success_count = 0
            for spk in student_pks:
                try:
                    student = Student.objects.get(pk=spk)
                    Enrollment.objects.create(
                        student=student,
                        lesson=lesson,
                        enrollment_date=enrollment_date,
                        end_date=end_date,
                        tuition_adjustment=tuition_adjustment,
                        memo=memo,
                        is_active=is_active,
                    )
                    success_count += 1
                except Exception:
                    messages.warning(request, f'{student.name} 학생은 이미 수강 중입니다.')
            if success_count:
                messages.success(request, f'{success_count}명의 수강 신청이 완료되었습니다.')
            return redirect('classes:lesson_detail', pk=lesson.pk)

    grade_groups, enrolled_ids = _get_grade_groups(lesson)
    today = datetime.date.today()

    return render(request, 'classes/enrollment_form.html', {
        'lesson': lesson,
        'action': 'create',
        'grade_groups': grade_groups,
        'enrolled_ids': enrolled_ids,
        'today': today,
    })


@login_required
def enrollment_edit(request, pk, enroll_pk):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    lesson = get_object_or_404(Lesson.objects.prefetch_related('schedules'), pk=pk)
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
    today = datetime.date.today()

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


@login_required
def auto_enroll_next_month(request):
    """다음 달 수강 신청 자동 생성"""
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('index')

    today = datetime.date.today()
    if today.month == 12:
        next_year, next_month = today.year + 1, 1
    else:
        next_year, next_month = today.year, today.month + 1

    first_of_next = datetime.date(next_year, next_month, 1)
    last_of_next = datetime.date(next_year, next_month,
                                 calendar.monthrange(next_year, next_month)[1])

    if request.method == 'POST':
        selected_ids = request.POST.getlist('enrollment_ids')
        created_count = 0
        skip_count = 0

        for enroll_id in selected_ids:
            try:
                enroll = Enrollment.objects.select_related('student', 'lesson').get(pk=enroll_id)
                # 중복 체크: 같은 학생+수업, 같은 시작일
                if Enrollment.objects.filter(
                    student=enroll.student,
                    lesson=enroll.lesson,
                    enrollment_date=first_of_next,
                ).exists():
                    skip_count += 1
                    continue
                Enrollment.objects.create(
                    student=enroll.student,
                    lesson=enroll.lesson,
                    enrollment_date=first_of_next,
                    end_date=last_of_next,
                    tuition_adjustment=0,  # 다음 달은 전월 조정 없이 기본 수강료
                    memo='',
                    is_active=True,
                )
                created_count += 1
            except Enrollment.DoesNotExist:
                continue

        msg = f'{next_year}년 {next_month}월 수강 신청 {created_count}건 생성 완료'
        if skip_count:
            msg += f' (이미 존재 {skip_count}건 제외)'
        messages.success(request, msg)
        return redirect('classes:auto_enroll_next_month')

    # 현재 활성 수강 신청 (만료 안 된 것)
    active_enrollments = Enrollment.objects.filter(
        is_active=True,
    ).filter(
        django_models.Q(end_date__isnull=True) | django_models.Q(end_date__gte=today)
    ).select_related(
        'student', 'lesson', 'lesson__teacher', 'lesson__subject'
    ).order_by('lesson__name', 'student__name')

    # 다음 달에 이미 등록된 (student_id, lesson_id) 쌍
    already_set = set(
        Enrollment.objects.filter(
            enrollment_date=first_of_next,
        ).values_list('student_id', 'lesson_id')
    )

    # 수업별 그룹핑
    lessons_dict = {}
    total_new = 0
    total_exists = 0
    for enroll in active_enrollments:
        lid = enroll.lesson_id
        if lid not in lessons_dict:
            lessons_dict[lid] = {
                'lesson': enroll.lesson,
                'items': [],
                'new_count': 0,
                'exists_count': 0,
            }
        already = (enroll.student_id, enroll.lesson_id) in already_set
        lessons_dict[lid]['items'].append({
            'enrollment': enroll,
            'already': already,
        })
        if already:
            lessons_dict[lid]['exists_count'] += 1
            total_exists += 1
        else:
            lessons_dict[lid]['new_count'] += 1
            total_new += 1

    lesson_groups = list(lessons_dict.values())

    return render(request, 'classes/auto_enroll.html', {
        'next_year': next_year,
        'next_month': next_month,
        'first_of_next': first_of_next,
        'last_of_next': last_of_next,
        'lesson_groups': lesson_groups,
        'total_new': total_new,
        'total_exists': total_exists,
        'total': total_new + total_exists,
    })
