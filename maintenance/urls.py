from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.MaintenanceCreateView.as_view(), name='maintenance_list'),  # 기본 페이지를 create로 설정
    path('create/', views.MaintenanceCreateView.as_view(), name='create'),
    path('monthly/', views.MonthlyReportView.as_view(), name='monthly_report'),
    path('yearly/', views.YearlyReportView.as_view(), name='yearly_report'),
    path('edit/<int:pk>/', views.MaintenanceUpdateView.as_view(), name='maintenance_edit'),
    path('pay/<int:pk>/', views.MaintenanceMarkPaidView.as_view(), name='mark_paid'),
    path('pay/<int:pk>/cancel/', views.MaintenanceCancelPaidView.as_view(), name='cancel_paid'),
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('rooms/add/', views.RoomCreateView.as_view(), name='room_add'),
    path('rooms/<int:pk>/edit/', views.RoomUpdateView.as_view(), name='room_edit'),
]