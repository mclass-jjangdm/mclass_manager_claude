"""
URL configuration for mclass_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from .views import IndexView, AdminLoginView
from django.contrib.auth.views import LogoutView
from common.views import (
    db_backup,
    google_drive_dashboard,
    google_drive_setup,
    google_drive_folder_detail,
    google_drive_create_folder,
    google_drive_upload_file,
    google_drive_share_folder,
    google_drive_delete,
)
from students.views import parent_lookup, parent_student_update, parent_logout, parent_grades, parent_grade_bulk_create, parent_mock_grade_create, parent_grade_import, parent_grade_edit


admin.site.site_header = "엠클래스수학과학전문학원"  # 로그인 페이지와 관리자 페이지 상단의 타이틀
admin.site.site_title = "m'class manager"   # 브라우저 탭에 표시되는 타이틀
admin.site.index_title = "m'class manager"  # 관리자 페이지의 메인 타이틀


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    # 학원 홈페이지 공개 URL (notice/, column/, news/, about/)
    path('', include('homepage.urls')),
    # Summernote 이미지 업로드
    path('summernote/', include('django_summernote.urls')),
    path('parent/', parent_lookup, name='parent_lookup'),
    path('parent/update/<str:student_id>/', parent_student_update, name='parent_student_update'),
    path('parent/grades/<int:student_pk>/', parent_grades, name='parent_grades'),
    path('parent/grades/<int:student_pk>/school/bulk/', parent_grade_bulk_create, name='parent_grade_bulk_create'),
    path('parent/grades/<int:student_pk>/school/mock/', parent_mock_grade_create, name='parent_mock_grade_create'),
    path('parent/grades/<int:student_pk>/school/import/', parent_grade_import, name='parent_grade_import'),
    path('parent/grades/<int:student_pk>/edit/<int:grade_pk>/', parent_grade_edit, name='parent_grade_edit'),
    path('parent/exit/', parent_logout, name='parent_logout'),
    path('admin/db-backup/', db_backup, name='db_backup'),
    # Google Drive 관리
    path('admin/google-drive/', google_drive_dashboard, name='google_drive_dashboard'),
    path('admin/google-drive/setup/', google_drive_setup, name='google_drive_setup'),
    path('admin/google-drive/folder/<str:folder_id>/', google_drive_folder_detail, name='google_drive_folder_detail'),
    path('admin/google-drive/create-folder/', google_drive_create_folder, name='google_drive_create_folder'),
    path('admin/google-drive/upload/', google_drive_upload_file, name='google_drive_upload_file'),
    path('admin/google-drive/share/', google_drive_share_folder, name='google_drive_share_folder'),
    path('admin/google-drive/delete/<str:file_id>/', google_drive_delete, name='google_drive_delete'),
    path('admin/', admin.site.urls),
    path('login/', AdminLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('teachers/', include('teachers.urls')),
    path('students/', include('students.urls')),
    path('subjects/', include('subjects.urls')),
    path('grades/', include('grades.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('payment/', include('payment.urls')),
    path('bookstore/', include('bookstore.urls')),
    path('progress/', include('progress.urls')),
    path('classes/', include('classes.urls')),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico', permanent=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
