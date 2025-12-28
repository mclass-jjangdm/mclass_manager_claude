from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from students.models import Student
from subjects.models import Subject
from .models import Grade
from .forms import InternalGradeForm, MockExamGradeForm, InternalGradeBulkFormSet


@login_required
def internal_grade_create(request, student_pk):
    """내신 성적 입력"""
    student = get_object_or_404(Student, pk=student_pk)

    if request.method == 'POST':
        form = InternalGradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.student = student
            grade.full_clean()  # 모델 유효성 검사
            grade.save()
            messages.success(request, '내신 성적이 등록되었습니다.')
            return redirect('students:student_detail', pk=student_pk)
    else:
        form = InternalGradeForm(initial={'student': student})

    context = {
        'form': form,
        'student': student,
        'grade_type': 'internal',
    }
    return render(request, 'grades/grade_form.html', context)


@login_required
def mock_grade_create(request, student_pk):
    """모의고사 성적 입력"""
    student = get_object_or_404(Student, pk=student_pk)

    if request.method == 'POST':
        form = MockExamGradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.student = student
            grade.full_clean()  # 모델 유효성 검사
            grade.save()
            messages.success(request, '모의고사 성적이 등록되었습니다.')
            return redirect('students:student_detail', pk=student_pk)
    else:
        form = MockExamGradeForm(initial={'student': student})

    context = {
        'form': form,
        'student': student,
        'grade_type': 'mock',
    }
    return render(request, 'grades/grade_form.html', context)


@login_required
def grade_update(request, pk):
    """성적 수정"""
    grade = get_object_or_404(Grade, pk=pk)
    student = grade.student

    # 성적 유형에 따라 적절한 폼 선택
    if grade.grade_type == 'internal':
        FormClass = InternalGradeForm
        grade_type_label = '내신'
    else:
        FormClass = MockExamGradeForm
        grade_type_label = '모의고사'

    if request.method == 'POST':
        form = FormClass(request.POST, instance=grade)
        if form.is_valid():
            updated_grade = form.save(commit=False)
            updated_grade.full_clean()
            updated_grade.save()
            messages.success(request, f'{grade_type_label} 성적이 수정되었습니다.')
            return redirect('students:student_detail', pk=student.pk)
    else:
        form = FormClass(instance=grade)

    context = {
        'form': form,
        'student': student,
        'grade': grade,
        'grade_type': grade.grade_type,
        'is_update': True,
    }
    return render(request, 'grades/grade_form.html', context)


@login_required
def grade_delete(request, pk):
    """성적 삭제"""
    grade = get_object_or_404(Grade, pk=pk)
    student = grade.student

    if request.method == 'POST':
        grade_type_label = '내신' if grade.grade_type == 'internal' else '모의고사'
        grade.delete()
        messages.success(request, f'{grade_type_label} 성적이 삭제되었습니다.')
        return redirect('students:student_detail', pk=student.pk)

    context = {
        'grade': grade,
        'student': student,
    }
    return render(request, 'grades/grade_confirm_delete.html', context)


@login_required
def internal_grade_bulk_create(request, student_pk):
    """한 학기 내신 성적 일괄 입력"""
    student = get_object_or_404(Student, pk=student_pk)

    if request.method == 'POST':
        formset = InternalGradeBulkFormSet(request.POST, queryset=Grade.objects.none())
        if formset.is_valid():
            instances = formset.save(commit=False)
            created_count = 0
            for instance in instances:
                if instance.subject:  # 과목이 선택된 경우만 저장
                    instance.student = student
                    instance.grade_type = 'internal'
                    instance.full_clean()
                    instance.save()
                    created_count += 1
            messages.success(request, f'{created_count}개의 내신 성적이 등록되었습니다.')
            return redirect('students:student_detail', pk=student_pk)
    else:
        formset = InternalGradeBulkFormSet(queryset=Grade.objects.none())

    context = {
        'formset': formset,
        'student': student,
    }
    return render(request, 'grades/grade_bulk_form.html', context)


@login_required
def get_subjects_by_category(request):
    """교과별 과목 목록 반환 (AJAX)"""
    category = request.GET.get('category', '')

    if category:
        # Subject 모델의 category property를 사용하여 필터링
        all_subjects = Subject.objects.filter(is_active=True).order_by('subject_code')
        filtered_subjects = [s for s in all_subjects if s.category == category]

        data = [
            {'id': s.id, 'name': f'[{s.subject_code}] {s.name}'}
            for s in filtered_subjects
        ]
    else:
        # 교과를 선택하지 않은 경우 모든 활성 과목 반환
        subjects = Subject.objects.filter(is_active=True).order_by('subject_code')
        data = [
            {'id': s.id, 'name': f'[{s.subject_code}] {s.name}'}
            for s in subjects
        ]

    return JsonResponse({'subjects': data})
