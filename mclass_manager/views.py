from django.views.generic import TemplateView
from django.db.models import Count, Q


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
            from teachers.models import Teacher

            # 학년별 학생 수 집계
            grade_counts = Student.objects.filter(
                is_active=True
            ).values('grade').annotate(
                count=Count('id')
            ).order_by('grade')

            # 학년별 딕셔너리로 변환
            grade_stats = {item['grade']: item['count'] for item in grade_counts if item['grade']}

            # 총 학생 수
            total_students = Student.objects.filter(is_active=True).count()

            # 재직 중인 교사 수
            active_teachers = Teacher.objects.filter(
                Q(resignation_date__isnull=True)
            ).count()

            context['grade_stats'] = grade_stats
            context['total_students'] = total_students
            context['active_teachers'] = active_teachers

        return context