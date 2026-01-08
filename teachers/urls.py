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
]