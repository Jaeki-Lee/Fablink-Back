from .development import *

# 로컬 개발 환경에 특화된 설정
DEBUG = True

# CORS 설정 완화
CORS_ALLOW_ALL_ORIGINS = True

# 로깅 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}