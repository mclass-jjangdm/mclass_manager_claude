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
