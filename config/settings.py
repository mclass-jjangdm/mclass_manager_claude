# mclass_manager/config/settings.py
import os

from mclass_manager.settings import BASE_DIR

# PDF 파일 저장 경로 설정
REPORTS_DIR = os.path.join(BASE_DIR, 'media', 'reports', 'salary')
os.makedirs(REPORTS_DIR, exist_ok=True)

FONTS_DIR = os.path.join(BASE_DIR, 'static', 'fonts')