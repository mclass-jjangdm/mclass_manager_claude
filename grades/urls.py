from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    path('student/<int:student_pk>/internal/create/', views.internal_grade_create, name='internal_grade_create'),
    path('student/<int:student_pk>/internal/bulk-create/', views.internal_grade_bulk_create, name='internal_grade_bulk_create'),
    path('student/<int:student_pk>/mock/create/', views.mock_grade_create, name='mock_grade_create'),
    path('<int:pk>/update/', views.grade_update, name='grade_update'),
    path('<int:pk>/delete/', views.grade_delete, name='grade_delete'),
    path('api/subjects-by-category/', views.get_subjects_by_category, name='get_subjects_by_category'),
]
