import json
from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Column, ExamNews, Notice, SchoolIntro


# ─────────────────────────────────────────────
# 공개 뷰 (로그인 불필요)
# ─────────────────────────────────────────────

def homepage_index(request):
    """학원 홈페이지 메인"""
    notices = Notice.objects.filter(is_published=True)[:3]
    columns = Column.objects.filter(is_published=True)[:3]
    news_list = ExamNews.objects.filter(is_published=True)[:6]
    intro = SchoolIntro.get_instance()
    return render(request, 'homepage/index.html', {
        'notices': notices,
        'columns': columns,
        'news_list': news_list,
        'intro': intro,
    })


def notice_list(request):
    """공지사항 목록"""
    qs = Notice.objects.filter(is_published=True)
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    notices = paginator.get_page(page)
    return render(request, 'homepage/notice_list.html', {'notices': notices})


def notice_detail(request, pk):
    """공지사항 상세"""
    notice = get_object_or_404(Notice, pk=pk, is_published=True)
    prev_notice = Notice.objects.filter(is_published=True, pk__lt=pk).order_by('-pk').first()
    next_notice = Notice.objects.filter(is_published=True, pk__gt=pk).order_by('pk').first()
    return render(request, 'homepage/notice_detail.html', {
        'notice': notice,
        'prev_notice': prev_notice,
        'next_notice': next_notice,
    })


def column_list(request):
    """원장칼럼 목록"""
    qs = Column.objects.filter(is_published=True)
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    columns = paginator.get_page(page)
    return render(request, 'homepage/column_list.html', {'columns': columns})


def column_detail(request, pk):
    """원장칼럼 상세"""
    column = get_object_or_404(Column, pk=pk, is_published=True)
    prev_column = Column.objects.filter(is_published=True, pk__lt=pk).order_by('-pk').first()
    next_column = Column.objects.filter(is_published=True, pk__gt=pk).order_by('pk').first()
    return render(request, 'homepage/column_detail.html', {
        'column': column,
        'prev_column': prev_column,
        'next_column': next_column,
    })


def news_list(request):
    """입시뉴스 목록"""
    qs = ExamNews.objects.filter(is_published=True)
    paginator = Paginator(qs, 12)
    page = request.GET.get('page')
    news_list = paginator.get_page(page)
    return render(request, 'homepage/news_list.html', {'news_list': news_list})


def news_detail(request, pk):
    """입시뉴스 상세"""
    news = get_object_or_404(ExamNews, pk=pk, is_published=True)
    prev_news = ExamNews.objects.filter(is_published=True, pk__lt=pk).order_by('-pk').first()
    next_news = ExamNews.objects.filter(is_published=True, pk__gt=pk).order_by('pk').first()
    return render(request, 'homepage/news_detail.html', {
        'news': news,
        'prev_news': prev_news,
        'next_news': next_news,
    })


def about(request):
    """학원 소개"""
    intro = SchoolIntro.get_instance()
    return render(request, 'homepage/about.html', {'intro': intro})


# ─────────────────────────────────────────────
# 관리자 전용 뷰 (is_staff 필요)
# ─────────────────────────────────────────────

def _require_staff(request):
    """관리자 체크 헬퍼. True면 권한 없음."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return True
    return False


# ── 공지사항 CRUD ──

@login_required
def notice_create(request):
    if _require_staff(request):
        return redirect('homepage:notice_list')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        is_published = request.POST.get('is_published') == 'on'
        if title and content:
            Notice.objects.create(title=title, content=content,
                                  is_published=is_published, author=request.user)
            messages.success(request, '공지사항이 등록되었습니다.')
            return redirect('homepage:notice_list')
        messages.error(request, '제목과 내용을 입력해 주세요.')
    return render(request, 'homepage/notice_form.html', {'form_title': '공지사항 작성'})


@login_required
def notice_update(request, pk):
    if _require_staff(request):
        return redirect('homepage:notice_list')
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        notice.title = request.POST.get('title', '').strip()
        notice.content = request.POST.get('content', '').strip()
        notice.is_published = request.POST.get('is_published') == 'on'
        if notice.title and notice.content:
            notice.save()
            messages.success(request, '공지사항이 수정되었습니다.')
            return redirect('homepage:notice_detail', pk=pk)
        messages.error(request, '제목과 내용을 입력해 주세요.')
    return render(request, 'homepage/notice_form.html', {
        'object': notice, 'form_title': '공지사항 수정'
    })


@login_required
def notice_delete(request, pk):
    if _require_staff(request):
        return redirect('homepage:notice_list')
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        notice.delete()
        messages.success(request, '공지사항이 삭제되었습니다.')
        return redirect('homepage:notice_list')
    return render(request, 'homepage/confirm_delete.html', {
        'object_title': notice.title,
        'cancel_url': f'/notice/{pk}/',
    })


# ── 원장칼럼 CRUD ──

@login_required
def column_create(request):
    if _require_staff(request):
        return redirect('homepage:column_list')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        is_published = request.POST.get('is_published') == 'on'
        if title and content:
            Column.objects.create(title=title, content=content,
                                  is_published=is_published, author=request.user)
            messages.success(request, '칼럼이 등록되었습니다.')
            return redirect('homepage:column_list')
        messages.error(request, '제목과 내용을 입력해 주세요.')
    return render(request, 'homepage/column_form.html', {'form_title': '원장칼럼 작성'})


@login_required
def column_update(request, pk):
    if _require_staff(request):
        return redirect('homepage:column_list')
    column = get_object_or_404(Column, pk=pk)
    if request.method == 'POST':
        column.title = request.POST.get('title', '').strip()
        column.content = request.POST.get('content', '').strip()
        column.is_published = request.POST.get('is_published') == 'on'
        if column.title and column.content:
            column.save()
            messages.success(request, '칼럼이 수정되었습니다.')
            return redirect('homepage:column_detail', pk=pk)
        messages.error(request, '제목과 내용을 입력해 주세요.')
    return render(request, 'homepage/column_form.html', {
        'object': column, 'form_title': '원장칼럼 수정'
    })


@login_required
def column_delete(request, pk):
    if _require_staff(request):
        return redirect('homepage:column_list')
    column = get_object_or_404(Column, pk=pk)
    if request.method == 'POST':
        column.delete()
        messages.success(request, '칼럼이 삭제되었습니다.')
        return redirect('homepage:column_list')
    return render(request, 'homepage/confirm_delete.html', {
        'object_title': column.title,
        'cancel_url': f'/column/{pk}/',
    })


# ── 입시뉴스 CRUD + 스크래핑 ──

@login_required
def news_create(request):
    if _require_staff(request):
        return redirect('homepage:news_list')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        source_url = request.POST.get('source_url', '').strip()
        source_name = request.POST.get('source_name', '').strip()
        original_url = request.POST.get('original_url', '').strip()
        is_published = request.POST.get('is_published') == 'on'
        if title and content:
            ExamNews.objects.create(
                title=title, content=content,
                source_url=source_url, source_name=source_name,
                original_url=original_url, is_published=is_published,
            )
            messages.success(request, '입시뉴스가 등록되었습니다.')
            return redirect('homepage:news_list')
        messages.error(request, '제목과 내용을 입력해 주세요.')
    return render(request, 'homepage/news_form.html', {'form_title': '입시뉴스 추가'})


@login_required
def news_update(request, pk):
    if _require_staff(request):
        return redirect('homepage:news_list')
    news = get_object_or_404(ExamNews, pk=pk)
    if request.method == 'POST':
        news.title = request.POST.get('title', '').strip()
        news.content = request.POST.get('content', '').strip()
        news.source_url = request.POST.get('source_url', '').strip()
        news.source_name = request.POST.get('source_name', '').strip()
        news.original_url = request.POST.get('original_url', '').strip()
        news.is_published = request.POST.get('is_published') == 'on'
        if news.title and news.content:
            news.save()
            messages.success(request, '입시뉴스가 수정되었습니다.')
            return redirect('homepage:news_detail', pk=pk)
        messages.error(request, '제목과 내용을 입력해 주세요.')
    return render(request, 'homepage/news_form.html', {
        'object': news, 'form_title': '입시뉴스 수정'
    })


@login_required
def news_delete(request, pk):
    if _require_staff(request):
        return redirect('homepage:news_list')
    news = get_object_or_404(ExamNews, pk=pk)
    if request.method == 'POST':
        news.delete()
        messages.success(request, '입시뉴스가 삭제되었습니다.')
        return redirect('homepage:news_list')
    return render(request, 'homepage/confirm_delete.html', {
        'object_title': news.title,
        'cancel_url': f'/news/{pk}/',
    })


@login_required
def news_scrape(request):
    """URL에서 기사 제목/내용 스크래핑 (AJAX)"""
    if not request.user.is_staff:
        return JsonResponse({'error': '권한이 없습니다.'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

    try:
        data = json.loads(request.body)
        url = data.get('url', '').strip()
        if not url:
            return JsonResponse({'error': 'URL을 입력해 주세요.'}, status=400)

        import requests as req
        from bs4 import BeautifulSoup

        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        }
        response = req.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'lxml')

        # 제목 추출: og:title → h1 → <title>
        title = ''
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title = og_title['content'].strip()
        if not title:
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
        if not title and soup.title:
            title = soup.title.get_text(strip=True)

        # 본문 추출 우선순위: article → .article-body/.content/.news-body → main → body
        content = ''
        for selector in ['article', '[class*="article-body"]', '[class*="article_body"]',
                         '[class*="news-body"]', '[class*="content-body"]',
                         '[id*="article"]', 'main', '[class*="content"]']:
            el = soup.select_one(selector)
            if el:
                # 불필요한 태그 제거
                for tag in el.find_all(['script', 'style', 'nav', 'header',
                                        'footer', 'aside', 'figure', 'figcaption']):
                    tag.decompose()
                text = el.get_text(separator='\n', strip=True)
                if len(text) > 100:
                    content = text
                    break

        # 출처명 추출 (도메인)
        parsed = urlparse(url)
        source_name = parsed.netloc.replace('www.', '')

        return JsonResponse({
            'title': title,
            'content': content,
            'source_name': source_name,
            'original_url': url,
        })

    except Exception as e:
        return JsonResponse({'error': f'스크래핑 실패: {str(e)}'}, status=500)


# ── 학원소개 ──

@login_required
def about_update(request):
    if _require_staff(request):
        return redirect('homepage:about')
    intro = SchoolIntro.get_instance()
    if request.method == 'POST':
        intro.academy_name = request.POST.get('academy_name', '').strip()
        intro.subtitle = request.POST.get('subtitle', '').strip()
        intro.intro_text = request.POST.get('intro_text', '').strip()
        intro.vision_text = request.POST.get('vision_text', '').strip()
        intro.address = request.POST.get('address', '').strip()
        intro.phone = request.POST.get('phone', '').strip()
        intro.email = request.POST.get('email', '').strip()
        intro.save()
        messages.success(request, '학원 소개가 수정되었습니다.')
        return redirect('homepage:about')
    return render(request, 'homepage/about_form.html', {'object': intro})
