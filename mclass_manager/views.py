from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.utils import timezone


class AdminLoginView(LoginView):
    """관리자 전용 로그인 뷰 - 교사 계정 차단"""
    template_name = 'index.html'

    def form_valid(self, form):
        user = form.get_user()
        # 교사 계정인 경우 로그인 차단
        if hasattr(user, 'teacher_profile'):
            messages.error(self.request, '선생님 계정은 "선생님 포털 로그인"을 이용해 주세요.')
            return self.form_invalid(form)
        return super().form_valid(form)


class IndexView(TemplateView):
    template_name = 'index.html'

    # 공개 홈페이지로 서빙할 호스트 목록
    PUBLIC_HOSTS = ('mclass.co.kr', 'www.mclass.co.kr')

    def get(self, request, *args, **kwargs):
        host = request.get_host().split(':')[0].lower()
        # mclass.co.kr 는 로그인 여부·권한 무관하게 항상 공개 홈페이지
        if host in self.PUBLIC_HOSTS:
            from homepage.views import homepage_index
            return homepage_index(request)

        if request.user.is_authenticated:
            # manager.mclass.co.kr 의 로그인된 관리자 → 대시보드
            self.template_name = 'dashboard.html'
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            from students.models import Student
            from teachers.models import Teacher, TeacherStudentAssignment, TeacherUnavailability, Attendance, Salary
            from bookstore.models import StudentBookProgress, Book, BookStockLog
            from maintenance.models import Maintenance

            today = timezone.now().date()
            this_month = today.replace(day=1)

            # 학년별 학생 수 집계
            grade_counts = Student.objects.filter(
                is_active=True
            ).values('grade').annotate(count=Count('id'))
            grade_dict = {item['grade']: item['count'] for item in grade_counts if item['grade']}
            grade_order = ['K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11', 'K12']
            grade_stats = [(grade, grade_dict.get(grade, 0)) for grade in grade_order if grade in grade_dict]
            total_students = Student.objects.filter(is_active=True).count()

            # 재직 중인 교사 수
            active_teachers = Teacher.objects.filter(
                Q(resignation_date__isnull=True)
            ).count()

            # 출근 불가 일정 승인 대기 건수
            pending_unavailability_count = TeacherUnavailability.objects.filter(
                status='pending'
            ).count()

            # 오늘 학습 진도 통계
            today_assignments = TeacherStudentAssignment.objects.filter(date=today)
            today_assigned = today_assignments.filter(assignment_type='normal').count()
            today_absent = today_assignments.filter(assignment_type='absent').count()
            today_progress_records = StudentBookProgress.objects.filter(study_date=today).count()

            # 이번 달 입고 금액 / 미정산 금액
            # created_at__date__gte 는 이번 달 이후 전체를 포함하므로, year+month 로 이번 달만 정확히 필터
            month_logs = BookStockLog.objects.filter(
                created_at__year=today.year,
                created_at__month=today.month,
            )
            inbound = month_logs.filter(quantity__gt=0).aggregate(s=Sum('total_payment'))['s'] or 0
            returned = month_logs.filter(quantity__lt=0).aggregate(s=Sum('total_payment'))['s'] or 0
            month_inbound_payment = inbound - returned
            month_unpaid_payment = month_logs.filter(is_paid=False, quantity__gt=0).aggregate(
                s=Sum('total_payment'))['s'] or 0

            # 재고 부족 교재 (3권 이하)
            low_stock_count = Book.objects.filter(stock__lte=3).count()

            # 미납 학생 수 (unpaid_amount > 0)
            unpaid_student_count = Student.objects.filter(is_active=True, unpaid_amount__gt=0).count()

            # 오늘 출근 교사 수
            today_present = Attendance.objects.filter(date=today, is_present=True).count()

            # 이번 달 정산 - 지출
            month_maint = Maintenance.objects.filter(
                date__year=today.year,
                date__month=today.month,
            )
            month_rent = month_maint.aggregate(s=Sum('rent'))['s'] or 0
            month_charge = month_maint.aggregate(s=Sum('charge'))['s'] or 0
            month_salary = Salary.objects.filter(
                year=today.year,
                month=today.month,
            ).aggregate(s=Sum('total_amount'))['s'] or 0
            total_expense = month_rent + month_charge + month_salary + month_inbound_payment

            context.update({
                'grade_stats': grade_stats,
                'total_students': total_students,
                'active_teachers': active_teachers,
                'pending_unavailability_count': pending_unavailability_count,
                'today': today,
                'today_assigned': today_assigned,
                'today_absent': today_absent,
                'today_progress_records': today_progress_records,
                'month_inbound_payment': month_inbound_payment,
                'month_unpaid_payment': month_unpaid_payment,
                'low_stock_count': low_stock_count,
                'unpaid_student_count': unpaid_student_count,
                'today_present': today_present,
                'month_rent': month_rent,
                'month_charge': month_charge,
                'month_salary': month_salary,
                'total_expense': total_expense,
            })

        return context
