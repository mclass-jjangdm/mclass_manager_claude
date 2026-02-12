"""
카페24 가상 호스팅용 Passenger WSGI 설정 파일
"""
import os
import sys

# 프로젝트 경로 설정 (카페24 환경에 맞게 수정 필요)
# 예: /home/사용자ID/www/mclass_manager_claude
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_PATH)

# 가상환경 경로 설정 (카페24 환경에 맞게 수정 필요)
# 예: /home/사용자ID/venv/lib/python3.10/site-packages
VENV_PATH = os.path.join(os.path.dirname(PROJECT_PATH), 'venv', 'lib', 'python3.10', 'site-packages')
if os.path.exists(VENV_PATH):
    sys.path.insert(0, VENV_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mclass_manager.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
