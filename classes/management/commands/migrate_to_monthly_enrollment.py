"""
기존 Enrollment (end_date 방식) → MonthlyEnrollment 데이터 마이그레이션

사용법:
  python manage.py migrate_to_monthly_enrollment
      → 오늘 기준 이번 달 + 다음 달을 자동 처리

  python manage.py migrate_to_monthly_enrollment --year 2026 --month 4
      → 특정 연/월만 처리

  python manage.py migrate_to_monthly_enrollment --year 2026 --month 4 --status confirmed
      → 생성 시 상태를 confirmed 로 지정 (기본: confirmed)
"""

import calendar
import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q

from classes.models import Enrollment, MonthlyEnrollment


class Command(BaseCommand):
    help = '기존 Enrollment 데이터를 MonthlyEnrollment 으로 마이그레이션합니다.'

    def add_arguments(self, parser):
        parser.add_argument('--year',  type=int, default=None, help='대상 연도 (기본: 이번 달 + 다음 달)')
        parser.add_argument('--month', type=int, default=None, help='대상 월 (기본: 이번 달 + 다음 달)')
        parser.add_argument(
            '--status',
            choices=['confirmed', 'pending'],
            default='confirmed',
            help='생성할 MonthlyEnrollment 상태 (기본: confirmed)',
        )

    def handle(self, *args, **options):
        today = datetime.date.today()
        target_status = options['status']

        # 대상 연/월 목록 결정
        if options['year'] and options['month']:
            targets = [(options['year'], options['month'])]
        else:
            # 기본: 이번 달 + 다음 달
            this_year, this_month = today.year, today.month
            if this_month == 12:
                next_year, next_month = this_year + 1, 1
            else:
                next_year, next_month = this_year, this_month + 1
            targets = [(this_year, this_month), (next_year, next_month)]

        for year, month in targets:
            self.stdout.write(f'\n▶ {year}년 {month}월 처리 중...')
            self._migrate_month(year, month, target_status)

        self.stdout.write(self.style.SUCCESS('\n✅ 마이그레이션 완료'))

    def _migrate_month(self, year, month, status):
        first_of_month = datetime.date(year, month, 1)

        # 해당 월에 활성인 Enrollment 조회
        # enrollment_date <= 해당 월 1일  AND  (end_date null 또는 end_date >= 해당 월 1일)
        active_enrollments = Enrollment.objects.filter(
            is_active=True,
            enrollment_date__lte=first_of_month,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=first_of_month)
        ).select_related('student', 'lesson')

        created = 0
        skipped = 0

        for enroll in active_enrollments:
            obj, was_created = MonthlyEnrollment.objects.get_or_create(
                student=enroll.student,
                lesson=enroll.lesson,
                year=year,
                month=month,
                defaults={
                    'status': status,
                    'tuition_adjustment': enroll.tuition_adjustment,
                    'memo': enroll.memo,
                },
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(
            f'  생성: {created}건, 이미 존재(스킵): {skipped}건 '
            f'(총 활성 수강: {active_enrollments.count()}건)'
        )
