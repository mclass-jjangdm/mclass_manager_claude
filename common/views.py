import os
import subprocess
import logging
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

logger = logging.getLogger(__name__)


@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])  # GET -> POST로 변경 (보안 강화)
@csrf_protect
def db_backup(request):
    """
    데이터베이스 백업 다운로드 (관리자 전용)
    보안 개선사항:
    - POST 메서드만 허용
    - CSRF 토큰 필수
    - 비밀번호를 환경변수로 전달 (명령행 노출 방지)
    - 에러 메시지에서 상세 정보 제거
    """
    # 1. DB 설정 가져오기
    db_settings = settings.DATABASES['default']
    db_name = db_settings['NAME']
    db_user = db_settings['USER']
    db_password = db_settings['PASSWORD']
    db_host = db_settings['HOST']
    db_port = db_settings['PORT']

    # 2. 파일명 생성 (예: db_backup_2025_12_05.sql)
    filename = f"db_backup_{timezone.now().strftime('%Y_%m_%d')}.sql"

    # 3. mysqldump 명령어 실행
    # 비밀번호는 환경변수로 전달하여 프로세스 목록 노출 방지
    command = [
        'mysqldump',
        '-h', db_host,
        '-P', str(db_port),
        '-u', db_user,
        '--default-character-set=utf8mb4',
        '--skip-ssl',
        db_name
    ]

    # 환경변수에 비밀번호 설정 (명령행 노출 방지)
    env = os.environ.copy()
    env['MYSQL_PWD'] = db_password

    try:
        # 명령어를 실행하고 결과를 메모리로 가져옵니다.
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env  # 환경변수로 비밀번호 전달
        )
        output, error = process.communicate(timeout=300)  # 5분 타임아웃

        if process.returncode != 0:
            # 에러 로그는 서버에 기록하고, 사용자에게는 일반 메시지만 표시
            logger.error(f"DB backup failed: {error.decode('utf-8')}")
            return HttpResponse("백업 중 오류가 발생했습니다. 관리자에게 문의하세요.", status=500)

        # 보안 로그 기록
        logger.info(f"DB backup completed by user: {request.user.username}")

        # 4. 파일 다운로드 응답 생성
        response = HttpResponse(output, content_type='application/sql')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except subprocess.TimeoutExpired:
        logger.error("DB backup timed out")
        return HttpResponse("백업 시간이 초과되었습니다.", status=500)
    except Exception as e:
        logger.error(f"DB backup error: {str(e)}")
        return HttpResponse("서버 오류가 발생했습니다.", status=500)