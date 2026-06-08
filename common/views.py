import os
import subprocess
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_protect

from .services import GoogleDriveService

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


# ============================================
# Google Drive 관리 뷰
# ============================================

@login_required
@staff_member_required
def google_drive_dashboard(request):
    """Google Drive 관리 대시보드"""
    drive_service = GoogleDriveService()

    context = {
        'is_available': drive_service.is_available(),
        'folders': [],
        'error_message': None,
    }

    if not drive_service.is_available():
        context['error_message'] = 'Google Drive API가 설정되지 않았습니다. 서비스 계정 JSON 파일을 확인하세요.'
    else:
        # 루트 폴더 목록 조회
        context['folders'] = drive_service.list_folders()

    return render(request, 'common/google_drive_dashboard.html', context)


@login_required
@staff_member_required
@require_POST
def google_drive_setup(request):
    """MClass 폴더 구조 초기화"""
    drive_service = GoogleDriveService()

    if not drive_service.is_available():
        messages.error(request, 'Google Drive API를 사용할 수 없습니다.')
        return redirect('google_drive_dashboard')

    folder_ids = drive_service.setup_mclass_folder_structure()

    if folder_ids:
        messages.success(request, f'폴더 구조가 생성되었습니다. (생성된 폴더: {len(folder_ids)}개)')
    else:
        messages.error(request, '폴더 구조 생성에 실패했습니다.')

    return redirect('google_drive_dashboard')


@login_required
@staff_member_required
def google_drive_folder_detail(request, folder_id):
    """폴더 상세 보기 (파일 및 하위 폴더 목록)"""
    drive_service = GoogleDriveService()

    if not drive_service.is_available():
        messages.error(request, 'Google Drive API를 사용할 수 없습니다.')
        return redirect('google_drive_dashboard')

    # 현재 폴더 정보 및 경로 조회
    current_folder = drive_service.get_file_info(folder_id)
    folder_path = drive_service.get_folder_path(folder_id)

    context = {
        'folder_id': folder_id,
        'current_folder': current_folder,
        'folder_path': folder_path,
        'folders': drive_service.list_folders(parent_folder_id=folder_id),
        'files': drive_service.list_files(folder_id=folder_id),
    }

    return render(request, 'common/google_drive_folder_detail.html', context)


@login_required
@staff_member_required
@require_POST
def google_drive_create_folder(request):
    """폴더 생성"""
    drive_service = GoogleDriveService()

    if not drive_service.is_available():
        messages.error(request, 'Google Drive API를 사용할 수 없습니다.')
        return redirect('google_drive_dashboard')

    folder_name = request.POST.get('folder_name', '').strip()
    parent_folder_id = request.POST.get('parent_folder_id', '').strip() or None

    if not folder_name:
        messages.error(request, '폴더 이름을 입력하세요.')
        if parent_folder_id:
            return redirect('google_drive_folder_detail', folder_id=parent_folder_id)
        return redirect('google_drive_dashboard')

    folder_id = drive_service.create_folder(folder_name, parent_folder_id)

    if folder_id:
        messages.success(request, f'폴더 "{folder_name}"가 생성되었습니다.')
        # 생성된 폴더로 이동
        return redirect('google_drive_folder_detail', folder_id=folder_id)
    else:
        messages.error(request, '폴더 생성에 실패했습니다.')
        if parent_folder_id:
            return redirect('google_drive_folder_detail', folder_id=parent_folder_id)
        return redirect('google_drive_dashboard')


@login_required
@staff_member_required
@require_POST
def google_drive_upload_file(request):
    """파일 업로드"""
    import logging
    logger = logging.getLogger(__name__)

    drive_service = GoogleDriveService()

    if not drive_service.is_available():
        logger.error('Google Drive API를 사용할 수 없습니다.')
        messages.error(request, 'Google Drive API를 사용할 수 없습니다.')
        return redirect('google_drive_dashboard')

    folder_id = request.POST.get('folder_id', '').strip() or None
    uploaded_file = request.FILES.get('file')

    logger.info(f'파일 업로드 시도: folder_id={folder_id}, file={uploaded_file}')

    if not uploaded_file:
        messages.error(request, '파일을 선택하세요.')
        return redirect('google_drive_dashboard')

    # 파일 크기 검사
    if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
        messages.error(request, f'파일 크기가 너무 큽니다. (최대: {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB)')
        return redirect('google_drive_dashboard')

    logger.info(f'파일 정보: name={uploaded_file.name}, size={uploaded_file.size}, content_type={uploaded_file.content_type}')

    try:
        file_content = uploaded_file.read()
        logger.info(f'파일 읽기 완료: {len(file_content)} bytes')

        result = drive_service.upload_file_from_bytes(
            file_content=file_content,
            file_name=uploaded_file.name,
            folder_id=folder_id,
            mime_type=uploaded_file.content_type
        )
        logger.info(f'업로드 결과: {result}')
    except Exception as e:
        logger.error(f'파일 업로드 중 예외 발생: {str(e)}', exc_info=True)
        result = None

    if result:
        messages.success(request, f'파일 "{uploaded_file.name}"가 업로드되었습니다.')
    else:
        messages.error(request, '파일 업로드에 실패했습니다.')

    if folder_id:
        return redirect('google_drive_folder_detail', folder_id=folder_id)
    return redirect('google_drive_dashboard')


@login_required
@staff_member_required
@require_POST
def google_drive_share_folder(request):
    """폴더 공유"""
    drive_service = GoogleDriveService()

    if not drive_service.is_available():
        return JsonResponse({'success': False, 'error': 'API를 사용할 수 없습니다.'})

    folder_id = request.POST.get('folder_id', '').strip()
    email = request.POST.get('email', '').strip()
    role = request.POST.get('role', 'reader')

    if not folder_id or not email:
        return JsonResponse({'success': False, 'error': '필수 정보가 누락되었습니다.'})

    success = drive_service.share_with_user(folder_id, email, role)

    if success:
        return JsonResponse({'success': True, 'message': f'{email}에게 공유되었습니다.'})
    else:
        return JsonResponse({'success': False, 'error': '공유 설정에 실패했습니다.'})


@login_required
@staff_member_required
@require_POST
def google_drive_delete(request, file_id):
    """파일/폴더 삭제"""
    drive_service = GoogleDriveService()

    if not drive_service.is_available():
        messages.error(request, 'Google Drive API를 사용할 수 없습니다.')
        return redirect('google_drive_dashboard')

    success = drive_service.delete_file(file_id)

    if success:
        messages.success(request, '삭제되었습니다.')
    else:
        messages.error(request, '삭제에 실패했습니다.')

    return redirect(request.META.get('HTTP_REFERER', 'google_drive_dashboard'))


@login_required
@user_passes_test(lambda u: u.is_staff)
def seal_upload(request):
    """학원장 직인 이미지 업로드 (관리자 전용)"""
    SEAL_FILENAME = 'signature'
    ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg')

    # 현재 직인 파일 경로 탐색
    current_seal = None
    for ext in ALLOWED_EXTENSIONS:
        path = os.path.join(settings.MEDIA_ROOT, f'{SEAL_FILENAME}.{ext}')
        if os.path.exists(path):
            current_seal = f'{settings.MEDIA_URL}{SEAL_FILENAME}.{ext}'
            break

    if request.method == 'POST':
        uploaded = request.FILES.get('seal_image')
        if not uploaded:
            messages.error(request, '파일을 선택해 주세요.')
            return redirect('seal_upload')

        ext = uploaded.name.rsplit('.', 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            messages.error(request, 'PNG 또는 JPG 파일만 업로드 가능합니다.')
            return redirect('seal_upload')

        # 기존 직인 파일 모두 삭제
        for old_ext in ALLOWED_EXTENSIONS:
            old_path = os.path.join(settings.MEDIA_ROOT, f'{SEAL_FILENAME}.{old_ext}')
            if os.path.exists(old_path):
                os.remove(old_path)

        save_path = os.path.join(settings.MEDIA_ROOT, f'{SEAL_FILENAME}.{ext}')
        with open(save_path, 'wb') as f:
            for chunk in uploaded.chunks():
                f.write(chunk)

        messages.success(request, f'직인 이미지가 업로드되었습니다. ({uploaded.name})')
        return redirect('seal_upload')

    return render(request, 'common/seal_upload.html', {'current_seal': current_seal})