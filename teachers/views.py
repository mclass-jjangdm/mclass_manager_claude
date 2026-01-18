from datetime import timedelta, datetime
from io import BytesIO
from pyexpat.errors import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Teacher, Attendance, Salary, TeacherUnavailability, TeacherStudentAssignment
from .forms import BulkAttendanceForm, TeacherForm, TeacherUnavailabilityForm, BulkUnavailabilityForm, TeacherStudentAssignmentForm
from django.contrib import messages
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import os
from django.views import View
from django.db.models import Min, Max
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import urllib.parse
from django.db import transaction, models
from config.fonts import FONT_CONFIGS


# 폰트 등록
def register_fonts():
    for font_config in FONT_CONFIGS.values():
        if isinstance(font_config.get('variants'), dict):
            # 여러 변형이 있는 폰트
            for variant in font_config['variants'].values():
                if os.path.exists(variant['path']):
                    pdfmetrics.registerFont(TTFont(variant['name'], variant['path']))
        else:
            # 단일 폰트
            if os.path.exists(font_config['path']):
                pdfmetrics.registerFont(TTFont(font_config['name'], font_config['path']))


# 폰트 등록 실행
register_fonts()


class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = 'teachers/teacher_list.html'
    context_object_name = 'teachers'

    def get_queryset(self):
        # 기본 쿼리셋은 재직 중인 교사만 반환
        return Teacher.objects.filter(is_active=True).order_by('-hire_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        show_inactive = self.request.GET.get('show_inactive') == 'on'

        # 재직 중인 교사
        context['active_teachers'] = Teacher.objects.filter(is_active=True).order_by('-hire_date')

        # 퇴사자 포함 체크 시에만 퇴사한 교사 조회
        if show_inactive:
            context['inactive_teachers'] = Teacher.objects.filter(is_active=False).order_by('-resignation_date')
        else:
            context['inactive_teachers'] = []

        context['show_inactive'] = show_inactive
        return context


class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = Teacher
    template_name = 'teachers/teacher_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.object

        # 현재 년월 또는 쿼리 파라미터로 전달된 년월
        year = int(self.request.GET.get('year', timezone.now().year))
        month = int(self.request.GET.get('month', timezone.now().month))

        # 해당 월의 시작일과 종료일
        month_start = timezone.datetime(year, month, 1).date()
        if month == 12:
            month_end = timezone.datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = timezone.datetime(year, month + 1, 1).date() - timedelta(days=1)

        # 근무 기록 조회
        attendance_records = Attendance.objects.filter(
            teacher=teacher,
            date__range=[month_start, month_end]
        ).order_by('date')

        # 총 근무 시간 계산 및 각 레코드에 근무 시간 추가
        total_hours = 0
        total_minutes = 0
        work_days = 0
        for record in attendance_records:
            if record.start_time and record.end_time and record.is_present:
                start = timezone.datetime.combine(record.date, record.start_time)
                end = timezone.datetime.combine(record.date, record.end_time)
                duration = end - start
                hours = duration.total_seconds() / 3600
                h = int(hours)
                m = int((hours - h) * 60)
                record.work_hours = f"{h}시간 {m}분"
                total_hours += h
                total_minutes += m
                work_days += 1
            else:
                record.work_hours = "-"

        # 분을 시간으로 변환
        total_hours += total_minutes // 60
        total_minutes = total_minutes % 60

        # 예상 급여 계산 (시급 * 총 근무 시간)
        total_work_hours_decimal = total_hours + (total_minutes / 60)
        estimated_salary = int(teacher.base_salary * total_work_hours_decimal)

        context['attendance_records'] = attendance_records
        context['current_year'] = year
        context['current_month'] = month
        context['total_hours'] = total_hours
        context['total_minutes'] = total_minutes
        context['total_work_hours'] = f"{total_hours}시간 {total_minutes}분"
        context['work_days'] = work_days
        context['estimated_salary'] = estimated_salary

        # 이전/다음 달 계산
        if month == 1:
            context['prev_year'] = year - 1
            context['prev_month'] = 12
        else:
            context['prev_year'] = year
            context['prev_month'] = month - 1

        if month == 12:
            context['next_year'] = year + 1
            context['next_month'] = 1
        else:
            context['next_year'] = year
            context['next_month'] = month + 1

        # 월별 급여 내역 조회
        monthly_salaries = Salary.objects.filter(
            teacher=teacher
        ).order_by('-year', '-month')

        # 각 월의 근무 시간 계산
        for salary in monthly_salaries:
            salary_month_start = timezone.datetime(salary.year, salary.month, 1).date()
            if salary.month == 12:
                salary_month_end = timezone.datetime(salary.year + 1, 1, 1).date() - timedelta(days=1)
            else:
                salary_month_end = timezone.datetime(salary.year, salary.month + 1, 1).date() - timedelta(days=1)

            month_records = Attendance.objects.filter(
                teacher=teacher,
                date__range=[salary_month_start, salary_month_end],
                is_present=True,
                start_time__isnull=False,
                end_time__isnull=False
            )

            month_hours = 0
            month_minutes = 0
            for rec in month_records:
                start = timezone.datetime.combine(rec.date, rec.start_time)
                end = timezone.datetime.combine(rec.date, rec.end_time)
                duration = end - start
                hours = duration.total_seconds() / 3600
                month_hours += int(hours)
                month_minutes += int((hours - int(hours)) * 60)

            month_hours += month_minutes // 60
            month_minutes = month_minutes % 60
            salary.work_hours = f"{month_hours}시간 {month_minutes}분"

        # 총 급여 합계
        total_salary_amount = sum(s.total_amount for s in monthly_salaries)
        total_salary_days = sum(s.work_days for s in monthly_salaries)

        # 총 근무 시간 계산
        all_records = Attendance.objects.filter(
            teacher=teacher,
            is_present=True,
            start_time__isnull=False,
            end_time__isnull=False
        )
        all_hours = 0
        all_minutes = 0
        for rec in all_records:
            start = timezone.datetime.combine(rec.date, rec.start_time)
            end = timezone.datetime.combine(rec.date, rec.end_time)
            duration = end - start
            hours = duration.total_seconds() / 3600
            all_hours += int(hours)
            all_minutes += int((hours - int(hours)) * 60)

        all_hours += all_minutes // 60
        all_minutes = all_minutes % 60

        context['monthly_salaries'] = monthly_salaries
        context['total_salary_amount'] = total_salary_amount
        context['total_salary_days'] = total_salary_days
        context['total_salary_hours'] = f"{all_hours}시간 {all_minutes}분"

        return context


class TeacherCreateView(LoginRequiredMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'
    success_url = reverse_lazy('teachers:teacher_list')


class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'
    success_url = reverse_lazy('teachers:teacher_list')


class AttendanceCreateView(LoginRequiredMixin, View):
    def get(self, request):
        teachers = Teacher.objects.filter(is_active=True).order_by('name')
        form = BulkAttendanceForm(teachers=teachers)
        current_date = timezone.now().date()
        month_start = current_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # 선택된 날짜 (기본값: 오늘)
        selected_date = current_date

        # 해당 날짜의 출근 불가 교사 조회
        unavailable_teacher_ids = set(
            TeacherUnavailability.objects.filter(
                date=selected_date,
                teacher__is_active=True
            ).values_list('teacher_id', flat=True)
        )

        # 출근 불가 사유 조회
        unavailability_reasons = {
            u.teacher_id: u
            for u in TeacherUnavailability.objects.filter(
                date=selected_date,
                teacher__is_active=True
            ).select_related('teacher')
        }

        monthly_records = Attendance.objects.filter(date__range=[month_start, month_end]).order_by('teacher', 'date')

        teacher_records = {}
        for record in monthly_records:
            if record.teacher not in teacher_records:
                teacher_records[record.teacher] = {'records': [], 'total_hours': 0}

            if record.start_time and record.end_time:
                start_datetime = timezone.make_aware(timezone.datetime.combine(record.date, record.start_time))
                end_datetime = timezone.make_aware(timezone.datetime.combine(record.date, record.end_time))
                work_hours = (end_datetime - start_datetime).total_seconds() / 3600
                record.work_hours = round(work_hours, 2)
                teacher_records[record.teacher]['total_hours'] += record.work_hours
            else:
                record.work_hours = None

            teacher_records[record.teacher]['records'].append(record)

        context = {
            'form': form,
            'teachers': teachers,
            'teacher_records': teacher_records,
            'current_month': current_date.strftime('%Y년 %m월'),
            'selected_date': selected_date,
            'unavailable_teacher_ids': unavailable_teacher_ids,
            'unavailability_reasons': unavailability_reasons,
        }
        return render(request, 'teachers/attendance_form.html', context)

    def post(self, request):
        teachers = Teacher.objects.filter(is_active=True)
        form = BulkAttendanceForm(request.POST, teachers=teachers)
        if form.is_valid():
            date = form.cleaned_data['date']

            # 해당 날짜의 출근 불가 교사 조회
            unavailable_teacher_ids = set(
                TeacherUnavailability.objects.filter(
                    date=date,
                    teacher__is_active=True
                ).values_list('teacher_id', flat=True)
            )

            for teacher in teachers:
                # 출근 불가 교사는 건너뜀
                if teacher.id in unavailable_teacher_ids:
                    continue

                is_present = form.cleaned_data.get(f'is_present_{teacher.id}', False)
                start_time = form.cleaned_data.get(f'start_time_{teacher.id}')
                end_time = form.cleaned_data.get(f'end_time_{teacher.id}')

                if is_present:
                    Attendance.objects.update_or_create(
                        teacher=teacher,
                        date=date,
                        defaults={
                            'start_time': start_time,
                            'end_time': end_time
                        }
                    )
                else:
                    Attendance.objects.filter(teacher=teacher, date=date).delete()

            messages.success(request, '출근 기록이 성공적으로 저장되었습니다.')
            return redirect('teachers:attendance_create')

        # 폼이 유효하지 않은 경우, 에러와 함께 폼을 다시 렌더링
        current_date = timezone.now().date()
        context = {
            'form': form,
            'teachers': teachers,
            'teacher_records': {},
            'current_month': current_date.strftime('%Y년 %m월'),
            'selected_date': current_date,
            'unavailable_teacher_ids': set(),
            'unavailability_reasons': {},
        }
        return render(request, 'teachers/attendance_form.html', context)


class SalaryCalculationView(LoginRequiredMixin, View):
    template_name = 'teachers/salary_calculation.html'

    def calculate_work_hours(self, teacher, year, month):
        attendances = Attendance.objects.filter(
            teacher=teacher,
            date__year=year,
            date__month=month,
            is_present=True
        )
        
        total_hours = 0
        for attendance in attendances:
            if attendance.start_time and attendance.end_time:
                # Convert time objects to datetime for calculation
                start = datetime.combine(attendance.date, attendance.start_time)
                end = datetime.combine(attendance.date, attendance.end_time)
                hours = (end - start).total_seconds() / 3600
                total_hours += hours
                
        return total_hours, attendances.count()

    def get_active_teachers_for_month(self, year, month):
        # 해당 월의 첫날과 마지막날 계산
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)

        return Teacher.objects.filter(
            # 입사일이 해당 월 마지막날보다 이전이거나 같고
            hire_date__lte=end_date
        ).filter(
            # 퇴사일이 없거나, 퇴사일이 해당 월 첫날보다 이후인 경우
            models.Q(resignation_date__isnull=True) | 
            models.Q(resignation_date__gte=start_date)
        )

    def get(self, request):
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))

        salary_data = []
        total_salary = 0

        # 해당 월에 근무한 선생님들만 필터링
        teachers = self.get_active_teachers_for_month(year, month)

        for teacher in teachers:
            work_hours, work_days = self.calculate_work_hours(teacher, year, month)

            base_amount = int(work_hours * teacher.base_salary)

            # 기존 급여 레코드에서 추가급여 가져오기
            try:
                existing_salary = Salary.objects.get(teacher=teacher, year=year, month=month)
                additional_amount = existing_salary.additional_amount
            except Salary.DoesNotExist:
                additional_amount = 0

            total_amount = base_amount + additional_amount

            salary_data.append({
                'teacher': teacher,
                'teacher_id': teacher.id,
                'work_days': work_days,
                'work_hours': work_hours,
                'base_amount': base_amount,
                'additional_amount': additional_amount,
                'bank_name': teacher.bank.name if teacher.bank else None,
                'account_number': teacher.account_number,
                'total_amount': total_amount
            })

            total_salary += total_amount

        context = {
            'year': year,
            'month': month,
            'years': range(2020, timezone.now().year + 1),
            'months': range(1, 13),
            'salary_data': salary_data,
            'total_salary': total_salary
        }

        return render(request, self.template_name, context)

    def post(self, request):
        year = int(request.POST.get('year', timezone.now().year))
        month = int(request.POST.get('month', timezone.now().month))

        try:
            with transaction.atomic():
                # 각 선생님의 추가급여 업데이트
                for key, value in request.POST.items():
                    if key.startswith('additional_amount_'):
                        teacher_id = int(key.split('_')[-1])
                        additional_amount = int(value) if value else 0

                        teacher = Teacher.objects.get(id=teacher_id)
                        work_hours, work_days = self.calculate_work_hours(teacher, year, month)

                        base_amount = int(work_hours * teacher.base_salary)
                        total_amount = base_amount + additional_amount

                        Salary.objects.update_or_create(
                            teacher=teacher,
                            year=year,
                            month=month,
                            defaults={
                                'work_days': work_days,
                                'base_amount': base_amount,
                                'additional_amount': additional_amount,
                                'total_amount': total_amount
                            }
                        )

                messages.success(request, '급여가 성공적으로 저장되었습니다.')
        except Exception as e:
            messages.error(request, f'급여 저장 중 오류가 발생했습니다: {str(e)}')

        return redirect(f'{request.path}?year={year}&month={month}')


class SalaryTableView(LoginRequiredMixin, View):
    def get(self, request):
        current_year = timezone.now().year
        selected_year = request.GET.get('year')
        year = int(selected_year) if selected_year else current_year

        date_range = Attendance.objects.aggregate(
            min_date=Min('date'),
            max_date=Max('date')
        )

        if date_range['min_date'] and date_range['max_date']:
            start_year = date_range['min_date'].year
            end_year = date_range['max_date'].year
            year_range = range(start_year, end_year + 1)
        else:
            year_range = range(current_year - 2, current_year + 1)

        # 모든 선생님 (활성 상태 및 퇴직)
        teachers = Teacher.objects.all()
        months = range(1, 13)

        # 해당 연도의 모든 급여 데이터를 미리 조회 (성능 최적화)
        saved_salaries = {}
        for salary in Salary.objects.filter(year=year).select_related('teacher'):
            key = (salary.teacher_id, salary.month)
            saved_salaries[key] = salary.total_amount  # 기본급 + 추가급여 포함된 총액

        salary_table = []
        grand_total = 0

        # 활성 상태 선생님 급여 계산
        for teacher in teachers.filter(is_active=True):
            teacher_data = {'teacher': teacher}
            total = 0

            for month in months:
                # 저장된 급여 데이터가 있으면 사용 (추가급여 포함)
                key = (teacher.id, month)
                if key in saved_salaries:
                    salary = saved_salaries[key]
                else:
                    # 저장된 데이터가 없으면 근무시간으로 기본급만 계산
                    start_date = datetime(year, month, 1)
                    if month == 12:
                        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                    else:
                        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

                    attendances = Attendance.objects.filter(
                        teacher=teacher,
                        date__range=[start_date, end_date]
                    )

                    work_hours = sum(
                        (a.end_time.hour * 60 + a.end_time.minute) - (a.start_time.hour * 60 + a.start_time.minute)
                        for a in attendances if a.start_time and a.end_time
                    ) / 60

                    salary = int(work_hours * (teacher.base_salary or 15000))

                teacher_data[month] = salary
                total += salary

            teacher_data['total'] = total
            grand_total += total
            salary_table.append(teacher_data)

        # 퇴직 선생님 급여 계산 (활성 상태 선생님과 같은 방식으로 계산)
        for teacher in teachers.filter(is_active=False):
            teacher_data = {'teacher': teacher}
            total = 0

            for month in months:
                # 저장된 급여 데이터가 있으면 사용 (추가급여 포함)
                key = (teacher.id, month)
                if key in saved_salaries:
                    salary = saved_salaries[key]
                else:
                    # 저장된 데이터가 없으면 근무시간으로 기본급만 계산
                    start_date = datetime(year, month, 1)
                    if month == 12:
                        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                    else:
                        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

                    attendances = Attendance.objects.filter(teacher=teacher, date__range=[start_date, end_date])
                    work_hours = sum(
                        (a.end_time.hour * 60 + a.end_time.minute) - (a.start_time.hour * 60 + a.start_time.minute)
                        for a in attendances if a.start_time and a.end_time
                    ) / 60

                    salary = int(work_hours * (teacher.base_salary or 15000))

                teacher_data[month] = salary
                total += salary

            teacher_data['total'] = total
            grand_total += total
            salary_table.append(teacher_data)

        # 통계 데이터 계산
        statistics = self.calculate_statistics(salary_table, months, year)

        context = {
            'year': year,
            'year_range': sorted(list(year_range), reverse=True),
            'months': months,
            'salary_table': salary_table,
            'grand_total': grand_total,
            'statistics': statistics,
        }

        return render(request, 'teachers/salary_table.html', context)

    def calculate_statistics(self, salary_table, months, year):
        """급여 통계 데이터 계산"""
        import statistics as stats

        # 월별 총액 계산
        monthly_totals = []
        for month in months:
            month_total = sum(row.get(month, 0) for row in salary_table)
            monthly_totals.append(month_total)

        # 교사별 연간 총액
        teacher_totals = [row['total'] for row in salary_table if row['total'] > 0]

        # 0이 아닌 월별 급여만 추출 (개인별)
        all_nonzero_salaries = []
        for row in salary_table:
            for month in months:
                salary = row.get(month, 0)
                if salary > 0:
                    all_nonzero_salaries.append(salary)

        # 기본 통계
        statistics = {
            'monthly_totals': monthly_totals,
            'monthly_labels': [f'{m}월' for m in months],
        }

        # 연간 총 급여
        statistics['total_yearly'] = sum(monthly_totals)

        # 월 평균 급여 지출 (급여가 지급된 월 기준)
        nonzero_months = [t for t in monthly_totals if t > 0]
        statistics['avg_monthly_expense'] = int(sum(nonzero_months) / len(nonzero_months)) if nonzero_months else 0

        # 최고/최저 월 급여 지출
        if nonzero_months:
            statistics['max_monthly_expense'] = max(nonzero_months)
            statistics['min_monthly_expense'] = min(nonzero_months)
            statistics['max_month'] = monthly_totals.index(max(monthly_totals)) + 1
            statistics['min_month'] = monthly_totals.index(min([t for t in monthly_totals if t > 0] or [0])) + 1
        else:
            statistics['max_monthly_expense'] = 0
            statistics['min_monthly_expense'] = 0
            statistics['max_month'] = 0
            statistics['min_month'] = 0

        # 교사 수
        statistics['teacher_count'] = len([t for t in teacher_totals if t > 0])

        # 교사 평균 연봉
        statistics['avg_teacher_yearly'] = int(sum(teacher_totals) / len(teacher_totals)) if teacher_totals else 0

        # 개인별 월 평균 급여
        statistics['avg_individual_monthly'] = int(sum(all_nonzero_salaries) / len(all_nonzero_salaries)) if all_nonzero_salaries else 0

        # 개인별 월 급여 최고/최저
        if all_nonzero_salaries:
            statistics['max_individual_monthly'] = max(all_nonzero_salaries)
            statistics['min_individual_monthly'] = min(all_nonzero_salaries)
        else:
            statistics['max_individual_monthly'] = 0
            statistics['min_individual_monthly'] = 0

        # 표준편차 (교사별 연간)
        if len(teacher_totals) > 1:
            statistics['std_teacher_yearly'] = int(stats.stdev(teacher_totals))
        else:
            statistics['std_teacher_yearly'] = 0

        # 중앙값 (교사별 연간)
        if teacher_totals:
            statistics['median_teacher_yearly'] = int(stats.median(teacher_totals))
        else:
            statistics['median_teacher_yearly'] = 0

        # 교사별 급여 데이터 (차트용)
        teacher_names = [row['teacher'].name for row in salary_table if row['total'] > 0]
        teacher_salary_totals = [row['total'] for row in salary_table if row['total'] > 0]
        statistics['teacher_names'] = teacher_names
        statistics['teacher_salary_totals'] = teacher_salary_totals

        return statistics


class TeacherPDFReportView(LoginRequiredMixin, View):
    def get(self, request, teacher_id):
        teacher = get_object_or_404(Teacher, id=teacher_id)
        buffer = BytesIO()

        class NumberedCanvas(canvas.Canvas):
            def __init__(self, *args, **kwargs):
                canvas.Canvas.__init__(self, *args, **kwargs)
                self._saved_page_states = []

            def showPage(self):
                self._saved_page_states.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                num_pages = len(self._saved_page_states)
                for state in self._saved_page_states:
                    self.__dict__.update(state)
                    self.draw_page_footer(num_pages)
                    canvas.Canvas.showPage(self)
                canvas.Canvas.save(self)

            def draw_page_footer(self, page_count):
                self.setFont('NanumGothicBold', 10)
                # 학원명 (중앙)
                self.drawCentredString(A4[0]/2, 20*mm, "엠클래스수학과학전문학원")
                # 페이지 번호 (우측)
                page_num = f"{self._pageNumber} / {page_count}"
                self.drawRightString(A4[0] - 20*mm, 20*mm, page_num)

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=30*mm,
            title=f"{teacher.name} 선생님 근무 내역 보고서",
            author="엠클래스수학과학전문학원",
            subject=f"{teacher.name} 선생님 근무 보고서",
            creator="MClass Manager"
        )

        elements = []        

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Korean', fontName='NanumGothic', fontSize=10, leading=14, encoding='utf-8'))
        styles.add(ParagraphStyle(name='KoreanTitle', fontName='NanumGothicBold', fontSize=16, leading=20, alignment=1, encoding='utf-8'))
        styles.add(ParagraphStyle(name='KoreanSubtitle', fontName='NanumGothicBold', fontSize=12, leading=16, encoding='utf-8'))
        styles.add(ParagraphStyle(
            name='AttendanceDetail',
            fontName='Ubuntu-Regular',
            fontSize=9,
            leading=12,
            encoding='utf-8'
        ))

        # First page content (existing code remains the same)
        elements.append(Paragraph(f"{teacher.name} 선생님 근무 내역", styles['KoreanTitle']))
        elements.append(Spacer(1, 10*mm))

        # 기본 정보
        data = [
            ["이름:", teacher.name],
            ["전화번호:", teacher.get_formatted_phone_number() or ""],
            ["이메일:", teacher.email or ""],
            ["입사일:", teacher.hire_date.strftime("%Y-%m-%d") if teacher.hire_date else "정보 없음"],
            ["퇴사일:", teacher.resignation_date.strftime("%Y-%m-%d") if teacher.resignation_date else "재직 중"]
        ]
        t = Table(data, colWidths=[50*mm, 120*mm])
        t.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'NanumGothic'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10*mm))

        # 출근 기록
        elements.append(Paragraph("근무 기록", styles['KoreanSubtitle']))
        elements.append(Spacer(1, 5*mm))

        attendances = Attendance.objects.filter(teacher=teacher).order_by('date')
        
        # Salary 모델에서 저장된 급여 정보 가져오기
        saved_salaries = {
            f"{s.year}-{s.month:02d}": s
            for s in Salary.objects.filter(teacher=teacher)
        }

        monthly_data = {}

        # 출근 기록이 있는 경우 근무시간 계산
        if attendances:
            for attendance in attendances:
                year_month = attendance.date.strftime("%Y-%m")
                if year_month not in monthly_data:
                    monthly_data[year_month] = {'hours': 0, 'base_amount': 0, 'additional_amount': 0}

                if attendance.start_time and attendance.end_time:
                    start_datetime = datetime.combine(attendance.date, attendance.start_time)
                    end_datetime = datetime.combine(attendance.date, attendance.end_time)
                    if end_datetime < start_datetime:  # 자정을 넘긴 경우
                        end_datetime += timedelta(days=1)
                    work_hours = (end_datetime - start_datetime).total_seconds() / 3600
                    monthly_data[year_month]['hours'] += work_hours
                    monthly_data[year_month]['base_amount'] = int(monthly_data[year_month]['hours'] * teacher.base_salary)

        # 저장된 급여 정보 추가 (근무 기록이 없어도 추가급여만 있는 경우 포함)
        for year_month, salary in saved_salaries.items():
            if year_month not in monthly_data:
                # 근무 기록은 없지만 급여 데이터가 있는 경우
                monthly_data[year_month] = {
                    'hours': 0,
                    'base_amount': salary.base_amount,
                    'additional_amount': salary.additional_amount
                }
            else:
                # 근무 기록이 있는 경우 추가급여만 업데이트
                monthly_data[year_month]['additional_amount'] = salary.additional_amount

        # 월별 데이터가 있는 경우 테이블 생성
        if monthly_data:
            attendance_data = [["년/월", "근무시간", "기본급", "추가급여", "총 급여"]]
            total_hours = 0
            total_base = 0
            total_additional = 0
            total_amount = 0

            for year_month in sorted(monthly_data.keys()):
                data = monthly_data[year_month]
                year, month = year_month.split('-')
                hours = round(data['hours'], 1)
                base_amount = data['base_amount']
                additional_amount = data['additional_amount']
                total = base_amount + additional_amount

                attendance_data.append([
                    f"{year}년 {month}월",
                    f"{hours}시간",
                    f"{base_amount:,}원",
                    f"{additional_amount:,}원",
                    f"{total:,}원"
                ])
                total_hours += hours
                total_base += base_amount
                total_additional += additional_amount
                total_amount += total

            attendance_data.append([
                "총계",
                f"{total_hours:.1f}시간",
                f"{total_base:,}원",
                f"{total_additional:,}원",
                f"{total_amount:,}원"
            ])

            t = Table(attendance_data, colWidths=[40*mm, 35*mm, 35*mm, 35*mm, 35*mm])
            t.setStyle(TableStyle([
                ('FONT', (0,0), (-1,-1), 'NanumGothic'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("근무 기록이 없습니다.", styles['Korean']))

        # Add page break before attendance details
        elements.append(PageBreak())
        
        # Add attendance details title
        elements.append(Paragraph("상세 근무 기록", styles['KoreanSubtitle']))
        elements.append(Spacer(1, 5*mm))

        # Get all attendance records sorted by date
        attendances = Attendance.objects.filter(
            teacher=teacher
        ).order_by('-date')  # Latest first

        # Create attendance details table
        attendance_data = [["날짜", "시작", "종료", "수업 시간"]]
        
        for attendance in attendances:
            if attendance.start_time and attendance.end_time:
                start_datetime = datetime.combine(attendance.date, attendance.start_time)
                end_datetime = datetime.combine(attendance.date, attendance.end_time)
                if end_datetime < start_datetime:  # Handle overnight shifts
                    end_datetime += timedelta(days=1)
                work_hours = (end_datetime - start_datetime).total_seconds() / 3600
                
                attendance_data.append([
                    attendance.date.strftime("%Y-%m-%d"),
                    attendance.start_time.strftime("%H:%M"),
                    attendance.end_time.strftime("%H:%M"),
                    f"{work_hours:.1f}시간"
                ])

        # Create table with appropriate styling
        attendance_table = Table(
            attendance_data,
            colWidths=[45*mm, 40*mm, 40*mm, 45*mm],
            repeatRows=1  # Repeat header row on each page
        )
        
        attendance_table.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'NanumGothic'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        
        elements.append(attendance_table)

        # Build PDF
        doc.build(elements, canvasmaker=NumberedCanvas)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        filename = f"{teacher.name} 선생님 근무내역 보고서.pdf"
        encoded_filename = urllib.parse.quote(filename.encode('utf-8'))
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename*=UTF-8\'\'{encoded_filename}'
        response.write(pdf)
        
        return response


class SalaryPDFReportView(LoginRequiredMixin, View):
    def get(self, request, year, month):

        # 날짜 범위 계산
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

        buffer = BytesIO()

        # **PDF 문서 생성 및 메타데이터 설정**
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=30*mm,
            bottomMargin=20*mm,
            title=f"{year}년 {month}월 급여 내역",  # 메타데이터 제목 설정
            author="엠클래스수학과학전문학원",
            subject=f"{year}년 {month}월 급여 내역서",
            creator="MClass Manager"
        )

        # **푸터 함수 정의**
        def add_footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('NanumGothicBold', 10)
            # 페이지 너비 계산
            page_width = A4[0]
            # 푸터 텍스트 정의
            footer_text = "엠클래스수학과학전문학원"
            # 텍스트를 페이지 가로 중앙에 배치
            canvas.drawCentredString(page_width / 2, 15 * mm, footer_text)
            canvas.restoreState()

        # 스타일 정의
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Korean',
            fontName='NanumGothic',
            fontSize=10,
            leading=14
        ))
        styles.add(ParagraphStyle(
            name='KoreanTitle',
            fontName='NanumGothicBold',
            fontSize=16,
            leading=20,
            alignment=1
        ))

        # 표준 테이블 폭 설정
        TABLE_WIDTH = 170*mm

        elements = []

        # 제목 추가
        title = f"{year}년 {month}월 급여 내역"
        elements.append(Paragraph(title, styles['KoreanTitle']))
        elements.append(Spacer(1, 20))

        # 급여 데이터 계산 - Salary 모델에서 가져오기
        salaries = Salary.objects.filter(year=year, month=month).select_related('teacher')

        data = [['이름', '기본급', '추가급여', '총 급여']]
        total_base = 0
        total_additional = 0
        total_amount = 0

        for salary in salaries:
            total_base += salary.base_amount
            total_additional += salary.additional_amount
            total_amount += salary.total_amount
            data.append([
                salary.teacher.name,
                f"{salary.base_amount:,}원",
                f"{salary.additional_amount:,}원",
                f"{salary.total_amount:,}원"
            ])

        data.append([
            "합계",
            f"{total_base:,}원",
            f"{total_additional:,}원",
            f"{total_amount:,}원"
        ])

        # 테이블 생성 (4개 컬럼: 이름, 기본급, 추가급여, 총 급여)
        col_widths = [TABLE_WIDTH * 0.25, TABLE_WIDTH * 0.25, TABLE_WIDTH * 0.25, TABLE_WIDTH * 0.25]
        table = Table(data, colWidths=col_widths)

        # 테이블 스타일 설정
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # 헤더 중앙 정렬
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # 이름 중앙 정렬
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # 금액 컬럼들 우측 정렬
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # 헤더 배경
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),  # 합계 행 배경
        ]))

        elements.append(table)

        # **PDF 생성 (푸터 추가)**
        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)

        pdf = buffer.getvalue()
        buffer.close()

        # 파일명 설정
        filename = f"{year}년 {month}월 급여내역서.pdf"
        encoded_filename = urllib.parse.quote(filename.encode('utf-8'))

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
        response.write(pdf)

        return response


def teacher_send_email(request, pk):
    """교사에게 이메일 발송"""
    from django.core.mail import EmailMessage
    from django.conf import settings
    from .forms import TeacherEmailForm

    teacher = get_object_or_404(Teacher, pk=pk)

    if not teacher.email:
        messages.error(request, '해당 교사의 이메일 주소가 등록되어 있지 않습니다.')
        return redirect('teachers:teacher_detail', pk=pk)

    if request.method == 'POST':
        form = TeacherEmailForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # 발신자 이메일 설정 (admin 사용자인 경우 jjangdm@mclass.co.kr 사용)
            from_email = settings.DEFAULT_FROM_EMAIL if request.user.username == 'admin' else settings.EMAIL_HOST_USER

            try:
                # EmailMessage 객체 생성
                email = EmailMessage(
                    subject=subject,
                    body=message,
                    from_email=from_email,
                    to=[teacher.email],
                )

                # 첨부파일 처리
                files = request.FILES.getlist('attachments')
                for file in files:
                    email.attach(file.name, file.read(), file.content_type)

                # 이메일 전송
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f'Sending email to {teacher.email} from {from_email}')

                result = email.send(fail_silently=False)

                logger.info(f'Email send result: {result}')

                messages.success(request, f'{teacher.name} 교사에게 이메일을 성공적으로 발송했습니다.')
                return redirect('teachers:teacher_detail', pk=pk)
            except Exception as e:
                import logging
                import traceback
                logger = logging.getLogger(__name__)
                logger.error(f'Email sending failed: {str(e)}')
                logger.error(traceback.format_exc())
                messages.error(request, f'이메일 발송 중 오류가 발생했습니다: {str(e)}')
    else:
        form = TeacherEmailForm()

    context = {
        'form': form,
        'teacher': teacher,
    }
    return render(request, 'teachers/teacher_email_form.html', context)


@login_required
def teacher_resign(request, pk):
    """교사 퇴사 처리"""
    teacher = get_object_or_404(Teacher, pk=pk)
    
    if request.method == 'POST':
        teacher.resignation_date = timezone.now().date()
        teacher.is_active = False
        teacher.save()
        messages.success(request, f'{teacher.name} 교사가 퇴사 처리되었습니다.')
        return redirect('teachers:teacher_detail', pk=pk)
    
    return render(request, 'teachers/teacher_resign_confirm.html', {'teacher': teacher})


@login_required
def teacher_rehire(request, pk):
    """교사 재입사 처리"""
    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        teacher.resignation_date = None
        teacher.is_active = True
        teacher.save()
        messages.success(request, f'{teacher.name} 교사가 재입사 처리되었습니다.')
        return redirect('teachers:teacher_detail', pk=pk)

    return render(request, 'teachers/teacher_rehire_confirm.html', {'teacher': teacher})


class UnavailabilityListView(LoginRequiredMixin, View):
    """출근 불가 일정 목록 및 날짜별 조회"""

    def get(self, request):
        selected_date = request.GET.get('date')

        if selected_date:
            # 특정 날짜 선택 시 출근 가능/불가 교사 분류
            try:
                check_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                check_date = timezone.now().date()

            # 해당 날짜에 출근 불가인 교사들
            unavailable_records = TeacherUnavailability.objects.filter(
                date=check_date,
                teacher__is_active=True
            ).select_related('teacher')

            unavailable_teacher_ids = unavailable_records.values_list('teacher_id', flat=True)

            # 출근 가능한 교사들
            available_teachers = Teacher.objects.filter(
                is_active=True
            ).exclude(id__in=unavailable_teacher_ids).order_by('name')

            # 출근 불가한 교사들 (사유 포함)
            unavailable_teachers = unavailable_records.order_by('teacher__name')

            context = {
                'selected_date': check_date,
                'available_teachers': available_teachers,
                'unavailable_teachers': unavailable_teachers,
                'available_count': available_teachers.count(),
                'unavailable_count': unavailable_teachers.count(),
            }
        else:
            # 날짜 미선택 시 전체 일정 목록
            context = {
                'selected_date': None,
                'upcoming_unavailabilities': TeacherUnavailability.objects.filter(
                    date__gte=timezone.now().date(),
                    teacher__is_active=True
                ).select_related('teacher').order_by('date', 'teacher__name')[:50],
            }

        return render(request, 'teachers/unavailability_list.html', context)


class UnavailabilityCreateView(LoginRequiredMixin, View):
    """출근 불가 일정 등록"""

    def get(self, request):
        form = TeacherUnavailabilityForm()
        bulk_form = BulkUnavailabilityForm()
        context = {
            'form': form,
            'bulk_form': bulk_form,
        }
        return render(request, 'teachers/unavailability_form.html', context)

    def post(self, request):
        if 'bulk_submit' in request.POST:
            # 기간 일괄 등록
            bulk_form = BulkUnavailabilityForm(request.POST)
            if bulk_form.is_valid():
                teacher = bulk_form.cleaned_data['teacher']
                start_date = bulk_form.cleaned_data['start_date']
                end_date = bulk_form.cleaned_data['end_date']
                reason = bulk_form.cleaned_data['reason']
                memo = bulk_form.cleaned_data['memo']

                created_count = 0
                current_date = start_date
                while current_date <= end_date:
                    _, created = TeacherUnavailability.objects.get_or_create(
                        teacher=teacher,
                        date=current_date,
                        defaults={'reason': reason, 'memo': memo}
                    )
                    if created:
                        created_count += 1
                    current_date += timedelta(days=1)

                messages.success(request, f'{teacher.name} 교사의 출근 불가 일정 {created_count}건이 등록되었습니다.')
                return redirect('teachers:unavailability_list')

            form = TeacherUnavailabilityForm()
            context = {'form': form, 'bulk_form': bulk_form}
            return render(request, 'teachers/unavailability_form.html', context)
        else:
            # 단일 날짜 등록
            form = TeacherUnavailabilityForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, '출근 불가 일정이 등록되었습니다.')
                return redirect('teachers:unavailability_list')

            bulk_form = BulkUnavailabilityForm()
            context = {'form': form, 'bulk_form': bulk_form}
            return render(request, 'teachers/unavailability_form.html', context)


@login_required
def unavailability_delete(request, pk):
    """출근 불가 일정 삭제"""
    unavailability = get_object_or_404(TeacherUnavailability, pk=pk)

    if request.method == 'POST':
        teacher_name = unavailability.teacher.name
        date_str = unavailability.date.strftime('%Y-%m-%d')
        unavailability.delete()
        messages.success(request, f'{teacher_name} 교사의 {date_str} 출근 불가 일정이 삭제되었습니다.')
        return redirect('teachers:unavailability_list')

    return render(request, 'teachers/unavailability_confirm_delete.html', {'unavailability': unavailability})


@login_required
def unavailability_bulk_delete(request):
    """출근 불가 일정 일괄 삭제"""
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if teacher_id and start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()

                deleted_count, _ = TeacherUnavailability.objects.filter(
                    teacher_id=teacher_id,
                    date__range=[start, end]
                ).delete()

                messages.success(request, f'{deleted_count}건의 출근 불가 일정이 삭제되었습니다.')
            except ValueError:
                messages.error(request, '날짜 형식이 올바르지 않습니다.')
        else:
            messages.error(request, '필수 정보가 누락되었습니다.')

    return redirect('teachers:unavailability_list')


class AssignmentListView(LoginRequiredMixin, View):
    """날짜별 교사-학생 배정 조회"""

    def get(self, request):
        from students.models import Student

        selected_date = request.GET.get('date')

        if selected_date:
            try:
                check_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                check_date = timezone.now().date()
        else:
            check_date = timezone.now().date()

        # 해당 날짜에 출근 불가인 교사 ID
        unavailable_teacher_ids = set(
            TeacherUnavailability.objects.filter(
                date=check_date,
                teacher__is_active=True
            ).values_list('teacher_id', flat=True)
        )

        # 출근 가능한 교사들
        available_teachers = Teacher.objects.filter(
            is_active=True
        ).exclude(id__in=unavailable_teacher_ids).order_by('name')

        # 해당 날짜의 배정 정보
        assignments = TeacherStudentAssignment.objects.filter(
            date=check_date
        ).select_related('teacher', 'student').order_by('teacher__name', 'student__name')

        # 교사별 배정된 학생 그룹화
        teacher_assignments = {}
        assigned_student_ids = set()
        for teacher in available_teachers:
            teacher_assignments[teacher] = []

        # 원장/결석/예외 학생 리스트
        director_assignments = []
        absent_assignments = []
        exception_assignments = []

        for assignment in assignments:
            assigned_student_ids.add(assignment.student_id)
            if assignment.assignment_type == 'director':
                director_assignments.append(assignment)
            elif assignment.assignment_type == 'absent':
                absent_assignments.append(assignment)
            elif assignment.assignment_type == 'exception':
                exception_assignments.append(assignment)
            elif assignment.teacher in teacher_assignments:
                teacher_assignments[assignment.teacher].append(assignment)

        # 배정되지 않은 학생들
        unassigned_students = Student.objects.filter(
            is_active=True
        ).exclude(id__in=assigned_student_ids).order_by('grade', 'name')

        # 학년별 그룹화 (미배정 학생)
        grade_order = ['K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11', 'K12']
        grade_labels = {
            'K5': '초5', 'K6': '초6', 'K7': '중1', 'K8': '중2',
            'K9': '중3', 'K10': '고1', 'K11': '고2', 'K12': '고3'
        }
        unassigned_by_grade = {}
        for grade in grade_order:
            students_in_grade = [s for s in unassigned_students if s.grade == grade]
            if students_in_grade:
                unassigned_by_grade[grade] = {
                    'label': grade_labels.get(grade, grade),
                    'students': students_in_grade
                }
        # 학년 미지정 학생
        no_grade_students = [s for s in unassigned_students if not s.grade]
        if no_grade_students:
            unassigned_by_grade['none'] = {
                'label': '미지정',
                'students': no_grade_students
            }

        # 모든 활성 학생
        all_students = Student.objects.filter(is_active=True).order_by('grade', 'name')

        context = {
            'selected_date': check_date,
            'available_teachers': available_teachers,
            'teacher_assignments': teacher_assignments,
            'director_assignments': director_assignments,
            'absent_assignments': absent_assignments,
            'exception_assignments': exception_assignments,
            'unassigned_students': unassigned_students,
            'unassigned_by_grade': unassigned_by_grade,
            'all_students': all_students,
            'unavailable_teacher_ids': unavailable_teacher_ids,
            'total_assigned': assignments.count(),
            'total_unassigned': unassigned_students.count(),
            'grade_labels': grade_labels,
        }

        return render(request, 'teachers/assignment_list.html', context)


class AssignmentCreateView(LoginRequiredMixin, View):
    """교사-학생 배정 등록"""

    def get(self, request):
        from students.models import Student

        date = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        teacher_id = request.GET.get('teacher')

        # 해당 날짜에 출근 불가인 교사 ID
        unavailable_teacher_ids = set(
            TeacherUnavailability.objects.filter(
                date=date,
                teacher__is_active=True
            ).values_list('teacher_id', flat=True)
        )

        # 출근 가능한 교사들
        available_teachers = Teacher.objects.filter(
            is_active=True
        ).exclude(id__in=unavailable_teacher_ids).order_by('name')

        # 해당 날짜에 이미 배정된 학생 ID
        assigned_student_ids = set(
            TeacherStudentAssignment.objects.filter(
                date=date
            ).values_list('student_id', flat=True)
        )

        # 배정 가능한 학생들 (아직 배정되지 않은 학생)
        available_students = Student.objects.filter(
            is_active=True
        ).exclude(id__in=assigned_student_ids).order_by('name')

        context = {
            'available_teachers': available_teachers,
            'available_students': available_students,
            'selected_date': date,
            'selected_teacher_id': int(teacher_id) if teacher_id else None,
        }

        return render(request, 'teachers/assignment_form.html', context)

    def post(self, request):
        date = request.POST.get('date')
        teacher_id = request.POST.get('teacher')
        student_ids = request.POST.getlist('students')
        assignment_type = request.POST.get('assignment_type', 'normal')

        # 결석/예외인 경우 teacher_id가 없어도 됨
        if not date or not student_ids:
            messages.error(request, '필수 정보가 누락되었습니다.')
            return redirect('progress:assignment_list')

        if assignment_type == 'normal' and not teacher_id:
            messages.error(request, '교사를 선택해주세요.')
            return redirect('progress:assignment_list')

        teacher = get_object_or_404(Teacher, pk=teacher_id) if teacher_id else None
        created_count = 0

        for student_id in student_ids:
            _, created = TeacherStudentAssignment.objects.get_or_create(
                student_id=student_id,
                date=date,
                defaults={
                    'teacher': teacher,
                    'assignment_type': assignment_type
                }
            )
            if created:
                created_count += 1

        if created_count > 0:
            if assignment_type == 'director':
                messages.success(request, f'{created_count}명의 학생이 원장 배정되었습니다.')
            elif assignment_type == 'absent':
                messages.success(request, f'{created_count}명의 학생이 결석 처리되었습니다.')
            elif assignment_type == 'exception':
                messages.success(request, f'{created_count}명의 학생이 예외 처리되었습니다.')
            else:
                messages.success(request, f'{teacher.name} 교사에게 {created_count}명의 학생이 배정되었습니다.')
        else:
            messages.info(request, '이미 배정된 학생입니다.')

        return redirect(f"/progress/assignment/?date={date}")


@login_required
def assignment_delete(request, pk):
    """배정 삭제"""
    assignment = get_object_or_404(TeacherStudentAssignment, pk=pk)
    date_str = assignment.date.strftime('%Y-%m-%d')

    if request.method == 'POST':
        student_name = assignment.student.name
        if assignment.teacher:
            teacher_name = assignment.teacher.name
            messages.success(request, f'{student_name} 학생의 {teacher_name} 교사 배정이 삭제되었습니다.')
        else:
            type_label = dict(TeacherStudentAssignment.ASSIGNMENT_TYPE_CHOICES).get(assignment.assignment_type, assignment.assignment_type)
            messages.success(request, f'{student_name} 학생의 {type_label} 배정이 삭제되었습니다.')
        assignment.delete()
        return redirect(f"/progress/assignment/?date={date_str}")

    return render(request, 'teachers/assignment_confirm_delete.html', {
        'assignment': assignment,
        'date_str': date_str
    })


@login_required
def assignment_bulk_delete(request):
    """날짜별 배정 일괄 삭제"""
    if request.method == 'POST':
        date = request.POST.get('date')
        teacher_id = request.POST.get('teacher_id')

        if date:
            queryset = TeacherStudentAssignment.objects.filter(date=date)
            if teacher_id:
                queryset = queryset.filter(teacher_id=teacher_id)

            deleted_count, _ = queryset.delete()
            messages.success(request, f'{deleted_count}건의 배정이 삭제되었습니다.')
        else:
            messages.error(request, '날짜가 누락되었습니다.')

    return redirect('progress:assignment_list')


@login_required
def assignment_change_teacher(request, pk):
    """배정 교사 변경 (결석/예외에서 교사로 변경 포함)"""
    from django.http import JsonResponse

    assignment = get_object_or_404(TeacherStudentAssignment, pk=pk)

    if request.method == 'POST':
        new_teacher_id = request.POST.get('new_teacher')
        if new_teacher_id:
            new_teacher = get_object_or_404(Teacher, pk=new_teacher_id)
            old_teacher_name = assignment.teacher.name if assignment.teacher else assignment.get_assignment_type_display()
            assignment.teacher = new_teacher
            assignment.assignment_type = 'normal'  # 교사로 변경 시 일반 타입으로 변경
            assignment.save()

            # AJAX 요청인 경우 JSON 응답
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})

            messages.success(request, f'{assignment.student.name} 학생의 담당 교사가 {old_teacher_name}에서 {new_teacher.name}(으)로 변경되었습니다.')

    return redirect(f"/progress/assignment/?date={assignment.date.strftime('%Y-%m-%d')}")


@login_required
def assignment_change_type(request, pk):
    """배정 유형 변경 (교사 → 결석/예외 또는 결석 ↔ 예외)"""
    from django.http import JsonResponse

    assignment = get_object_or_404(TeacherStudentAssignment, pk=pk)

    if request.method == 'POST':
        new_type = request.POST.get('assignment_type')
        if new_type in ['absent', 'exception']:
            old_type = assignment.get_assignment_type_display()
            assignment.assignment_type = new_type
            assignment.teacher = None  # 결석/예외로 변경 시 교사 해제
            assignment.save()

            # AJAX 요청인 경우 JSON 응답
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})

            new_type_display = '결석' if new_type == 'absent' else '예외'
            messages.success(request, f'{assignment.student.name} 학생이 {new_type_display}(으)로 변경되었습니다.')

    return redirect(f"/progress/assignment/?date={assignment.date.strftime('%Y-%m-%d')}")


@login_required
def assignment_unassign(request, pk):
    """배정 해제 (미배정으로 이동)"""
    from django.http import JsonResponse

    assignment = get_object_or_404(TeacherStudentAssignment, pk=pk)

    if request.method == 'POST':
        student_name = assignment.student.name
        date_str = assignment.date.strftime('%Y-%m-%d')
        assignment.delete()

        # AJAX 요청인 경우 JSON 응답
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        messages.success(request, f'{student_name} 학생의 배정이 해제되었습니다.')
        return redirect(f"/progress/assignment/?date={date_str}")

    return redirect('progress:assignment_list')


class TeacherProgressView(LoginRequiredMixin, View):
    """교사용 배정 학생 진도 관리 페이지"""

    def get(self, request, teacher_pk=None):
        from students.models import Student
        from bookstore.models import BookSale, StudentBookProgress

        # 날짜 선택 (기본: 오늘)
        selected_date = request.GET.get('date')
        if selected_date:
            try:
                check_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                check_date = timezone.now().date()
        else:
            check_date = timezone.now().date()

        # 교사 선택 (URL 파라미터 또는 쿼리스트링)
        teacher = None
        if teacher_pk:
            teacher = get_object_or_404(Teacher, pk=teacher_pk)
        else:
            teacher_id = request.GET.get('teacher')
            if teacher_id:
                teacher = get_object_or_404(Teacher, pk=teacher_id)

        # 해당 날짜에 이 교사에게 배정된 학생들
        assignments = []
        student_data = []

        if teacher:
            assignments = TeacherStudentAssignment.objects.filter(
                teacher=teacher,
                date=check_date,
                assignment_type='normal'
            ).select_related('student')

            # 각 학생별 교재 진도 정보 수집
            for assignment in assignments:
                student = assignment.student
                # 학생에게 지급된 교재들
                book_sales = BookSale.objects.filter(student=student).select_related('book')

                books_data = []
                for sale in book_sales:
                    # 교재에 목차가 있는 경우만 진도 관리 가능
                    if sale.book.contents.exists():
                        stats = sale.get_progress_stats()
                        books_data.append({
                            'sale': sale,
                            'book': sale.book,
                            'stats': stats,
                        })

                student_data.append({
                    'student': student,
                    'assignment': assignment,
                    'books': books_data,
                })

        # 활성 교사 목록 (교사 선택용)
        available_teachers = Teacher.objects.filter(is_active=True).order_by('name')

        context = {
            'selected_date': check_date,
            'teacher': teacher,
            'available_teachers': available_teachers,
            'assignments': assignments,
            'student_data': student_data,
        }

        return render(request, 'teachers/teacher_progress.html', context)


class DailyProgressSummaryView(LoginRequiredMixin, View):
    """관리자용 일별 전체 수업 기록 조회"""

    def get(self, request):
        from students.models import Student
        from bookstore.models import BookSale, StudentBookProgress

        # 날짜 선택 (기본: 오늘)
        selected_date = request.GET.get('date')
        if selected_date:
            try:
                check_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                check_date = timezone.now().date()
        else:
            check_date = timezone.now().date()

        # 해당 날짜의 모든 배정 정보
        all_assignments = TeacherStudentAssignment.objects.filter(
            date=check_date
        ).select_related('teacher', 'student').order_by('teacher__name', 'student__name')

        # 교사별 데이터 구성
        teacher_summary = {}

        for assignment in all_assignments:
            if assignment.assignment_type != 'normal':
                continue  # 결석, 예외 등은 별도 처리

            teacher = assignment.teacher
            if teacher not in teacher_summary:
                teacher_summary[teacher] = {
                    'teacher': teacher,
                    'students': [],
                    'total_students': 0,
                }

            student = assignment.student

            # 학생의 교재별 진도 정보
            book_sales = BookSale.objects.filter(student=student).select_related('book')
            books_progress = []

            for sale in book_sales:
                if sale.book.contents.exists():
                    # 오늘 날짜로 기록된 진도 항목 수
                    today_records = sale.progress_records.filter(study_date=check_date).count()
                    stats = sale.get_progress_stats()
                    books_progress.append({
                        'sale': sale,
                        'book': sale.book,
                        'stats': stats,
                        'today_records': today_records,
                    })

            teacher_summary[teacher]['students'].append({
                'student': student,
                'assignment': assignment,
                'books': books_progress,
            })
            teacher_summary[teacher]['total_students'] += 1

        # 결석 학생
        absent_assignments = all_assignments.filter(assignment_type='absent')

        # 예외 학생
        exception_assignments = all_assignments.filter(assignment_type='exception')

        # 원장 배정 학생
        director_assignments = all_assignments.filter(assignment_type='director')

        # 통계
        total_assigned = all_assignments.filter(assignment_type='normal').count()
        total_absent = absent_assignments.count()
        total_exception = exception_assignments.count()
        total_director = director_assignments.count()

        # 오늘 기록된 총 진도 평가 수
        total_progress_today = StudentBookProgress.objects.filter(study_date=check_date).count()

        # 학생 기준 데이터 구성
        student_list = []
        for assignment in all_assignments:
            if assignment.assignment_type != 'normal':
                continue

            student = assignment.student
            teacher = assignment.teacher

            # 학생의 교재별 진도 정보
            book_sales = BookSale.objects.filter(student=student).select_related('book')
            books_progress = []

            for sale in book_sales:
                if sale.book.contents.exists():
                    today_records = sale.progress_records.filter(study_date=check_date).count()
                    stats = sale.get_progress_stats()
                    books_progress.append({
                        'sale': sale,
                        'book': sale.book,
                        'stats': stats,
                        'today_records': today_records,
                    })

            student_list.append({
                'student': student,
                'teacher': teacher,
                'assignment': assignment,
                'books': books_progress,
            })

        # 학생 이름순 정렬
        student_list.sort(key=lambda x: x['student'].name)

        # 뷰 모드 (teacher 또는 student)
        view_mode = request.GET.get('view', 'student')

        context = {
            'selected_date': check_date,
            'teacher_summary': teacher_summary,
            'student_list': student_list,
            'absent_assignments': absent_assignments,
            'exception_assignments': exception_assignments,
            'director_assignments': director_assignments,
            'total_assigned': total_assigned,
            'total_absent': total_absent,
            'total_exception': total_exception,
            'total_director': total_director,
            'total_progress_today': total_progress_today,
            'view_mode': view_mode,
        }

        return render(request, 'teachers/daily_progress_summary.html', context)


# ==================== 교사 계정 관리 ====================

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse


class TeacherLoginView(View):
    """교사 전용 로그인 페이지"""

    def get(self, request):
        if request.user.is_authenticated:
            # 이미 로그인된 경우
            if hasattr(request.user, 'teacher_profile'):
                return redirect('progress:my_progress')
            # 관리자 또는 일반 사용자는 메인 대시보드로
            return redirect('index')
        return render(request, 'teachers/teacher_login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # 교사 프로필이 있으면 교사 진도 페이지로
            if hasattr(user, 'teacher_profile'):
                messages.success(request, f'{user.teacher_profile.name} 선생님, 환영합니다!')
                return redirect('progress:my_progress')
            else:
                # 관리자 또는 일반 사용자는 메인 대시보드로
                return redirect('index')
        else:
            return render(request, 'teachers/teacher_login.html', {
                'error_message': '아이디 또는 비밀번호가 올바르지 않습니다.',
                'username': username,  # 입력한 아이디 유지
            })


class TeacherLogoutView(View):
    """교사 로그아웃"""

    def get(self, request):
        logout(request)
        messages.info(request, '로그아웃되었습니다.')
        return redirect('login')


class TeacherMyProgressView(LoginRequiredMixin, View):
    """교사 자신의 배정 학생 진도 관리 페이지"""

    def get(self, request):
        from bookstore.models import BookSale, StudentBookProgress

        # 현재 로그인한 사용자의 교사 프로필 확인
        if not hasattr(request.user, 'teacher_profile'):
            messages.error(request, '교사 계정이 아닙니다.')
            return redirect('students:student_list')

        teacher = request.user.teacher_profile

        # 날짜 선택 (기본: 오늘)
        selected_date = request.GET.get('date')
        if selected_date:
            try:
                check_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                check_date = timezone.now().date()
        else:
            check_date = timezone.now().date()

        # 해당 날짜에 이 교사에게 배정된 학생들
        assignments = TeacherStudentAssignment.objects.filter(
            teacher=teacher,
            date=check_date,
            assignment_type='normal'
        ).select_related('student')

        # 각 학생별 교재 진도 정보 수집
        student_data = []
        for assignment in assignments:
            student = assignment.student
            book_sales = BookSale.objects.filter(student=student).select_related('book')

            books_data = []
            for sale in book_sales:
                if sale.book.contents.exists():
                    stats = sale.get_progress_stats()
                    books_data.append({
                        'sale': sale,
                        'book': sale.book,
                        'stats': stats,
                    })

            student_data.append({
                'student': student,
                'assignment': assignment,
                'books': books_data,
            })

        context = {
            'selected_date': check_date,
            'teacher': teacher,
            'student_data': student_data,
            'is_my_page': True,  # 자신의 페이지임을 표시
        }

        return render(request, 'teachers/teacher_my_progress.html', context)


@login_required
def teacher_account_create(request, pk):
    """교사에게 로그인 계정 생성 (관리자용)"""
    teacher = get_object_or_404(Teacher, pk=pk)

    if teacher.user:
        messages.warning(request, f'{teacher.name} 선생님은 이미 계정이 있습니다.')
        return redirect('teachers:teacher_detail', pk=pk)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        # 유효성 검사
        if not username:
            messages.error(request, '사용자명을 입력해주세요.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, '이미 사용 중인 사용자명입니다.')
        elif len(password) < 4:
            messages.error(request, '비밀번호는 4자 이상이어야 합니다.')
        elif password != password_confirm:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
        else:
            # 계정 생성
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=teacher.name,
                email=teacher.email or ''
            )
            teacher.user = user
            teacher.save()
            messages.success(request, f'{teacher.name} 선생님의 계정이 생성되었습니다. (ID: {username})')
            return redirect('teachers:teacher_detail', pk=pk)

    return render(request, 'teachers/teacher_account_create.html', {'teacher': teacher})


@login_required
def teacher_account_delete(request, pk):
    """교사 계정 삭제 (관리자용)"""
    teacher = get_object_or_404(Teacher, pk=pk)

    if not teacher.user:
        messages.warning(request, f'{teacher.name} 선생님은 계정이 없습니다.')
        return redirect('teachers:teacher_detail', pk=pk)

    if request.method == 'POST':
        user = teacher.user
        teacher.user = None
        teacher.save()
        user.delete()
        messages.success(request, f'{teacher.name} 선생님의 계정이 삭제되었습니다.')
        return redirect('teachers:teacher_detail', pk=pk)

    return render(request, 'teachers/teacher_account_delete.html', {'teacher': teacher})


@login_required
def teacher_password_reset(request, pk):
    """교사 비밀번호 재설정 (관리자용)"""
    teacher = get_object_or_404(Teacher, pk=pk)

    if not teacher.user:
        messages.warning(request, f'{teacher.name} 선생님은 계정이 없습니다.')
        return redirect('teachers:teacher_detail', pk=pk)

    if request.method == 'POST':
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if len(password) < 4:
            messages.error(request, '비밀번호는 4자 이상이어야 합니다.')
        elif password != password_confirm:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
        else:
            teacher.user.set_password(password)
            teacher.user.save()
            messages.success(request, f'{teacher.name} 선생님의 비밀번호가 변경되었습니다.')
            return redirect('teachers:teacher_detail', pk=pk)

    return render(request, 'teachers/teacher_password_reset.html', {'teacher': teacher})
