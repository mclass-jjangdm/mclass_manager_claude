# mclass_manager/middleware.py
# 교사 접근 권한 제한 미들웨어

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
import re


class TeacherAccessRestrictionMiddleware:
    """
    교사 계정의 접근을 제한하는 미들웨어
    교사는 자신의 진도 페이지와 진도 평가 페이지만 접근 가능
    """

    # 교사가 접근할 수 있는 URL 패턴
    ALLOWED_PATHS = [
        r'^/progress/my/$',  # 교사 자신의 수업 페이지
        r'^/bookstore/sale/\d+/progress/$',  # 학생 진도 목록 페이지
        r'^/bookstore/sale/\d+/progress/\d+/$',  # 진도 평가 상세 페이지
        r'^/bookstore/sale/\d+/progress/bulk-update/$',  # 일괄 평가 페이지
        r'^/accounts/',  # 로그인/로그아웃 관련 (django-allauth)
        r'^/login/$',  # 로그인
        r'^/logout/$',  # 로그아웃 (POST)
        r'^/teachers/login/$',  # 교사 로그인 페이지
        r'^/static/',  # 정적 파일
        r'^/media/',  # 미디어 파일
        r'^/__debug__/',  # 디버그 툴바
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
                return redirect('progress:my_progress')

            # 허용된 경로인지 확인
            if not self._is_allowed_path(path):
                messages.warning(request, '접근 권한이 없습니다. 교사 포털에서 내 수업 정보만 확인할 수 있습니다.')
                return redirect('progress:my_progress')

        return self.get_response(request)

    def _is_allowed_path(self, path):
        """경로가 허용된 패턴과 일치하는지 확인"""
        for pattern in self.allowed_patterns:
            if pattern.match(path):
                return True
        return False
