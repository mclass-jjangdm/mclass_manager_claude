from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from students.models import Student
from subjects.models import Subject
from .models import Grade
from .forms import InternalGradeForm, MockExamGradeForm, InternalGradeBulkFormSet, GradeImportForm
import csv
import io
import json
from decimal import Decimal, InvalidOperation
from collections import defaultdict


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


@login_required
def grade_import(request, student_pk):
    """CSV/Excel 파일에서 성적 일괄 임포트"""
    student = get_object_or_404(Student, pk=student_pk)

    if request.method == 'POST':
        form = GradeImportForm(request.POST, request.FILES)
        if form.is_valid():
            grade_type = form.cleaned_data['grade_type']
            uploaded_file = request.FILES['file']

            # 파일 확장자 확인
            file_name = uploaded_file.name.lower()

            try:
                if file_name.endswith('.csv'):
                    result = process_csv_file(uploaded_file, student, grade_type)
                elif file_name.endswith(('.xlsx', '.xls')):
                    result = process_excel_file(uploaded_file, student, grade_type)
                else:
                    messages.error(request, '지원하지 않는 파일 형식입니다. CSV 또는 Excel 파일만 업로드 가능합니다.')
                    return redirect('grades:grade_import', student_pk=student_pk)

                if result['success']:
                    messages.success(request, f"{result['created_count']}개의 성적이 등록되었습니다.")
                    if result['errors']:
                        for error in result['errors'][:5]:  # 최대 5개 에러만 표시
                            messages.warning(request, error)
                        if len(result['errors']) > 5:
                            messages.warning(request, f"... 외 {len(result['errors']) - 5}개의 오류가 더 있습니다.")
                else:
                    messages.error(request, result['message'])
                    for error in result['errors'][:5]:
                        messages.error(request, error)

                return redirect('students:student_detail', pk=student_pk)

            except Exception as e:
                messages.error(request, f'파일 처리 중 오류가 발생했습니다: {str(e)}')
                return redirect('grades:grade_import', student_pk=student_pk)
    else:
        form = GradeImportForm()

    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'grades/grade_import.html', context)


def process_csv_file(uploaded_file, student, grade_type):
    """CSV 파일 처리"""
    errors = []
    created_count = 0

    try:
        # 파일 내용 읽기 (UTF-8 또는 CP949 시도)
        content = uploaded_file.read()
        try:
            decoded_content = content.decode('utf-8-sig')  # BOM 처리
        except UnicodeDecodeError:
            decoded_content = content.decode('cp949')  # 한글 Windows 인코딩

        reader = csv.DictReader(io.StringIO(decoded_content))

        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):  # 헤더 다음 행부터
                try:
                    grade = create_grade_from_row(row, student, grade_type, row_num)
                    if grade:
                        created_count += 1
                except ValueError as e:
                    errors.append(f"행 {row_num}: {str(e)}")
                except Exception as e:
                    errors.append(f"행 {row_num}: 처리 실패 - {str(e)}")

        return {
            'success': True,
            'created_count': created_count,
            'errors': errors,
            'message': '파일 처리가 완료되었습니다.'
        }

    except Exception as e:
        return {
            'success': False,
            'created_count': 0,
            'errors': errors,
            'message': f'CSV 파일 읽기 실패: {str(e)}'
        }


def process_excel_file(uploaded_file, student, grade_type):
    """Excel 파일 처리"""
    errors = []
    created_count = 0

    try:
        import openpyxl
    except ImportError:
        return {
            'success': False,
            'created_count': 0,
            'errors': [],
            'message': 'Excel 파일 처리를 위해 openpyxl 라이브러리가 필요합니다. pip install openpyxl'
        }

    try:
        workbook = openpyxl.load_workbook(uploaded_file, data_only=True)
        sheet = workbook.active

        # 헤더 행 읽기
        headers = []
        for cell in sheet[1]:
            headers.append(cell.value.strip() if cell.value else '')

        with transaction.atomic():
            for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                if not any(row):  # 빈 행 건너뛰기
                    continue

                try:
                    row_dict = dict(zip(headers, row))
                    grade = create_grade_from_row(row_dict, student, grade_type, row_num)
                    if grade:
                        created_count += 1
                except ValueError as e:
                    errors.append(f"행 {row_num}: {str(e)}")
                except Exception as e:
                    errors.append(f"행 {row_num}: 처리 실패 - {str(e)}")

        return {
            'success': True,
            'created_count': created_count,
            'errors': errors,
            'message': '파일 처리가 완료되었습니다.'
        }

    except Exception as e:
        return {
            'success': False,
            'created_count': 0,
            'errors': errors,
            'message': f'Excel 파일 읽기 실패: {str(e)}'
        }


def clean_bom(text):
    """BOM 및 불필요한 문자 제거"""
    if text is None:
        return ''
    text = str(text)
    # 다양한 BOM 문자 제거
    bom_chars = ['\ufeff', '\ufffe', '\xef\xbb\xbf', '\xff\xfe', '\xfe\xff']
    for bom in bom_chars:
        text = text.replace(bom, '')
    return text.strip()


def normalize_row(row):
    """행의 키와 값을 정규화 (BOM 제거, 공백 제거)"""
    normalized = {}
    for key, value in row.items():
        if key:
            # 키에서 BOM과 공백 제거
            clean_key = clean_bom(str(key)).replace(' ', '')
            # 값에서도 BOM 제거
            clean_value = clean_bom(value) if value is not None else value
            normalized[clean_key] = clean_value
    return normalized


def get_value(row, *keys):
    """여러 가능한 키 이름으로 값 찾기"""
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return ''


def create_grade_from_row(row, student, grade_type, row_num):
    """행 데이터에서 Grade 객체 생성"""

    # 행 키 정규화
    row = normalize_row(row)

    # 필수 필드 확인
    subject_code = str(get_value(row, '과목코드', '과목_코드', 'subject_code') or '').strip()
    subject_name = str(get_value(row, '과목명', '과목', '과목이름', 'subject_name', 'subject') or '').strip()

    if not subject_code and not subject_name:
        return None  # 빈 행 건너뛰기

    # 과목 찾기
    subject = None
    if subject_code:
        subject = Subject.objects.filter(subject_code=subject_code, is_active=True).first()
    if not subject and subject_name:
        # 정확한 이름 매칭
        subject = Subject.objects.filter(name=subject_name, is_active=True).first()
        # 띄어쓰기 무시 매칭 (기술가정 = 기술 가정)
        if not subject:
            search_name_no_space = subject_name.replace(' ', '')
            for s in Subject.objects.filter(is_active=True):
                if s.name.replace(' ', '') == search_name_no_space:
                    subject = s
                    break
        # 부분 매칭 시도
        if not subject:
            subject = Subject.objects.filter(name__icontains=subject_name, is_active=True).first()

    if not subject:
        raise ValueError(f"과목을 찾을 수 없습니다: 코드={subject_code}, 이름={subject_name}")

    # 공통 필드 파싱 (다양한 헤더명 지원)
    year = parse_int(get_value(row, '학년', 'year', 'grade'), '학년')

    # 진로선택 여부 먼저 확인
    is_elective_raw = get_value(row, '진로선택', '진로_선택', '선택과목', 'elective')
    is_elective = str(is_elective_raw).strip().lower() in ['1', 'true', 'yes', 'y', 'o', '예', '진로선택', '○', 'v', '선택']

    # 중복 체크 (grade_type에 따라 다른 조건)
    if grade_type == 'internal':
        semester = parse_int(get_value(row, '학기', 'semester'), '학기')
        existing = Grade.objects.filter(
            student=student,
            grade_type='internal',
            subject=subject,
            year=year,
            semester=semester
        ).exists()
        if existing:
            raise ValueError(f"이미 등록된 성적입니다: {year}학년 {semester}학기 {subject.name}")
    else:  # mock
        exam_year_val = parse_int(get_value(row, '시험연도', '연도', '시험_연도', 'exam_year', 'year'), '시험연도')
        exam_month_val = parse_int(get_value(row, '시험월', '월', '시험_월', 'exam_month', 'month'), '시험월')
        exam_name_val = str(get_value(row, '시험명', '모의고사명', '시험이름', '시험_명', 'exam_name') or '').strip()
        existing = Grade.objects.filter(
            student=student,
            grade_type='mock',
            subject=subject,
            year=year,
            exam_year=exam_year_val,
            exam_month=exam_month_val,
            exam_name=exam_name_val
        ).exists()
        if existing:
            raise ValueError(f"이미 등록된 성적입니다: {exam_year_val}년 {exam_month_val}월 {exam_name_val} {subject.name}")

    score = parse_decimal(get_value(row, '원점수', '점수', 'score'), '원점수')
    subject_average = parse_decimal(get_value(row, '과목평균', '평균', '과목_평균', 'average', 'avg'), '과목평균')

    # 진로선택 과목일 경우 등급/표준편차 대신 성취도/분포비율
    if is_elective and grade_type == 'internal':
        subject_stddev = None
        grade_rank = None
    else:
        subject_stddev = parse_decimal(get_value(row, '표준편차', '표준_편차', 'stddev', 'std'), '표준편차')
        grade_rank = parse_int(get_value(row, '등급', 'rank', 'grade_rank'), '등급')
        if not (1 <= grade_rank <= 9):
            raise ValueError(f"등급은 1~9 사이여야 합니다: {grade_rank}")

    # Grade 객체 생성
    grade_obj = Grade(
        student=student,
        grade_type=grade_type,
        subject=subject,
        year=year,
        score=score,
        subject_average=subject_average,
        subject_stddev=subject_stddev,
        grade_rank=grade_rank,
    )

    if grade_type == 'internal':
        # 내신 전용 필드
        semester = parse_int(get_value(row, '학기', 'semester'), '학기')
        credits = parse_int(get_value(row, '단위', '이수단위', 'credits', 'unit'), '단위')

        if semester not in [1, 2]:
            raise ValueError(f"학기는 1 또는 2여야 합니다: {semester}")

        grade_obj.semester = semester
        grade_obj.credits = credits
        grade_obj.is_elective = is_elective

        # 진로선택 과목일 경우 성취도와 분포비율 파싱
        if is_elective:
            achievement_level = str(get_value(row, '성취도', 'achievement', 'achievement_level') or '').strip().upper()
            if achievement_level not in ['A', 'B', 'C']:
                raise ValueError(f"성취도는 A, B, C 중 하나여야 합니다: {achievement_level}")

            distribution_a = parse_decimal_optional(get_value(row, '분포비율A', 'A비율', '성취도A비율', 'distribution_a'))
            distribution_b = parse_decimal_optional(get_value(row, '분포비율B', 'B비율', '성취도B비율', 'distribution_b'))
            distribution_c = parse_decimal_optional(get_value(row, '분포비율C', 'C비율', '성취도C비율', 'distribution_c'))

            if distribution_a is None:
                raise ValueError("진로선택 과목은 분포비율A가 필수입니다")
            if distribution_b is None:
                raise ValueError("진로선택 과목은 분포비율B가 필수입니다")
            if distribution_c is None:
                raise ValueError("진로선택 과목은 분포비율C가 필수입니다")

            grade_obj.achievement_level = achievement_level
            grade_obj.distribution_a = distribution_a
            grade_obj.distribution_b = distribution_b
            grade_obj.distribution_c = distribution_c

    else:  # mock
        # 모의고사 전용 필드
        exam_year = parse_int(get_value(row, '시험연도', '연도', '시험_연도', 'exam_year', 'year'), '시험연도')
        exam_month = parse_int(get_value(row, '시험월', '월', '시험_월', 'exam_month', 'month'), '시험월')
        exam_name = str(get_value(row, '시험명', '모의고사명', '시험이름', '시험_명', 'exam_name') or '').strip()
        percentile = parse_decimal(get_value(row, '백분위', '백분_위', 'percentile'), '백분위')

        if not exam_name:
            raise ValueError("시험명이 필요합니다")
        if not (1 <= exam_month <= 12):
            raise ValueError(f"시험월은 1~12 사이여야 합니다: {exam_month}")

        grade_obj.exam_year = exam_year
        grade_obj.exam_month = exam_month
        grade_obj.exam_name = exam_name
        grade_obj.percentile = percentile

    grade_obj.full_clean()
    grade_obj.save()
    return grade_obj


def parse_int(value, field_name):
    """정수 파싱 헬퍼"""
    if value is None or str(value).strip() == '':
        raise ValueError(f"{field_name}이(가) 필요합니다")
    try:
        return int(float(str(value).strip()))  # Excel에서 숫자가 float로 올 수 있음
    except (ValueError, TypeError):
        raise ValueError(f"{field_name} 값이 올바르지 않습니다: {value}")


def parse_decimal(value, field_name):
    """소수 파싱 헬퍼"""
    if value is None or str(value).strip() == '':
        raise ValueError(f"{field_name}이(가) 필요합니다")
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"{field_name} 값이 올바르지 않습니다: {value}")


def parse_decimal_optional(value):
    """선택적 소수 파싱 헬퍼"""
    if value is None or str(value).strip() == '':
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError, TypeError):
        return None


@login_required
def delete_all_grades(request, student_pk):
    """학생의 모든 성적 삭제"""
    student = get_object_or_404(Student, pk=student_pk)

    if request.method == 'POST':
        deleted_count = Grade.objects.filter(student=student).count()
        Grade.objects.filter(student=student).delete()
        messages.success(request, f'{deleted_count}개의 성적이 삭제되었습니다.')

    return redirect('students:student_detail', pk=student_pk)


@login_required
def student_grades(request, student_pk):
    """학생 성적 전용 페이지"""
    student = get_object_or_404(Student, pk=student_pk)

    # 성적 데이터 조회
    internal_grades = Grade.objects.filter(
        student=student,
        grade_type='internal'
    ).select_related('subject').order_by('-year', '-semester', 'subject__subject_code')

    mock_grades = Grade.objects.filter(
        student=student,
        grade_type='mock'
    ).select_related('subject').order_by('-exam_year', '-exam_month', 'subject__subject_code')

    # 학기별 평균 내신 등급 계산 (진로선택 과목 제외)
    semester_stats = defaultdict(lambda: {'total_weighted': 0, 'total_credits': 0})
    year_stats = defaultdict(lambda: {'total_weighted': 0, 'total_credits': 0})

    # 학기별/교과별 성적 데이터 (차트용) - 진로선택 제외, 교과별 집계
    semester_category_grades = defaultdict(lambda: defaultdict(lambda: {'total_weighted': 0, 'total_credits': 0}))

    # 교과별 전체 통계 (교과 조합 분석용)
    category_stats = defaultdict(lambda: {'total_weighted': 0, 'total_credits': 0})

    for grade in internal_grades:
        # 차트용 데이터 수집 (진로선택 과목 제외)
        if not grade.is_elective:
            key = f"{grade.year}-{grade.semester}"
            category = grade.curriculum or '기타'
            semester_category_grades[key][category]['total_weighted'] += grade.grade_rank * grade.credits
            semester_category_grades[key][category]['total_credits'] += grade.credits

            # 교과별 전체 통계
            category_stats[category]['total_weighted'] += grade.grade_rank * grade.credits
            category_stats[category]['total_credits'] += grade.credits

        if grade.is_elective:  # 진로선택 과목은 평균 계산에서 제외
            continue

        semester_key = (grade.year, grade.semester)
        semester_stats[semester_key]['total_weighted'] += grade.grade_rank * grade.credits
        semester_stats[semester_key]['total_credits'] += grade.credits

        # 학년별 통계
        year_stats[grade.year]['total_weighted'] += grade.grade_rank * grade.credits
        year_stats[grade.year]['total_credits'] += grade.credits

    # 학기별 평균 계산 및 정렬
    semester_averages = []
    for (year, semester), stats in sorted(semester_stats.items()):
        if stats['total_credits'] > 0:
            avg = Decimal(stats['total_weighted']) / Decimal(stats['total_credits'])
            semester_averages.append({
                'year': year,
                'semester': semester,
                'average': round(avg, 2),
                'total_credits': stats['total_credits'],
            })

    # 전체 평균 등급 계산 (동일 가중치)
    total_weighted_sum = sum(s['total_weighted'] for s in semester_stats.values())
    total_credits_sum = sum(s['total_credits'] for s in semester_stats.values())
    overall_average = None
    if total_credits_sum > 0:
        overall_average = round(Decimal(total_weighted_sum) / Decimal(total_credits_sum), 2)

    # 학년별 가중치 적용 전체 등급 계산
    weighted_averages = []
    weight_configs = [
        {'name': '30:30:40', 'weights': {1: 30, 2: 30, 3: 40}},
        {'name': '20:40:40', 'weights': {1: 20, 2: 40, 3: 40}},
        {'name': '20:30:50', 'weights': {1: 20, 2: 30, 3: 50}},
    ]

    for config in weight_configs:
        weights = config['weights']
        weighted_sum = Decimal(0)
        weight_sum = Decimal(0)

        for year in [1, 2, 3]:
            if year in year_stats and year_stats[year]['total_credits'] > 0:
                year_avg = Decimal(year_stats[year]['total_weighted']) / Decimal(year_stats[year]['total_credits'])
                weighted_sum += year_avg * Decimal(weights[year])
                weight_sum += Decimal(weights[year])

        if weight_sum > 0:
            weighted_avg = round(weighted_sum / weight_sum, 2)
            weighted_averages.append({
                'name': config['name'],
                'average': weighted_avg,
            })

    # 차트용 데이터 준비 (교과별 평균 등급)
    chart_data = []
    for semester_key in sorted(semester_category_grades.keys()):
        year, sem = semester_key.split('-')
        semester_data = {
            'label': f"{year}학년 {sem}학기",
            'categories': {}
        }
        for category, stats in semester_category_grades[semester_key].items():
            if stats['total_credits'] > 0:
                avg_grade = round(float(stats['total_weighted']) / float(stats['total_credits']), 2)
                semester_data['categories'][category] = {
                    'average': avg_grade,
                    'total_credits': stats['total_credits'],
                }
        chart_data.append(semester_data)

    # 교과 조합별 평균 분석
    category_combinations = [
        {'name': '국수영과', 'categories': ['국어', '수학', '영어', '과학']},
        {'name': '국수영사', 'categories': ['국어', '수학', '영어', '사회']},
        {'name': '국수영사과', 'categories': ['국어', '수학', '영어', '사회', '과학']},
    ]

    combination_averages = []
    for combo in category_combinations:
        total_weighted = 0
        total_credits = 0
        missing_categories = []

        for cat in combo['categories']:
            if cat in category_stats and category_stats[cat]['total_credits'] > 0:
                total_weighted += category_stats[cat]['total_weighted']
                total_credits += category_stats[cat]['total_credits']
            else:
                missing_categories.append(cat)

        if total_credits > 0:
            avg = round(Decimal(total_weighted) / Decimal(total_credits), 2)
            combination_averages.append({
                'name': combo['name'],
                'categories': combo['categories'],
                'average': avg,
                'total_credits': total_credits,
                'missing': missing_categories,
            })

    # 일반 내신 성적과 진로선택 성적 분리
    regular_internal_grades = [g for g in internal_grades if not g.is_elective]
    elective_grades = [g for g in internal_grades if g.is_elective]

    context = {
        'student': student,
        'internal_grades': regular_internal_grades,
        'elective_grades': elective_grades,
        'mock_grades': mock_grades,
        'semester_averages': semester_averages,
        'overall_average': overall_average,
        'weighted_averages': weighted_averages,
        'combination_averages': combination_averages,
        'chart_data': json.dumps(chart_data, ensure_ascii=False),
    }
    return render(request, 'grades/student_grades.html', context)


@login_required
def download_grade_template(request, template_type):
    """성적 입력 템플릿 다운로드"""

    if template_type == 'internal':
        # 내신 성적 템플릿
        filename = 'internal_grade_template.csv'
        headers = ['학년', '학기', '과목명', '단위', '원점수', '과목평균', '표준편차', '등급', '진로선택', '성취도', '분포비율A', '분포비율B', '분포비율C']
        sample_data = [
            ['1', '1', '국어', '3', '85', '70.5', '12.3', '2', '', '', '', '', ''],
            ['1', '1', '수학Ⅰ', '4', '92', '68.2', '15.1', '1', '', '', '', '', ''],
            ['1', '1', '영어', '3', '88', '72.1', '11.5', '2', '', '', '', '', ''],
            ['2', '1', '물리학Ⅱ', '3', '85', '72.3', '', '', '진로선택', 'A', '25.5', '45.2', '29.3'],
            ['2', '1', '화학Ⅱ', '3', '78', '68.5', '', '', '진로선택', 'B', '20.1', '50.3', '29.6'],
        ]
    else:  # mock
        # 모의고사 성적 템플릿
        filename = 'mock_exam_template.csv'
        headers = ['학년', '시험연도', '시험월', '시험명', '과목명', '원점수', '과목평균', '표준편차', '등급', '백분위']
        sample_data = [
            ['2', '2024', '3', '3월 학력평가', '국어', '85', '70.5', '12.3', '2', '88'],
            ['2', '2024', '3', '3월 학력평가', '수학', '92', '68.2', '15.1', '1', '95'],
            ['2', '2024', '6', '6월 모의평가', '국어', '82', '68.1', '11.8', '2', '85'],
        ]

    # CSV 응답 생성
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # UTF-8 BOM 추가 (Excel에서 한글 깨짐 방지)
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(headers)
    for row in sample_data:
        writer.writerow(row)

    return response
