# =================================================================
# scripts/restore_db.sh - 데이터베이스 복원
# =================================================================

#!/bin/bash

BACKUP_DIR="backups"

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

if [[ "$1" == "dev" && "$2" != "" ]]; then
    log_warning "개발 데이터베이스를 복원합니다..."
    echo "🚨 기존 개발 데이터가 모두 삭제됩니다!"
    read -p "정말로 복원하시겠습니까? (yes 입력): " confirm
    
    if [[ $confirm == "yes" ]]; then
        BACKUP_FILE="$BACKUP_DIR/$2"
        
        # 백업 파일 존재 확인
        if [ ! -f "$BACKUP_FILE" ]; then
            log_error "백업 파일을 찾을 수 없습니다: $BACKUP_FILE"
            exit 1
        fi
        
        log_info "개발 데이터베이스를 복원합니다..."
        
        # 압축 파일인지 확인
        if [[ "$BACKUP_FILE" == *.gz ]]; then
            log_info "압축 파일을 해제하여 복원합니다..."
            gunzip -c $BACKUP_FILE | PGPASSWORD=dev123 psql -h localhost -U fablink_dev_user -d fablink_dev_db
        else
            PGPASSWORD=dev123 psql -h localhost -U fablink_dev_user -d fablink_dev_db < $BACKUP_FILE
        fi
        
        log_success "개발 DB 복원이 완료되었습니다."
        
        # Django 마이그레이션 상태 확인
        log_info "Django 마이그레이션 상태를 확인합니다..."
        python manage.py showmigrations
        
    else
        log_error "복원이 취소되었습니다."
    fi
    
elif [[ "$1" == "prod" && "$2" != "" ]]; then
    log_warning "운영 데이터베이스를 복원합니다..."
    echo "🚨🚨🚨 이는 운영환경입니다! 매우 신중하게 진행하세요! 🚨🚨🚨"
    echo "📋 복원 전 체크리스트:"
    echo "   1. 현재 운영 DB 백업 완료했나요?"
    echo "   2. 서비스 중단 공지했나요?"
    echo "   3. 복원할 백업 파일이 정확한가요?"
    echo ""
    read -p "모든 체크리스트를 확인했습니까? (RESTORE_PRODUCTION 입력): " confirm
    
    if [[ $confirm == "RESTORE_PRODUCTION" ]]; then
        BACKUP_FILE="$BACKUP_DIR/$2"
        
        # 백업 파일 존재 확인
        if [ ! -f "$BACKUP_FILE" ]; then
            log_error "백업 파일을 찾을 수 없습니다: $BACKUP_FILE"
            exit 1
        fi
        
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
        
        log_info "운영 데이터베이스를 복원합니다..."
        
        # 압축 파일인지 확인
        if [[ "$BACKUP_FILE" == *.gz ]]; then
            log_info "압축 파일을 해제하여 복원합니다..."
            gunzip -c $BACKUP_FILE | PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME
        else
            PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME < $BACKUP_FILE
        fi
        
        log_success "운영 DB 복원이 완료되었습니다."
        
        # Django 마이그레이션 상태 확인
        log_info "Django 마이그레이션 상태를 확인합니다..."
        python manage.py showmigrations
        
        log_warning "복원 후 확인사항:"
        echo "   1. 웹사이트 정상 작동 확인"
        echo "   2. 주요 기능 테스트"
        echo "   3. 로그 파일 확인"
        echo "   4. 서비스 재개 공지"
        
    else
        log_error "운영 DB 복원이 취소되었습니다."
    fi
    
else
    echo "🔧 사용법: ./scripts/restore_db.sh [dev|prod] [백업파일명]"
    echo ""
    echo "📋 설명:"
    echo "   dev   - 개발 데이터베이스 복원"
    echo "   prod  - 운영 데이터베이스 복원 (매우 신중하게!)"
    echo ""
    echo "📁 사용 가능한 백업 파일 목록:"
    
    if [ -d "$BACKUP_DIR" ] && [ "$(ls -A $BACKUP_DIR)" ]; then
        echo ""
        echo "📅 개발환경 백업:"
        ls -lht $BACKUP_DIR/fablink_dev_backup_* 2>/dev/null | head -5
        echo ""
        echo "🏭 운영환경 백업:"
        ls -lht $BACKUP_DIR/fablink_prod_backup_* 2>/dev/null | head -5
        echo ""
        echo "💡 사용 예시:"
        echo "   ./scripts/restore_db.sh dev fablink_dev_backup_20240722_143022.sql"
        echo "   ./scripts/restore_db.sh prod fablink_prod_backup_20240722_143022.sql.gz"
    else
        echo "❌ 백업 파일이 없습니다. 먼저 백업을 실행하세요:"
        echo "   ./scripts/backup_db.sh dev"
        echo "   ./scripts/backup_db.sh prod"
    fi
    
    exit 1
fi
