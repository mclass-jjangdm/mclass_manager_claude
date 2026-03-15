from .models import ConsultationRequest, VisitorStat


def consultation_count(request):
    """모든 페이지에 신규 상담 신청 건수를 제공하는 context processor"""
    if request.user.is_authenticated and request.user.is_staff:
        new_count = ConsultationRequest.objects.filter(status='new').count()
        return {'new_consultation_count': new_count}
    return {'new_consultation_count': 0}


def visitor_counter(request):
    """방문자 수 카운트 및 제공 (homepage app 공개 페이지 전용)"""
    # homepage app의 GET 요청에만 카운트
    try:
        app_name = request.resolver_match.app_name if request.resolver_match else ''
    except Exception:
        app_name = ''

    if request.method == 'GET' and app_name == 'homepage':
        try:
            VisitorStat.record_visit(request.session)
        except Exception:
            pass

    # 방문자 통계 데이터 제공 (항상)
    try:
        today_count, total_count = VisitorStat.get_stats()
    except Exception:
        today_count, total_count = 0, 0

    return {
        'visitor_today': today_count,
        'visitor_total': total_count,
    }
