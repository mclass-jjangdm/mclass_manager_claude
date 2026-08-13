from datetime import timedelta, datetime
from io import BytesIO
from pyexpat.errors import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import Teacher, Attendance, Salary, TeacherUnavailability, TeacherStudentAssignment, Message, MessageReadStatus, UnavailabilityBlockedDate, UnavailabilitySettings
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
        current_date = timezone.now().date()

        # 선택된 날짜 (쿼리 파라미터 또는 기본값: 오늘)
        date_param = request.GET.get('date')
        if date_param:
            try:
                selected_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                selected_date = current_date
        else:
            selected_date = current_date

        form = BulkAttendanceForm(teachers=teachers, initial={'date': selected_date})

        # 선택된 날짜 기준으로 월 계산
        month_start = selected_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

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

        # 해당 날짜의 기존 근무 기록 조회 (수정용)
        existing_attendances = {
            a.teacher_id: a
            for a in Attendance.objects.filter(
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
            'current_month': selected_date.strftime('%Y년 %m월'),
            'selected_date': selected_date,
            'unavailable_teacher_ids': unavailable_teacher_ids,
            'unavailability_reasons': unavailability_reasons,
            'existing_attendances': existing_attendances,
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
            hire_date__lte=end_date,
        ).filter(
            # 퇴사일이 없거나, 퇴사일이 해당 월 첫날보다 이후인 경우 (퇴직자도 해당 월 근무 시 포함)
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
                salary_id = existing_salary.id
                date_paid = existing_salary.date_paid
            except Salary.DoesNotExist:
                additional_amount = 0
                salary_id = None
                date_paid = None

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
                'total_amount': total_amount,
                'salary_id': salary_id,
                'date_paid': date_paid,
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


class SalaryBulkMarkPaidView(LoginRequiredMixin, View):
    def post(self, request):
        year = int(request.POST.get('year', timezone.now().year))
        month = int(request.POST.get('month', timezone.now().month))
        date_paid_str = request.POST.get('date_paid', '')
        try:
            date_paid = datetime.strptime(date_paid_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, '올바른 날짜를 입력해주세요.')
            return redirect(reverse('teachers:salary_calculation') + f'?year={year}&month={month}')
        updated = Salary.objects.filter(year=year, month=month, date_paid__isnull=True).update(date_paid=date_paid)
        messages.success(request, f'{year}년 {month}월 급여 {updated}건이 일괄 지급 처리되었습니다.')
        return redirect(reverse('teachers:salary_calculation') + f'?year={year}&month={month}')


class SalaryMarkPaidView(LoginRequiredMixin, View):
    def post(self, request, pk):
        salary = get_object_or_404(Salary, pk=pk)
        date_paid_str = request.POST.get('date_paid', '')
        try:
            salary.date_paid = datetime.strptime(date_paid_str, '%Y-%m-%d').date()
            salary.save()
            messages.success(request, f'{salary.teacher.name} {salary.year}년 {salary.month}월 급여 지급 처리되었습니다.')
        except (ValueError, TypeError):
            messages.error(request, '올바른 날짜를 입력해주세요.')
        return redirect(
            reverse('teachers:salary_calculation')
            + f'?year={salary.year}&month={salary.month}'
        )


class SalaryCancelPaidView(LoginRequiredMixin, View):
    def post(self, request, pk):
        salary = get_object_or_404(Salary, pk=pk)
        year, month = salary.year, salary.month
        salary.date_paid = None
        salary.save()
        messages.success(request, f'{salary.teacher.name} {year}년 {month}월 급여 지급이 취소되었습니다.')
        return redirect(
            reverse('teachers:salary_calculation')
            + f'?year={year}&month={month}'
        )


class AttendanceStatsView(LoginRequiredMixin, View):
    """교사별 월별 근무시간 통계 대시보드 (Chart.js)"""
    template_name = 'teachers/attendance_stats.html'

    def get(self, request):
        import json as _json
        current_year = timezone.now().year
        year = int(request.GET.get('year', current_year))

        teachers = Teacher.objects.filter(is_active=True).order_by('name')
        months = list(range(1, 13))
        month_labels = [f"{m}월" for m in months]

        # 교사별 월별 근무시간 집계
        datasets = []
        COLORS = [
            '#6366f1', '#f59e0b', '#10b981', '#ef4444',
            '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6',
        ]
        for idx, teacher in enumerate(teachers):
            monthly_hours = []
            for month in months:
                attendances = Attendance.objects.filter(
                    teacher=teacher, date__year=year, date__month=month, is_present=True
                )
                total = 0
                for a in attendances:
                    if a.start_time and a.end_time:
                        start = datetime.combine(a.date, a.start_time)
                        end = datetime.combine(a.date, a.end_time)
                        total += (end - start).total_seconds() / 3600
                monthly_hours.append(round(total, 1))
            color = COLORS[idx % len(COLORS)]
            datasets.append({
                'label': teacher.name,
                'data': monthly_hours,
                'borderColor': color,
                'backgroundColor': color + '33',
                'tension': 0.3,
                'fill': False,
            })

        # 연간 합계 (교사별)
        summary = []
        for teacher in teachers:
            attendances = Attendance.objects.filter(
                teacher=teacher, date__year=year, is_present=True
            )
            total_hours = 0
            for a in attendances:
                if a.start_time and a.end_time:
                    start = datetime.combine(a.date, a.start_time)
                    end = datetime.combine(a.date, a.end_time)
                    total_hours += (end - start).total_seconds() / 3600
            total_days = Attendance.objects.filter(
                teacher=teacher, date__year=year, is_present=True
            ).count()
            summary.append({
                'teacher': teacher,
                'total_hours': round(total_hours, 1),
                'total_days': total_days,
            })

        context = {
            'year': year,
            'years': range(2020, current_year + 1),
            'month_labels_json': _json.dumps(month_labels, ensure_ascii=False),
            'datasets_json': _json.dumps(datasets, ensure_ascii=False),
            'summary': summary,
        }
        return render(request, self.template_name, context)


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

        # 급여 데이터 실시간 계산
        salary_view = SalaryCalculationView()
        teachers = salary_view.get_active_teachers_for_month(year, month)

        data = [['이름', '기본급', '추가급여', '총 급여']]
        total_base = 0
        total_additional = 0
        total_amount = 0

        for teacher in teachers:
            work_hours, work_days = salary_view.calculate_work_hours(teacher, year, month)
            base_amount = int(work_hours * teacher.base_salary)

            # URL 파라미터로 전달된 추가급여 우선 사용, 없으면 DB에서 가져오기
            param_key = f'additional_{teacher.id}'
            if param_key in request.GET:
                additional_amount = int(request.GET.get(param_key) or 0)
            else:
                try:
                    existing_salary = Salary.objects.get(teacher=teacher, year=year, month=month)
                    additional_amount = existing_salary.additional_amount
                except Salary.DoesNotExist:
                    additional_amount = 0

            row_total = base_amount + additional_amount
            total_base += base_amount
            total_additional += additional_amount
            total_amount += row_total
            data.append([
                teacher.name,
                f"{base_amount:,}원",
                f"{additional_amount:,}원",
                f"{row_total:,}원"
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


class SalarySlipPDFView(LoginRequiredMixin, View):
    """교사 개인 급여 명세서 PDF 생성"""
    def get(self, request, teacher_pk, year, month):
        teacher = get_object_or_404(Teacher, pk=teacher_pk)

        # 실시간 급여 계산
        salary_view = SalaryCalculationView()
        work_hours, work_days = salary_view.calculate_work_hours(teacher, year, month)
        base_amount = int(work_hours * teacher.base_salary)

        # 추가급여: URL 파라미터 우선, 없으면 DB
        param_key = f'additional_{teacher.pk}'
        if param_key in request.GET:
            additional_amount = int(request.GET.get(param_key) or 0)
        else:
            try:
                existing = Salary.objects.get(teacher=teacher, year=year, month=month)
                additional_amount = existing.additional_amount
            except Salary.DoesNotExist:
                additional_amount = 0

        total_amount = base_amount + additional_amount

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=25*mm, leftMargin=25*mm,
            topMargin=25*mm, bottomMargin=20*mm,
            title=f"{year}년 {month}월 급여 명세서 - {teacher.name}",
            author="엠클래스수학과학전문학원",
        )

        def add_footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('NanumGothicBold', 9)
            canvas.drawCentredString(A4[0] / 2, 12 * mm, "엠클래스수학과학전문학원")
            canvas.restoreState()

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='KR', fontName='NanumGothic', fontSize=10, leading=16))
        styles.add(ParagraphStyle(name='KRTitle', fontName='NanumGothicBold', fontSize=17,
                                  leading=22, alignment=1))
        styles.add(ParagraphStyle(name='KRSub', fontName='NanumGothicBold', fontSize=11,
                                  leading=16, alignment=1, textColor=colors.HexColor('#4338ca')))
        styles.add(ParagraphStyle(name='KRLabel', fontName='NanumGothicBold', fontSize=10, leading=16))

        elements = []

        # 제목
        elements.append(Paragraph(f"{year}년 {month}월 급여 명세서", styles['KRTitle']))
        elements.append(Spacer(1, 6*mm))
        elements.append(Paragraph(teacher.name, styles['KRSub']))
        elements.append(Spacer(1, 8*mm))

        # 기본 정보 테이블
        info_data = [
            ['성명', teacher.name, '지급월', f"{year}년 {month}월"],
            ['근무일수', f"{work_days}일", '근무시간', f"{work_hours:.1f}시간"],
            ['시급', f"{teacher.base_salary:,}원", '', ''],
        ]
        info_table = Table(info_data, colWidths=[30*mm, 55*mm, 30*mm, 55*mm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
            ('FONTNAME', (0, 0), (0, -1), 'NanumGothicBold'),
            ('FONTNAME', (2, 0), (2, -1), 'NanumGothicBold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f3f4f6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUND', (0, 2), (-1, 2), colors.white),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 8*mm))

        # 급여 내역 테이블
        pay_data = [
            ['항목', '금액'],
            ['기본급 (시급 × 근무시간)', f"{base_amount:,}원"],
            ['추가급여', f"{additional_amount:,}원"],
        ]
        pay_table = Table(pay_data, colWidths=[100*mm, 70*mm])
        pay_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
            ('FONTNAME', (0, 0), (-1, 0), 'NanumGothicBold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(pay_table)
        elements.append(Spacer(1, 0))

        # 합계 행
        total_data = [['지급 합계', f"{total_amount:,}원"]]
        total_table = Table(total_data, colWidths=[100*mm, 70*mm])
        total_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothicBold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4338ca')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eef2ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e1b4b')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(total_table)

        # 계좌 정보
        elements.append(Spacer(1, 10*mm))
        bank_info = teacher.bank.name if teacher.bank else '-'
        account_data = [
            ['입금 계좌', f"{bank_info}  {teacher.account_number or '-'}"],
        ]
        account_table = Table(account_data, colWidths=[30*mm, 140*mm])
        account_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
            ('FONTNAME', (0, 0), (0, 0), 'NanumGothicBold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f3f4f6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(account_table)

        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
        pdf = buffer.getvalue()
        buffer.close()

        filename = f"{year}년 {month}월 급여명세서_{teacher.name}.pdf"
        encoded_filename = urllib.parse.quote(filename.encode('utf-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
        response.write(pdf)
        return response


class TeacherMyWorkReportPDFView(LoginRequiredMixin, View):
    """교사 자신의 월별 근무 기록 PDF 다운로드"""

    DAY_NAMES = ['월', '화', '수', '목', '금', '토', '일']

    def get(self, request, year, month):
        if not hasattr(request.user, 'teacher_profile'):
            messages.error(request, '교사 계정만 접근 가능합니다.')
            return redirect('teachers:message_list')

        teacher = request.user.teacher_profile

        # 해당 월 출근 기록
        attendances = Attendance.objects.filter(
            teacher=teacher, date__year=year, date__month=month
        ).order_by('date')

        # 근무 시간 계산
        salary_view = SalaryCalculationView()
        work_hours, work_days = salary_view.calculate_work_hours(teacher, year, month)
        base_amount = int(work_hours * teacher.base_salary)

        # 추가급여
        try:
            existing = Salary.objects.get(teacher=teacher, year=year, month=month)
            additional_amount = existing.additional_amount
        except Salary.DoesNotExist:
            additional_amount = 0

        total_amount = base_amount + additional_amount

        # PDF 생성
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=20*mm, leftMargin=20*mm,
            topMargin=20*mm, bottomMargin=30*mm,
            title=f"{year}년 {month}월 근무 기록 - {teacher.name}",
            author="엠클래스수학과학전문학원",
        )

        def add_footer(c, doc):
            c.saveState()
            c.setFont('NanumGothicBold', 9)
            c.drawCentredString(A4[0] / 2, 12 * mm, "엠클래스수학과학전문학원")
            c.restoreState()

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='KR', fontName='NanumGothic', fontSize=10, leading=16))
        styles.add(ParagraphStyle(name='KRTitle', fontName='NanumGothicBold', fontSize=17,
                                  leading=22, alignment=1))
        styles.add(ParagraphStyle(name='KRSub', fontName='NanumGothicBold', fontSize=11,
                                  leading=16, alignment=1, textColor=colors.HexColor('#4338ca')))
        styles.add(ParagraphStyle(name='KRLabel', fontName='NanumGothicBold', fontSize=11, leading=16))

        elements = []

        # 제목
        elements.append(Paragraph(f"{year}년 {month}월 근무 기록", styles['KRTitle']))
        elements.append(Spacer(1, 6*mm))
        elements.append(Paragraph(teacher.name, styles['KRSub']))
        elements.append(Spacer(1, 8*mm))

        # 일별 근무 기록 테이블
        elements.append(Paragraph("일별 근무 기록", styles['KRLabel']))
        elements.append(Spacer(1, 3*mm))

        att_data = [['날짜', '요일', '출근', '퇴근', '근무시간']]
        att_style = [
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
            ('FONTNAME', (0, 0), (-1, 0), 'NanumGothicBold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]

        for i, att in enumerate(attendances, start=1):
            day_name = self.DAY_NAMES[att.date.weekday()]
            start_str = att.start_time.strftime('%H:%M') if att.start_time else '-'
            end_str = att.end_time.strftime('%H:%M') if att.end_time else '-'
            if att.start_time and att.end_time:
                start_dt = datetime.combine(att.date, att.start_time)
                end_dt = datetime.combine(att.date, att.end_time)
                if end_dt < start_dt:
                    end_dt += timedelta(days=1)
                hours = (end_dt - start_dt).total_seconds() / 3600
                hours_str = f"{hours:.1f}시간"
            else:
                hours_str = '-'
            att_data.append([att.date.strftime('%Y-%m-%d'), day_name, start_str, end_str, hours_str])
            # 토/일 요일 색상
            if att.date.weekday() == 5:
                att_style.append(('TEXTCOLOR', (1, i), (1, i), colors.HexColor('#2563eb')))
            elif att.date.weekday() == 6:
                att_style.append(('TEXTCOLOR', (1, i), (1, i), colors.HexColor('#dc2626')))
            # 짝수 행 배경
            if i % 2 == 0:
                att_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9fafb')))

        if len(att_data) == 1:
            att_data.append(['근무 기록 없음', '', '', '', ''])
            att_style.append(('SPAN', (0, 1), (-1, 1)))

        att_table = Table(att_data, colWidths=[40*mm, 18*mm, 32*mm, 32*mm, 38*mm])
        att_table.setStyle(TableStyle(att_style))
        elements.append(att_table)
        elements.append(Spacer(1, 8*mm))

        # 근무 요약
        elements.append(Paragraph("근무 요약", styles['KRLabel']))
        elements.append(Spacer(1, 3*mm))
        summary_data = [
            ['근무일수', f"{work_days}일", '총 근무시간', f"{work_hours:.1f}시간"],
            ['시급', f"{teacher.base_salary:,}원", '', ''],
        ]
        summary_table = Table(summary_data, colWidths=[30*mm, 55*mm, 30*mm, 55*mm])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
            ('FONTNAME', (0, 0), (0, -1), 'NanumGothicBold'),
            ('FONTNAME', (2, 0), (2, -1), 'NanumGothicBold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f3f4f6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 8*mm))

        # 급여 내역
        elements.append(Paragraph("급여 내역", styles['KRLabel']))
        elements.append(Spacer(1, 3*mm))
        pay_data = [
            ['항목', '금액'],
            ['기본급 (시급 × 근무시간)', f"{base_amount:,}원"],
            ['추가급여', f"{additional_amount:,}원"],
        ]
        pay_table = Table(pay_data, colWidths=[100*mm, 70*mm])
        pay_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
            ('FONTNAME', (0, 0), (-1, 0), 'NanumGothicBold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(pay_table)
        elements.append(Spacer(1, 0))

        total_data = [['지급 합계', f"{total_amount:,}원"]]
        total_table = Table(total_data, colWidths=[100*mm, 70*mm])
        total_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothicBold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4338ca')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eef2ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e1b4b')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(total_table)

        # 계좌 정보
        elements.append(Spacer(1, 10*mm))
        bank_info = teacher.bank.name if teacher.bank else '-'
        account_data = [['입금 계좌', f"{bank_info}  {teacher.account_number or '-'}"]]
        account_table = Table(account_data, colWidths=[30*mm, 140*mm])
        account_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
            ('FONTNAME', (0, 0), (0, 0), 'NanumGothicBold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f3f4f6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(account_table)

        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
        pdf = buffer.getvalue()
        buffer.close()

        filename = f"{year}년 {month}월 근무기록_{teacher.name}.pdf"
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

            # 해당 날짜에 출근 불가인 교사들 (승인된 일정만)
            unavailable_records = TeacherUnavailability.objects.filter(
                date=check_date,
                status='approved',  # 승인된 일정만 출근 불가로 표시
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
            today = timezone.now().date()

            # 승인 대기 목록
            pending_unavailabilities = TeacherUnavailability.objects.filter(
                status='pending',
                date__gte=today,
                teacher__is_active=True
            ).select_related('teacher').order_by('date', 'teacher__name')

            # 최근 승인/반려 이력 (최근 30일 이내, 최대 20건)
            from datetime import timedelta
            thirty_days_ago = today - timedelta(days=30)
            review_history = TeacherUnavailability.objects.filter(
                status__in=['approved', 'rejected'],
                reviewed_at__isnull=False,
                reviewed_at__date__gte=thirty_days_ago,
                created_by_admin=False  # 교사가 신청한 것만 (관리자 직접 등록 제외)
            ).select_related('teacher').order_by('-reviewed_at')[:20]

            context = {
                'selected_date': None,
                'upcoming_unavailabilities': TeacherUnavailability.objects.filter(
                    date__gte=today,
                    status='approved',
                    teacher__is_active=True
                ).select_related('teacher').order_by('date', 'teacher__name')[:50],
                'pending_unavailabilities': pending_unavailabilities,
                'pending_count': pending_unavailabilities.count(),
                'review_history': review_history,
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


@login_required
@staff_member_required
def unavailability_approve(request, pk):
    """출근 불가 일정 승인"""
    unavailability = get_object_or_404(TeacherUnavailability, pk=pk)

    if request.method == 'POST':
        unavailability.status = 'approved'
        unavailability.reviewed_at = timezone.now()
        unavailability.save()
        messages.success(request, f'{unavailability.teacher.name} 선생님의 {unavailability.date} 출근 불가 일정이 승인되었습니다.')

    return redirect('teachers:unavailability_list')


@login_required
@staff_member_required
def unavailability_reject(request, pk):
    """출근 불가 일정 반려"""
    unavailability = get_object_or_404(TeacherUnavailability, pk=pk)

    if request.method == 'POST':
        reject_reason = request.POST.get('reject_reason', '').strip()
        unavailability.status = 'rejected'
        unavailability.reviewed_at = timezone.now()
        unavailability.reject_reason = reject_reason
        unavailability.save()
        messages.success(request, f'{unavailability.teacher.name} 선생님의 {unavailability.date} 출근 불가 일정이 반려되었습니다.')

    return redirect('teachers:unavailability_list')


@login_required
@staff_member_required
def unavailability_settings(request):
    """출근 불가 일정 설정 관리 - 차단 날짜만 관리"""
    today = timezone.now().date()

    # 차단 날짜 목록
    blocked_dates = UnavailabilityBlockedDate.objects.filter(date__gte=today).order_by('date')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_blocked_date':
            date_str = request.POST.get('blocked_date', '')
            reason = request.POST.get('blocked_reason', '').strip()

            try:
                blocked_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                if blocked_date < today:
                    messages.error(request, '과거 날짜는 차단할 수 없습니다.')
                elif UnavailabilityBlockedDate.objects.filter(date=blocked_date).exists():
                    messages.warning(request, '이미 차단된 날짜입니다.')
                else:
                    UnavailabilityBlockedDate.objects.create(date=blocked_date, reason=reason)
                    messages.success(request, f'{blocked_date} 날짜가 차단되었습니다.')
            except ValueError:
                messages.error(request, '올바른 날짜 형식이 아닙니다.')

        elif action == 'remove_blocked_date':
            blocked_id = request.POST.get('blocked_id')
            try:
                blocked = UnavailabilityBlockedDate.objects.get(pk=blocked_id)
                date = blocked.date
                blocked.delete()
                messages.success(request, f'{date} 차단이 해제되었습니다.')
            except UnavailabilityBlockedDate.DoesNotExist:
                messages.error(request, '차단 날짜를 찾을 수 없습니다.')

        return redirect('teachers:unavailability_settings')

    context = {
        'blocked_dates': blocked_dates,
        'today': today,
    }
    return render(request, 'teachers/unavailability_settings.html', context)


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
        from django.http import JsonResponse

        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        date = request.POST.get('date')
        teacher_id = request.POST.get('teacher')
        student_ids = request.POST.getlist('students')
        assignment_type = request.POST.get('assignment_type', 'normal')

        # 결석/예외인 경우 teacher_id가 없어도 됨
        if not date or not student_ids:
            if is_ajax:
                return JsonResponse({'success': False, 'error': '필수 정보가 누락되었습니다.'}, status=400)
            messages.error(request, '필수 정보가 누락되었습니다.')
            return redirect('progress:assignment_list')

        if assignment_type == 'normal' and not teacher_id:
            if is_ajax:
                return JsonResponse({'success': False, 'error': '교사를 선택해주세요.'}, status=400)
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

        if is_ajax:
            return JsonResponse({'success': True})

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


@login_required
def assignment_update_absence_reason(request, pk):
    """결석 사유 업데이트"""
    from django.http import JsonResponse

    assignment = get_object_or_404(TeacherStudentAssignment, pk=pk)

    if request.method == 'POST':
        absence_reason = request.POST.get('absence_reason', '')

        # 유효한 사유인지 확인
        valid_reasons = ['', 'sick', 'family', 'personal', 'other']
        if absence_reason in valid_reasons:
            assignment.absence_reason = absence_reason
            assignment.save()

            # AJAX 요청인 경우 JSON 응답
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'absence_reason': absence_reason,
                    'absence_reason_display': assignment.get_absence_reason_display()
                })

            messages.success(request, f'{assignment.student.name} 학생의 결석 사유가 변경되었습니다.')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': '유효하지 않은 결석 사유입니다.'}, status=400)

    return redirect(f"/progress/assignment/?date={assignment.date.strftime('%Y-%m-%d')}")


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
                # 학생에게 지급된 교재들 (학습 완료 제외)
                book_sales = BookSale.objects.filter(student=student, is_learning_completed=False).select_related('book')

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
            'students_with_books': sum(1 for sd in student_data if sd['books']),
        }

        return render(request, 'teachers/teacher_progress.html', context)


class DailyProgressSummaryView(LoginRequiredMixin, View):
    """관리자용 일별 전체 수업 기록 조회"""

    def get_chapter_progress(self, book_sale):
        """교재의 대단원별 진행 상황 분석"""
        from bookstore.models import BookContent
        from django.db.models import Count, Q

        book = book_sale.book
        chapters = {}

        # 대단원별 전체 항목 수
        chapter_totals = BookContent.objects.filter(book=book).values(
            'chapter_num', 'chapter_title'
        ).annotate(total=Count('id'))

        for ch in chapter_totals:
            chapters[ch['chapter_num']] = {
                'title': ch['chapter_title'],
                'total': ch['total'],
                'completed': 0,
            }

        # 대단원별 완료 항목 수
        completed_records = book_sale.progress_records.filter(
            study_date__isnull=False
        ).exclude(achievement='').select_related('book_content')

        for record in completed_records:
            ch_num = record.book_content.chapter_num
            if ch_num in chapters:
                chapters[ch_num]['completed'] += 1

        # 마무리 중인 대단원 (80% 이상 완료)
        finishing_chapters = []
        for ch_num, ch_data in chapters.items():
            if ch_data['total'] > 0:
                progress = ch_data['completed'] / ch_data['total']
                if progress >= 0.8 and progress < 1.0:
                    finishing_chapters.append({
                        'chapter_num': ch_num,
                        'title': ch_data['title'],
                        'completed': ch_data['completed'],
                        'total': ch_data['total'],
                        'progress': int(progress * 100),
                    })

        return finishing_chapters

    def get_section_progress(self, book_sale):
        """교재의 중단원별 진행 상황 분석"""
        from bookstore.models import BookContent
        from django.db.models import Count

        book = book_sale.book
        sections = {}

        # 중단원별 전체 항목 수 (대단원+중단원 조합으로 그룹화)
        section_totals = BookContent.objects.filter(book=book).values(
            'chapter_num', 'chapter_title', 'section_num', 'section_title'
        ).annotate(total=Count('id'))

        for sec in section_totals:
            key = (sec['chapter_num'], sec['section_num'])
            sections[key] = {
                'chapter_num': sec['chapter_num'],
                'chapter_title': sec['chapter_title'],
                'section_num': sec['section_num'],
                'section_title': sec['section_title'],
                'total': sec['total'],
                'completed': 0,
            }

        # 중단원별 완료 항목 수
        completed_records = book_sale.progress_records.filter(
            study_date__isnull=False
        ).exclude(achievement='').select_related('book_content')

        for record in completed_records:
            key = (record.book_content.chapter_num, record.book_content.section_num)
            if key in sections:
                sections[key]['completed'] += 1

        # 마무리 중인 중단원 (80% 이상 완료)
        finishing_sections = []
        for key, sec_data in sections.items():
            if sec_data['total'] > 0:
                progress = sec_data['completed'] / sec_data['total']
                if progress >= 0.8 and progress < 1.0:
                    finishing_sections.append({
                        'chapter_num': sec_data['chapter_num'],
                        'chapter_title': sec_data['chapter_title'],
                        'section_num': sec_data['section_num'],
                        'section_title': sec_data['section_title'],
                        'completed': sec_data['completed'],
                        'total': sec_data['total'],
                        'progress': int(progress * 100),
                    })

        return finishing_sections

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

        # 알림 목록 수집
        homework_not_done_list = []  # 과제 미수행 학생
        needs_review_list = []  # 보완 추천 대상
        chapter_finishing_list = []  # 대단원 마무리 중인 학생
        section_finishing_list = []  # 중단원 마무리 중인 학생

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

            # 학생의 교재별 진도 정보 (학습 완료 처리된 교재 제외)
            book_sales = BookSale.objects.filter(student=student, is_learning_completed=False).select_related('book')
            books_progress = []

            for sale in book_sales:
                if sale.book.contents.exists():
                    # 오늘 날짜로 기록된 진도 항목 수
                    today_records = sale.progress_records.filter(study_date=check_date).count()
                    stats = sale.get_progress_stats()

                    # 과제 미수행 항목 (학습 완료했지만 과제 미수행)
                    homework_pending = sale.progress_records.filter(
                        study_date__isnull=False,
                        homework_done=False
                    ).exclude(achievement='').select_related('book_content')

                    for record in homework_pending:
                        homework_not_done_list.append({
                            'student': student,
                            'teacher': teacher,
                            'book': sale.book,
                            'content': record.book_content,
                            'study_date': record.study_date,
                        })

                    # 보완 추천 항목
                    review_items = sale.progress_records.filter(
                        needs_review=True
                    ).select_related('book_content')

                    for record in review_items:
                        needs_review_list.append({
                            'student': student,
                            'teacher': teacher,
                            'book': sale.book,
                            'sale': sale,
                            'content': record.book_content,
                            'achievement': record.achievement,
                        })

                    # 대단원 마무리 중인 항목
                    finishing_chapters = self.get_chapter_progress(sale)
                    for ch in finishing_chapters:
                        chapter_finishing_list.append({
                            'student': student,
                            'teacher': teacher,
                            'book': sale.book,
                            'chapter_num': ch['chapter_num'],
                            'chapter_title': ch['title'],
                            'progress': ch['progress'],
                            'completed': ch['completed'],
                            'total': ch['total'],
                        })

                    # 중단원 마무리 중인 항목
                    finishing_sections = self.get_section_progress(sale)
                    for sec in finishing_sections:
                        section_finishing_list.append({
                            'student': student,
                            'teacher': teacher,
                            'book': sale.book,
                            'chapter_num': sec['chapter_num'],
                            'chapter_title': sec['chapter_title'],
                            'section_num': sec['section_num'],
                            'section_title': sec['section_title'],
                            'progress': sec['progress'],
                            'completed': sec['completed'],
                            'total': sec['total'],
                        })

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

        # 원장 배정 학생 상세 정보 (교재 진도 포함, 학습 완료 제외)
        director_student_list = []
        for assignment in director_assignments:
            student = assignment.student
            book_sales = BookSale.objects.filter(student=student, is_learning_completed=False).select_related('book')
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
            director_student_list.append({
                'student': student,
                'assignment': assignment,
                'books': books_progress,
            })
        director_student_list.sort(key=lambda x: x['student'].name)

        # 통계
        total_assigned = all_assignments.filter(assignment_type='normal').count()
        total_absent = absent_assignments.count()
        total_exception = exception_assignments.count()
        total_director = director_assignments.count()

        # 오늘 기록된 총 진도 평가 수 (LearningRecord 사용)
        from progress.models import LearningRecord
        total_progress_today = LearningRecord.objects.filter(date=check_date, record_type='textbook').count()

        # 오늘의 수업 활동 조회 (LearningRecord 사용, 교재 진도 제외)
        activities = LearningRecord.objects.filter(
            date=check_date
        ).exclude(record_type='textbook').select_related('student', 'teacher', 'subject').order_by('-created_at')
        total_activities = activities.count()

        # 학생 기준 데이터 구성
        student_list = []
        for assignment in all_assignments:
            if assignment.assignment_type != 'normal':
                continue

            student = assignment.student
            teacher = assignment.teacher

            # 학생의 교재별 진도 정보 (학습 완료 제외)
            book_sales = BookSale.objects.filter(student=student, is_learning_completed=False).select_related('book')
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
            'director_student_list': director_student_list,
            'total_assigned': total_assigned,
            'total_absent': total_absent,
            'total_exception': total_exception,
            'total_director': total_director,
            'total_progress_today': total_progress_today,
            'view_mode': view_mode,
            # 알림 목록 추가
            'homework_not_done_list': homework_not_done_list,
            'needs_review_list': needs_review_list,
            'chapter_finishing_list': chapter_finishing_list,
            'section_finishing_list': section_finishing_list,
            # 수업 활동
            'activities': activities,
            'total_activities': total_activities,
        }

        return render(request, 'teachers/daily_progress_summary.html', context)


class StudentClassDashboardView(LoginRequiredMixin, View):
    """날짜 무관한 전체 학생 수업 현황 대시보드"""

    def get(self, request):
        from students.models import Student
        from bookstore.models import BookSale

        # 모든 활성 학생
        students = Student.objects.filter(is_active=True).select_related('school')

        student_list = []
        for student in students:
            # 교재별 진도 (목차가 있는 것만, 학습 완료 제외)
            book_sales = BookSale.objects.filter(student=student, is_learning_completed=False).select_related('book')
            books_progress = []
            for sale in book_sales:
                if sale.book.contents.exists():
                    stats = sale.get_progress_stats()
                    last_record = sale.progress_records.filter(
                        study_date__isnull=False
                    ).order_by('-study_date').first()
                    books_progress.append({
                        'sale': sale,
                        'book': sale.book,
                        'stats': stats,
                        'last_study_date': last_record.study_date if last_record else None,
                    })

            student_list.append({
                'student': student,
                'books': books_progress,
            })

        # 학년 순 정렬 (K5→K12), 학년 없는 학생은 맨 뒤, 동일 학년은 이름 순
        def grade_sort_key(item):
            grade = item['student'].grade
            if grade and grade.startswith('K'):
                try:
                    return (int(grade[1:]), item['student'].name)
                except ValueError:
                    pass
            return (99, item['student'].name)

        student_list.sort(key=grade_sort_key)

        context = {
            'student_list': student_list,
            'total_students': len(student_list),
        }
        return render(request, 'teachers/student_class_dashboard.html', context)


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
                return redirect('teachers:message_list')
            # 관리자 또는 일반 사용자는 메인 대시보드로
            return redirect('index')
        return render(request, 'teachers/teacher_login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # 교사 프로필이 있으면 전체 공지 페이지로
            if hasattr(user, 'teacher_profile'):
                messages.success(request, f'{user.teacher_profile.name} 선생님, 환영합니다!')
                return redirect('teachers:message_list')
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
    """교사 자신의 배정 학생 진도 관리 페이지 (LearningRecord 사용)"""

    def get(self, request):
        from bookstore.models import BookSale, StudentBookProgress
        from progress.models import LearningRecord

        # 현재 로그인한 사용자의 교사 프로필 확인
        if not hasattr(request.user, 'teacher_profile'):
            # 관리자(staff)는 관리자 대시보드로, 일반 사용자도 대시보드로
            if request.user.is_staff:
                return redirect('progress:dashboard')
            else:
                messages.error(request, '교사 계정이 아닙니다.')
                return redirect('progress:dashboard')

        teacher = request.user.teacher_profile

        # 반려된 출근 불가 일정 알림 (읽지 않은 것만)
        rejected_unavailabilities = TeacherUnavailability.objects.filter(
            teacher=teacher,
            status='rejected',
            reject_notified=False  # 아직 알림을 보지 않은 것
        ).order_by('-reviewed_at')

        if rejected_unavailabilities.exists():
            for unavail in rejected_unavailabilities:
                reject_reason = unavail.reject_reason or '사유 없음'
                messages.warning(
                    request,
                    f'⚠️ {unavail.date.strftime("%Y-%m-%d")} 출근 불가 일정이 반려되었습니다. (사유: {reject_reason})'
                )
            # 알림 표시 완료 처리
            rejected_unavailabilities.update(reject_notified=True)

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

        # 각 학생별 교재 진도 정보 수집 (학습 완료 제외)
        student_data = []
        for assignment in assignments:
            student = assignment.student
            book_sales = BookSale.objects.filter(student=student, is_learning_completed=False).select_related('book')

            books_data = []
            for sale in book_sales:
                if sale.book.contents.exists():
                    stats = sale.get_progress_stats()
                    books_data.append({
                        'sale': sale,
                        'book': sale.book,
                        'stats': stats,
                    })

            # 해당 학생에 대한 지시사항 메시지 조회
            student_messages = Message.objects.filter(
                student=student,
                message_type='instruction'
            ).order_by('-created_at')[:3]

            # 해당 학생의 오늘 수업 활동 조회 (LearningRecord 사용, 교재 진도 제외)
            student_activities = LearningRecord.objects.filter(
                student=student,
                date=check_date
            ).exclude(record_type='textbook').select_related('subject')

            student_data.append({
                'student': student,
                'assignment': assignment,
                'books': books_data,
                'messages': student_messages,
                'activities': student_activities,
            })

        # 오늘 이 교사의 전체 수업 활동 조회 (LearningRecord 사용, 교재 진도 제외)
        my_activities = LearningRecord.objects.filter(
            teacher=teacher,
            date=check_date
        ).exclude(record_type='textbook').select_related('student', 'subject')

        context = {
            'selected_date': check_date,
            'teacher': teacher,
            'student_data': student_data,
            'my_activities': my_activities,
            'total_activities': my_activities.count(),
            'students_with_books': sum(1 for sd in student_data if sd['books']),
            'is_my_page': True,  # 자신의 페이지임을 표시
        }

        return render(request, 'teachers/teacher_my_progress.html', context)


@login_required
def teacher_activity_create(request):
    """교사 자신의 수업 활동 생성 (LearningRecord 사용)"""
    from progress.models import LearningRecord
    from progress.forms import LearningRecordForm
    from students.models import Student

    # 교사 계정 확인
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, '교사 계정만 이용할 수 있습니다.')
        return redirect('progress:my_progress')

    teacher = request.user.teacher_profile

    # 날짜 파라미터 확인
    date_str = request.GET.get('date') or request.POST.get('date')
    if date_str:
        try:
            initial_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            initial_date = timezone.now().date()
    else:
        initial_date = timezone.now().date()

    # 해당 날짜에 이 교사에게 배정된 학생들만 선택 가능
    assigned_student_ids = TeacherStudentAssignment.objects.filter(
        teacher=teacher,
        date=initial_date
    ).values_list('student_id', flat=True)

    students = Student.objects.filter(
        id__in=assigned_student_ids,
        is_active=True
    ).select_related('school').order_by('name')

    if request.method == 'POST':
        form = LearningRecordForm(request.POST, initial_date=initial_date, students=students, hide_student_id=True)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.teacher = teacher  # 자동으로 현재 교사 설정
            activity.save()
            messages.success(request, f"'{activity.title}' 수업 활동이 등록되었습니다.")

            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(f'/progress/my/?date={initial_date.strftime("%Y-%m-%d")}')
    else:
        form = LearningRecordForm(initial_date=initial_date, students=students, hide_student_id=True)
        # 교사 필드 초기값 설정 및 숨김
        form.initial['teacher'] = teacher

    return render(request, 'teachers/teacher_activity_form.html', {
        'form': form,
        'title': '수업 활동 추가',
        'selected_date': initial_date,
        'teacher': teacher,
    })


@login_required
def teacher_activity_update(request, pk):
    """교사 자신의 수업 활동 수정 (LearningRecord 사용)"""
    from progress.models import LearningRecord
    from progress.forms import LearningRecordForm

    # 교사 계정 확인
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, '교사 계정만 이용할 수 있습니다.')
        return redirect('progress:my_progress')

    teacher = request.user.teacher_profile
    # LearningRecord에서 조회 (수업 활동: textbook 제외)
    activity = get_object_or_404(LearningRecord, pk=pk)

    # 교재 진도 기록은 이 뷰에서 수정 불가
    if activity.record_type == 'textbook':
        messages.error(request, '교재 진도 기록은 진도 평가 페이지에서 수정해주세요.')
        return redirect('progress:my_progress')

    # 자신이 등록한 활동만 수정 가능
    if activity.teacher != teacher:
        messages.error(request, '자신이 등록한 수업 활동만 수정할 수 있습니다.')
        return redirect('progress:my_progress')

    if request.method == 'POST':
        form = LearningRecordForm(request.POST, instance=activity, hide_student_id=True)
        if form.is_valid():
            activity = form.save()
            messages.success(request, f"'{activity.title}' 수업 활동이 수정되었습니다.")

            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(f'/progress/my/?date={activity.date.strftime("%Y-%m-%d")}')
    else:
        form = LearningRecordForm(instance=activity, hide_student_id=True)

    return render(request, 'teachers/teacher_activity_form.html', {
        'form': form,
        'activity': activity,
        'title': '수업 활동 수정',
        'selected_date': activity.date,
        'teacher': teacher,
    })


@login_required
def teacher_activity_delete(request, pk):
    """교사 자신의 수업 활동 삭제 (LearningRecord 사용)"""
    from progress.models import LearningRecord

    # 교사 계정 확인
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, '교사 계정만 이용할 수 있습니다.')
        return redirect('progress:my_progress')

    teacher = request.user.teacher_profile
    # LearningRecord에서 조회
    activity = get_object_or_404(LearningRecord, pk=pk)

    # 교재 진도 기록은 삭제 불가
    if activity.record_type == 'textbook':
        messages.error(request, '교재 진도 기록은 삭제할 수 없습니다.')
        return redirect('progress:my_progress')

    # 자신이 등록한 활동만 삭제 가능
    if activity.teacher != teacher:
        messages.error(request, '자신이 등록한 수업 활동만 삭제할 수 있습니다.')
        return redirect('progress:my_progress')

    if request.method == 'POST':
        date = activity.date
        title = activity.title
        activity.delete()
        messages.success(request, f"'{title}' 수업 활동이 삭제되었습니다.")

        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(f'/progress/my/?date={date.strftime("%Y-%m-%d")}')

    return redirect('progress:my_progress')


class TeacherMyUnavailabilityView(LoginRequiredMixin, View):
    """교사 자신의 출근 불가 일정 관리"""

    def get(self, request):
        # 교사 계정 확인
        if not hasattr(request.user, 'teacher_profile'):
            messages.error(request, '교사 계정만 이용할 수 있습니다.')
            return redirect('index')

        teacher = request.user.teacher_profile
        today = timezone.now().date()

        # 오늘 이후의 출근 불가 일정 조회
        unavailabilities = TeacherUnavailability.objects.filter(
            teacher=teacher,
            date__gte=today
        ).order_by('date')

        # 과거 일정 (최근 30일)
        past_unavailabilities = TeacherUnavailability.objects.filter(
            teacher=teacher,
            date__lt=today,
            date__gte=today - timedelta(days=30)
        ).order_by('-date')

        context = {
            'unavailabilities': unavailabilities,
            'past_unavailabilities': past_unavailabilities,
            'today': today,
        }
        return render(request, 'teachers/teacher_my_unavailability.html', context)


@login_required
def teacher_my_unavailability_create(request):
    """교사 자신의 출근 불가 일정 등록"""
    # 교사 계정 확인
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, '교사 계정만 이용할 수 있습니다.')
        return redirect('index')

    teacher = request.user.teacher_profile
    today = timezone.now().date()

    # 차단된 날짜 목록
    blocked_dates = list(UnavailabilityBlockedDate.objects.filter(
        date__gte=today
    ).values_list('date', flat=True))

    if request.method == 'POST':
        date_str = request.POST.get('date', '')
        reason = request.POST.get('reason', 'personal')
        memo = request.POST.get('memo', '').strip()

        try:
            unavail_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, '올바른 날짜 형식이 아닙니다.')
            return redirect('teachers:teacher_my_unavailability')

        # 과거 날짜 등록 불가
        if unavail_date < today:
            messages.error(request, '과거 날짜에는 출근 불가 일정을 등록할 수 없습니다.')
            return redirect('teachers:teacher_my_unavailability')

        # 차단된 날짜 확인
        if unavail_date in blocked_dates:
            blocked = UnavailabilityBlockedDate.objects.filter(date=unavail_date).first()
            reason_text = f" ({blocked.reason})" if blocked and blocked.reason else ""
            messages.error(request, f'{unavail_date} 날짜는 출근 불가 등록이 차단되어 있습니다{reason_text}.')
            return redirect('teachers:teacher_my_unavailability')

        # 중복 확인
        if TeacherUnavailability.objects.filter(teacher=teacher, date=unavail_date).exists():
            messages.warning(request, f'{unavail_date} 날짜에 이미 출근 불가 일정이 등록되어 있습니다.')
            return redirect('teachers:teacher_my_unavailability')

        # 교사별 월간 최대 등록 가능 일수 확인 (설정된 경우에만)
        if teacher.max_unavailability_per_month:
            month_start = unavail_date.replace(day=1)
            if unavail_date.month == 12:
                month_end = unavail_date.replace(year=unavail_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = unavail_date.replace(month=unavail_date.month + 1, day=1) - timedelta(days=1)

            month_count = TeacherUnavailability.objects.filter(
                teacher=teacher,
                date__gte=month_start,
                date__lte=month_end,
                status__in=['pending', 'approved']
            ).count()

            if month_count >= teacher.max_unavailability_per_month:
                messages.error(request, f'{unavail_date.month}월에는 이미 최대 {teacher.max_unavailability_per_month}일의 출근 불가 일정이 등록되어 있습니다.')
                return redirect('teachers:teacher_my_unavailability')

        # 교사가 등록한 일정은 항상 승인 대기 상태
        TeacherUnavailability.objects.create(
            teacher=teacher,
            date=unavail_date,
            reason=reason,
            memo=memo,
            status='pending',
            created_by_admin=False
        )

        messages.success(request, f'{unavail_date} 출근 불가 일정이 등록되었습니다. 관리자 승인 후 적용됩니다.')
        return redirect('teachers:teacher_my_unavailability')

    # GET 요청 시 폼 페이지
    # 이번 달 등록 현황 계산
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    month_count = TeacherUnavailability.objects.filter(
        teacher=teacher,
        date__gte=month_start,
        date__lte=month_end,
        status__in=['pending', 'approved']
    ).count()

    # 교사별 제한 (없으면 무제한)
    max_days = teacher.max_unavailability_per_month
    if max_days:
        remaining_count = max(0, max_days - month_count)
    else:
        remaining_count = None  # None이면 무제한

    # 차단 날짜 정보 (날짜와 사유 포함)
    blocked_dates_info = {}
    for blocked in UnavailabilityBlockedDate.objects.filter(date__gte=today):
        blocked_dates_info[blocked.date.strftime('%Y-%m-%d')] = blocked.reason or '등록 불가'

    context = {
        'today': today,
        'reason_choices': TeacherUnavailability.REASON_CHOICES,
        'blocked_dates_info': blocked_dates_info,
        'teacher': teacher,
        'remaining_count': remaining_count,
        'month_count': month_count,
        'max_days': max_days,
    }
    return render(request, 'teachers/teacher_my_unavailability_form.html', context)


@login_required
def teacher_my_unavailability_delete(request, pk):
    """교사 자신의 출근 불가 일정 삭제 (승인 대기 상태만 가능)"""
    # 교사 계정 확인
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, '교사 계정만 이용할 수 있습니다.')
        return redirect('index')

    teacher = request.user.teacher_profile
    today = timezone.now().date()

    unavailability = get_object_or_404(TeacherUnavailability, pk=pk, teacher=teacher)

    # 과거 일정 삭제 불가
    if unavailability.date < today:
        messages.error(request, '과거 일정은 삭제할 수 없습니다.')
        return redirect('teachers:teacher_my_unavailability')

    # 승인 대기 상태만 삭제 가능 (승인/반려된 일정은 이력 보존)
    if unavailability.status != 'pending':
        messages.error(request, '승인 또는 반려된 일정은 삭제할 수 없습니다.')
        return redirect('teachers:teacher_my_unavailability')

    if request.method == 'POST':
        date = unavailability.date
        unavailability.delete()
        messages.success(request, f'{date} 출근 불가 신청이 취소되었습니다.')

    return redirect('teachers:teacher_my_unavailability')


@login_required
@staff_member_required
def teacher_account_create(request, pk):
    """교사에게 로그인 계정 생성 (관리자용) - 임시 비밀번호 자동 생성"""
    import secrets
    import string

    teacher = get_object_or_404(Teacher, pk=pk)

    if teacher.user:
        messages.warning(request, f'{teacher.name} 선생님은 이미 계정이 있습니다.')
        return redirect('teachers:teacher_detail', pk=pk)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()

        # 유효성 검사
        if not username:
            messages.error(request, '사용자명을 입력해주세요.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, '이미 사용 중인 사용자명입니다.')
        else:
            # 임시 비밀번호 생성 (숫자 4자리)
            temp_password = ''.join(secrets.choice(string.digits) for _ in range(4))

            # 계정 생성
            user = User.objects.create_user(
                username=username,
                password=temp_password,
                first_name=teacher.name,
                email=teacher.email or ''
            )
            teacher.user = user
            teacher.save()

            # 생성 완료 후 임시 비밀번호를 한 번만 표시
            return render(request, 'teachers/teacher_account_create.html', {
                'teacher': teacher,
                'temp_password': temp_password,
                'created_username': username,
                'account_created': True,
            })

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
@staff_member_required
def teacher_password_reset(request, pk):
    """교사 비밀번호 재설정 (관리자용) - 임시 비밀번호 자동 생성"""
    import secrets
    import string

    teacher = get_object_or_404(Teacher, pk=pk)

    if not teacher.user:
        messages.warning(request, f'{teacher.name} 선생님은 계정이 없습니다.')
        return redirect('teachers:teacher_detail', pk=pk)

    temp_password = None

    if request.method == 'POST':
        # 임시 비밀번호 생성 (숫자 4자리)
        temp_password = ''.join(secrets.choice(string.digits) for _ in range(4))

        teacher.user.set_password(temp_password)
        teacher.user.save()

        # 비밀번호를 템플릿에 한 번만 표시
        return render(request, 'teachers/teacher_password_reset.html', {
            'teacher': teacher,
            'temp_password': temp_password,
            'password_reset_success': True,
        })

    return render(request, 'teachers/teacher_password_reset.html', {'teacher': teacher})


@login_required
def teacher_password_change(request):
    """교사 자신의 비밀번호 변경"""
    user = request.user

    # 교사 계정인지 확인
    if not hasattr(user, 'teacher_profile'):
        messages.error(request, '교사 계정만 이용할 수 있습니다.')
        return redirect('index')

    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        new_password_confirm = request.POST.get('new_password_confirm', '')

        # 현재 비밀번호 확인
        if not user.check_password(current_password):
            messages.error(request, '현재 비밀번호가 일치하지 않습니다.')
        elif len(new_password) < 4:
            messages.error(request, '새 비밀번호는 4자 이상이어야 합니다.')
        elif new_password != new_password_confirm:
            messages.error(request, '새 비밀번호가 일치하지 않습니다.')
        elif current_password == new_password:
            messages.error(request, '새 비밀번호는 현재 비밀번호와 달라야 합니다.')
        else:
            user.set_password(new_password)
            user.save()
            # 비밀번호 변경 후 다시 로그인
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, '비밀번호가 변경되었습니다.')
            return redirect('progress:my_progress')

    return render(request, 'teachers/teacher_password_change.html')


# ==================== 메시지 관리 ====================

class MessageListView(LoginRequiredMixin, View):
    """메시지 목록 조회"""

    def get(self, request):
        user = request.user
        is_teacher = hasattr(user, 'teacher_profile')

        # 받은 메시지 (개인 + 전체 공지)
        received_messages = list(Message.objects.filter(
            models.Q(recipient=user) | models.Q(recipient__isnull=True)
        ).exclude(sender=user).order_by('-created_at'))

        # 전체 공지(recipient=None)의 읽음 상태를 MessageReadStatus에서 확인
        global_notice_ids = [m.pk for m in received_messages if m.recipient is None]
        read_global_ids = set(MessageReadStatus.objects.filter(
            user=user,
            message_id__in=global_notice_ids
        ).values_list('message_id', flat=True))

        # 각 메시지에 사용자별 읽음 상태 추가
        unread_count = 0
        for message in received_messages:
            if message.recipient is None:
                # 전체 공지는 MessageReadStatus로 확인
                message.is_read_by_user = message.pk in read_global_ids
            else:
                # 개인 메시지는 기존 is_read 필드 사용
                message.is_read_by_user = message.is_read

            if not message.is_read_by_user:
                unread_count += 1

        # 보낸 메시지
        sent_messages = Message.objects.filter(sender=user).order_by('-created_at')

        # 탭 선택
        tab = request.GET.get('tab', 'received')

        context = {
            'received_messages': received_messages,
            'sent_messages': sent_messages,
            'unread_count': unread_count,
            'tab': tab,
            'is_teacher': is_teacher,
        }

        return render(request, 'teachers/message_list.html', context)


class MessageDetailView(LoginRequiredMixin, View):
    """메시지 상세 조회"""

    def get(self, request, pk):
        message = get_object_or_404(Message, pk=pk)
        user = request.user

        # 권한 확인
        has_permission = False

        # 1. 발신자는 항상 볼 수 있음
        if message.sender == user:
            has_permission = True
        # 2. 수신자는 볼 수 있음
        elif message.recipient == user:
            has_permission = True
        # 3. 전체 공지(recipient=None)는 모두 볼 수 있음
        elif message.recipient is None:
            has_permission = True
        # 4. 학생 관련 메시지는 해당 학생을 담당하는 교사도 볼 수 있음
        elif message.student and hasattr(user, 'teacher_profile'):
            today = timezone.now().date()
            is_assigned = TeacherStudentAssignment.objects.filter(
                teacher=user.teacher_profile,
                student=message.student,
                date=today,
                assignment_type='normal'
            ).exists()
            if is_assigned:
                has_permission = True

        if not has_permission:
            messages.error(request, '접근 권한이 없습니다.')
            return redirect('teachers:message_list')

        # 읽음 처리
        if message.recipient == user and not message.is_read:
            # 특정 수신자가 있는 메시지는 기존 방식으로 처리
            message.is_read = True
            message.save()
        elif message.recipient is None:
            # 전체 공지는 MessageReadStatus로 읽음 상태 기록
            MessageReadStatus.objects.get_or_create(
                message=message,
                user=user
            )

        # 답변 목록
        replies = message.replies.all().order_by('created_at')

        context = {
            'message': message,
            'replies': replies,
        }

        return render(request, 'teachers/message_detail.html', context)


class MessageCreateView(LoginRequiredMixin, View):
    """메시지 작성 (원장 → 교사 지시사항)"""

    def get(self, request):
        from students.models import Student

        # 관리자(is_staff)만 지시사항 작성 가능
        if not request.user.is_staff:
            messages.error(request, '지시사항 작성 권한이 없습니다.')
            return redirect('teachers:message_list')

        # 교사 목록
        teachers = Teacher.objects.filter(is_active=True, user__isnull=False).order_by('name')

        # 학생 목록
        students = Student.objects.filter(is_active=True).order_by('name')

        # 미리 선택된 교사/학생 (URL 파라미터)
        selected_teacher_id = request.GET.get('teacher')
        selected_student_id = request.GET.get('student')

        context = {
            'teachers': teachers,
            'students': students,
            'selected_teacher_id': int(selected_teacher_id) if selected_teacher_id else None,
            'selected_student_id': int(selected_student_id) if selected_student_id else None,
        }

        return render(request, 'teachers/message_form.html', context)

    def post(self, request):
        if not request.user.is_staff:
            messages.error(request, '지시사항 작성 권한이 없습니다.')
            return redirect('teachers:message_list')

        recipient_id = request.POST.get('recipient')
        student_id = request.POST.get('student')
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if not title or not content:
            messages.error(request, '제목과 내용을 입력해주세요.')
            return redirect('teachers:message_create')

        # 수신자 (비워두면 전체 공지)
        recipient = None
        if recipient_id:
            recipient = get_object_or_404(User, pk=recipient_id)

        # 관련 학생
        student = None
        if student_id:
            from students.models import Student
            student = get_object_or_404(Student, pk=student_id)

        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            student=student,
            message_type='instruction',
            title=title,
            content=content,
        )

        if recipient:
            messages.success(request, f'{recipient.teacher_profile.name if hasattr(recipient, "teacher_profile") else recipient.username} 님에게 메시지를 보냈습니다.')
        else:
            messages.success(request, '전체 공지가 등록되었습니다.')

        return redirect('teachers:message_list')


class MessageReplyView(LoginRequiredMixin, View):
    """메시지 답변 작성"""

    def post(self, request, pk):
        parent_message = get_object_or_404(Message, pk=pk)
        content = request.POST.get('content', '').strip()

        if not content:
            messages.error(request, '답변 내용을 입력해주세요.')
            return redirect('teachers:message_detail', pk=pk)

        # 답변 생성
        Message.objects.create(
            sender=request.user,
            recipient=parent_message.sender,  # 원본 메시지 보낸 사람에게
            student=parent_message.student,
            message_type='reply',
            parent=parent_message,
            title=f'Re: {parent_message.title}',
            content=content,
        )

        messages.success(request, '답변이 등록되었습니다.')
        return redirect('teachers:message_detail', pk=pk)


@login_required
def message_delete(request, pk):
    """메시지 삭제"""
    message = get_object_or_404(Message, pk=pk)

    # 본인이 보낸 메시지만 삭제 가능
    if message.sender != request.user:
        messages.error(request, '삭제 권한이 없습니다.')
        return redirect('teachers:message_list')

    if request.method == 'POST':
        message.delete()
        messages.success(request, '메시지가 삭제되었습니다.')
        return redirect('teachers:message_list')

    return render(request, 'teachers/message_confirm_delete.html', {'message': message})


@login_required
def message_mark_read(request):
    """메시지 일괄 읽음 처리"""
    if request.method == 'POST':
        user = request.user

        # 개인 메시지 읽음 처리 (기존 방식)
        Message.objects.filter(recipient=user).exclude(sender=user).update(is_read=True)

        # 전체 공지 읽음 처리 (MessageReadStatus 생성)
        global_notices = Message.objects.filter(
            recipient__isnull=True
        ).exclude(sender=user)

        for notice in global_notices:
            MessageReadStatus.objects.get_or_create(
                message=notice,
                user=user
            )

        messages.success(request, '모든 메시지를 읽음 처리했습니다.')

    return redirect('teachers:message_list')


@login_required
def message_dismiss(request, pk):
    """메시지 알림 닫기 (배너에서 X 버튼 클릭 시)"""
    from django.http import JsonResponse

    if request.method == 'POST':
        message = get_object_or_404(Message, pk=pk)
        user = request.user

        # MessageReadStatus 생성 또는 업데이트
        status, created = MessageReadStatus.objects.get_or_create(
            message=message,
            user=user,
            defaults={'dismissed': True}
        )
        if not created:
            status.dismissed = True
            status.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)


@login_required
def teacher_shared_drive(request):
    """교사용 공유자료 Google Drive 뷰"""
    from common.services import GoogleDriveService

    teacher = getattr(request.user, 'teacher_profile', None)
    teacher_email = teacher.email if teacher else None

    drive_service = GoogleDriveService()

    context = {
        'teacher': teacher,
        'teacher_email': teacher_email,
        'is_available': drive_service.is_available(),
        'shared_folder_link': None,
        'folders': [],
        'files': [],
        'error': None,
    }

    if not drive_service.is_available():
        context['error'] = 'Google Drive 서비스를 현재 사용할 수 없습니다. 관리자에게 문의하세요.'
        return render(request, 'teachers/teacher_shared_drive.html', context)

    # '공유자료' 폴더 찾기
    shared_folder_id = drive_service.find_folder('공유자료')
    if not shared_folder_id:
        context['error'] = '공유자료 폴더를 찾을 수 없습니다. 관리자가 먼저 구글 드라이브 폴더 구조를 생성해야 합니다.'
        return render(request, 'teachers/teacher_shared_drive.html', context)

    # Google Drive webViewLink 가져오기
    folder_info = drive_service.get_file_info(shared_folder_id)
    if folder_info:
        context['shared_folder_link'] = folder_info.get('webViewLink')

    # 교사 이메일로 공유자료 폴더 자동 공유 (reader 권한, 알림 이메일 없음)
    if teacher_email:
        drive_service.share_with_user(shared_folder_id, teacher_email, role='reader', send_notification=False)

    context['folders'] = drive_service.list_folders(parent_folder_id=shared_folder_id)
    context['files'] = drive_service.list_files(folder_id=shared_folder_id)

    return render(request, 'teachers/teacher_shared_drive.html', context)
