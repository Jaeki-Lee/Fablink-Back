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


env = get_env_variable('DJANGO_ENV', 'development')
if 'production' in env:
    from .production import *
elif 'development' in env:
    from .development import *
else:
    from .local import *