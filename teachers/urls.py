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
]