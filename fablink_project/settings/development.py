# fablink_project/settings/development.py (수정)
from .base import *

# 개발환경 디버그 모드
DEBUG = True

# 개발환경용 데이터베이스 (이미 있음 - 수정하기)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DEV_DB_NAME', 'fablink_dev_db'),
        'USER': os.getenv('DEV_DB_USER', 'fablink_dev_user'),
        'PASSWORD': os.getenv('DEV_DB_PASSWORD', 'dev123'),
        'HOST': os.getenv('DEV_DB_HOST', 'localhost'),
        'PORT': os.getenv('DEV_DB_PORT', '5432'),
        'OPTIONS': {
            'client_encoding': 'UTF8',
        },
        'TEST': {
            'NAME': 'test_fablink_dev_db',  # 테스트용 DB
        }
    }
}

# 개발환경용 이메일 백엔드 (콘솔 출력)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 개발환경에서만 사용할 추가 앱
INSTALLED_APPS += [
    'django_extensions',  # 개발 도구
]

# 개발환경 전용 설정
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# 개발환경용 로깅 (콘솔 출력)
LOGGING['handlers']['console'] = {
    'level': 'DEBUG',
    'class': 'logging.StreamHandler',
    'formatter': 'verbose',
}
LOGGING['root']['handlers'] = ['console']