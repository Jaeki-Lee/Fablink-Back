# fablink_project/settings/prod.py
from .base import *
import dj_database_url

# 운영환경 보안 설정
DEBUG = False
ALLOWED_HOSTS = [
    'api.fablink.com',
    'fablink.com',
    '.amazonaws.com',  # AWS ELB, CloudFront 등
]

# AWS Aurora PostgreSQL 데이터베이스 설정 (운영환경)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'fablink_prod_db'),
        'USER': os.getenv('DB_USER', 'fablink_prod_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),  # 필수값
        'HOST': os.getenv('DB_HOST'),  # Aurora 운영 클러스터 엔드포인트
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',  # Aurora는 SSL 필수
            'client_encoding': 'UTF8',
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 600,  # 운영환경은 길게 설정
        'TEST': {
            'NAME': 'test_fablink_prod_db',
        }
    }
}

# DATABASE_URL 환경변수 지원 (Heroku, Railway 등)
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
    }

# DynamoDB 설정 (운영환경)
USE_DYNAMODB = os.getenv('USE_DYNAMODB', 'True').lower() == 'true'
if USE_DYNAMODB:
    DYNAMODB_SETTINGS = {
        'region_name': os.getenv('DYNAMODB_REGION', 'ap-northeast-2'),
        'aws_access_key_id': os.getenv('DYNAMODB_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.getenv('DYNAMODB_SECRET_ACCESS_KEY'),
        'table_prefix': os.getenv('DYNAMODB_TABLE_PREFIX', 'fablink_prod'),
    }
    
    # DynamoDB 테이블 설정
    DYNAMODB_TABLES = {
        'user_sessions': f"{DYNAMODB_SETTINGS['table_prefix']}_user_sessions",
        'cache_data': f"{DYNAMODB_SETTINGS['table_prefix']}_cache_data",
        'analytics': f"{DYNAMODB_SETTINGS['table_prefix']}_analytics",
        'logs': f"{DYNAMODB_SETTINGS['table_prefix']}_logs",
    }

# 보안 설정
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# AWS S3 설정 (운영환경)
USE_S3 = os.getenv('USE_S3', 'True').lower() == 'true'
if USE_S3:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'fablink-prod-uploads')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'ap-northeast-2')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
    
    # Static 파일
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Media 파일
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# 캐시 설정 (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'ssl_cert_reqs': None,
            },
        }
    }
}

# 세션 저장소
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Celery 설정 (운영환경)
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# 로깅 설정 (운영환경용)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/fablink/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    ],
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['file'],
            'propagate': False,
        },
    },
}

# CORS 설정 (운영환경)
CORS_ALLOWED_ORIGINS = [
    "https://fablink.com",
    "https://www.fablink.com",
]
CORS_ALLOW_CREDENTIALS = True

# 모니터링 및 성능 설정
if 'SENTRY_DSN' in os.environ:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True
    )
