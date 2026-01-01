# progress/urls.py

from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    # 문제 유형 관리
    path('types/', views.ProblemTypeListView.as_view(), name='problem_type_list'),
    path('types/create/', views.ProblemTypeCreateView.as_view(), name='problem_type_create'),
    path('types/upload/', views.ProblemTypeUploadView.as_view(), name='problem_type_upload'),
    path('types/<int:pk>/delete/', views.ProblemTypeDeleteView.as_view(), name='problem_type_delete'),

    # 교재-문제 연결 관리
    path('problems/', views.BookProblemListView.as_view(), name='book_problem_list'),
    path('problems/create/', views.BookProblemCreateView.as_view(), name='book_problem_create'),
    path('problems/<int:pk>/delete/', views.BookProblemDeleteView.as_view(), name='book_problem_delete'),

    # 학생 진도표 관리
    path('', views.StudentProgressListView.as_view(), name='student_progress_list'),
    path('create/', views.StudentProgressCreateView.as_view(), name='student_progress_create'),
    path('<int:pk>/', views.StudentProgressDetailView.as_view(), name='student_progress_detail'),

    # 진도 항목 업데이트 (AJAX)
    path('entry/<int:pk>/update/', views.ProgressEntryUpdateView.as_view(), name='progress_entry_update'),
]
