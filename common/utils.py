"""
공통 유틸리티 함수들
"""
import os
import logging
import requests
from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


# ============================================
# 파일 업로드 보안 유틸리티
# ============================================

def validate_file_extension(filename, allowed_extensions=None):
    """
    파일 확장자 검증

    Args:
        filename: 파일명
        allowed_extensions: 허용된 확장자 집합 (기본값: settings.ALLOWED_UPLOAD_EXTENSIONS)

    Raises:
        ValidationError: 허용되지 않은 확장자인 경우
    """
    if allowed_extensions is None:
        allowed_extensions = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS', {
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'jpg', 'jpeg', 'png', 'gif', 'bmp',
            'txt', 'csv', 'hwp', 'zip'
        })

    ext = filename.split('.')[-1].lower() if '.' in filename else ''

    if ext not in allowed_extensions:
        raise ValidationError(
            f"허용되지 않는 파일 형식입니다. 허용된 형식: {', '.join(sorted(allowed_extensions))}"
        )

    return ext


def validate_file_size(file, max_size=None):
    """
    파일 크기 검증

    Args:
        file: 업로드된 파일 객체
        max_size: 최대 파일 크기 (바이트, 기본값: settings.MAX_UPLOAD_SIZE)

    Raises:
        ValidationError: 파일 크기 초과 시
    """
    if max_size is None:
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)  # 10MB

    if file.size > max_size:
        max_mb = max_size / (1024 * 1024)
        file_mb = file.size / (1024 * 1024)
        raise ValidationError(
            f"파일 크기가 너무 큽니다. (최대 {max_mb:.1f}MB, 현재 {file_mb:.1f}MB)"
        )


def validate_file_content_type(file, allowed_mime_types=None):
    """
    파일 MIME 타입 검증 (Content-Type 헤더 기반)

    Args:
        file: 업로드된 파일 객체
        allowed_mime_types: 허용된 MIME 타입 집합

    Raises:
        ValidationError: 허용되지 않은 MIME 타입인 경우
    """
    if allowed_mime_types is None:
        allowed_mime_types = getattr(settings, 'ALLOWED_UPLOAD_MIME_TYPES', {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'image/jpeg',
            'image/png',
            'image/gif',
            'text/plain',
            'text/csv',
        })

    content_type = getattr(file, 'content_type', '')

    # application/octet-stream은 알 수 없는 타입이므로 확장자 기반으로 허용
    if content_type == 'application/octet-stream':
        logger.warning(f"File {file.name} has generic content type, relying on extension validation")
        return

    if content_type and content_type not in allowed_mime_types:
        raise ValidationError(
            f"허용되지 않는 파일 타입입니다. (타입: {content_type})"
        )


def validate_uploaded_file(file, allowed_extensions=None, max_size=None, allowed_mime_types=None):
    """
    업로드된 파일 종합 검증

    Args:
        file: 업로드된 파일 객체
        allowed_extensions: 허용된 확장자 집합
        max_size: 최대 파일 크기 (바이트)
        allowed_mime_types: 허용된 MIME 타입 집합

    Raises:
        ValidationError: 검증 실패 시
    """
    # 확장자 검증
    validate_file_extension(file.name, allowed_extensions)

    # 파일 크기 검증
    validate_file_size(file, max_size)

    # MIME 타입 검증
    validate_file_content_type(file, allowed_mime_types)

    return True


def sanitize_filename(filename):
    """
    파일명 안전하게 처리 (경로 탐색 공격 방지)

    Args:
        filename: 원본 파일명

    Returns:
        안전한 파일명
    """
    # 경로 구분자 제거
    filename = os.path.basename(filename)

    # 위험한 문자 제거
    dangerous_chars = ['..', '/', '\\', '\x00', '\n', '\r']
    for char in dangerous_chars:
        filename = filename.replace(char, '')

    # 빈 파일명 방지
    if not filename:
        filename = 'unnamed_file'

    return filename


def send_sms(phone_number, message, msg_type='SMS'):
    """
    Aligo SMS API를 사용한 문자 발송 함수

    Args:
        phone_number (str): 수신자 전화번호 (하이픈 제거된 형태)
        message (str): 발송할 메시지
        msg_type (str): 메시지 타입 ('SMS', 'LMS', 'MMS')

    Returns:
        tuple: (성공 여부, 메시지)
    """
    # SMS API 설정
    api_key = getattr(settings, 'SMS_API_KEY', None)
    userid = getattr(settings, 'SMS_USER_ID', None)
    sender_number = getattr(settings, 'SMS_SENDER_NUMBER', None)
    send_url = 'https://apis.aligo.in/send/'

    if not all([api_key, userid, sender_number]):
        return False, "SMS API 설정이 완료되지 않았습니다. (API KEY, USER ID, 발신번호 필요)"

    # 전화번호 유효성 검사
    if not phone_number or len(phone_number) < 10:
        return False, "유효하지 않은 전화번호입니다."

    # 메시지 길이에 따라 자동으로 SMS/LMS 결정
    if msg_type == 'SMS' and len(message.encode('utf-8')) > 90:
        msg_type = 'LMS'

    try:
        # Aligo API 규격에 맞춘 데이터
        sms_data = {
            'key': api_key,
            'userid': userid,
            'sender': sender_number,
            'receiver': phone_number,
            'msg': message,
            'msg_type': msg_type,
        }

        # LMS인 경우 제목 추가
        if msg_type == 'LMS':
            sms_data['title'] = message[:20]  # 메시지 앞 20자를 제목으로

        # API 호출
        response = requests.post(send_url, data=sms_data, timeout=10)
        result = response.json()

        # 결과 확인
        if result.get('result_code') == '1':
            return True, "문자가 발송되었습니다."
        else:
            error_msg = result.get('message', '알 수 없는 오류')
            return False, f"발송 실패: {error_msg}"

    except requests.exceptions.Timeout:
        return False, "발송 시간 초과"
    except requests.exceptions.RequestException as e:
        return False, f"네트워크 오류: {str(e)}"
    except Exception as e:
        return False, f"오류 발생: {str(e)}"


def send_sms_bulk(recipients_data, message, msg_type='SMS'):
    """
    Aligo SMS API를 사용한 대량 문자 발송 함수

    Args:
        recipients_data (list): 수신자 정보 리스트 [{'phone': '01012345678', 'name': '홍길동'}, ...]
        message (str): 발송할 메시지
        msg_type (str): 메시지 타입 ('SMS', 'LMS')

    Returns:
        tuple: (성공 건수, 실패 목록)
    """
    # SMS API 설정
    api_key = getattr(settings, 'SMS_API_KEY', None)
    userid = getattr(settings, 'SMS_USER_ID', None)
    sender_number = getattr(settings, 'SMS_SENDER_NUMBER', None)
    mass_send_url = 'https://apis.aligo.in/send_mass/'

    if not all([api_key, userid, sender_number]):
        return 0, ["SMS API 설정이 완료되지 않았습니다."]

    # 메시지 길이에 따라 자동으로 SMS/LMS 결정
    if msg_type == 'SMS' and len(message.encode('utf-8')) > 90:
        msg_type = 'LMS'

    try:
        # Aligo 대량 발송 API 규격에 맞춘 데이터
        sms_data = {
            'key': api_key,
            'userid': userid,
            'sender': sender_number,
            'cnt': len(recipients_data),
            'msg_type': msg_type,
        }

        # LMS인 경우 제목 추가
        if msg_type == 'LMS':
            sms_data['title'] = message[:20]

        # 각 수신자별 데이터 추가
        for idx, recipient in enumerate(recipients_data, start=1):
            sms_data[f'rec_{idx}'] = recipient['phone']
            # 이름 치환이 있는 경우
            if '%이름%' in message or '%고객명%' in message:
                custom_msg = message.replace('%이름%', recipient.get('name', ''))
                custom_msg = custom_msg.replace('%고객명%', recipient.get('name', ''))
                sms_data[f'msg_{idx}'] = custom_msg
            else:
                sms_data[f'msg_{idx}'] = message

        # API 호출
        response = requests.post(mass_send_url, data=sms_data, timeout=30)
        result = response.json()

        # 결과 확인
        if result.get('result_code') == '1':
            success_count = int(result.get('success_cnt', 0))
            return success_count, []
        else:
            error_msg = result.get('message', '알 수 없는 오류')
            return 0, [f"발송 실패: {error_msg}"]

    except requests.exceptions.Timeout:
        return 0, ["발송 시간 초과"]
    except requests.exceptions.RequestException as e:
        return 0, [f"네트워크 오류: {str(e)}"]
    except Exception as e:
        return 0, [f"오류 발생: {str(e)}"]


def get_sms_remain():
    """
    SMS 발송 가능 건수 조회

    Returns:
        dict: {'SMS': 건수, 'LMS': 건수, 'MMS': 건수} 또는 None
    """
    api_key = getattr(settings, 'SMS_API_KEY', None)
    userid = getattr(settings, 'SMS_USER_ID', None)
    remain_url = 'https://apis.aligo.in/remain/'

    if not all([api_key, userid]):
        return None

    try:
        remain_data = {
            'key': api_key,
            'userid': userid,
        }

        response = requests.post(remain_url, data=remain_data, timeout=10)
        result = response.json()

        if result.get('result_code') == '1':
            return {
                'SMS': int(result.get('SMS_CNT', 0)),
                'LMS': int(result.get('LMS_CNT', 0)),
                'MMS': int(result.get('MMS_CNT', 0)),
            }
        return None

    except Exception:
        return None
