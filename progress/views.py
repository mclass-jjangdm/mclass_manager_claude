# progress/views.py
# 학습 진도 관리 (학생 배정 및 진도 평가)
#
# 대부분의 뷰는 progress/urls.py에서 teachers.views와 bookstore.views를 사용합니다.
# 이 파일은 수업 활동(StudentActivity) 관련 뷰를 포함합니다.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import StudentActivity
from .forms import StudentActivityForm
from students.models import Student
from teachers.models import Teacher, TeacherStudentAssignment


@login_required
def student_activity_create(request):
    """수업 활동 생성"""
    # 날짜 파라미터 확인
    date_str = request.GET.get('date') or request.POST.get('date')
    if date_str:
        try:
            from datetime import datetime
            initial_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            initial_date = timezone.now().date()
    else:
        initial_date = timezone.now().date()

    # 해당 날짜에 배정된 학생들 조회
    assigned_student_ids = TeacherStudentAssignment.objects.filter(
        date=initial_date
    ).values_list('student_id', flat=True)

    # 배정된 학생들 + 활성 학생들
    students = Student.objects.filter(is_active=True).select_related('school').order_by('name')

    if request.method == 'POST':
        form = StudentActivityForm(request.POST, initial_date=initial_date, students=students)
        if form.is_valid():
            activity = form.save()
            messages.success(request, f"'{activity.title}' 수업 활동이 등록되었습니다.")

            # 리다이렉트
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('progress:dashboard')

    else:
        form = StudentActivityForm(initial_date=initial_date, students=students)

    return render(request, 'progress/student_activity_form.html', {
        'form': form,
        'title': '수업 활동 추가',
        'selected_date': initial_date,
        'assigned_student_ids': list(assigned_student_ids),
    })


@login_required
def student_activity_update(request, pk):
    """수업 활동 수정"""
    activity = get_object_or_404(StudentActivity, pk=pk)

    if request.method == 'POST':
        form = StudentActivityForm(request.POST, instance=activity)
        if form.is_valid():
            activity = form.save()
            messages.success(request, f"'{activity.title}' 수업 활동이 수정되었습니다.")

            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('progress:dashboard')

    else:
        form = StudentActivityForm(instance=activity)

    return render(request, 'progress/student_activity_form.html', {
        'form': form,
        'activity': activity,
        'title': '수업 활동 수정',
        'selected_date': activity.date,
    })


@login_required
@require_POST
def student_activity_delete(request, pk):
    """수업 활동 삭제"""
    activity = get_object_or_404(StudentActivity, pk=pk)
    title = activity.title
    date = activity.date
    activity.delete()

    messages.success(request, f"'{title}' 수업 활동이 삭제되었습니다.")

    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(f'/progress/?date={date.strftime("%Y-%m-%d")}')


@login_required
def student_activity_list_ajax(request):
    """수업 활동 목록 조회 (AJAX)"""
    date_str = request.GET.get('date')
    student_id = request.GET.get('student_id')

    activities = StudentActivity.objects.select_related('student', 'teacher', 'subject')

    if date_str:
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            activities = activities.filter(date=date)
        except ValueError:
            pass

    if student_id:
        activities = activities.filter(student_id=student_id)

    activities = activities.order_by('-date', '-created_at')[:50]

    data = [{
        'id': a.id,
        'student_name': a.student.name,
        'teacher_name': a.teacher.name if a.teacher else '-',
        'date': a.date.strftime('%Y-%m-%d'),
        'activity_type': a.get_activity_type_display(),
        'title': a.title,
        'subject': a.subject.name if a.subject else '-',
        'achievement': a.get_achievement_display() if a.achievement else '-',
        'score_display': a.score_display or '-',
        'memo': a.memo,
    } for a in activities]

    return JsonResponse({'activities': data})
