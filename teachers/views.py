from datetime import timedelta, datetime
from io import BytesIO
from pyexpat.errors import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import Teacher, Attendance, Salary
from .forms import BulkAttendanceForm, TeacherForm
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
        queryset = Teacher.objects.all()
        show_inactive = self.request.GET.get('show_inactive') == 'on'
        if not show_inactive:
            queryset = queryset.filter(is_active=True)
        active_teachers = queryset.filter(is_active=True).order_by('-hire_date')
        inactive_teachers = queryset.filter(is_active=False).order_by('-resignation_date') # 퇴사 날짜 기준으로 역순 정렬
        return active_teachers, inactive_teachers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_inactive'] = self.request.GET.get('show_inactive') == 'on'
        context['active_teachers'], context['inactive_teachers'] = self.get_queryset()
        return context


class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = Teacher
    template_name = 'teachers/teacher_detail.html'


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
        teachers = Teacher.objects.filter(is_active=True)
        form = BulkAttendanceForm(teachers=teachers)
        current_date = timezone.now().date()
        month_start = current_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
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
            'teacher_records': teacher_records,
            'current_month': current_date.strftime('%Y년 %m월')
        }
        return render(request, 'teachers/attendance_form.html', context)

    def post(self, request):
        teachers = Teacher.objects.filter(is_active=True)
        form = BulkAttendanceForm(request.POST, teachers=teachers)
        if form.is_valid():
            date = form.cleaned_data['date']
            for teacher in teachers:
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
            'teacher_records': {},
            'current_month': current_date.strftime('%Y년 %m월')
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
        
        try:
            with transaction.atomic():
                for teacher in teachers:
                    work_hours, work_days = self.calculate_work_hours(teacher, year, month)
                    
                    # 근무 시간이 있는 경우만 급여 계산
                    if work_hours > 0:
                        base_amount = int(work_hours * teacher.base_salary)
                        additional_amount = teacher.additional_salary or 0
                        total_amount = base_amount + additional_amount

                        # Create or update salary record
                        salary, created = Salary.objects.update_or_create(
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

                        salary_data.append({
                            'teacher': teacher,
                            'work_days': work_days,
                            'work_hours': work_hours,
                            'bank_name': teacher.bank.name if teacher.bank else None,
                            'account_number': teacher.account_number,
                            'total_amount': total_amount
                        })
                        
                        total_salary += total_amount

        except Exception as e:
            messages.error(request, f'급여 계산 중 오류가 발생했습니다: {str(e)}')

        context = {
            'year': year,
            'month': month,
            'years': range(2020, timezone.now().year + 1),
            'months': range(1, 13),
            'salary_data': salary_data,
            'total_salary': total_salary
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
        
        salary_table = []
        grand_total = 0

        # 활성 상태 선생님 급여 계산
        for teacher in teachers.filter(is_active=True):
            teacher_data = {'teacher': teacher}
            total = 0
            
            for month in months:
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
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1) - timedelta(days=1)

                attendances = Attendance.objects.filter(teacher=teacher, date__range=[start_date, end_date])
                # 계산식 수정
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

        context = {
            'year': year,
            'year_range': sorted(list(year_range), reverse=True),
            'months': months,
            'salary_table': salary_table,
            'grand_total': grand_total,
        }

        return render(request, 'teachers/salary_table.html', context)


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
        
        if attendances:
            monthly_data = {}
            for attendance in attendances:
                year_month = attendance.date.strftime("%Y-%m")
                if year_month not in monthly_data:
                    monthly_data[year_month] = {'hours': 0, 'amount': 0}
                
                if attendance.start_time and attendance.end_time:
                    start_datetime = datetime.combine(attendance.date, attendance.start_time)
                    end_datetime = datetime.combine(attendance.date, attendance.end_time)
                    if end_datetime < start_datetime:  # 자정을정 경우
                        end_datetime += timedelta(days=1)
                    work_hours = (end_datetime - start_datetime).total_seconds() / 3600
                    monthly_data[year_month]['hours'] += work_hours
                    monthly_data[year_month]['amount'] += work_hours * teacher.base_salary

            attendance_data = [["년/월", "근무시간", "급여"]]
            total_hours = 0
            total_amount = 0
            for year_month, data in monthly_data.items():
                year, month = year_month.split('-')
                hours = round(data['hours'], 1)
                amount = round(data['amount'])
                attendance_data.append([f"{year}년 {month}월", f"{hours}시간", f"{amount:,}원"])
                total_hours += hours
                total_amount += amount
            
            attendance_data.append(["총계", f"{total_hours:.1f}시간", f"{total_amount:,}원"])

            t = Table(attendance_data, colWidths=[60*mm, 50*mm, 60*mm])
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

        # 급여 데이터 계산
        teachers = Teacher.objects.filter(
            attendance__date__range=[start_date, end_date]
        ).distinct()

        data = [['이름', '급여']]
        total_amount = 0

        for teacher in teachers:
            attendances = Attendance.objects.filter(
                teacher=teacher,
                date__range=[start_date, end_date],
                is_present=True,
                start_time__isnull=False,
                end_time__isnull=False
            )

            work_hours = sum(
                ((a.end_time.hour * 60 + a.end_time.minute) -
                 (a.start_time.hour * 60 + a.start_time.minute))
                for a in attendances
            ) / 60

            salary = int(work_hours * (teacher.base_salary or 15000))
            total_amount += salary
            data.append([teacher.name, f"{salary:,}원"])

        data.append(["합계", f"{total_amount:,}원"])

        # 테이블 생성
        col_widths = [TABLE_WIDTH * 0.4, TABLE_WIDTH * 0.4]
        table = Table(data, colWidths=col_widths)

        # 테이블 스타일 설정
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # 헤더 중앙 정렬
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # 이름 중앙 정렬
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),   # 금액 우측 정렬
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
