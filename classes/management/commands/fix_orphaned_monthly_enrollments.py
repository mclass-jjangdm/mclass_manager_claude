"""
고아 MonthlyEnrollment 탐지 및 수정 명령어

'고아' = MonthlyEnrollment는 있으나 해당 (student, lesson) 쌍의 Enrollment가 없는 레코드.
이 상태에서는 student_detail 수납 현황 카드에 납부 버튼이 나타나지 않는다.

사용법:
  # 고아 현황만 출력 (수정 없음)
  python manage.py fix_orphaned_monthly_enrollments

  # 고아 MonthlyEnrollment를 cancelled 처리
  python manage.py fix_orphaned_monthly_enrollments --action cancel

  # 고아 Enrollment를 비활성(is_active=False)으로 재생성 (납부 처리 가능하게 복구)
  python manage.py fix_orphaned_monthly_enrollments --action restore
"""
from django.core.management.base import BaseCommand
from django.db.models import Subquery, OuterRef

from classes.models import Enrollment, MonthlyEnrollment


class Command(BaseCommand):
    help = '고아 MonthlyEnrollment(Enrollment 없는 레코드) 탐지 및 수정'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            choices=['cancel', 'restore'],
            default=None,
            help=(
                'cancel: 고아 MonthlyEnrollment를 cancelled 처리\n'
                'restore: 누락된 Enrollment를 비활성으로 재생성 (납부 버튼 복구)'
            ),
        )

    def handle(self, *args, **options):
        # Enrollment가 존재하는 (student_id, lesson_id) 쌍
        existing_pairs = set(
            Enrollment.objects.values_list('student_id', 'lesson_id')
        )

        # 모든 non-cancelled MonthlyEnrollment
        orphans = [
            me for me in MonthlyEnrollment.objects.exclude(status='cancelled')
                                                   .select_related('student', 'lesson')
            if (me.student_id, me.lesson_id) not in existing_pairs
        ]

        if not orphans:
            self.stdout.write(self.style.SUCCESS('고아 MonthlyEnrollment 없음. 데이터 정상.'))
            return

        self.stdout.write(self.style.WARNING(f'고아 MonthlyEnrollment {len(orphans)}건 발견:'))
        for me in orphans:
            self.stdout.write(
                f'  pk={me.pk}  {me.student.name} / {me.lesson.name}  '
                f'{me.year}년 {me.month}월  status={me.status}'
            )

        action = options['action']
        if action is None:
            self.stdout.write('\n수정하려면 --action cancel 또는 --action restore 옵션을 추가하세요.')
            return

        if action == 'cancel':
            pks = [me.pk for me in orphans]
            updated = MonthlyEnrollment.objects.filter(pk__in=pks).update(status='cancelled')
            self.stdout.write(self.style.SUCCESS(f'{updated}건을 cancelled 처리했습니다.'))

        elif action == 'restore':
            created = 0
            for me in orphans:
                _, made = Enrollment.objects.get_or_create(
                    student=me.student,
                    lesson=me.lesson,
                    defaults={
                        'enrollment_date': me.created_at.date() if me.created_at else me.lesson.created_at.date(),
                        'is_active': False,
                    },
                )
                if made:
                    created += 1
                    self.stdout.write(
                        f'  Enrollment 생성: {me.student.name} / {me.lesson.name} (is_active=False)'
                    )
                else:
                    self.stdout.write(
                        f'  이미 존재(스킵): {me.student.name} / {me.lesson.name}'
                    )
            self.stdout.write(self.style.SUCCESS(f'Enrollment {created}건 재생성 완료.'))
