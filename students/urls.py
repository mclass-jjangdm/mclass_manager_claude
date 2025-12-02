from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.StudentListView.as_view(), name='student_list'),
    path('create/', views.StudentCreateView.as_view(), name='student_create'),
    path('import/', views.student_import, name='student_import'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/update/', views.student_update, name='student_update'),
    path('export/', views.student_export, name='student_export'),
    path('<int:pk>/files/', views.student_files, name='student_files'),
    path('file/<int:file_id>/delete/', views.delete_student_file, name='delete_student_file'),
]