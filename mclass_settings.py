
SECRET_KEY = 'django-insecure-(yz2)zztlb_#hb-)fqyjo9pe@hl#a*cvecl61=em*z)gz4hz+r'

db_password = 'mclass@0104'


# mclass_settings.py에 추가할 내용

# 1. SMTP 서버 정보 (사용하는 이메일 서비스에 따라 다름)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # SMTP 사용
EMAIL_HOST = 'smtp.gmail.com'  # Gmail 예시, 다른 서비스 사용 시 변경
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# 2. 이메일 계정 정보
EMAIL_HOST_USER = 'jjangdm@mclass.co.kr'  # 실제 발송에 사용할 이메일
EMAIL_HOST_PASSWORD = 'mclass@0104'  # 이메일 비밀번호 또는 앱 비밀번호

# 3. 기본 발신자 (이미 설정됨)
DEFAULT_FROM_EMAIL = 'jjangdm@mclass.co.kr'


