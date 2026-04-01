from django.db import migrations


def populate_tuition_fee(apps, schema_editor):
    MonthlyEnrollment = apps.get_model('classes', 'MonthlyEnrollment')
    to_update = []
    for me in MonthlyEnrollment.objects.select_related('lesson').filter(tuition_fee__isnull=True):
        me.tuition_fee = me.lesson.base_tuition
        to_update.append(me)
    if to_update:
        MonthlyEnrollment.objects.bulk_update(to_update, ['tuition_fee'])


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0004_tuition_fee_snapshot'),
    ]

    operations = [
        migrations.RunPython(populate_tuition_fee, migrations.RunPython.noop),
    ]
