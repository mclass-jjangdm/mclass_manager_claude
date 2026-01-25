# teachers/context_processors.py
# 교사 포털용 컨텍스트 프로세서

from .models import Message, MessageReadStatus


def teacher_notices(request):
    """
    교사 포털에서 전체 공지 메시지를 가져오는 컨텍스트 프로세서
    모든 공지를 표시하고, 각 공지의 읽음 상태를 함께 전달
    dismissed된 공지는 표시하지 않음
    """
    notices = []
    unread_notice_count = 0

    if request.user.is_authenticated and hasattr(request.user, 'teacher_profile'):
        # 전체 공지 (recipient=None, message_type='instruction')
        # MySQL 호환성을 위해 list()로 먼저 평가
        all_notices = list(Message.objects.filter(
            recipient__isnull=True,
            message_type='instruction'
        ).order_by('-created_at')[:10])  # dismissed 제외 후 5개를 위해 더 많이 가져옴

        # 현재 사용자의 읽음 상태 (dismissed 포함)
        notice_ids = [n.pk for n in all_notices]
        read_statuses = {
            rs.message_id: rs
            for rs in MessageReadStatus.objects.filter(
                user=request.user,
                message_id__in=notice_ids
            )
        }

        # dismissed되지 않은 공지만 표시, 최대 5개
        filtered_notices = []
        for notice in all_notices:
            status = read_statuses.get(notice.pk)
            # dismissed된 공지는 제외
            if status and status.dismissed:
                continue
            notice.is_read_by_user = status is not None
            filtered_notices.append(notice)
            if len(filtered_notices) >= 5:
                break

        notices = filtered_notices

        # 읽지 않은 전체 공지 수
        unread_notice_count = len([n for n in notices if not n.is_read_by_user])

    return {
        'global_notices': notices,
        'unread_notice_count': unread_notice_count,
    }
