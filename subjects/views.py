from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Subject


class SubjectListView(LoginRequiredMixin, ListView):
    """과목 목록 페이지"""
    model = Subject
    template_name = 'subjects/subject_list.html'
    context_object_name = 'subjects'

    def get_queryset(self):
        queryset = Subject.objects.all()
        search_query = self.request.GET.get('search', '')
        show_inactive = self.request.GET.get('show_inactive') == 'on'

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        if not show_inactive:
            queryset = queryset.filter(is_active=True)

        return queryset.order_by('subject_code')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_inactive'] = self.request.GET.get('show_inactive') == 'on'
        context['search_query'] = self.request.GET.get('search', '')

        # 카테고리별 그룹화
        from collections import defaultdict
        subjects = self.get_queryset()
        grouped = defaultdict(list)

        for subject in subjects:
            grouped[subject.category].append(subject)

        context['grouped_subjects'] = dict(sorted(grouped.items()))

        # 선택된 카테고리 처리
        selected_category = self.request.GET.get('category', '')
        context['selected_category'] = selected_category

        if selected_category and selected_category in context['grouped_subjects']:
            context['selected_subjects'] = context['grouped_subjects'][selected_category]
        else:
            context['selected_subjects'] = []

        return context


class SubjectCreateView(LoginRequiredMixin, CreateView):
    """과목 등록 페이지"""
    model = Subject
    template_name = 'subjects/subject_form.html'
    fields = ['subject_code', 'name', 'special_code', 'memo', 'is_active']
    success_url = reverse_lazy('subjects:subject_list')

    def form_valid(self, form):
        messages.success(self.request, f'{form.instance.name} 과목이 등록되었습니다.')
        return super().form_valid(form)


class SubjectUpdateView(LoginRequiredMixin, UpdateView):
    """과목 수정 페이지"""
    model = Subject
    template_name = 'subjects/subject_form.html'
    fields = ['subject_code', 'name', 'special_code', 'memo', 'is_active']
    success_url = reverse_lazy('subjects:subject_list')

    def form_valid(self, form):
        messages.success(self.request, f'{form.instance.name} 과목이 수정되었습니다.')
        return super().form_valid(form)


class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    """과목 삭제 페이지"""
    model = Subject
    template_name = 'subjects/subject_confirm_delete.html'
    success_url = reverse_lazy('subjects:subject_list')

    def delete(self, request, *args, **kwargs):
        subject = self.get_object()
        messages.success(request, f'{subject.name} 과목이 삭제되었습니다.')
        return super().delete(request, *args, **kwargs)


from django.core.management import call_command
from io import StringIO


@login_required
def bulk_import_subjects(request):
    """CSV 파일에서 과목 일괄 가져오기"""
    if request.method == 'POST':
        confirm = request.POST.get('confirm')

        if confirm == 'yes':
            # import_subjects 명령 실행
            try:
                out = StringIO()
                call_command('import_subjects', stdout=out, stdin=StringIO('yes\n'))
                output = out.getvalue()

                # 성공 메시지 추출
                if '성공적으로 가져와졌습니다' in output:
                    messages.success(request, 'CSV 파일에서 과목을 성공적으로 가져왔습니다.')
                else:
                    messages.info(request, output)

            except Exception as e:
                messages.error(request, f'과목 가져오기 중 오류가 발생했습니다: {str(e)}')

            return redirect('subjects:subject_list')
        else:
            return redirect('subjects:subject_list')

    # GET 요청: 확인 페이지 표시
    subject_count = Subject.objects.count()
    return render(request, 'subjects/bulk_import_confirm.html', {
        'subject_count': subject_count
    })
