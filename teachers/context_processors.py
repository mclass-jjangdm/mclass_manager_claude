# teachers/context_processors.py
# 교사 포털용 컨텍스트 프로세서

from .models import Message, MessageReadStatus


def teacher_notices(request):
    """
    교사 포털에서 전체 공지 메시지를 가져오는 컨텍스트 프로세서
    모든 공지를 표시하고, 각 공지의 읽음 상태를 함께 전달
    """
    notices = []
    unread_notice_count = 0

    if request.user.is_authenticated and hasattr(request.user, 'teacher_profile'):
        # 전체 공지 (recipient=None, message_type='instruction')
        # MySQL 호환성을 위해 list()로 먼저 평가
        all_notices = list(Message.objects.filter(
            recipient__isnull=True,
            message_type='instruction'
        ).order_by('-created_at')[:5])

        # 현재 사용자가 읽은 메시지 ID 목록
        notice_ids = [n.pk for n in all_notices]
        read_message_ids = set(MessageReadStatus.objects.filter(
            user=request.user,
            message_id__in=notice_ids
        ).values_list('message_id', flat=True))

        # 각 공지에 읽음 상태 추가
        for notice in all_notices:
            notice.is_read_by_user = notice.pk in read_message_ids

        # 모든 공지 표시 (읽음 여부 관계없이)
        notices = all_notices

        # 읽지 않은 전체 공지 수
        unread_notice_count = len([n for n in all_notices if not n.is_read_by_user])

    return {
        'global_notices': notices,
        'unread_notice_count': unread_notice_count,
    }
