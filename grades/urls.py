from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    path('student/<int:student_pk>/', views.student_grades, name='student_grades'),
    path('student/<int:student_pk>/internal/create/', views.internal_grade_create, name='internal_grade_create'),
    path('student/<int:student_pk>/internal/bulk-create/', views.internal_grade_bulk_create, name='internal_grade_bulk_create'),
    path('student/<int:student_pk>/mock/create/', views.mock_grade_create, name='mock_grade_create'),
    path('student/<int:student_pk>/import/', views.grade_import, name='grade_import'),
    path('<int:pk>/update/', views.grade_update, name='grade_update'),
    path('<int:pk>/delete/', views.grade_delete, name='grade_delete'),
    path('student/<int:student_pk>/delete-all/', views.delete_all_grades, name='delete_all_grades'),
    path('api/subjects-by-category/', views.get_subjects_by_category, name='get_subjects_by_category'),
    path('template/<str:template_type>/download/', views.download_grade_template, name='download_grade_template'),
]
