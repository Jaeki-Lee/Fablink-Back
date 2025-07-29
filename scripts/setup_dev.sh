# =================================================================
# scripts/setup_dev.sh - 개발환경 Django 설정
# =================================================================

#!/bin/bash

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

echo "🚀 FabLink 개발환경 Django 설정을 시작합니다..."

# 가상환경 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    log_error "가상환경이 활성화되지 않았습니다."
    echo "다음 명령어로 가상환경을 활성화하세요:"
    echo "source venv/bin/activate  # Linux/Mac"
    echo "venv\\Scripts\\activate     # Windows"
    exit 1
fi

# .env 파일 존재 확인
if [ ! -f ".env" ]; then
    log_error ".env 파일이 없습니다. 먼저 ./scripts/setup_postgresql_dev.sh 를 실행하세요."
    exit 1
fi

# 환경변수 설정
export DJANGO_ENV=development

# 패키지 설치
log_info "개발환경 패키지를 설치합니다..."
pip install -r requirements/development.txt

# Django 설정 검증
log_info "Django 설정을 검증합니다..."
python manage.py check
if [ $? -ne 0 ]; then
    log_error "Django 설정에 문제가 있습니다."
    exit 1
fi

# 데이터베이스 연결 테스트
log_info "데이터베이스 연결을 테스트합니다..."
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT version()')
result = cursor.fetchone()
print(f'✅ PostgreSQL 연결 성공: {result[0][:50]}...')
"

# 데이터베이스 초기화 옵션
echo ""
echo -e "${YELLOW}🗄️ 데이터베이스 설정 옵션:${NC}"
echo "1) 기본 마이그레이션 (기존 데이터 유지)"
echo "2) 데이터베이스 완전 초기화 (모든 데이터 삭제)"
echo "3) 데이터베이스 DROP & 재생성 (테이블 구조 변경 시)"
echo ""
read -p "선택하세요 (1-3, 기본값: 1): " db_option

case $db_option in
    2)
        log_warning "⚠️ 모든 데이터베이스 데이터를 삭제합니다!"
        read -p "정말로 계속하시겠습니까? (yes/no): " confirm
        if [[ $confirm == "yes" ]]; then
            log_info "데이터베이스를 완전 초기화합니다..."
            python manage.py flush --noinput
            log_success "모든 데이터가 삭제되었습니다."
            
            log_info "마이그레이션을 실행합니다..."
            python manage.py makemigrations
            python manage.py migrate
        else
            log_info "데이터베이스 초기화를 취소했습니다."
            log_info "기본 마이그레이션을 실행합니다..."
            python manage.py makemigrations
            python manage.py migrate
        fi
        ;;
    3)
        log_warning "⚠️ 데이터베이스를 완전히 DROP하고 재생성합니다!"
        log_warning "⚠️ 모든 데이터와 테이블 구조가 삭제됩니다!"
        read -p "정말로 계속하시겠습니까? (yes/no): " confirm
        if [[ $confirm == "yes" ]]; then
            # .env에서 데이터베이스 정보 읽기
            source .env
            
            log_info "기존 마이그레이션 파일을 백업합니다..."
            mkdir -p backups/migrations/$(date +%Y%m%d_%H%M%S)
            find apps/*/migrations -name "*.py" ! -name "__init__.py" -exec cp {} backups/migrations/$(date +%Y%m%d_%H%M%S)/ \; 2>/dev/null || true
            
            log_info "마이그레이션 파일을 삭제합니다..."
            find apps/*/migrations -name "*.py" ! -name "__init__.py" -delete 2>/dev/null || true
            
            log_info "데이터베이스 연결을 종료합니다..."
            sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" 2>/dev/null || true
            
            log_info "데이터베이스를 DROP합니다..."
            sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"
            
            log_info "데이터베이스를 재생성합니다..."
            sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
            
            log_info "새 마이그레이션을 생성합니다..."
            python manage.py makemigrations
            
            log_info "마이그레이션을 적용합니다..."
            python manage.py migrate
            
            log_success "데이터베이스가 완전히 재생성되었습니다."
        else
            log_info "데이터베이스 재생성을 취소했습니다."
            log_info "기본 마이그레이션을 실행합니다..."
            python manage.py makemigrations
            python manage.py migrate
        fi
        ;;
    *)
        log_info "기본 마이그레이션을 실행합니다..."
        python manage.py makemigrations
        python manage.py migrate
        ;;
esac

# 개발용 슈퍼유저 생성
log_info "개발용 슈퍼유저를 생성합니다..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(user_id='admin').exists():
    try:
        User.objects.create_superuser(
            user_id='admin', 
            password='admin123',
            name='관리자',
            user_type='designer'
        )
        print('✅ 개발용 슈퍼유저 생성: admin/admin123')
        print('   - User ID: admin')
        print('   - Password: admin123') 
        print('   - Name: 관리자')
    except Exception as e:
        print(f'⚠️ 슈퍼유저 생성 실패: {e}')
        print('나중에 수동으로 생성: python manage.py createsuperuser')
else:
    print('✅ 슈퍼유저가 이미 존재합니다.')
"

# 테스트 데이터 로드 (선택)
echo ""
read -p "🧪 테스트 데이터를 생성하시겠습니까? (y/n): " create_test_data
if [[ $create_test_data == "y" || $create_test_data == "Y" ]]; then
    if [ -f "fixtures/test_data.json" ]; then
        python manage.py loaddata fixtures/test_data.json
        log_success "테스트 데이터가 로드되었습니다."
    else
        log_warning "fixtures/test_data.json 파일이 없습니다. 건너뛰겠습니다."
    fi
fi

# 정적 파일 수집 (선택)
read -p "📂 정적 파일을 수집하시겠습니까? (y/n): " collect_static
if [[ $collect_static == "y" || $collect_static == "Y" ]]; then
    python manage.py collectstatic --noinput
    log_success "정적 파일이 수집되었습니다."
fi

echo ""
log_success "🎉 FabLink 개발환경 설정이 완료되었습니다!"
echo ""
echo -e "${BLUE}🚀 서버 시작:${NC}"
echo "   python manage.py runserver"
echo ""
echo -e "${BLUE}🌐 접속 주소:${NC}"
echo "   • 메인: http://localhost:8000/"
echo "   • 관리자: http://localhost:8000/admin/"
echo "   • API: http://localhost:8000/api/"
echo ""
echo -e "${BLUE}👤 관리자 계정:${NC}"
echo "   • User ID: admin"
echo "   • Password: admin123"
echo "   • Name: 관리자"
echo ""
echo -e "${BLUE}🔗 로그인 API 테스트:${NC}"
echo "   curl -X POST http://localhost:8000/api/accounts/login/ \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"user_id\":\"admin\", \"password\":\"admin123\"}'"
echo ""
echo -e "${BLUE}🗄️ 데이터베이스 접속:${NC}"
echo "   psql -h localhost -U fablink_dev_user -d fablink_dev_db"
echo ""