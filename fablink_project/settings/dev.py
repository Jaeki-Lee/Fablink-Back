# fablink_project/settings/dev.py
from .base import *

# 개발환경 디버그 모드
DEBUG = True

# 개발환경용 허용 호스트
ALLOWED_HOSTS = [
    'dev-api.fablink.com',
    'localhost',
    '127.0.0.1',
    '.amazonaws.com',  # AWS 환경
]

# 데이터베이스 설정 (개발 서버용)
if os.getenv('USE_SQLITE', 'False').lower() == 'true':
    # SQLite 사용 (로컬 테스트용)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # AWS Aurora PostgreSQL 데이터베이스 설정
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'fablink_dev_db'),
            'USER': os.getenv('DB_USER', 'fablink_dev_user'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',
                'client_encoding': 'UTF8',
                'connect_timeout': 10,
            },
            'CONN_MAX_AGE': 300,
            'TEST': {
                'NAME': 'test_fablink_dev_db',
            }
        }
    }

# 개발환경용 이메일 백엔드 (실제 SMTP 사용)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# 개발환경에서만 사용할 추가 앱
DEV_APPS = [
    'debug_toolbar',  # 디버그 툴바
]

# django_extensions가 이미 있는지 확인 후 추가
if 'django_extensions' not in INSTALLED_APPS:
    DEV_APPS.append('django_extensions')

INSTALLED_APPS += DEV_APPS

# 개발환경 전용 설정
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# 개발환경용 CORS 설정
CORS_ALLOWED_ORIGINS = [
    "https://dev.fablink.com",
    "http://localhost:3000",  # 로컬 프론트엔드 테스트용
]

# AWS S3 사용 (개발환경)
USE_S3 = os.getenv('USE_S3', 'True').lower() == 'true'
if USE_S3:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'fablink-dev-uploads')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'ap-northeast-2')
    
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'
    
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'

# 개발환경용 로깅
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
