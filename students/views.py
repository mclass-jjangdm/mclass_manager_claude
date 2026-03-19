import logging
import datetime
import csv
import io
from openpyxl import load_workbook, Workbook
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView
from django.http import HttpResponse
from .models import Student, School, StudentFile
from .forms import StudentForm, StudentImportForm, BulkSMSForm, StudentFileUploadForm
from common.utils import send_sms, validate_uploaded_file

logger = logging.getLogger(__name__)


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    success_url = reverse_lazy('students:student_list')
    context_object_name = 'students'

    def get_queryset(self):
        from django.db.models import Sum, F, Case, When, IntegerField
        from bookstore.models import BookSale

        queryset = Student.objects.select_related('school')
        search_query = self.request.GET.get('search', '')
        show_inactive = self.request.GET.get('show_inactive') == 'on'

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        if not show_inactive:
            queryset = queryset.filter(is_active=True)

        # 미결제 도서 금액 총액을 annotate로 추가
        queryset = queryset.annotate(
            unpaid_book_total=Sum(
                Case(
                    When(book_sales__is_paid=False,
                         then=F('book_sales__price') * F('book_sales__quantity')),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )

        return queryset.order_by('-is_active', 'grade', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_inactive'] = self.request.GET.get('show_inactive') == 'on'
        context['search_query'] = self.request.GET.get('search', '')

        # 정렬 방식 가져오기 (기본값: grade)
        group_by = self.request.GET.get('group_by', 'grade')
        context['group_by'] = group_by

        # 학생 그룹화
        students = self.get_queryset()
        from collections import defaultdict

        if group_by == 'school':
            # 학교별 그룹화
            grouped = defaultdict(list)
            for student in students:
                school_name = student.school.name if student.school else '미지정'
                grouped[school_name].append(student)
            context['grouped_students'] = dict(sorted(grouped.items()))
        else:
            # 학년별 그룹화 (기본)
            grade_order = ['K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11', 'K12', '졸업']
            grouped = defaultdict(list)
            for student in students:
                grade = student.grade if student.grade else '미지정'
                grouped[grade].append(student)

            # 학년 순서대로 정렬
            sorted_grouped = {}
            for grade in grade_order:
                if grade in grouped:
                    sorted_grouped[grade] = grouped[grade]
            # 미지정이나 기타 학년 추가
            for grade, student_list in grouped.items():
                if grade not in grade_order:
                    sorted_grouped[grade] = student_list

            context['grouped_students'] = sorted_grouped

        return context


class StudentCreateView(LoginRequiredMixin, CreateView):
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')

    def get_initial(self):
        initial = super().get_initial()
        consultation_pk = self.request.GET.get('consultation_pk')
        if consultation_pk:
            try:
                from homepage.models import ConsultationRequest
                c = ConsultationRequest.objects.get(pk=consultation_pk)
                initial['name'] = c.name
                initial['gender'] = c.gender
                initial['grade'] = c.grade
                initial['phone_number'] = c.phone_number
                initial['email'] = c.email
                initial['parent_phone'] = c.parent_phone
                initial['interview_info'] = c.get_interview_info_text()
            except Exception:
                pass
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['consultation_pk'] = self.request.GET.get('consultation_pk')
        return ctx

    def form_valid(self, form):
        student = form.save(commit=False)
        student.student_id = self.generate_student_id()
        student.save()

        # 상담 신청이 있으면 처리 상태를 '등록 완료'로 업데이트
        consultation_pk = self.request.POST.get('consultation_pk') or self.request.GET.get('consultation_pk')
        if consultation_pk:
            try:
                from homepage.models import ConsultationRequest
                c = ConsultationRequest.objects.get(pk=consultation_pk)
                c.status = 'registered'
                c.save()
            except Exception:
                pass

        messages.success(self.request, f"학생 '{student.name}' 등록되었습니다.")
        return redirect('students:student_list')

    def generate_student_id(self):
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(8)])


@login_required
def student_detail(request, pk):
    from bookstore.models import BookSale
    from grades.models import Grade
    from django.utils import timezone

    student = get_object_or_404(Student, pk=pk)

    # 교재 구매 내역 조회
    unpaid_sales = BookSale.objects.filter(student=student, is_paid=False).select_related('book').order_by('-sale_date', '-pk')
    paid_sales = BookSale.objects.filter(student=student, is_paid=True).select_related('book').order_by('-sale_date', '-pk')

    # 총 납부 금액 계산
    total_paid = sum(sale.get_total_price() for sale in paid_sales)

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
    from collections import defaultdict
    from decimal import Decimal
    import json

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
        'unpaid_sales': unpaid_sales,
        'paid_sales': paid_sales,
        'total_unpaid': student.unpaid_amount,
        'total_paid': total_paid,
        'internal_grades': regular_internal_grades,
        'elective_grades': elective_grades,
        'mock_grades': mock_grades,
        'semester_averages': semester_averages,
        'overall_average': overall_average,
        'weighted_averages': weighted_averages,
        'combination_averages': combination_averages,
        'chart_data': json.dumps(chart_data, ensure_ascii=False),
        'today': timezone.now().date(),
    }
    return render(request, 'students/student_detail.html', context)


@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, '학생 정보가 성공적으로 수정되었습니다.')
            return redirect('students:student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {'form': form})


@login_required
def student_import(request):
    if request.method == 'POST':
        form = StudentImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = form.cleaned_data['file']
                file_ext = file.name.split('.')[-1].lower()

                # 헬퍼 함수: 빈값 체크
                def is_empty(value):
                    return value is None or str(value).strip() == ''

                # 날짜 필드 처리 함수
                def parse_date(value):
                    if is_empty(value):
                        return None
                    elif isinstance(value, (datetime.date, datetime.datetime)):
                        return value.date() if isinstance(value, datetime.datetime) else value
                    elif isinstance(value, str):
                        for fmt in ('%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d'):
                            try:
                                return datetime.datetime.strptime(value.strip(), fmt).date()
                            except ValueError:
                                continue
                        return None  # 지원되지 않는 형식일 경우
                    else:
                        return None

                # 파일 읽기
                rows = []
                if file_ext == 'csv':
                    content = file.read()
                    try:
                        decoded = content.decode('utf-8-sig')
                    except UnicodeDecodeError:
                        decoded = content.decode('cp949')
                    reader = csv.DictReader(io.StringIO(decoded))
                    rows = list(reader)
                else:
                    wb = load_workbook(file, read_only=True)
                    ws = wb.active
                    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                    for excel_row in ws.iter_rows(min_row=2, values_only=True):
                        rows.append(dict(zip(headers, excel_row)))
                    wb.close()

                # 중복 체크를 위한 카운터 초기화
                new_count = 0
                duplicate_count = 0

                # 각 행 처리
                for row in rows:
                    school_name = str(row.get('school') or '').strip()
                    if school_name:
                        school, created = School.objects.get_or_create(name=school_name)
                    else:
                        school = None

                    first_class_date = parse_date(row.get('first_class_date'))
                    quit_date = parse_date(row.get('quit_date'))

                    student_data = {
                        'school': school,
                        'grade': row.get('grade'),
                        'phone_number': row.get('phone_number'),
                        'email': row.get('email'),
                        'gender': row.get('gender'),
                        'parent_phone': row.get('parent_phone'),
                        'receipt_number': row.get('receipt_number'),
                        'first_class_date': first_class_date,
                        'quit_date': quit_date,
                        'etc': row.get('etc'),
                        # 필요한 다른 필드 추가
                    }

                    student, created = Student.objects.update_or_create(
                        name=row['name'],
                        defaults=student_data
                    )
                    if created:
                        new_count += 1
                    else:
                        duplicate_count += 1

                messages.success(request, f"{new_count}명 학생이 새로 추가되었고, {duplicate_count}명 학생은 이미 존재하여 업데이트되었습니다.")
                return redirect('students:student_list')
            except Exception as e:
                # 에러 로그는 서버에 기록하고 사용자에게는 일반 메시지만 표시
                logger.error(f"Student import error: {str(e)}")
                messages.error(request, "파일 처리 중 오류가 발생했습니다. 파일 형식을 확인해주세요.")
        else:
            messages.error(request, "폼이 유효하지 않습니다.")
    else:
        form = StudentImportForm()
    return render(request, 'students/student_import.html', {'form': form})


@login_required
def student_export(request):
    students = Student.objects.all()

    # openpyxl로 Excel 파일 생성
    wb = Workbook()
    ws = wb.active
    ws.title = '학생 목록'

    # 헤더 작성
    headers = ['name', 'school', 'grade', 'phone_number', 'email', 'gender',
               'parent_phone', 'receipt_number', 'interview_date', 'interview_score',
               'interview_info', 'first_class_date', 'quit_date', 'etc']
    ws.append(headers)

    # 데이터 작성
    for student in students:
        row = [
            student.name,
            student.school.name if student.school else '',
            student.grade,
            student.phone_number,
            student.email,
            student.get_gender_display(),
            student.parent_phone,
            student.receipt_number,
            student.interview_date.strftime('%Y-%m-%d') if student.interview_date else '',
            student.interview_score,
            student.interview_info,
            student.first_class_date.strftime('%Y-%m-%d') if student.first_class_date else '',
            student.quit_date.strftime('%Y-%m-%d') if student.quit_date else '',
            student.etc,
        ]
        ws.append(row)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="students.xlsx"'
    wb.save(response)

    return response


@login_required
def student_import_sample(request):
    """학생 데이터 가져오기용 샘플 파일 다운로드"""
    file_format = request.GET.get('format', 'xlsx')

    # 샘플 데이터
    headers = ['name', 'school', 'grade', 'phone_number', 'email', 'gender',
               'parent_phone', 'receipt_number', 'interview_date', 'interview_score',
               'interview_info', 'first_class_date', 'quit_date', 'etc']

    sample_rows = [
        ['홍길동', '서울중학교', 'K7', '010-1234-5678', 'hong@example.com', 'M',
         '010-1111-2222', '010-1111-2222', '2024-01-15', 8, '성실한 학생', '2024-02-01', '', '특이사항 없음'],
        ['김철수', '한국고등학교', 'K10', '010-9876-5432', 'kim@example.com', 'F',
         '010-3333-4444', '010-3333-4444', '2024-02-20', 7, '수학에 관심이 많음', '2024-03-01', '', ''],
    ]

    if file_format == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="student_import_sample.csv"'
        writer = csv.writer(response)
        writer.writerow(headers)
        writer.writerows(sample_rows)
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = '학생 샘플'
        ws.append(headers)
        for row in sample_rows:
            ws.append(row)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="student_import_sample.xlsx"'
        wb.save(response)

    return response

@login_required
def student_files(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            description = form.cleaned_data.get('description', '')

            try:
                student_file = StudentFile(
                    student=student,
                    file=file,
                    file_name=file.name,
                    description=description
                )
                student_file.save()
                messages.success(request, '파일이 성공적으로 업로드되었습니다.')
            except Exception as e:
                logger.error(f"File upload error for student {pk}: {str(e)}")
                messages.error(request, '파일 업로드 중 오류가 발생했습니다.')

            return redirect('students:student_files', pk=pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = StudentFileUploadForm()

    files = student.files.all()
    context = {
        'student': student,
        'files': files,
        'form': form,
    }
    return render(request, 'students/student_files.html', context)

@login_required
def delete_student_file(request, file_id):
    file = get_object_or_404(StudentFile, id=file_id)
    student_pk = file.student.pk

    if request.method == 'POST':
        file.file.delete()  # 실제 파일 삭제
        file.delete()       # DB 레코드 삭제
        messages.success(request, '파일이 삭제되었습니다.')

    return redirect('students:student_files', pk=student_pk)


@login_required
def bulk_sms_send(request):
    """여러 학생/학부모에게 일괄 문자 발송 - 독립 페이지"""

    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        target = request.POST.get('target')
        message = request.POST.get('message')

        if not student_ids:
            messages.error(request, '발송 대상 학생을 선택해주세요.')
            return redirect('students:bulk_sms_send')

        if not message:
            messages.error(request, '메시지를 입력해주세요.')
            return redirect('students:bulk_sms_send')

        # 선택된 학생들 조회
        students = Student.objects.filter(pk__in=student_ids, is_active=True)

        success_count = 0
        fail_messages = []

        for student in students:
            # 학생에게 발송
            if target in ['student', 'both'] and student.phone_number:
                phone = student.phone_number.replace('-', '').strip()
                is_success, msg = send_sms(phone, message)
                if is_success:
                    success_count += 1
                else:
                    fail_messages.append(f"{student.name}(학생): {msg}")

            # 학부모에게 발송
            if target in ['parent', 'both'] and student.parent_phone:
                phone = student.parent_phone.replace('-', '').strip()
                is_success, msg = send_sms(phone, message)
                if is_success:
                    success_count += 1
                else:
                    fail_messages.append(f"{student.name}(학부모): {msg}")

        # 결과 메시지 처리
        if success_count > 0:
            messages.success(request, f"{success_count}건의 문자를 발송했습니다.")

        if fail_messages:
            for f_msg in fail_messages[:10]:  # 최대 10개까지만 표시
                messages.error(request, f_msg)
            if len(fail_messages) > 10:
                messages.error(request, f"외 {len(fail_messages) - 10}건의 발송 실패")

        return redirect('students:bulk_sms_send')

    # GET 요청: 모든 재원 중인 학생 목록 표시
    students = Student.objects.filter(is_active=True).select_related('school').order_by('grade', 'name')

    # 학년별 그룹화
    from collections import defaultdict
    grade_order = ['K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11', 'K12']
    grouped = defaultdict(list)

    for student in students:
        grade = student.grade if student.grade else '미지정'
        grouped[grade].append(student)

    # 학년 순서대로 정렬
    sorted_grouped = {}
    for grade in grade_order:
        if grade in grouped:
            sorted_grouped[grade] = grouped[grade]
    # 미지정 추가
    for grade, student_list in grouped.items():
        if grade not in grade_order:
            sorted_grouped[grade] = student_list

    return render(request, 'students/bulk_sms_page.html', {
        'grouped_students': sorted_grouped,
    })


@login_required
def student_send_email(request, pk):
    """학생에게 이메일 발송"""
    from django.core.mail import EmailMessage
    from django.conf import settings
    from .forms import StudentEmailForm

    student = get_object_or_404(Student, pk=pk)

    if not student.email:
        messages.error(request, '해당 학생의 이메일 주소가 등록되어 있지 않습니다.')
        return redirect('students:student_detail', pk=pk)

    if request.method == 'POST':
        form = StudentEmailForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # 발신자 이메일 설정
            from_email = settings.DEFAULT_FROM_EMAIL if request.user.username == 'admin' else settings.EMAIL_HOST_USER

            try:
                # EmailMessage 객체 생성
                email = EmailMessage(
                    subject=subject,
                    body=message,
                    from_email=from_email,
                    to=[student.email],
                )

                # 첨부파일 처리
                files = request.FILES.getlist('attachments')
                for file in files:
                    email.attach(file.name, file.read(), file.content_type)

                # 이메일 전송
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f'Sending email to {student.email} from {from_email}')

                result = email.send(fail_silently=False)

                logger.info(f'Email send result: {result}')

                messages.success(request, f'{student.name} 학생에게 이메일을 성공적으로 발송했습니다.')
                return redirect('students:student_detail', pk=pk)
            except Exception as e:
                logger.error(f'Email sending failed for student {pk}: {str(e)}', exc_info=True)
                messages.error(request, '이메일 발송 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
    else:
        form = StudentEmailForm()

    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'students/student_email_form.html', context)


@login_required
def student_send_sms(request, pk):
    """학생에게 문자 발송"""
    from .forms import StudentSMSForm
    import requests

    student = get_object_or_404(Student, pk=pk)

    if not student.phone_number:
        messages.error(request, '해당 학생의 전화번호가 등록되어 있지 않습니다.')
        return redirect('students:student_detail', pk=pk)

    if request.method == 'POST':
        form = StudentSMSForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']

            try:
                # Aligo SMS API 설정
                from django.conf import settings

                sms_url = 'https://apis.aligo.in/send/'
                sms_data = {
                    'key': settings.SMS_API_KEY,
                    'user_id': settings.SMS_USER_ID,
                    'sender': settings.SMS_SENDER_NUMBER,
                    'receiver': student.phone_number,
                    'msg': message,
                    'msg_type': 'LMS' if len(message.encode('euc-kr')) > 90 else 'SMS',
                    'title': '엠클래스' if len(message.encode('euc-kr')) > 90 else '',
                }

                response = requests.post(sms_url, data=sms_data)
                result = response.json()

                if result.get('result_code') == '1':
                    messages.success(request, f'{student.name} 학생에게 문자를 성공적으로 발송했습니다.')
                else:
                    messages.error(request, f'문자 발송 실패: {result.get("message", "알 수 없는 오류")}')

                return redirect('students:student_detail', pk=pk)
            except Exception as e:
                logger.error(f'SMS sending failed for student {pk}: {str(e)}', exc_info=True)
                messages.error(request, '문자 발송 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
    else:
        form = StudentSMSForm()

    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'students/student_sms_form.html', context)


@login_required
def student_send_sms_parent(request, pk):
    """부모님에게 문자 발송"""
    from .forms import StudentSMSForm
    import requests

    student = get_object_or_404(Student, pk=pk)

    if not student.parent_phone:
        messages.error(request, '해당 학생의 부모님 전화번호가 등록되어 있지 않습니다.')
        return redirect('students:student_detail', pk=pk)

    if request.method == 'POST':
        form = StudentSMSForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']

            try:
                # Aligo SMS API 설정
                from django.conf import settings

                sms_url = 'https://apis.aligo.in/send/'
                sms_data = {
                    'key': settings.SMS_API_KEY,
                    'user_id': settings.SMS_USER_ID,
                    'sender': settings.SMS_SENDER_NUMBER,
                    'receiver': student.parent_phone,
                    'msg': message,
                    'msg_type': 'LMS' if len(message.encode('euc-kr')) > 90 else 'SMS',
                    'title': '엠클래스' if len(message.encode('euc-kr')) > 90 else '',
                }

                response = requests.post(sms_url, data=sms_data)
                result = response.json()

                if result.get('result_code') == '1':
                    messages.success(request, f'{student.name} 학생 부모님에게 문자를 성공적으로 발송했습니다.')
                else:
                    messages.error(request, f'문자 발송 실패: {result.get("message", "알 수 없는 오류")}')

                return redirect('students:student_detail', pk=pk)
            except Exception as e:
                logger.error(f'SMS sending to parent failed for student {pk}: {str(e)}', exc_info=True)
                messages.error(request, '문자 발송 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
    else:
        form = StudentSMSForm()

    context = {
        'form': form,
        'student': student,
        'is_parent': True,  # 부모님에게 보내는 것임을 표시
    }
    return render(request, 'students/student_sms_form.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def grade_promotion_confirm(request):
    """학년 일괄 증가 확인 페이지 (관리자 전용)"""
    # 현재 학년별 학생 수 집계
    from django.db.models import Count

    grade_stats = Student.objects.filter(
        is_active=True
    ).values('grade').annotate(
        count=Count('id')
    ).order_by('grade')

    # 학년 증가 후 예상 결과 계산
    grade_mapping = {
        'K5': 'K6', 'K6': 'K7', 'K7': 'K8', 'K8': 'K9',
        'K9': 'K10', 'K10': 'K11', 'K11': 'K12', 'K12': '졸업'
    }

    changes = []
    for stat in grade_stats:
        current_grade = stat['grade']
        count = stat['count']
        new_grade = grade_mapping.get(current_grade, current_grade)

        # 해당 학년의 학생 이름 목록 조회
        students = Student.objects.filter(
            is_active=True,
            grade=current_grade
        ).order_by('name')

        changes.append({
            'current': current_grade,
            'new': new_grade,
            'count': count,
            'students': students
        })

    context = {
        'changes': changes,
        'total_students': sum(stat['count'] for stat in grade_stats),
    }
    return render(request, 'students/grade_promotion_confirm.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def grade_promotion_execute(request):
    """학년 일괄 증가 실행 (관리자 전용)"""
    if request.method != 'POST':
        messages.error(request, '잘못된 접근입니다.')
        return redirect('students:student_list')

    # 학년 매핑
    grade_mapping = {
        'K5': 'K6', 'K6': 'K7', 'K7': 'K8', 'K8': 'K9',
        'K9': 'K10', 'K10': 'K11', 'K11': 'K12', 'K12': '졸업'
    }

    # 활성 학생들만 대상
    active_students = Student.objects.filter(is_active=True)

    updated_count = 0
    graduated_count = 0

    for student in active_students:
        if student.grade in grade_mapping:
            new_grade = grade_mapping[student.grade]
            if new_grade == '졸업':
                # K12 학생은 졸업 처리
                student.grade = '졸업'
                student.is_active = False
                student.quit_date = datetime.date.today()
                graduated_count += 1
            else:
                student.grade = new_grade
                updated_count += 1
            student.save()

    messages.success(
        request,
        f'학년 증가가 완료되었습니다. (진급: {updated_count}명, 졸업: {graduated_count}명)'
    )
    return redirect('students:student_list')


@login_required
def student_quit(request, pk):
    """학생 퇴원 처리"""
    from django.utils import timezone

    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student.quit_date = timezone.now().date()
        student.is_active = False
        student.save()
        messages.success(request, f'{student.name} 학생이 퇴원 처리되었습니다.')
        return redirect('students:student_detail', pk=pk)

    return render(request, 'students/student_quit_confirm.html', {'student': student})


@login_required
def student_readmit(request, pk):
    """학생 재입원 처리"""
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student.quit_date = None
        student.is_active = True
        student.save()
        messages.success(request, f'{student.name} 학생이 재입원 처리되었습니다.')
        return redirect('students:student_detail', pk=pk)

    return render(request, 'students/student_readmit_confirm.html', {'student': student})


def parent_lookup(request):
    """학부모 교재 결제 내역 조회 (로그인 불필요)"""
    from bookstore.models import BookSale

    student = None
    unpaid_sales = []
    paid_sales = []
    total_unpaid = 0
    total_paid = 0
    error_message = None

    # 세션에서 학생 정보 복원 시도
    student_name = request.POST.get('student_name', '').strip()
    student_id = request.POST.get('student_id', '').strip()

    # POST 요청이 아니면 세션에서 복원
    if request.method != 'POST' and 'parent_student_id' in request.session:
        student_id = request.session.get('parent_student_id', '')
        student_name = request.session.get('parent_student_name', '')

    if student_name and student_id:
        try:
            student = Student.objects.get(name=student_name, student_id=student_id)

            # 세션에 학생 정보 저장
            request.session['parent_student_id'] = student_id
            request.session['parent_student_name'] = student_name

            # 미결제 내역
            unpaid_sales = BookSale.objects.filter(
                student=student, is_paid=False
            ).select_related('book').order_by('-sale_date')
            total_unpaid = sum(sale.get_total_price() for sale in unpaid_sales)

            # 결제 완료 내역
            paid_sales = BookSale.objects.filter(
                student=student, is_paid=True
            ).select_related('book').order_by('-payment_date')
            total_paid = sum(sale.get_total_price() for sale in paid_sales)

        except Student.DoesNotExist:
            error_message = '학생 정보를 찾을 수 없습니다. 이름과 고유번호를 확인해 주세요.'
    elif request.method == 'POST':
        error_message = '학생 이름과 고유번호를 모두 입력해 주세요.'

    context = {
        'student': student,
        'unpaid_sales': unpaid_sales,
        'paid_sales': paid_sales,
        'total_unpaid': total_unpaid,
        'total_paid': total_paid,
        'error_message': error_message,
        'bank_account': '신한은행 110-247-214359 장동민(엠클래스수학과학전문학원)',
    }
    return render(request, 'students/parent_lookup.html', context)


def parent_logout(request):
    """부모님 페이지 나가기 (세션 정리)"""
    if 'parent_student_id' in request.session:
        del request.session['parent_student_id']
    if 'parent_student_name' in request.session:
        del request.session['parent_student_name']
    return redirect('index')


def parent_student_update(request, student_id):
    """부모님용 학생 정보 수정 (로그인 불필요, 제한된 필드만 수정 가능)"""
    from .forms import ParentStudentUpdateForm

    student = get_object_or_404(Student, student_id=student_id)

    if request.method == 'POST':
        form = ParentStudentUpdateForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return render(request, 'students/parent_student_update.html', {
                'student': student,
                'form': form,
                'success_message': '학생 정보가 성공적으로 수정되었습니다.'
            })
    else:
        form = ParentStudentUpdateForm(instance=student)

    return render(request, 'students/parent_student_update.html', {
        'student': student,
        'form': form,
    })


def parent_grades(request, student_pk):
    """학부모용 성적 조회 (세션 기반 인증, 로그인 불필요)"""
    import json
    from collections import defaultdict
    from grades.models import Grade
    from progress.models import LearningRecord

    # 세션 인증
    session_student_id = request.session.get('parent_student_id', '')
    session_student_name = request.session.get('parent_student_name', '')
    if not session_student_id or not session_student_name:
        return redirect('parent_lookup')

    student = get_object_or_404(Student, pk=student_pk)
    if student.student_id != session_student_id or student.name != session_student_name:
        return redirect('parent_lookup')

    # ── 퀴즈/테스트 기록 ─────────────────────────────
    TEST_TYPE_LABELS = {
        'quiz': '퀴즈', 'practice': '연습 문제',
        'booklet': '제본 교재', 'entrance_exam': '입학 시험', 'other': '기타',
    }
    raw_test_records = LearningRecord.objects.filter(
        student=student,
        record_type__in=['quiz', 'practice', 'booklet', 'entrance_exam', 'other']
    ).select_related('subject').order_by('-date', '-created_at')

    processed_test_records = []
    for rec in raw_test_records:
        quiz_detail = None
        if rec.quiz_results:
            total = rec.quiz_results.get('total', 0)
            wrong_nums = sorted(rec.quiz_results.get('wrong', []))
            correct_count = total - len(wrong_nums)
            correct_pct = round(correct_count / total * 100, 1) if total else 0
            wrong_pct = round(100 - correct_pct, 1) if total else 0
            quiz_detail = {
                'total': total,
                'wrong_nums': wrong_nums,
                'q_range': list(range(1, total + 1)),
                'correct_count': correct_count,
                'wrong_count': len(wrong_nums),
                'correct_pct': correct_pct,
                'segments_json': json.dumps([
                    {'p': correct_pct, 'c': '#22c55e'},
                    {'p': wrong_pct, 'c': '#f87171'},
                ]) if total > 0 else '[]',
            }
        processed_test_records.append({
            'rec': rec,
            'quiz_detail': quiz_detail,
            'type_label': TEST_TYPE_LABELS.get(rec.record_type, rec.record_type),
        })

    # ── 학교 시험 성적 (내신) ─────────────────────────
    GRADE_RANK_COLORS = {
        1: 'indigo', 2: 'blue', 3: 'cyan', 4: 'green',
        5: 'yellow', 6: 'orange', 7: 'red', 8: 'red', 9: 'red',
    }
    internal_grades = Grade.objects.filter(
        student=student, grade_type='internal'
    ).select_related('subject').order_by('year', 'semester', 'subject__subject_code')

    grade_groups = defaultdict(list)
    for g in internal_grades:
        grade_groups[(g.year, g.semester)].append(g)
    sorted_grade_groups = [
        {'year': k[0], 'semester': k[1], 'grades': v}
        for k, v in sorted(grade_groups.items(), reverse=True)
    ]

    # ── 진도 평가 분석 ────────────────────────────────
    ACHIEVEMENT_META = [
        {'code': 'A', 'label': '우수',   'color': 'indigo', 'hex': '#6366f1'},
        {'code': 'B', 'label': '양호',   'color': 'green',  'hex': '#22c55e'},
        {'code': 'C', 'label': '보통',   'color': 'yellow', 'hex': '#facc15'},
        {'code': 'D', 'label': '미흡',   'color': 'orange', 'hex': '#fb923c'},
        {'code': 'F', 'label': '재학습', 'color': 'red',    'hex': '#f87171'},
    ]
    textbook_records = LearningRecord.objects.filter(
        student=student,
        record_type='textbook',
        achievement__in=['A', 'B', 'C', 'D', 'F'],
    ).select_related('book_sale__book')

    book_map = {}
    for rec in textbook_records:
        if rec.book_sale_id not in book_map:
            book_map[rec.book_sale_id] = {'book_sale': rec.book_sale, 'records': []}
        book_map[rec.book_sale_id]['records'].append(rec)

    book_progress_data = []
    overall_counts = {m['code']: 0 for m in ACHIEVEMENT_META}
    for bs_id, data in book_map.items():
        counts = {m['code']: 0 for m in ACHIEVEMENT_META}
        for rec in data['records']:
            if rec.achievement in counts:
                counts[rec.achievement] += 1
                overall_counts[rec.achievement] += 1
        total = sum(counts.values())
        levels = [
            {**m, 'count': counts[m['code']],
             'percent': round(counts[m['code']] / total * 100, 1) if total else 0}
            for m in ACHIEVEMENT_META
        ]
        book_progress_data.append({
            'book_sale': data['book_sale'],
            'levels': levels,
            'total': total,
            'segments_json': json.dumps([
                {'p': l['percent'], 'c': l['hex']} for l in levels if l['percent'] > 0
            ]),
        })

    overall_total = sum(overall_counts.values())
    overall_levels = [
        {**m, 'count': overall_counts[m['code']],
         'percent': round(overall_counts[m['code']] / overall_total * 100, 1) if overall_total else 0}
        for m in ACHIEVEMENT_META
    ]
    overall_segments_json = json.dumps([
        {'p': l['percent'], 'c': l['hex']} for l in overall_levels if l['percent'] > 0
    ]) if overall_total > 0 else '[]'

    context = {
        'student': student,
        'test_records': processed_test_records,
        'grade_groups': sorted_grade_groups,
        'book_progress_data': book_progress_data,
        'overall_levels': overall_levels,
        'overall_total': overall_total,
        'overall_segments_json': overall_segments_json,
        'achievement_meta': ACHIEVEMENT_META,
        'grade_rank_colors': GRADE_RANK_COLORS,
    }
    return render(request, 'students/parent_grades.html', context)


def _parent_auth(request, student_pk):
    """학부모 세션 인증 헬퍼. 인증된 Student 반환, 실패 시 None 반환."""
    session_id = request.session.get('parent_student_id', '')
    session_name = request.session.get('parent_student_name', '')
    if not session_id or not session_name:
        return None
    try:
        student = Student.objects.get(pk=student_pk)
        if student.student_id != session_id or student.name != session_name:
            return None
        return student
    except Student.DoesNotExist:
        return None


def parent_grade_bulk_create(request, student_pk):
    """학부모용 한 학기 내신 성적 일괄 입력 (세션 인증)"""
    from grades.models import Grade
    from subjects.models import Subject
    from decimal import Decimal, InvalidOperation

    student = _parent_auth(request, student_pk)
    if not student:
        return redirect('parent_lookup')

    is_2022 = (student.curriculum_year == 2022)

    if is_2022:
        subjects = Subject.objects.filter(is_active=True, curriculum_year=2022).order_by('subject_code')
    else:
        subjects = Subject.objects.filter(is_active=True).exclude(curriculum_year=2022).order_by('subject_code')

    error_message = None

    if request.method == 'POST':
        year = request.POST.get('year', '').strip()
        semester = request.POST.get('semester', '').strip()
        grade_count = int(request.POST.get('grade_count', 0))

        if not year or not semester:
            error_message = '학년과 학기를 선택해 주세요.'
        else:
            created_count = 0
            for i in range(grade_count):
                subject_id = request.POST.get(f'grades[{i}][subject]', '').strip()
                score_str = request.POST.get(f'grades[{i}][score]', '').strip()
                avg_str = request.POST.get(f'grades[{i}][subject_average]', '0').strip() or '0'

                if not subject_id or not score_str:
                    continue
                try:
                    subject = Subject.objects.get(pk=subject_id)
                    score = Decimal(score_str)
                    subject_average = Decimal(avg_str)

                    if is_2022:
                        def _int(key):
                            v = request.POST.get(f'grades[{i}][{key}]', '').strip()
                            return int(v) if v else None

                        def _dec(key):
                            v = request.POST.get(f'grades[{i}][{key}]', '').strip()
                            return Decimal(v) if v else None

                        credits = _int('credits')
                        enrolled_count = _int('enrolled_count')
                        subject_rank = _int('subject_rank')
                        same_rank_count = _int('same_rank_count')
                        grade_rank = _int('grade_rank')
                        achievement_level = request.POST.get(f'grades[{i}][achievement_level]', '').strip() or None
                        percentile = _dec('percentile')

                        Grade.objects.create(
                            student=student,
                            grade_type='internal',
                            subject=subject,
                            year=int(year),
                            semester=int(semester),
                            credits=credits,
                            score=score,
                            subject_average=None,
                            subject_stddev=None,
                            grade_rank=grade_rank,
                            subject_classification='general',
                            is_elective=False,
                            enrolled_count=enrolled_count,
                            subject_rank=subject_rank,
                            same_rank_count=same_rank_count,
                            achievement_level=achievement_level,
                            percentile=percentile,
                        )
                    else:
                        grade_rank_str = request.POST.get(f'grades[{i}][grade_rank]', '').strip()
                        is_elective = request.POST.get(f'grades[{i}][is_elective]') == '1'
                        grade_rank = int(grade_rank_str) if grade_rank_str and not is_elective else None
                        achievement_level = request.POST.get(f'grades[{i}][achievement_level]', '').strip() or None
                        Grade.objects.create(
                            student=student,
                            grade_type='internal',
                            subject=subject,
                            year=int(year),
                            semester=int(semester),
                            score=score,
                            subject_average=subject_average,
                            grade_rank=grade_rank,
                            is_elective=is_elective,
                            achievement_level=achievement_level if is_elective else None,
                        )
                    created_count += 1
                except Exception:
                    continue
            if created_count > 0:
                return redirect('parent_grades', student_pk=student_pk)
            error_message = '과목과 원점수를 입력해 주세요.'

    import datetime

    # 학부모용 2022 템플릿에 쓸 subject 목록 (classification 포함)
    subjects_with_class = []
    TYPE_MAP = {'0': 'common', '1': 'general', '2': 'elective', '3': 'fusion'}
    for s in subjects:
        sc = ''
        if is_2022 and len(s.subject_code) == 6:
            sc = TYPE_MAP.get(s.subject_code[2], '')
        subjects_with_class.append({'id': s.pk, 'name': s.name, 'code': s.subject_code, 'classification': sc})

    context = {
        'student': student,
        'subjects': subjects,
        'subjects_list': subjects_with_class,
        'current_year': datetime.date.today().year,
        'error_message': error_message,
        'is_2022': is_2022,
    }
    template = 'students/parent_grade_bulk_2022.html' if is_2022 else 'students/parent_grade_bulk.html'
    return render(request, template, context)


def parent_mock_grade_create(request, student_pk):
    """학부모용 2022 내신 성적 일괄 입력 (세션 인증)"""
    from grades.models import Grade
    from subjects.models import Subject
    from decimal import Decimal

    student = _parent_auth(request, student_pk)
    if not student:
        return redirect('parent_lookup')

    subjects = Subject.objects.filter(is_active=True, curriculum_year=2022).order_by('subject_code')
    TYPE_MAP = {'0': 'common', '1': 'general', '2': 'elective', '3': 'fusion'}
    subjects_list = []
    for s in subjects:
        sc = TYPE_MAP.get(s.subject_code[2], '') if len(s.subject_code) == 6 else ''
        subjects_list.append({'id': s.pk, 'name': s.name, 'category': s.category, 'classification': sc})

    error_message = None

    if request.method == 'POST':
        year = request.POST.get('year', '').strip()
        semester = request.POST.get('semester', '').strip()
        grade_count = int(request.POST.get('grade_count', 0))

        if not year or not semester:
            error_message = '학년과 학기를 선택해 주세요.'
        else:
            created_count = 0
            for i in range(grade_count):
                subject_id = request.POST.get(f'grades[{i}][subject]', '').strip()
                score_str = request.POST.get(f'grades[{i}][score]', '').strip()
                credits_str = request.POST.get(f'grades[{i}][credits]', '').strip()
                enrolled_str = request.POST.get(f'grades[{i}][enrolled_count]', '').strip()

                if not subject_id or not score_str or not credits_str or not enrolled_str:
                    continue
                try:
                    def _int(key):
                        v = request.POST.get(f'grades[{i}][{key}]', '').strip()
                        return int(v) if v else None

                    def _dec(key):
                        v = request.POST.get(f'grades[{i}][{key}]', '').strip()
                        return Decimal(v) if v else None

                    subject = Subject.objects.get(pk=subject_id)
                    Grade.objects.create(
                        student=student,
                        grade_type='internal',
                        subject=subject,
                        year=int(year),
                        semester=int(semester),
                        credits=_int('credits'),
                        score=Decimal(score_str),
                        subject_average=None,
                        subject_stddev=None,
                        grade_rank=_int('grade_rank'),
                        subject_classification='general',
                        is_elective=False,
                        enrolled_count=_int('enrolled_count'),
                        subject_rank=_int('subject_rank'),
                        same_rank_count=_int('same_rank_count'),
                        achievement_level=request.POST.get(f'grades[{i}][achievement_level]', '').strip() or None,
                        percentile=_dec('percentile'),
                    )
                    created_count += 1
                except Exception:
                    continue
            if created_count > 0:
                return redirect('parent_grades', student_pk=student_pk)
            error_message = '과목, 점수, 단위수, 수강자수를 입력해 주세요.'

    context = {
        'student': student,
        'subjects_list': subjects_list,
        'error_message': error_message,
    }
    return render(request, 'students/parent_mock_grade.html', context)


def parent_grade_import(request, student_pk):
    """학부모용 성적 파일 업로드 (세션 인증)"""
    from grades.views import process_csv_file, process_excel_file

    student = _parent_auth(request, student_pk)
    if not student:
        return redirect('parent_lookup')

    error_message = None
    success_message = None

    if request.method == 'POST':
        grade_type = request.POST.get('grade_type', 'internal')
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            error_message = '파일을 선택해 주세요.'
        else:
            file_name = uploaded_file.name.lower()
            try:
                if file_name.endswith('.csv'):
                    result = process_csv_file(uploaded_file, student, grade_type)
                elif file_name.endswith(('.xlsx', '.xls')):
                    result = process_excel_file(uploaded_file, student, grade_type)
                else:
                    error_message = 'CSV 또는 Excel 파일만 업로드 가능합니다.'
                    result = None
                if result:
                    if result.get('success_count', 0) > 0:
                        success_message = f"{result['success_count']}개의 성적이 등록되었습니다."
                    if result.get('error_count', 0) > 0:
                        error_message = f"{result['error_count']}개 행에서 오류가 발생했습니다: {', '.join(result.get('errors', [])[:3])}"
            except Exception as e:
                error_message = f'파일 처리 중 오류: {str(e)}'

    context = {
        'student': student,
        'error_message': error_message,
        'success_message': success_message,
    }
    return render(request, 'students/parent_grade_import.html', context)