# progress/urls.py
# 학습 진도 관리 (학생 배정 및 진도 평가)

from django.urls import path
from teachers import views as teacher_views
from bookstore import views as bookstore_views
from . import views

app_name = 'progress'

urlpatterns = [
    # 메인 대시보드 (일별 수업 기록)
    path('', teacher_views.DailyProgressSummaryView.as_view(), name='dashboard'),

    # 학생 배정 관리
    path('assignment/', teacher_views.AssignmentListView.as_view(), name='assignment_list'),
    path('assignment/create/', teacher_views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignment/<int:pk>/delete/', teacher_views.assignment_delete, name='assignment_delete'),
    path('assignment/bulk-delete/', teacher_views.assignment_bulk_delete, name='assignment_bulk_delete'),
    path('assignment/<int:pk>/change-teacher/', teacher_views.assignment_change_teacher, name='assignment_change_teacher'),
    path('assignment/<int:pk>/change-type/', teacher_views.assignment_change_type, name='assignment_change_type'),
    path('assignment/<int:pk>/unassign/', teacher_views.assignment_unassign, name='assignment_unassign'),

    # 교사용 진도 관리
    path('teacher/', teacher_views.TeacherProgressView.as_view(), name='teacher_progress'),
    path('teacher/<int:teacher_pk>/', teacher_views.TeacherProgressView.as_view(), name='teacher_progress_detail'),

    # 교사 자신의 진도 페이지
    path('my/', teacher_views.TeacherMyProgressView.as_view(), name='my_progress'),

    # 학생 교재 진도 평가 (bookstore에서 이동)
    path('book/<int:sale_pk>/', bookstore_views.student_book_progress_list, name='student_book_progress_list'),
    path('book/<int:sale_pk>/<int:progress_pk>/', bookstore_views.student_book_progress_update, name='student_book_progress_update'),
    path('book/<int:sale_pk>/bulk/', bookstore_views.student_book_progress_bulk_update, name='student_book_progress_bulk_update'),
]
