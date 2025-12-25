"""
공통 유틸리티 함수들
"""
import requests
from django.conf import settings


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
