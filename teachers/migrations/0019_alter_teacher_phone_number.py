# Generated manually to fix phone_number field length
from django.db import migrations, models
import teachers.models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0018_fix_phone_validator'),
    ]

    operations = [
        # 먼저 SQL로 컬럼 크기를 직접 변경
        migrations.RunSQL(
            "ALTER TABLE teachers_teacher MODIFY COLUMN phone_number VARCHAR(13);",
            reverse_sql="ALTER TABLE teachers_teacher MODIFY COLUMN phone_number VARCHAR(11);"
        ),
        # 그 다음 Django 모델 필드 업데이트
        migrations.AlterField(
            model_name='teacher',
            name='phone_number',
            field=models.CharField(
                blank=True, 
                max_length=13, 
                null=True, 
                validators=[teachers.models.phone_number_validator], 
                verbose_name='전화번호'
            ),
        ),
    ]
