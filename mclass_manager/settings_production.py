"""
카페24 가상 호스팅용 프로덕션 설정
이 파일을 사용하려면 환경변수 설정:
DJANGO_SETTINGS_MODULE=mclass_manager.settings_production
"""
from .settings import *

# 프로덕션 모드
DEBUG = False

# 허용 호스트 설정 (실제 도메인으로 변경 필요)
ALLOWED_HOSTS = [
    'mclass.co.kr',
    'www.mclass.co.kr',
    # 카페24 기본 도메인
    '사용자ID.cafe24.com',
]

# CSRF 신뢰 도메인
CSRF_TRUSTED_ORIGINS = [
    'https://mclass.co.kr',
    'https://www.mclass.co.kr',
]

# 데이터베이스 설정 (카페24 MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', '사용자ID'),
        'USER': os.environ.get('DB_USER', '사용자ID'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# 정적 파일 설정
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 미디어 파일 설정
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# WhiteNoise 정적 파일 압축
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 보안 설정
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# 로깅 설정 (프로덕션용)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# 캐시 설정 (파일 기반 - 가상 호스팅에서 memcached/redis 사용 불가 시)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
    }
}

# 세션 설정
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600 * 8  # 8시간
