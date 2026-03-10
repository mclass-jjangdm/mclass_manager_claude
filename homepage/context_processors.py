from .models import ConsultationRequest


def consultation_count(request):
    """모든 페이지에 신규 상담 신청 건수를 제공하는 context processor"""
    if request.user.is_authenticated and request.user.is_staff:
        new_count = ConsultationRequest.objects.filter(status='new').count()
        return {'new_consultation_count': new_count}
    return {'new_consultation_count': 0}
