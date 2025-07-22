from .base import *

# 개발환경 디버그 모드
DEBUG = True

# 개발환경용 데이터베이스
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'fablink_db'),
        'USER': os.getenv('DB_USER', 'fablink_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'test123'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# 개발환경용 이메일 백엔드 (콘솔 출력)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 개발환경에서만 사용할 추가 앱 (있다면)
INSTALLED_APPS += [
    # 'django_extensions',  # 필요시 주석 해제
]