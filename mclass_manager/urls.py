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
from .views import IndexView
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView


admin.site.site_header = "엠클래스수학과학전문학원"  # 로그인 페이지와 관리자 페이지 상단의 타이틀
admin.site.site_title = "m'class manager"   # 브라우저 탭에 표시되는 타이틀
admin.site.index_title = "m'class manager"  # 관리자 페이지의 메인 타이틀


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='index.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('teachers/', include('teachers.urls')),
    path('students/', include('students.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('books/', include('books.urls')),
    path('bookstore/', include('bookstore.urls')),
    path('payment/', include('payment.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)