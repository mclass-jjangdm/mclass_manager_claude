import csv
import os
from django.core.management.base import BaseCommand
from subjects.models import Subject


class Command(BaseCommand):
    help = 'Import subjects from subject_list.csv'

    def handle(self, *args, **options):
        # CSV 파일 경로 (Django 프로젝트 루트)
        from django.conf import settings
        # Docker 환경에서는 /app/subject_list.csv
        csv_file = os.path.join(settings.BASE_DIR, 'subject_list.csv')

        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'CSV 파일을 찾을 수 없습니다: {csv_file}'))
            return

        # 기존 데이터 확인
        existing_count = Subject.objects.count()
        if existing_count > 0:
            self.stdout.write(self.style.WARNING(f'이미 {existing_count}개의 과목이 등록되어 있습니다.'))
            response = input('기존 데이터를 삭제하고 새로 가져오시겠습니까? (yes/no): ')
            if response.lower() != 'yes':
                self.stdout.write(self.style.WARNING('작업이 취소되었습니다.'))
                return
            Subject.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('기존 데이터가 삭제되었습니다.'))

        # CSV 파일 읽기 및 데이터 가져오기
        imported_count = 0
        skipped_count = 0

        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                subject_code = row['과목코드'].strip()
                name = row['과목명'].strip()
                special_code = row['특수코드'].strip() if row['특수코드'].strip() else None
                memo = row['메모'].strip() if row['메모'].strip() else None
                extra = row['여분'].strip() if row['여분'].strip() else None

                if not subject_code or not name:
                    skipped_count += 1
                    continue

                # 과목 생성 또는 업데이트
                Subject.objects.update_or_create(
                    subject_code=subject_code,
                    defaults={
                        'name': name,
                        'special_code': special_code,
                        'memo': memo,
                        'extra': extra,
                        'is_active': True,
                    }
                )
                imported_count += 1

        self.stdout.write(self.style.SUCCESS(f'총 {imported_count}개의 과목이 성공적으로 가져와졌습니다.'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'{skipped_count}개의 행이 건너뛰어졌습니다.'))
