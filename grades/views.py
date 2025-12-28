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
            grade.grade_type = 'internal'
            grade.full_clean()  # 모델 유효성 검사
            grade.save()
            messages.success(request, '내신 성적이 등록되었습니다.')
            return redirect('students:student_detail', pk=student_pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = InternalGradeForm()

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
            grade.grade_type = 'mock'
            grade.full_clean()  # 모델 유효성 검사
            grade.save()
            messages.success(request, '모의고사 성적이 등록되었습니다.')
            return redirect('students:student_detail', pk=student_pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = MockExamGradeForm()

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
            try:
                updated_grade = form.save(commit=False)
                updated_grade.full_clean()
                updated_grade.save()
                messages.success(request, f'{grade_type_label} 성적이 수정되었습니다.')
                return redirect('students:student_detail', pk=student.pk)
            except Exception as e:
                messages.error(request, f'성적 수정 중 오류가 발생했습니다: {str(e)}')
        else:
            # 폼 에러 출력
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
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
        try:
            year = request.POST.get('year')
            semester = request.POST.get('semester')
            grade_count = int(request.POST.get('grade_count', 0))

            if not year or not semester:
                messages.error(request, '학년과 학기를 선택해주세요.')
                return redirect('grades:internal_grade_bulk_create', student_pk=student_pk)

            created_count = 0
            for i in range(grade_count):
                subject_id = request.POST.get(f'grades[{i}][subject]')
                credits = request.POST.get(f'grades[{i}][credits]')
                score = request.POST.get(f'grades[{i}][score]')
                subject_average = request.POST.get(f'grades[{i}][subject_average]')
                subject_stddev = request.POST.get(f'grades[{i}][subject_stddev]')
                grade_rank = request.POST.get(f'grades[{i}][grade_rank]')
                is_elective = request.POST.get(f'grades[{i}][is_elective]') == '1'

                if subject_id:
                    subject = Subject.objects.get(pk=subject_id)
                    grade = Grade(
                        student=student,
                        grade_type='internal',
                        subject=subject,
                        year=year,
                        semester=semester,
                        credits=credits,
                        score=score,
                        subject_average=subject_average,
                        subject_stddev=subject_stddev,
                        grade_rank=grade_rank,
                        is_elective=is_elective
                    )
                    grade.full_clean()
                    grade.save()
                    created_count += 1

            messages.success(request, f'{created_count}개의 내신 성적이 등록되었습니다.')
            return redirect('students:student_detail', pk=student_pk)

        except Exception as e:
            messages.error(request, f'성적 저장 중 오류가 발생했습니다: {str(e)}')
            return redirect('grades:internal_grade_bulk_create', student_pk=student_pk)

    context = {
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
