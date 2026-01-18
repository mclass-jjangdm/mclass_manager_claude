from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.utils import timezone


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # 로그인된 사용자는 대시보드를 보여줌
            self.template_name = 'dashboard.html'
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            from students.models import Student
            from teachers.models import Teacher, TeacherStudentAssignment
            from bookstore.models import StudentBookProgress

            today = timezone.now().date()

            # 학년별 학생 수 집계
            grade_counts = Student.objects.filter(
                is_active=True
            ).values('grade').annotate(
                count=Count('id')
            )

            # 학년별 딕셔너리로 변환
            grade_dict = {item['grade']: item['count'] for item in grade_counts if item['grade']}

            # K5~K12 순서대로 정렬된 리스트 생성
            grade_order = ['K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11', 'K12']
            grade_stats = [(grade, grade_dict.get(grade, 0)) for grade in grade_order if grade in grade_dict]

            # 총 학생 수
            total_students = Student.objects.filter(is_active=True).count()

            # 재직 중인 교사 수
            active_teachers = Teacher.objects.filter(
                Q(resignation_date__isnull=True)
            ).count()

            # 오늘 학습 진도 통계
            today_assignments = TeacherStudentAssignment.objects.filter(date=today)
            today_assigned = today_assignments.filter(assignment_type='normal').count()
            today_absent = today_assignments.filter(assignment_type='absent').count()
            today_progress_records = StudentBookProgress.objects.filter(study_date=today).count()

            context['grade_stats'] = grade_stats
            context['total_students'] = total_students
            context['active_teachers'] = active_teachers
            context['today'] = today
            context['today_assigned'] = today_assigned
            context['today_absent'] = today_absent
            context['today_progress_records'] = today_progress_records

        return context
