
# =================================================================
# scripts/setup_postgresql_dev.sh - 개발환경 PostgreSQL DB 생성
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

log_info "FabLink 개발환경 PostgreSQL 데이터베이스 설정을 시작합니다..."

# PostgreSQL 설치 확인
if ! command -v psql &> /dev/null; then
    log_warning "PostgreSQL이 설치되지 않았습니다. 설치를 진행합니다..."
    
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y postgresql postgresql-contrib
        log_success "PostgreSQL 설치가 완료되었습니다."
    else
        log_error "지원하지 않는 운영체제입니다. PostgreSQL을 수동으로 설치해주세요."
        exit 1
    fi
else
    log_success "PostgreSQL이 이미 설치되어 있습니다."
fi

# PostgreSQL 서비스 시작
log_info "PostgreSQL 서비스를 시작합니다..."
sudo systemctl start postgresql
sudo systemctl enable postgresql
log_success "PostgreSQL 서비스가 시작되었습니다."

# 개발환경 데이터베이스 및 사용자 생성 (template0 사용으로 collation 문제 해결)
log_info "개발환경 데이터베이스와 사용자를 생성합니다..."

sudo -u postgres psql << 'EOSQL'
-- 기존 데이터베이스 및 사용자 삭제 (있다면)
DROP DATABASE IF EXISTS fablink_dev_db;
DROP USER IF EXISTS fablink_dev_user;

-- 개발환경 사용자 생성
CREATE USER fablink_dev_user WITH PASSWORD 'dev123';
ALTER ROLE fablink_dev_user SET client_encoding TO 'utf8';
ALTER ROLE fablink_dev_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE fablink_dev_user SET timezone TO 'Asia/Seoul';
ALTER USER fablink_dev_user CREATEDB;

-- 개발환경 데이터베이스 생성 (template0 사용으로 collation 문제 해결)
CREATE DATABASE fablink_dev_db
    WITH 
    OWNER = fablink_dev_user
    ENCODING = 'UTF8'
    TEMPLATE = template0
    LC_COLLATE = 'C.UTF-8'
    LC_CTYPE = 'C.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE fablink_dev_db TO fablink_dev_user;

\echo '✅ 개발환경 PostgreSQL 설정 완료!'
\echo '📋 데이터베이스: fablink_dev_db'
\echo '👤 사용자: fablink_dev_user'
\echo '🔑 비밀번호: dev123'
EOSQL

# 추가 권한 설정
sudo -u postgres psql -d fablink_dev_db << 'EOSQL'
GRANT ALL ON SCHEMA public TO fablink_dev_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fablink_dev_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fablink_dev_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO fablink_dev_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO fablink_dev_user;
EOSQL

# .env 파일 생성
log_info "개발환경 .env 파일을 생성합니다..."

cat > .env << 'ENVEOF'
# Django Settings (Development)
SECRET_KEY=django-insecure-dev-key-12345-change-in-production!@#$%
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Development PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=fablink_dev_db
DB_USER=fablink_dev_user
DB_PASSWORD=dev123
DB_HOST=localhost
DB_PORT=5432

# Email Settings (Console for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=dev@fablink.com
EMAIL_HOST_PASSWORD=

# File Storage (Local for development)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# Celery (Redis for async tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Environment
DJANGO_ENV=development
ENVEOF

# 연결 테스트
log_info "데이터베이스 연결을 테스트합니다..."
if PGPASSWORD=dev123 psql -h localhost -U fablink_dev_user -d fablink_dev_db -c "SELECT version();" > /dev/null 2>&1; then
    log_success "데이터베이스 연결 테스트 성공!"
else
    log_error "데이터베이스 연결 테스트 실패!"
    exit 1
fi

echo ""
log_success "🎉 개발환경 PostgreSQL 설정이 완료되었습니다!"
echo ""
echo -e "${BLUE}📋 개발 데이터베이스 정보:${NC}"
echo "   🏷️  데이터베이스: fablink_dev_db"
echo "   👤 사용자: fablink_dev_user"
echo "   🔑 비밀번호: dev123"
echo "   🌐 호스트: localhost:5432"
echo ""
echo -e "${YELLOW}🚀 다음 단계: ./scripts/setup_dev.sh 실행${NC}"
echo ""
EOF