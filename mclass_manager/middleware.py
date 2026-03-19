# mclass_manager/middleware.py
# 교사 접근 권한 제한 미들웨어 + 서브도메인 리다이렉트

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
import re


class SubdomainRoutingMiddleware:
    """
    서브도메인 요청을 URL은 유지한 채 내부적으로 해당 경로로 라우팅

    teacher.mclass.co.kr/       →  /teachers/       (선생님 포털)
    teacher.mclass.co.kr/login/ →  /teachers/login/ (선생님 로그인)
    parents.mclass.co.kr/       →  /parent/          (학부모 포털)
    """

    # 서브도메인별 경로 매핑 테이블
    SUBDOMAIN_PATH_MAP = {
        'teacher': {
            '/': '/teachers/',
            '/login/': '/teachers/login/',
        },
        'parents': {
            '/': '/parent/',
        },
    }
    MAIN_DOMAIN = 'mclass.co.kr'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()

        for subdomain, path_map in self.SUBDOMAIN_PATH_MAP.items():
            if host == f'{subdomain}.{self.MAIN_DOMAIN}':
                # 슬래시 정규화 후 매핑 테이블 조회
                path = request.path if request.path.endswith('/') else request.path + '/'
                if path in path_map:
                    new_path = path_map[path]
                    request.path_info = new_path
                    request.path = new_path
                    request.META['PATH_INFO'] = new_path
                break

        return self.get_response(request)


class TeacherAccessRestrictionMiddleware:
    """
    교사 계정의 접근을 제한하는 미들웨어
    교사는 자신의 진도 페이지와 진도 평가 페이지만 접근 가능
    """

    # 교사가 접근할 수 있는 URL 패턴
    ALLOWED_PATHS = [
        r'^/progress/my/$',  # 교사 자신의 수업 페이지
        r'^/progress/book/\d+/$',  # 학생 진도 목록 페이지 (새 URL)
        r'^/progress/book/\d+/\d+/$',  # 진도 평가 상세 페이지 (새 URL)
        r'^/progress/book/\d+/bulk/$',  # 일괄 평가 페이지 (새 URL)
        r'^/bookstore/sale/\d+/progress/',  # 기존 URL 리다이렉트 허용
        r'^/teachers/messages/',  # 메시지 관련 페이지
        r'^/teachers/password/change/$',  # 비밀번호 변경 페이지
        r'^/teachers/my-work-report/',  # 교사 근무 기록 PDF 다운로드
        r'^/teachers/my-unavailability/',  # 출근 불가 일정 관리
        r'^/teachers/my-activity/',  # 교사용 수업 활동 관리
        r'^/teachers/shared-drive/',  # 공유자료 Google Drive
        r'^/accounts/',  # 로그인/로그아웃 관련 (django-allauth)
        r'^/login/$',  # 로그인
        r'^/logout/$',  # 로그아웃 (POST)
        r'^/teachers/login/$',  # 교사 로그인 페이지
        r'^/static/',  # 정적 파일
        r'^/media/',  # 미디어 파일
        r'^/__debug__/',  # 디버그 툴바
        # 홈페이지 공개 페이지
        r'^/notice/',
        r'^/column/',
        r'^/news/',
        r'^/about/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response
        # 패턴 컴파일
        self.allowed_patterns = [re.compile(pattern) for pattern in self.ALLOWED_PATHS]

    def __call__(self, request):
        # 로그인하지 않은 사용자는 통과
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 관리자(superuser) 또는 staff는 모든 접근 허용
        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        # 교사 프로필이 있는 사용자만 제한
        if hasattr(request.user, 'teacher_profile'):
            path = request.path

            # 홈페이지 접근 시 교사 포털로 바로 리다이렉트 (메시지 없이)
            if path == '/' or path == '/index/':
                return redirect('teachers:message_list')

            # 허용된 경로인지 확인
            if not self._is_allowed_path(path):
                messages.warning(request, '접근 권한이 없습니다. 교사 포털에서 허용된 페이지만 확인할 수 있습니다.')
                return redirect('teachers:message_list')

        return self.get_response(request)

    def _is_allowed_path(self, path):
        """경로가 허용된 패턴과 일치하는지 확인"""
        for pattern in self.allowed_patterns:
            if pattern.match(path):
                return True
        return False
