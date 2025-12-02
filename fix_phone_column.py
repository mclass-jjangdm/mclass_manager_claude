#!/usr/bin/env python
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mclass_manager.settings')
sys.path.append('c:/Users/JANGDONGMIN/django_project/mclass_manager')

django.setup()

from django.core.management import execute_from_command_line
from django.db import connection

print("Attempting to run migration...")

try:
    # 직접 SQL로 컬럼 크기 변경
    with connection.cursor() as cursor:
        print("Checking current phone_number column...")
        cursor.execute("SHOW COLUMNS FROM teachers_teacher LIKE 'phone_number';")
        result = cursor.fetchone()
        print(f"Current column info: {result}")
        
        print("Updating phone_number column to VARCHAR(13)...")
        cursor.execute("ALTER TABLE teachers_teacher MODIFY COLUMN phone_number VARCHAR(13);")
        print("Column updated successfully!")
        
        # 확인
        cursor.execute("SHOW COLUMNS FROM teachers_teacher LIKE 'phone_number';")
        result = cursor.fetchone()
        print(f"Updated column info: {result}")
        
except Exception as e:
    print(f"Error: {e}")

print("Migration completed!")
