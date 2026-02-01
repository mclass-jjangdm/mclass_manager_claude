"""
Google Drive API 서비스 모듈

교사/학생 폴더 관리, 파일 업로드, 폴더 공유 기능 제공
"""
import os
import logging
from io import BytesIO
from typing import Optional, List, Dict, Any

from django.conf import settings

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleDriveService:
    """Google Drive API 서비스 클래스"""

    FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'

    def __init__(self, delegated_user_email: str = None):
        """
        Google Drive 서비스 초기화

        Args:
            delegated_user_email: 도메인 전체 위임 시 사용할 사용자 이메일
        """
        self.service = None
        self.delegated_user_email = delegated_user_email or getattr(
            settings, 'GOOGLE_DELEGATED_USER_EMAIL', ''
        )
        self._initialize_service()

    def _initialize_service(self):
        """Google Drive API 서비스 초기화"""
        try:
            credentials_file = getattr(
                settings, 'GOOGLE_SERVICE_ACCOUNT_FILE', ''
            )

            if not credentials_file or not os.path.exists(credentials_file):
                logger.error(f'Google 서비스 계정 파일을 찾을 수 없습니다: {credentials_file}')
                return

            scopes = getattr(
                settings, 'GOOGLE_DRIVE_SCOPES',
                ['https://www.googleapis.com/auth/drive']
            )

            credentials = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=scopes
            )

            # 도메인 전체 위임 사용 시
            if self.delegated_user_email:
                credentials = credentials.with_subject(self.delegated_user_email)

            self.service = build('drive', 'v3', credentials=credentials)
            logger.info('Google Drive 서비스가 초기화되었습니다.')

        except Exception as e:
            logger.error(f'Google Drive 서비스 초기화 실패: {str(e)}')
            self.service = None

    def is_available(self) -> bool:
        """서비스 사용 가능 여부 확인"""
        return self.service is not None

    # ==========================================
    # 폴더 관리 기능
    # ==========================================

    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        파일/폴더 정보 조회

        Args:
            file_id: 파일 또는 폴더 ID

        Returns:
            파일 정보 {id, name, parents, webViewLink} 또는 None
        """
        if not self.is_available():
            return None

        try:
            file_info = self.service.files().get(
                fileId=file_id,
                fields='id, name, parents, webViewLink, mimeType'
            ).execute()
            return file_info
        except HttpError as e:
            logger.error(f'파일 정보 조회 실패: {str(e)}')
            return None

    def get_folder_path(self, folder_id: str) -> List[Dict[str, str]]:
        """
        폴더 경로(breadcrumb) 조회

        Args:
            folder_id: 폴더 ID

        Returns:
            경로 목록 [{id, name}, ...] (루트부터 현재 폴더까지)
        """
        if not self.is_available():
            return []

        path = []
        current_id = folder_id

        try:
            # 최대 10단계까지 탐색 (무한 루프 방지)
            for _ in range(10):
                if not current_id:
                    break

                file_info = self.service.files().get(
                    fileId=current_id,
                    fields='id, name, parents'
                ).execute()

                path.insert(0, {
                    'id': file_info.get('id'),
                    'name': file_info.get('name')
                })

                parents = file_info.get('parents', [])
                if parents:
                    current_id = parents[0]
                else:
                    break

            return path

        except HttpError as e:
            logger.error(f'폴더 경로 조회 실패: {str(e)}')
            return path

    def create_folder(
        self,
        name: str,
        parent_folder_id: str = None,
        description: str = ''
    ) -> Optional[str]:
        """
        폴더 생성

        Args:
            name: 폴더 이름
            parent_folder_id: 부모 폴더 ID (없으면 루트에 생성)
            description: 폴더 설명

        Returns:
            생성된 폴더 ID 또는 None
        """
        if not self.is_available():
            logger.error('Google Drive 서비스를 사용할 수 없습니다.')
            return None

        try:
            file_metadata = {
                'name': name,
                'mimeType': self.FOLDER_MIME_TYPE,
                'description': description,
            }

            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            elif getattr(settings, 'GOOGLE_DRIVE_ROOT_FOLDER_ID', ''):
                file_metadata['parents'] = [settings.GOOGLE_DRIVE_ROOT_FOLDER_ID]

            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()

            logger.info(f'폴더 생성 완료: {name} (ID: {folder.get("id")})')
            return folder.get('id')

        except HttpError as e:
            logger.error(f'폴더 생성 실패: {str(e)}')
            return None

    def find_folder(
        self,
        name: str,
        parent_folder_id: str = None
    ) -> Optional[str]:
        """
        폴더 이름으로 검색

        Args:
            name: 폴더 이름
            parent_folder_id: 부모 폴더 ID

        Returns:
            폴더 ID 또는 None
        """
        if not self.is_available():
            return None

        try:
            query = f"name='{name}' and mimeType='{self.FOLDER_MIME_TYPE}' and trashed=false"

            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            elif getattr(settings, 'GOOGLE_DRIVE_ROOT_FOLDER_ID', ''):
                query += f" and '{settings.GOOGLE_DRIVE_ROOT_FOLDER_ID}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()

            files = results.get('files', [])
            if files:
                return files[0].get('id')
            return None

        except HttpError as e:
            logger.error(f'폴더 검색 실패: {str(e)}')
            return None

    def get_or_create_folder(
        self,
        name: str,
        parent_folder_id: str = None,
        description: str = ''
    ) -> Optional[str]:
        """
        폴더가 있으면 ID 반환, 없으면 생성

        Args:
            name: 폴더 이름
            parent_folder_id: 부모 폴더 ID
            description: 폴더 설명

        Returns:
            폴더 ID 또는 None
        """
        folder_id = self.find_folder(name, parent_folder_id)
        if folder_id:
            return folder_id
        return self.create_folder(name, parent_folder_id, description)

    def list_folders(
        self,
        parent_folder_id: str = None,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        폴더 목록 조회

        Args:
            parent_folder_id: 부모 폴더 ID
            page_size: 페이지 크기

        Returns:
            폴더 목록 [{id, name, webViewLink}, ...]
        """
        if not self.is_available():
            return []

        try:
            query = f"mimeType='{self.FOLDER_MIME_TYPE}' and trashed=false"

            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            elif getattr(settings, 'GOOGLE_DRIVE_ROOT_FOLDER_ID', ''):
                query += f" and '{settings.GOOGLE_DRIVE_ROOT_FOLDER_ID}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, webViewLink)',
                pageSize=page_size,
                orderBy='name'
            ).execute()

            return results.get('files', [])

        except HttpError as e:
            logger.error(f'폴더 목록 조회 실패: {str(e)}')
            return []

    # ==========================================
    # 파일 업로드 기능
    # ==========================================

    def upload_file(
        self,
        file_path: str,
        folder_id: str = None,
        file_name: str = None,
        mime_type: str = None
    ) -> Optional[Dict[str, str]]:
        """
        로컬 파일 업로드

        Args:
            file_path: 로컬 파일 경로
            folder_id: 업로드할 폴더 ID
            file_name: 저장할 파일 이름 (None이면 원본 이름 사용)
            mime_type: MIME 타입 (None이면 자동 감지)

        Returns:
            {id, name, webViewLink} 또는 None
        """
        if not self.is_available():
            return None

        if not os.path.exists(file_path):
            logger.error(f'파일을 찾을 수 없습니다: {file_path}')
            return None

        try:
            file_metadata = {
                'name': file_name or os.path.basename(file_path)
            }

            if folder_id:
                file_metadata['parents'] = [folder_id]
            elif getattr(settings, 'GOOGLE_DRIVE_ROOT_FOLDER_ID', ''):
                file_metadata['parents'] = [settings.GOOGLE_DRIVE_ROOT_FOLDER_ID]

            media = MediaFileUpload(
                file_path,
                mimetype=mime_type,
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()

            logger.info(f'파일 업로드 완료: {file.get("name")} (ID: {file.get("id")})')
            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'webViewLink': file.get('webViewLink')
            }

        except HttpError as e:
            logger.error(f'파일 업로드 실패: {str(e)}')
            return None

    def upload_file_from_bytes(
        self,
        file_content: bytes,
        file_name: str,
        folder_id: str = None,
        mime_type: str = 'application/octet-stream'
    ) -> Optional[Dict[str, str]]:
        """
        바이트 데이터로 파일 업로드 (메모리에서 직접 업로드)

        Args:
            file_content: 파일 내용 (bytes)
            file_name: 파일 이름
            folder_id: 업로드할 폴더 ID
            mime_type: MIME 타입

        Returns:
            {id, name, webViewLink} 또는 None
        """
        if not self.is_available():
            return None

        try:
            file_metadata = {
                'name': file_name
            }

            if folder_id:
                file_metadata['parents'] = [folder_id]
            elif getattr(settings, 'GOOGLE_DRIVE_ROOT_FOLDER_ID', ''):
                file_metadata['parents'] = [settings.GOOGLE_DRIVE_ROOT_FOLDER_ID]

            media = MediaIoBaseUpload(
                BytesIO(file_content),
                mimetype=mime_type,
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()

            logger.info(f'파일 업로드 완료: {file.get("name")} (ID: {file.get("id")})')
            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'webViewLink': file.get('webViewLink')
            }

        except HttpError as e:
            logger.error(f'파일 업로드 실패: {str(e)}')
            return None

    def list_files(
        self,
        folder_id: str = None,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        폴더 내 파일 목록 조회

        Args:
            folder_id: 폴더 ID
            page_size: 페이지 크기

        Returns:
            파일 목록 [{id, name, mimeType, webViewLink, size}, ...]
        """
        if not self.is_available():
            return []

        try:
            query = f"mimeType!='{self.FOLDER_MIME_TYPE}' and trashed=false"

            if folder_id:
                query += f" and '{folder_id}' in parents"
            elif getattr(settings, 'GOOGLE_DRIVE_ROOT_FOLDER_ID', ''):
                query += f" and '{settings.GOOGLE_DRIVE_ROOT_FOLDER_ID}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, webViewLink, size, createdTime)',
                pageSize=page_size,
                orderBy='createdTime desc'
            ).execute()

            return results.get('files', [])

        except HttpError as e:
            logger.error(f'파일 목록 조회 실패: {str(e)}')
            return []

    # ==========================================
    # 공유 기능
    # ==========================================

    def share_with_user(
        self,
        file_id: str,
        email: str,
        role: str = 'reader',
        send_notification: bool = True
    ) -> bool:
        """
        파일/폴더를 특정 사용자와 공유

        Args:
            file_id: 파일 또는 폴더 ID
            email: 공유할 사용자 이메일
            role: 권한 ('reader', 'writer', 'commenter')
            send_notification: 알림 이메일 발송 여부

        Returns:
            성공 여부
        """
        if not self.is_available():
            return False

        try:
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }

            self.service.permissions().create(
                fileId=file_id,
                body=permission,
                sendNotificationEmail=send_notification,
                fields='id'
            ).execute()

            logger.info(f'공유 설정 완료: {file_id} -> {email} ({role})')
            return True

        except HttpError as e:
            logger.error(f'공유 설정 실패: {str(e)}')
            return False

    def share_with_anyone(
        self,
        file_id: str,
        role: str = 'reader'
    ) -> Optional[str]:
        """
        파일/폴더를 링크가 있는 모든 사용자와 공유

        Args:
            file_id: 파일 또는 폴더 ID
            role: 권한 ('reader', 'writer')

        Returns:
            공유 링크 또는 None
        """
        if not self.is_available():
            return None

        try:
            permission = {
                'type': 'anyone',
                'role': role
            }

            self.service.permissions().create(
                fileId=file_id,
                body=permission,
                fields='id'
            ).execute()

            # 웹 링크 가져오기
            file = self.service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()

            logger.info(f'공개 공유 설정 완료: {file_id}')
            return file.get('webViewLink')

        except HttpError as e:
            logger.error(f'공개 공유 설정 실패: {str(e)}')
            return None

    def remove_permission(
        self,
        file_id: str,
        email: str
    ) -> bool:
        """
        특정 사용자의 공유 권한 제거

        Args:
            file_id: 파일 또는 폴더 ID
            email: 권한을 제거할 사용자 이메일

        Returns:
            성공 여부
        """
        if not self.is_available():
            return False

        try:
            # 권한 목록 조회
            permissions = self.service.permissions().list(
                fileId=file_id,
                fields='permissions(id, emailAddress)'
            ).execute()

            # 해당 이메일의 권한 찾기
            for perm in permissions.get('permissions', []):
                if perm.get('emailAddress', '').lower() == email.lower():
                    self.service.permissions().delete(
                        fileId=file_id,
                        permissionId=perm.get('id')
                    ).execute()
                    logger.info(f'권한 제거 완료: {file_id} -> {email}')
                    return True

            logger.warning(f'해당 이메일의 권한을 찾을 수 없습니다: {email}')
            return False

        except HttpError as e:
            logger.error(f'권한 제거 실패: {str(e)}')
            return False

    # ==========================================
    # 삭제 기능
    # ==========================================

    def delete_file(self, file_id: str) -> bool:
        """
        파일/폴더 삭제 (휴지통으로 이동)

        Args:
            file_id: 파일 또는 폴더 ID

        Returns:
            성공 여부
        """
        if not self.is_available():
            return False

        try:
            self.service.files().update(
                fileId=file_id,
                body={'trashed': True}
            ).execute()

            logger.info(f'파일/폴더 삭제 완료: {file_id}')
            return True

        except HttpError as e:
            logger.error(f'파일/폴더 삭제 실패: {str(e)}')
            return False

    # ==========================================
    # MClass 전용 기능
    # ==========================================

    def setup_mclass_folder_structure(self) -> Dict[str, str]:
        """
        MClass 기본 폴더 구조 생성

        Returns:
            생성된 폴더 ID 딕셔너리 {folder_name: folder_id}
        """
        folder_ids = {}

        # 루트 폴더 생성/확인
        root_id = self.get_or_create_folder(
            'MClass Manager',
            description='MClass Manager 시스템 파일'
        )
        if root_id:
            folder_ids['root'] = root_id

            # 교사 폴더
            teachers_id = self.get_or_create_folder(
                '교사',
                parent_folder_id=root_id,
                description='교사별 급여명세서 및 문서'
            )
            if teachers_id:
                folder_ids['teachers'] = teachers_id

            # 학생 폴더
            students_id = self.get_or_create_folder(
                '학생',
                parent_folder_id=root_id,
                description='학생별 자료'
            )
            if students_id:
                folder_ids['students'] = students_id

            # 공유 폴더
            shared_id = self.get_or_create_folder(
                '공유자료',
                parent_folder_id=root_id,
                description='교사들과 공유하는 자료'
            )
            if shared_id:
                folder_ids['shared'] = shared_id

        return folder_ids

    def create_teacher_folder(
        self,
        teacher_name: str,
        teacher_email: str = None,
        teachers_root_id: str = None
    ) -> Optional[str]:
        """
        교사 개인 폴더 생성 및 공유 설정

        Args:
            teacher_name: 교사 이름
            teacher_email: 교사 이메일 (공유용)
            teachers_root_id: 교사 루트 폴더 ID

        Returns:
            생성된 폴더 ID 또는 None
        """
        folder_id = self.get_or_create_folder(
            teacher_name,
            parent_folder_id=teachers_root_id,
            description=f'{teacher_name} 선생님 개인 폴더'
        )

        if folder_id and teacher_email:
            self.share_with_user(folder_id, teacher_email, role='reader')

        return folder_id

    def create_student_folder(
        self,
        student_name: str,
        students_root_id: str = None
    ) -> Optional[str]:
        """
        학생 개인 폴더 생성

        Args:
            student_name: 학생 이름
            students_root_id: 학생 루트 폴더 ID

        Returns:
            생성된 폴더 ID 또는 None
        """
        return self.get_or_create_folder(
            student_name,
            parent_folder_id=students_root_id,
            description=f'{student_name} 학생 자료 폴더'
        )

    def upload_salary_pdf(
        self,
        pdf_content: bytes,
        teacher_name: str,
        year: int,
        month: int,
        teacher_folder_id: str
    ) -> Optional[Dict[str, str]]:
        """
        급여명세서 PDF 업로드

        Args:
            pdf_content: PDF 파일 내용 (bytes)
            teacher_name: 교사 이름
            year: 연도
            month: 월
            teacher_folder_id: 교사 폴더 ID

        Returns:
            업로드된 파일 정보 또는 None
        """
        file_name = f'{teacher_name}_{year}년_{month}월_급여명세서.pdf'

        return self.upload_file_from_bytes(
            file_content=pdf_content,
            file_name=file_name,
            folder_id=teacher_folder_id,
            mime_type='application/pdf'
        )
