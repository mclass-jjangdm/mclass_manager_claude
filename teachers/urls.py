from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.TeacherListView.as_view(), name='teacher_list'),
    path('<int:pk>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
    path('create/', views.TeacherCreateView.as_view(), name='teacher_create'),
    path('<int:pk>/update/', views.TeacherUpdateView.as_view(), name='teacher_update'),
    path('attendance/create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('salary/calculate/', views.SalaryCalculationView.as_view(), name='salary_calculation'),
    path('salary/table/', views.SalaryTableView.as_view(), name='salary_table'),
    path('salary/table/<int:year>/', views.SalaryTableView.as_view(), name='salary_table_year'),
    path('teacher/<int:teacher_id>/pdf/', views.TeacherPDFReportView.as_view(), name='teacher_pdf_report'),
    path('salary/pdf/<int:year>/<int:month>/', views.SalaryPDFReportView.as_view(), name='salary_pdf_report'),
    path('<int:pk>/send-email/', views.teacher_send_email, name='teacher_send_email'),
    path('<int:pk>/resign/', views.teacher_resign, name='teacher_resign'),
    path('<int:pk>/rehire/', views.teacher_rehire, name='teacher_rehire'),
    # 출근 불가 일정 관리
    path('unavailability/', views.UnavailabilityListView.as_view(), name='unavailability_list'),
    path('unavailability/create/', views.UnavailabilityCreateView.as_view(), name='unavailability_create'),
    path('unavailability/<int:pk>/delete/', views.unavailability_delete, name='unavailability_delete'),
    path('unavailability/bulk-delete/', views.unavailability_bulk_delete, name='unavailability_bulk_delete'),
    # 교사-학생 배정 관리
    path('assignment/', views.AssignmentListView.as_view(), name='assignment_list'),
    path('assignment/create/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignment/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
    path('assignment/bulk-delete/', views.assignment_bulk_delete, name='assignment_bulk_delete'),
    path('assignment/<int:pk>/change-teacher/', views.assignment_change_teacher, name='assignment_change_teacher'),
    path('assignment/<int:pk>/change-type/', views.assignment_change_type, name='assignment_change_type'),
    path('assignment/<int:pk>/unassign/', views.assignment_unassign, name='assignment_unassign'),
    # 교사용 진도 관리
    path('progress/', views.TeacherProgressView.as_view(), name='teacher_progress'),
    path('<int:teacher_pk>/progress/', views.TeacherProgressView.as_view(), name='teacher_progress_detail'),
    # 관리자용 일별 기록 요약
    path('daily-summary/', views.DailyProgressSummaryView.as_view(), name='daily_progress_summary'),
    # 교사 계정 관리
    path('login/', views.TeacherLoginView.as_view(), name='teacher_login'),
    path('logout/', views.TeacherLogoutView.as_view(), name='teacher_logout'),
    path('my-progress/', views.TeacherMyProgressView.as_view(), name='teacher_my_progress'),
    path('<int:pk>/account/create/', views.teacher_account_create, name='teacher_account_create'),
    path('<int:pk>/account/delete/', views.teacher_account_delete, name='teacher_account_delete'),
    path('<int:pk>/password/reset/', views.teacher_password_reset, name='teacher_password_reset'),
]