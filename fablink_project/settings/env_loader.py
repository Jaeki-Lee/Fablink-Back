"""
환경별 환경변수 로드 유틸리티
"""
import os
from pathlib import Path
from dotenv import load_dotenv


def load_environment_variables():
    """
    환경에 따라 적절한 .env 파일을 로드합니다.
    
    환경 타입:
    - local: 로컬 개발 환경 (.env.local)
    - dev: 개발 서버 환경 (.env.dev)
    - prod: 운영 서버 환경 (.env.prod)
    
    우선순위:
    1. DJANGO_ENV 환경변수 확인
    2. 파일 존재 여부에 따라 자동 감지
    3. .env (기본값)
    """
    
    # 프로젝트 루트 디렉토리
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # 환경 타입 확인 (환경변수에서)
    django_env = os.getenv('DJANGO_ENV', '').lower()
    
    # 환경별 파일 경로 정의
    env_files = []
    
    # 1. 환경변수로 지정된 환경에 따라 파일 선택
    if django_env == 'prod':
        env_files.append(BASE_DIR / '.env.prod')
    elif django_env == 'dev':
        env_files.append(BASE_DIR / '.env.dev')
    elif django_env == 'local':
        env_files.append(BASE_DIR / '.env.local')
    
    # 2. 파일 존재 여부에 따라 자동 감지 (환경변수가 없는 경우)
    if not env_files:
        potential_files = [
            BASE_DIR / '.env.local',
            BASE_DIR / '.env.dev', 
            BASE_DIR / '.env.prod',
        ]
        
        for env_file in potential_files:
            if env_file.exists():
                env_files.append(env_file)
                break
    
    # 3. 기본 .env 파일도 추가 (낮은 우선순위)
    env_files.append(BASE_DIR / '.env')
    
    # 환경변수 파일 로드 (나중에 로드된 것이 우선순위 높음)
    loaded_files = []
    for env_file in reversed(env_files):  # 역순으로 로드하여 우선순위 보장
        if env_file.exists():
            load_dotenv(env_file, override=True)
            loaded_files.append(str(env_file.name))
    
    # 로드된 파일 정보 출력 (개발 환경에서만)
    if os.getenv('DEBUG', 'False').lower() == 'true':
        if loaded_files:
            print(f"🔧 환경변수 파일 로드됨: {', '.join(loaded_files)}")
            print(f"🌍 현재 환경: {get_environment_type()}")
        else:
            print("⚠️  환경변수 파일을 찾을 수 없습니다.")
    
    return loaded_files


def get_environment_type():
    """
    현재 환경 타입을 반환합니다.
    
    Returns:
        str: 'local', 'dev', 'prod' 중 하나
    """
    django_env = os.getenv('DJANGO_ENV', '').lower()
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    if django_env in ['local', 'dev', 'prod']:
        return django_env
    elif debug:
        return 'local'  # DEBUG=True면 로컬로 간주
    else:
        return 'prod'  # 기본값은 안전하게 production


def is_production():
    """운영 환경인지 확인"""
    return get_environment_type() == 'prod'


def is_development():
    """개발 환경인지 확인 (dev 서버)"""
    return get_environment_type() == 'dev'


def is_local():
    """로컬 환경인지 확인"""
    return get_environment_type() == 'local'


def is_debug_mode():
    """디버그 모드인지 확인 (local 또는 dev)"""
    return get_environment_type() in ['local', 'dev']
