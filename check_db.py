#!/usr/bin/env python
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mclass_manager.settings')
sys.path.append('c:/Users/JANGDONGMIN/django_project/mclass_manager')

django.setup()

from django.db import connection

# 데이터베이스 연결을 통해 테이블 스키마 확인
with connection.cursor() as cursor:
    cursor.execute("DESCRIBE teachers_teacher;")
    rows = cursor.fetchall()
    for row in rows:
        if 'phone_number' in row[0]:
            print(f"Phone number field: {row}")
            
    # 현재 전화번호 데이터 확인
    cursor.execute("SELECT id, name, phone_number FROM teachers_teacher WHERE phone_number IS NOT NULL LIMIT 10;")
    phone_data = cursor.fetchall()
    print("\nCurrent phone number data:")
    for data in phone_data:
        print(f"ID: {data[0]}, Name: {data[1]}, Phone: {data[2]} (Length: {len(data[2]) if data[2] else 0})")
