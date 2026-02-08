# progress/migrations/0009_migrate_data_to_learning_record.py
# 기존 StudentBookProgress와 StudentActivity 데이터를 LearningRecord로 이전

from django.db import migrations
from django.utils import timezone


def migrate_data_forward(apps, schema_editor):
    """기존 데이터를 LearningRecord로 이전"""
    StudentBookProgress = apps.get_model('bookstore', 'StudentBookProgress')
    StudentActivity = apps.get_model('progress', 'StudentActivity')
    LearningRecord = apps.get_model('progress', 'LearningRecord')

    # 1. StudentBookProgress -> LearningRecord (교재 진도)
    # study_date가 있는 것만 이전 (완료된 진도만)
    for progress in StudentBookProgress.objects.filter(study_date__isnull=False):
        # 목차 항목에서 title 생성
        content = progress.book_content
        title = f"{content.subsection_title} (p.{content.page})"

        LearningRecord.objects.create(
            student=progress.book_sale.student,
            record_type='textbook',
            date=progress.study_date,
            title=title,
            book_sale=progress.book_sale,
            book_content=progress.book_content,
            subject=progress.book_sale.book.subject if progress.book_sale.book else None,
            teacher=progress.teacher,
            achievement=progress.achievement or '',
            homework_checked=progress.homework_done,
            needs_review=progress.needs_review,
            memo='',
        )

    # 2. StudentActivity -> LearningRecord (수업 활동)
    for activity in StudentActivity.objects.all():
        LearningRecord.objects.create(
            student=activity.student,
            record_type=activity.activity_type,
            date=activity.date,
            title=activity.title,
            book_sale=None,
            book_content=None,
            subject=activity.subject,
            teacher=activity.teacher,
            achievement=activity.achievement or '',
            score=activity.score,
            total_score=activity.total_score,
            homework_checked=activity.homework_checked,
            needs_review=activity.needs_review,
            memo=activity.memo,
        )


def migrate_data_backward(apps, schema_editor):
    """롤백: LearningRecord 데이터 삭제 (기존 데이터는 유지)"""
    LearningRecord = apps.get_model('progress', 'LearningRecord')
    LearningRecord.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0008_add_learning_record_model'),
        ('bookstore', '0001_initial'),  # bookstore 앱 의존성
    ]

    operations = [
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
    ]
