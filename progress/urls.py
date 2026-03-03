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

    # 날짜 무관한 전체 학생 수업 현황 대시보드
    path('class-dashboard/', teacher_views.StudentClassDashboardView.as_view(), name='class_dashboard'),

    # 학생 배정 관리
    path('assignment/', teacher_views.AssignmentListView.as_view(), name='assignment_list'),
    path('assignment/create/', teacher_views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignment/<int:pk>/delete/', teacher_views.assignment_delete, name='assignment_delete'),
    path('assignment/bulk-delete/', teacher_views.assignment_bulk_delete, name='assignment_bulk_delete'),
    path('assignment/<int:pk>/change-teacher/', teacher_views.assignment_change_teacher, name='assignment_change_teacher'),
    path('assignment/<int:pk>/change-type/', teacher_views.assignment_change_type, name='assignment_change_type'),
    path('assignment/<int:pk>/unassign/', teacher_views.assignment_unassign, name='assignment_unassign'),
    path('assignment/<int:pk>/update-absence-reason/', teacher_views.assignment_update_absence_reason, name='assignment_update_absence_reason'),

    # 교사용 진도 관리
    path('teacher/', teacher_views.TeacherProgressView.as_view(), name='teacher_progress'),
    path('teacher/<int:teacher_pk>/', teacher_views.TeacherProgressView.as_view(), name='teacher_progress_detail'),

    # 교사 자신의 진도 페이지
    path('my/', teacher_views.TeacherMyProgressView.as_view(), name='my_progress'),

    # 학생 교재 진도 평가 (bookstore에서 이동)
    path('book/<int:sale_pk>/', bookstore_views.student_book_progress_list, name='student_book_progress_list'),
    path('book/<int:sale_pk>/<int:progress_pk>/', bookstore_views.student_book_progress_update, name='student_book_progress_update'),
    path('book/<int:sale_pk>/bulk/', bookstore_views.student_book_progress_bulk_update, name='student_book_progress_bulk_update'),
    path('book/<int:sale_pk>/<int:progress_pk>/reset/', bookstore_views.student_book_progress_reset, name='student_book_progress_reset'),
    path('book/<int:sale_pk>/bulk-reset/', bookstore_views.student_book_progress_bulk_reset, name='student_book_progress_bulk_reset'),

    # 수업 활동 관리
    path('activity/create/', views.student_activity_create, name='student_activity_create'),
    path('activity/<int:pk>/update/', views.student_activity_update, name='student_activity_update'),
    path('activity/<int:pk>/delete/', views.student_activity_delete, name='student_activity_delete'),
    path('activity/list/', views.student_activity_list_ajax, name='student_activity_list_ajax'),
]
