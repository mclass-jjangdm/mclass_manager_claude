from django.core.management.base import BaseCommand

from students.models import Student
from students.drive import ensure_student_drive_folder


class Command(BaseCommand):
    help = '재원 중인 학생들에게 구글 드라이브 개인 폴더를 생성합니다 (이미 있으면 건너뜀).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='퇴원생을 포함한 전체 학생을 대상으로 실행합니다.',
        )

    def handle(self, *args, **options):
        queryset = Student.objects.all() if options['all'] else Student.objects.filter(is_active=True)

        created = 0
        skipped = 0
        failed = 0

        for student in queryset:
            if student.drive_folder_id:
                skipped += 1
                continue

            folder_id = ensure_student_drive_folder(student)
            if folder_id:
                created += 1
                self.stdout.write(f'생성: {student.name} ({student.student_id})')
            else:
                failed += 1
                self.stdout.write(self.style.WARNING(f'실패: {student.name} ({student.student_id})'))

        self.stdout.write(self.style.SUCCESS(
            f'완료 - 생성 {created}건, 이미 있음(건너뜀) {skipped}건, 실패 {failed}건'
        ))
