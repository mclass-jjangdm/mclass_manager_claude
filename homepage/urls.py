from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'homepage'

urlpatterns = [
    # ── 로그인 / 로그아웃 (mclass.co.kr 자체 인증) ──
    path('login/', auth_views.LoginView.as_view(
        template_name='homepage/login.html',
        redirect_authenticated_user=True,
        next_page='/',           # 로그인 성공 후 항상 mclass.co.kr 홈으로
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # ── 홈페이지 콘텐츠 관리 (관리자 전용) ──
    path('manage/notices/', views.manage_notices, name='manage_notices'),
    path('manage/columns/', views.manage_columns, name='manage_columns'),
    path('manage/news/', views.manage_news, name='manage_news'),

    # 공지사항
    path('notice/', views.notice_list, name='notice_list'),
    path('notice/create/', views.notice_create, name='notice_create'),
    path('notice/<int:pk>/', views.notice_detail, name='notice_detail'),
    path('notice/<int:pk>/update/', views.notice_update, name='notice_update'),
    path('notice/<int:pk>/delete/', views.notice_delete, name='notice_delete'),

    # 원장칼럼
    path('column/', views.column_list, name='column_list'),
    path('column/create/', views.column_create, name='column_create'),
    path('column/<int:pk>/', views.column_detail, name='column_detail'),
    path('column/<int:pk>/update/', views.column_update, name='column_update'),
    path('column/<int:pk>/delete/', views.column_delete, name='column_delete'),

    # 입시뉴스
    path('news/', views.news_list, name='news_list'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/scrape/', views.news_scrape, name='news_scrape'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('news/<int:pk>/update/', views.news_update, name='news_update'),
    path('news/<int:pk>/delete/', views.news_delete, name='news_delete'),

    # 학원소개
    path('about/', views.about, name='about'),
    path('about/update/', views.about_update, name='about_update'),

    # 상담 신청 (공개)
    path('consult/', views.consultation_create, name='consultation_create'),
    path('consult/success/', views.consultation_success, name='consultation_success'),

    # 상담 신청 관리 (관리자)
    path('manage/consultations/', views.manage_consultations, name='manage_consultations'),
    path('manage/consultations/<int:pk>/status/', views.consultation_update_status, name='consultation_update_status'),
]
