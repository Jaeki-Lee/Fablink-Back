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

# AWS Aurora PostgreSQL 데이터베이스 설정 (개발 서버용)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'fablink_dev_db'),
        'USER': os.getenv('DB_USER', 'fablink_dev_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),  # 필수값
        'HOST': os.getenv('DB_HOST'),  # Aurora 개발 클러스터 엔드포인트
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',  # Aurora는 SSL 필수
            'client_encoding': 'UTF8',
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 300,  # 개발환경은 짧게 설정
        'TEST': {
            'NAME': 'test_fablink_dev_db',
        }
    }
}

# DynamoDB 설정 (개발환경)
USE_DYNAMODB = os.getenv('USE_DYNAMODB', 'True').lower() == 'true'
if USE_DYNAMODB:
    DYNAMODB_SETTINGS = {
        'region_name': os.getenv('DYNAMODB_REGION', 'ap-northeast-2'),
        'aws_access_key_id': os.getenv('DYNAMODB_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.getenv('DYNAMODB_SECRET_ACCESS_KEY'),
        'table_prefix': os.getenv('DYNAMODB_TABLE_PREFIX', 'fablink_dev'),
    }
    
    # DynamoDB 테이블 설정
    DYNAMODB_TABLES = {
        'user_sessions': f"{DYNAMODB_SETTINGS['table_prefix']}_user_sessions",
        'cache_data': f"{DYNAMODB_SETTINGS['table_prefix']}_cache_data",
        'analytics': f"{DYNAMODB_SETTINGS['table_prefix']}_analytics",
        'logs': f"{DYNAMODB_SETTINGS['table_prefix']}_logs",
    }

# 개발환경에서만 사용할 추가 앱
INSTALLED_APPS += [
    'django_extensions',  # 개발 도구
]

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
