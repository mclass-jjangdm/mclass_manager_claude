import os
import subprocess
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods

@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["GET"])
def db_backup(request):
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
    # 주의: 웹 컨테이너에서 DB 컨테이너로 접속하므로 host 설정이 중요합니다.
    command = [
        'mysqldump',
        '-h', db_host,
        '-P', str(db_port),
        '-u', db_user,
        f'-p{db_password}',  # 비밀번호 사이에 공백 없어야 함
        '--default-character-set=utf8mb4', # 한글 깨짐 방지
        '--skip-ssl',
        db_name
    ]

    try:
        # 명령어를 실행하고 결과를 메모리로 가져옵니다.
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, error = process.communicate()

        if process.returncode != 0:
            return HttpResponse(f"백업 중 오류가 발생했습니다: {error.decode('utf-8')}", status=500)

        # 4. 파일 다운로드 응답 생성
        response = HttpResponse(output, content_type='application/sql')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        return HttpResponse(f"서버 오류: {str(e)}", status=500)