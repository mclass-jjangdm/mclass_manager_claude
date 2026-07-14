"""
신학년도 학생 학년 진급 처리 명령어

매년 새 학년 시작 시 모든 재원생의 grade를 한 단계씩 올린다.
(K5→K6→K7→K8→K9→K10→K11→K12, K12는 졸업 처리 대상이므로 자동 진급하지 않음)

사용법:
  # 진급 대상 미리보기 (수정 없음)
  python manage.py promote_grades

  # 실제 진급 처리
  python manage.py promote_grades --apply
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from students.models import Student

GRADE_ORDER = ['K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11', 'K12']


class Command(BaseCommand):
    help = '재원생 학년을 한 단계씩 진급 처리 (K12는 졸업 대상이라 제외)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='실제로 저장. 지정하지 않으면 진급 대상만 미리보기.',
        )

    def handle(self, *args, **options):
        promotable = Student.objects.filter(
            is_active=True, grade__in=GRADE_ORDER[:-1]
        ).order_by('grade', 'name')

        graduating = Student.objects.filter(is_active=True, grade='K12').order_by('name')

        if not promotable.exists():
            self.stdout.write(self.style.SUCCESS('진급 대상 없음.'))
        else:
            self.stdout.write(f'진급 대상 {promotable.count()}명:')
            for s in promotable:
                next_grade = GRADE_ORDER[GRADE_ORDER.index(s.grade) + 1]
                self.stdout.write(f'  {s.name} (pk={s.pk})  {s.grade} → {next_grade}')

        if graduating.exists():
            self.stdout.write(self.style.WARNING(
                f'\nK12(고3) {graduating.count()}명은 자동 진급 대상이 아닙니다. '
                '졸업 처리가 필요하면 수동으로 확인하세요:'
            ))
            for s in graduating:
                self.stdout.write(f'  {s.name} (pk={s.pk})')

        if not options['apply']:
            self.stdout.write('\n실제로 적용하려면 --apply 옵션을 추가하세요.')
            return

        with transaction.atomic():
            updated = 0
            for s in promotable:
                s.grade = GRADE_ORDER[GRADE_ORDER.index(s.grade) + 1]
                s.save(update_fields=['grade'])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'\n{updated}명 진급 처리 완료.'))
