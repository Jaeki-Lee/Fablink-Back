import os
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name, default=None):
    """환경변수를 가져오는 헬퍼 함수"""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = f"Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)


# 환경 결정 (기본값: local)
env = get_env_variable('DJANGO_ENV', 'local')

print(f"🌍 Django 환경: {env}")

if env == 'prod':
    from .prod import *
    print("📦 운영 환경 설정 로드됨")
elif env == 'dev':
    from .dev import *
    print("🔧 개발 서버 환경 설정 로드됨")
else:  # local 또는 기타
    from .local import *
    print("💻 로컬 개발 환경 설정 로드됨")
