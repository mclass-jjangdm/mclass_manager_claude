# progress/migrations/0011_migrate_pending_progress.py
# 미완료 진도(study_date가 null인 항목)를 LearningRecord로 이전

from django.db import migrations


def migrate_pending_progress(apps, schema_editor):
    """미완료 진도 데이터를 LearningRecord로 이전"""
    StudentBookProgress = apps.get_model('bookstore', 'StudentBookProgress')
    LearningRecord = apps.get_model('progress', 'LearningRecord')

    # study_date가 null인 미완료 항목 이전
    for progress in StudentBookProgress.objects.filter(study_date__isnull=True):
        content = progress.book_content
        title = f"{content.subsection_title} (p.{content.page})"

        # 이미 이전되었는지 확인 (중복 방지)
        if not LearningRecord.objects.filter(
            book_sale=progress.book_sale,
            book_content=progress.book_content,
            record_type='textbook'
        ).exists():
            LearningRecord.objects.create(
                student=progress.book_sale.student,
                record_type='textbook',
                date=None,  # 미완료이므로 null
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


def rollback_pending_progress(apps, schema_editor):
    """롤백: 미완료 항목 삭제"""
    LearningRecord = apps.get_model('progress', 'LearningRecord')
    # date가 null인 교재 진도 항목 삭제
    LearningRecord.objects.filter(record_type='textbook', date__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0010_make_learning_record_date_nullable'),
        ('bookstore', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_pending_progress, rollback_pending_progress),
    ]
