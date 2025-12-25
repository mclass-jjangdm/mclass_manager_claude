from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.StudentListView.as_view(), name='student_list'),
    path('create/', views.StudentCreateView.as_view(), name='student_create'),
    path('import/', views.student_import, name='student_import'),
    path('export/', views.student_export, name='student_export'),
    path('sms/bulk/', views.bulk_sms_send, name='bulk_sms_send'),
    path('grade-promotion/confirm/', views.grade_promotion_confirm, name='grade_promotion_confirm'),
    path('grade-promotion/execute/', views.grade_promotion_execute, name='grade_promotion_execute'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/update/', views.student_update, name='student_update'),
    path('<int:pk>/files/', views.student_files, name='student_files'),
    path('<int:pk>/send-email/', views.student_send_email, name='student_send_email'),
    path('<int:pk>/send-sms/', views.student_send_sms, name='student_send_sms'),
    path('<int:pk>/send-sms-parent/', views.student_send_sms_parent, name='student_send_sms_parent'),
    path('file/<int:file_id>/delete/', views.delete_student_file, name='delete_student_file'),
]