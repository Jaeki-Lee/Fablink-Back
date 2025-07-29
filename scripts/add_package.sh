#!/bin/bash

# =================================================================
# scripts/add_package.sh - Django 패키지 추가 자동화
# =================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "📦 Django 패키지 추가 도구"
echo "=========================="

# 가상환경 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    log_error "가상환경이 활성화되지 않았습니다."
    echo "다음 명령어로 가상환경을 활성화하세요:"
    echo "source venv/bin/activate"
    exit 1
fi

# 패키지 이름 입력
if [ -z "$1" ]; then
    read -p "📦 추가할 패키지 이름을 입력하세요: " package_name
else
    package_name="$1"
fi

if [ -z "$package_name" ]; then
    log_error "패키지 이름이 필요합니다."
    exit 1
fi

# 패키지 버전 입력 (선택사항)
read -p "📌 특정 버전을 지정하시겠습니까? (예: 1.2.3, 엔터로 최신버전): " package_version

if [ -n "$package_version" ]; then
    full_package="${package_name}==${package_version}"
else
    full_package="$package_name"
fi

# 환경 선택
echo ""
echo "🎯 패키지를 어느 환경에 추가하시겠습니까?"
echo "1) base (모든 환경에서 사용)"
echo "2) development (개발환경에서만 사용)"
echo "3) production (운영환경에서만 사용)"
echo ""
read -p "선택하세요 (1-3): " env_choice

case $env_choice in
    1)
        requirements_file="requirements/base.txt"
        env_name="base (모든 환경)"
        ;;
    2)
        requirements_file="requirements/development.txt"
        env_name="development (개발환경)"
        ;;
    3)
        requirements_file="requirements/production.txt"
        env_name="production (운영환경)"
        ;;
    *)
        log_error "잘못된 선택입니다."
        exit 1
        ;;
esac

log_info "패키지: $full_package"
log_info "환경: $env_name"
log_info "파일: $requirements_file"

# 확인
read -p "계속하시겠습니까? (y/n): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
    log_info "취소되었습니다."
    exit 0
fi

# 1. requirements 파일에 추가
log_info "requirements 파일에 패키지를 추가합니다..."
echo "$full_package" >> "$requirements_file"
log_success "requirements 파일 업데이트 완료"

# 2. 패키지 설치
log_info "패키지를 설치합니다..."
if [ "$env_choice" == "1" ]; then
    pip install -r requirements/development.txt
else
    pip install -r "$requirements_file"
fi
log_success "패키지 설치 완료"

# 3. Django 앱인지 확인
log_info "Django 앱 여부를 확인합니다..."
python -c "
import importlib
try:
    module = importlib.import_module('$package_name')
    if hasattr(module, 'apps') or hasattr(module, 'default_app_config'):
        print('DJANGO_APP')
    else:
        print('REGULAR_PACKAGE')
except ImportError as e:
    print(f'IMPORT_ERROR: {e}')
" > /tmp/package_check.txt

package_type=$(cat /tmp/package_check.txt)

if [[ $package_type == "DJANGO_APP" ]]; then
    log_info "Django 앱으로 감지되었습니다."
    
    # INSTALLED_APPS에 추가할지 묻기
    read -p "🔧 INSTALLED_APPS에 추가하시겠습니까? (y/n): " add_to_apps
    
    if [[ $add_to_apps == "y" || $add_to_apps == "Y" ]]; then
        # base.py에 추가
        log_info "INSTALLED_APPS에 패키지를 추가합니다..."
        
        # INSTALLED_APPS 섹션 찾아서 추가
        python -c "
import re

# base.py 파일 읽기
with open('fablink_project/settings/base.py', 'r', encoding='utf-8') as f:
    content = f.read()

# INSTALLED_APPS 찾기
pattern = r'(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'
match = re.search(pattern, content, re.DOTALL)

if match:
    start, apps_content, end = match.groups()
    
    # 이미 추가되어 있는지 확인
    if \"'$package_name'\" not in apps_content:
        # 마지막 앱 뒤에 추가
        apps_lines = apps_content.strip().split('\n')
        
        # 마지막 줄에 콤마 추가 (없다면)
        if apps_lines and not apps_lines[-1].strip().endswith(','):
            apps_lines[-1] = apps_lines[-1] + ','
        
        # 새 앱 추가
        apps_lines.append(f\"    '$package_name',\")
        
        new_apps_content = '\n'.join(apps_lines)
        new_content = content.replace(match.group(0), start + new_apps_content + '\n' + end)
        
        # 파일 저장
        with open('fablink_project/settings/base.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print('ADDED')
    else:
        print('ALREADY_EXISTS')
else:
    print('NOT_FOUND')
" > /tmp/apps_result.txt

        apps_result=$(cat /tmp/apps_result.txt)
        
        case $apps_result in
            "ADDED")
                log_success "INSTALLED_APPS에 추가되었습니다."
                ;;
            "ALREADY_EXISTS")
                log_warning "이미 INSTALLED_APPS에 존재합니다."
                ;;
            "NOT_FOUND")
                log_error "INSTALLED_APPS를 찾을 수 없습니다. 수동으로 추가해주세요."
                ;;
        esac
        
        # 마이그레이션 필요한지 확인
        read -p "🔄 마이그레이션을 실행하시겠습니까? (y/n): " run_migration
        
        if [[ $run_migration == "y" || $run_migration == "Y" ]]; then
            log_info "마이그레이션을 실행합니다..."
            python manage.py makemigrations
            python manage.py migrate
            log_success "마이그레이션 완료"
        fi
    fi
    
elif [[ $package_type == "REGULAR_PACKAGE" ]]; then
    log_info "일반 Python 패키지입니다."
    
elif [[ $package_type == IMPORT_ERROR* ]]; then
    log_warning "패키지 import 중 오류가 발생했습니다:"
    echo "$package_type"
    log_info "패키지가 올바르게 설치되었는지 확인해주세요."
fi

# 4. 추가 설정이 필요한 유명한 패키지들에 대한 안내
case $package_name in
    "django-cors-headers")
        log_info "📝 추가 설정 안내:"
        echo "   MIDDLEWARE에 'corsheaders.middleware.CorsMiddleware'를 추가해주세요."
        echo "   CORS_ALLOWED_ORIGINS 설정을 추가해주세요."
        ;;
    "django-debug-toolbar")
        log_info "📝 추가 설정 안내:"
        echo "   MIDDLEWARE에 'debug_toolbar.middleware.DebugToolbarMiddleware'를 추가해주세요."
        echo "   INTERNAL_IPS 설정을 추가해주세요."
        echo "   urls.py에 debug_toolbar.urls를 추가해주세요."
        ;;
    "celery")
        log_info "📝 추가 설정 안내:"
        echo "   celery.py 파일을 생성해주세요."
        echo "   __init__.py에 celery app을 import해주세요."
        echo "   Redis/RabbitMQ 브로커 설정을 추가해주세요."
        ;;
    "django-rest-framework")
        log_info "📝 추가 설정 안내:"
        echo "   REST_FRAMEWORK 설정을 추가해주세요."
        echo "   urls.py에 DRF 관련 URL을 추가해주세요."
        ;;
esac

# 정리
rm -f /tmp/package_check.txt /tmp/apps_result.txt

echo ""
log_success "🎉 패키지 추가가 완료되었습니다!"
echo ""
echo -e "${BLUE}📋 요약:${NC}"
echo "   • 패키지: $full_package"
echo "   • 환경: $env_name"
echo "   • 파일: $requirements_file"
echo ""
echo -e "${BLUE}🔍 확인사항:${NC}"
echo "   • pip list | grep $package_name"
echo "   • python manage.py check"
echo ""
