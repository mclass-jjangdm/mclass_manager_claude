from django.urls import path
from . import views

app_name = 'homepage'

urlpatterns = [
    # ── 홈페이지 콘텐츠 관리 (관리자 전용, base.html 사용) ──
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
]
