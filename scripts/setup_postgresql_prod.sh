# =================================================================
# scripts/setup_postgresql_prod.sh - 운영환경 PostgreSQL DB 생성
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

log_warning "운영환경 PostgreSQL 데이터베이스 설정을 시작합니다..."
echo "🚨 이는 운영환경 설정입니다. 매우 신중하게 진행하세요!"

# 확인
read -p "🔐 운영환경 DB 설정을 계속하시겠습니까? (PRODUCTION 입력): " confirm
if [[ $confirm != "PRODUCTION" ]]; then
    log_error "운영환경 설정이 취소되었습니다."
    exit 1
fi

# PostgreSQL 설치 확인
if ! command -v psql &> /dev/null; then
    log_error "PostgreSQL이 설치되지 않았습니다. 먼저 설치해주세요."
    exit 1
fi

# PostgreSQL 서비스 시작
log_info "PostgreSQL 서비스를 확인합니다..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 강력한 비밀번호 생성
PROD_PASSWORD=$(openssl rand -base64 32)

log_info "운영환경 데이터베이스와 사용자를 생성합니다..."

sudo -u postgres psql << EOSQL
-- 기존 운영환경 데이터베이스 및 사용자 확인 및 삭제
DROP DATABASE IF EXISTS fablink_prod_db;
DROP USER IF EXISTS fablink_prod_user;

-- 운영환경 사용자 생성 (강력한 보안)
CREATE USER fablink_prod_user WITH PASSWORD '$PROD_PASSWORD';
ALTER ROLE fablink_prod_user SET client_encoding TO 'utf8';
ALTER ROLE fablink_prod_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE fablink_prod_user SET timezone TO 'Asia/Seoul';

-- 운영환경 데이터베이스 생성
CREATE DATABASE fablink_prod_db
    WITH 
    OWNER = fablink_prod_user
    ENCODING = 'UTF8'
    TEMPLATE = template0
    LC_COLLATE = 'C.UTF-8'
    LC_CTYPE = 'C.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = 50;

-- 제한된 권한 부여 (보안 강화)
GRANT CONNECT ON DATABASE fablink_prod_db TO fablink_prod_user;
GRANT USAGE ON SCHEMA public TO fablink_prod_user;
GRANT CREATE ON SCHEMA public TO fablink_prod_user;

\echo '✅ 운영환경 PostgreSQL 설정 완료!'
\echo '🔐 비밀번호가 자동 생성되었습니다.'
EOSQL

# 추가 권한 설정
sudo -u postgres psql -d fablink_prod_db << 'EOSQL'
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fablink_prod_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fablink_prod_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO fablink_prod_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO fablink_prod_user;
EOSQL

# 강력한 SECRET_KEY 생성
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# 운영환경 .env 파일 생성
log_info "운영환경 .env 파일을 생성합니다..."

cat > .env << EOF
# Django Settings (Production)
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Database (Production PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=fablink_prod_db
DB_USER=fablink_prod_user
DB_PASSWORD=${PROD_PASSWORD}
DB_HOST=localhost
DB_PORT=5432

# Email Settings (Production SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-smtp-password

# File Storage (AWS S3 for production)
USE_S3=True
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=fablink-production-media

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# Celery (Redis for production)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Environment
DJANGO_ENV=production
EOF

# 연결 테스트
log_info "운영 데이터베이스 연결을 테스트합니다..."
if PGPASSWORD=$PROD_PASSWORD psql -h localhost -U fablink_prod_user -d fablink_prod_db -c "SELECT version();" > /dev/null 2>&1; then
    log_success "운영 데이터베이스 연결 테스트 성공!"
else
    log_error "운영 데이터베이스 연결 테스트 실패!"
    exit 1
fi

# 보안 정보 저장
cat > .env.production.backup << EOF
# ⚠️ 이 정보를 안전한 곳에 백업하세요!
# 운영환경 데이터베이스 접속 정보

DB_NAME=fablink_prod_db
DB_USER=fablink_prod_user
DB_PASSWORD=${PROD_PASSWORD}
SECRET_KEY=${SECRET_KEY}

# 생성 날짜: $(date)
EOF

echo ""
log_success "🎉 운영환경 PostgreSQL 설정이 완료되었습니다!"
echo ""
echo -e "${BLUE}📋 운영 데이터베이스 정보:${NC}"
echo "   🏷️  데이터베이스: fablink_prod_db"
echo "   👤 사용자: fablink_prod_user"
echo "   🔑 비밀번호: ${PROD_PASSWORD}"
echo "   🌐 호스트: localhost:5432"
echo ""
echo -e "${RED}🔐 중요: 비밀번호가 .env.production.backup 파일에 저장되었습니다!${NC}"
echo -e "${YELLOW}🚀 다음 단계: ./scripts/setup_prod.sh 실행${NC}"
echo ""
