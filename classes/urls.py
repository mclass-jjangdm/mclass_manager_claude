from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    # 수업 (Lesson)
    path('', views.lesson_list, name='lesson_list'),
    path('create/', views.lesson_create, name='lesson_create'),
    path('<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('<int:pk>/edit/', views.lesson_edit, name='lesson_edit'),
    path('<int:pk>/delete/', views.lesson_delete, name='lesson_delete'),

    # 수강 신청 (Enrollment)
    path('<int:pk>/enroll/', views.enrollment_create, name='enrollment_create'),
    path('<int:pk>/enrollment/<int:enroll_pk>/edit/', views.enrollment_edit, name='enrollment_edit'),
    path('<int:pk>/enrollment/<int:enroll_pk>/delete/', views.enrollment_delete, name='enrollment_delete'),

    # 수강료 납부 (TuitionPayment)
    path('enrollment/<int:enroll_pk>/payment/create/', views.tuition_payment_create, name='tuition_payment_create'),
    path('enrollment/<int:enroll_pk>/payment/<int:pay_pk>/delete/', views.tuition_payment_delete, name='tuition_payment_delete'),

    # 월별 수강 신청 (MonthlyEnrollment)
    path('monthly/', views.monthly_enrollment_list, name='monthly_enrollment_list'),
    path('monthly/create/', views.monthly_enrollment_create, name='monthly_enrollment_create'),
    path('monthly/export/', views.monthly_enrollment_export_xlsx, name='monthly_enrollment_export_xlsx'),
    path('monthly/bulk-confirm/', views.monthly_enrollment_bulk_confirm, name='monthly_enrollment_bulk_confirm'),
    path('monthly/bulk-delete/', views.monthly_enrollment_bulk_delete, name='monthly_enrollment_bulk_delete'),
    path('monthly/<int:pk>/edit/', views.monthly_enrollment_edit, name='monthly_enrollment_edit'),
    path('monthly/<int:pk>/delete/', views.monthly_enrollment_delete, name='monthly_enrollment_delete'),
]
