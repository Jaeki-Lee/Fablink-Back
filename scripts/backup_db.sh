# =================================================================
# scripts/backup_db.sh - 데이터베이스 백업
# =================================================================

#!/bin/bash

# 백업 디렉토리 설정
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

if [[ "$1" == "dev" ]]; then
    log_info "개발 데이터베이스를 백업합니다..."
    
    BACKUP_FILE="$BACKUP_DIR/fablink_dev_backup_$DATE.sql"
    PGPASSWORD=dev123 pg_dump -h localhost -U fablink_dev_user -d fablink_dev_db > $BACKUP_FILE
    
    log_success "개발 DB 백업 완료: $BACKUP_FILE"
    echo "📊 백업 파일 크기: $(du -h $BACKUP_FILE | cut -f1)"
    
elif [[ "$1" == "prod" ]]; then
    log_info "운영 데이터베이스를 백업합니다..."
    echo "🚨 운영 DB 백업을 위해 .env 파일에서 정보를 로드합니다..."
    
    # .env 파일에서 DB 정보 로드
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | grep -E '^(DB_|DJANGO_ENV)' | xargs)
    else
        log_error ".env 파일이 없습니다."
        exit 1
    fi
    
    # 운영환경 확인
    if [[ "$DJANGO_ENV" != "production" ]]; then
        log_error "현재 환경이 운영환경이 아닙니다. DJANGO_ENV=$DJANGO_ENV"
        exit 1
    fi
    
    BACKUP_FILE="$BACKUP_DIR/fablink_prod_backup_$DATE.sql"
    PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_FILE
    
    log_success "운영 DB 백업 완료: $BACKUP_FILE"
    echo "📊 백업 파일 크기: $(du -h $BACKUP_FILE | cut -f1)"
    
    # 백업 파일 압축 (운영환경은 용량이 클 수 있음)
    log_info "백업 파일을 압축합니다..."
    gzip $BACKUP_FILE
    log_success "압축 완료: $BACKUP_FILE.gz"
    echo "📊 압축된 파일 크기: $(du -h $BACKUP_FILE.gz | cut -f1)"
    
else
    echo "🔧 사용법: ./scripts/backup_db.sh [dev|prod]"
    echo ""
    echo "📋 설명:"
    echo "   dev   - 개발 데이터베이스 백업 (fablink_dev_db)"
    echo "   prod  - 운영 데이터베이스 백업 (fablink_prod_db)"
    echo ""
    echo "📁 백업 파일은 backups/ 디렉토리에 저장됩니다."
    echo ""
    
    # 기존 백업 파일 목록 표시
    if [ -d "$BACKUP_DIR" ] && [ "$(ls -A $BACKUP_DIR)" ]; then
        echo "📋 기존 백업 파일:"
        ls -lh $BACKUP_DIR/
    fi
    
    exit 1
fi

# 백업 정리 (30일 이상된 백업 파일 삭제)
log_info "오래된 백업 파일을 정리합니다 (30일 이상)..."
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
log_success "백업 정리가 완료되었습니다."

echo ""
echo "📋 현재 백업 파일 목록:"
ls -lh $BACKUP_DIR/ | tail -10