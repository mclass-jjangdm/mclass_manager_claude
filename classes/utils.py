import calendar
from datetime import date, timedelta
from django.db.models import Sum


DAY_CODE = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}


def _class_days_in_month(lesson, year, month):
    """해당 월에 수업이 있는 날짜 목록 반환"""
    schedule_weekdays = {DAY_CODE[s.day] for s in lesson.schedules.all()}
    if not schedule_weekdays:
        return []
    _, last_day = calendar.monthrange(year, month)
    return [
        date(year, month, d)
        for d in range(1, last_day + 1)
        if date(year, month, d).weekday() in schedule_weekdays
    ]


def _class_days_in_range(lesson, start, end):
    """해당 기간(start~end, 양끝 포함)에 수업이 있는 날짜 목록 반환"""
    schedule_weekdays = {DAY_CODE[s.day] for s in lesson.schedules.all()}
    if not schedule_weekdays or start > end:
        return []
    return [
        d for d in (start + timedelta(days=i) for i in range((end - start).days + 1))
        if d.weekday() in schedule_weekdays
    ]


def calculate_prorated_tuition(lesson, year, month, start_date):
    """
    수강 시작일 기준 일할 수강료 계산.
    시작일 이후(포함) 수업 일수 / 월 전체 수업 일수 × 기본 수강료
    수업 일정이 없거나 해당 월이 아닌 경우 base_tuition 반환.
    """
    all_days = _class_days_in_month(lesson, year, month)
    total = len(all_days)
    if total == 0:
        return lesson.base_tuition

    payable_days = sum(1 for d in all_days if d >= start_date)
    if payable_days == total:
        return lesson.base_tuition

    raw = lesson.base_tuition * payable_days / total
    return round(raw / 1000) * 1000


def calculate_refund(enrollment, quit_date):
    """
    퇴원일 기준 환불 금액 계산.

    특별 수업(is_special)은 수업 기간이 월 경계를 넘나들거나 한 달보다
    훨씬 짧을 수 있어, 퇴원월의 달력 기준이 아니라 수업 시작일~종료일
    전체 기간을 기준으로 계산한다. 일반 수업은 퇴원월 1개월 기준.

    환불 정책 (법정 기준):
    - 수업일의 1/3 미만 수강 → 전액 환불
    - 수업일의 1/3 이상 1/2 미만 수강 → 50% 환불
    - 수업일의 1/2 이상 수강 → 환불 없음
    """
    from classes.models import MonthlyEnrollment, TuitionPayment

    year, month = quit_date.year, quit_date.month
    lesson = enrollment.lesson

    if lesson.is_special and lesson.start_date and lesson.end_date:
        all_days = _class_days_in_range(lesson, lesson.start_date, lesson.end_date)
    else:
        all_days = _class_days_in_month(lesson, year, month)
    total = len(all_days)

    if total == 0:
        return {
            'total_days': 0,
            'passed_days': 0,
            'ratio': 0,
            'tuition': 0,
            'refund_amount': 0,
            'refund_rate': 0,
            'policy': '수업 일정 없음',
        }

    passed_days = sum(1 for d in all_days if d <= quit_date)
    ratio = passed_days / total  # 수강 비율

    # MonthlyEnrollment에서 해당 월 수강료 조회
    try:
        me = MonthlyEnrollment.objects.get(
            student=enrollment.student,
            lesson=lesson,
            year=year,
            month=month,
        )
        tuition = me.adjusted_tuition
    except MonthlyEnrollment.DoesNotExist:
        tuition = enrollment.adjusted_tuition

    # 이미 납부한 금액 확인
    paid = TuitionPayment.objects.filter(
        enrollment=enrollment,
        year=year,
        month=month,
    ).aggregate(total=Sum('amount'))['total'] or 0

    if ratio < 1 / 3:
        refund_rate = 100
        policy = f'수업일 1/3 미만 수강 ({passed_days}/{total}일) → 전액 환불'
    elif ratio < 1 / 2:
        refund_rate = 50
        policy = f'수업일 1/3~1/2 수강 ({passed_days}/{total}일) → 50% 환불'
    else:
        refund_rate = 0
        policy = f'수업일 1/2 이상 수강 ({passed_days}/{total}일) → 환불 없음'

    # 실제 납부액을 초과해 환불할 수 없음 (청구가 삭제/취소된 달은 paid=0 → 환불 없음)
    refund_amount = min(round(tuition * refund_rate / 100), paid)
    if paid == 0:
        policy += ' (납부 내역 없음 → 환불 없음)'

    return {
        'total_days': total,
        'passed_days': passed_days,
        'ratio': ratio,
        'tuition': tuition,
        'paid': paid,
        'refund_rate': refund_rate,
        'refund_amount': refund_amount,
        'policy': policy,
    }
