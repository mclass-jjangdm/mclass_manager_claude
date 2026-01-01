from django.urls import path
from . import views

app_name = 'subjects'

urlpatterns = [
    path('', views.SubjectListView.as_view(), name='subject_list'),
    path('create/', views.SubjectCreateView.as_view(), name='subject_create'),
    path('bulk-import/', views.bulk_import_subjects, name='bulk_import'),
    path('<int:pk>/update/', views.SubjectUpdateView.as_view(), name='subject_update'),
    path('<int:pk>/delete/', views.SubjectDeleteView.as_view(), name='subject_delete'),
]
