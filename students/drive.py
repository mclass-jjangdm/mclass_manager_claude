"""학생 개인 구글 드라이브 폴더 연동 헬퍼"""
import logging

from django.conf import settings

from common.services import GoogleDriveService

logger = logging.getLogger(__name__)

STUDENTS_ROOT_FOLDER_NAME = '학생'


def ensure_student_drive_folder(student):
    """학생의 구글 드라이브 개인 폴더 ID를 반환. 없으면 생성 후 저장."""
    if student.drive_folder_id:
        return student.drive_folder_id

    drive_service = GoogleDriveService()
    if not drive_service.is_available():
        logger.warning(f'Google Drive 서비스를 사용할 수 없어 학생 폴더 생성을 건너뜁니다: {student.name}')
        return None

    students_root_id = drive_service.get_or_create_folder(
        STUDENTS_ROOT_FOLDER_NAME,
        parent_folder_id=getattr(settings, 'GOOGLE_DRIVE_ROOT_FOLDER_ID', '') or None,
        description='학생별 자료',
    )
    if not students_root_id:
        logger.error('학생 루트 폴더를 확보하지 못했습니다.')
        return None

    folder_id = drive_service.create_student_folder(student.folder_name, students_root_id)
    if not folder_id:
        logger.error(f'학생 개인 폴더 생성 실패: {student.name}')
        return None

    student.drive_folder_id = folder_id
    student.save(update_fields=['drive_folder_id'])
    return folder_id


def upload_file_to_student_folder(student, file_name, content, mime_type=None):
    """학생 개인 폴더에 파일 업로드. 폴더가 없으면 먼저 생성."""
    folder_id = ensure_student_drive_folder(student)
    if not folder_id:
        return None

    drive_service = GoogleDriveService()
    return drive_service.upload_file_from_bytes(
        file_content=content,
        file_name=file_name,
        folder_id=folder_id,
        mime_type=mime_type or 'application/octet-stream',
    )


def list_student_drive_files(student):
    """학생 개인 폴더 내 파일 목록 조회"""
    if not student.drive_folder_id:
        return []

    drive_service = GoogleDriveService()
    return drive_service.list_files(folder_id=student.drive_folder_id)


def get_student_drive_file(student, file_id):
    """파일이 실제로 이 학생의 폴더에 속하는지 확인 후 다운로드 데이터 반환"""
    if not student.drive_folder_id:
        return None

    drive_service = GoogleDriveService()
    file_info = drive_service.get_file_info(file_id)
    if not file_info or student.drive_folder_id not in file_info.get('parents', []):
        return None

    return drive_service.download_file(file_id)
