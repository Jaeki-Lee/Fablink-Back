#!/bin/bash

# 환경별 환경변수 파일 생성 스크립트
# 사용법: ./scripts/setup_env.sh [local|dev|prod]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 도움말 출력
show_help() {
    echo "환경별 환경변수 파일 생성 스크립트"
    echo ""
    echo "사용법:"
    echo "  ./scripts/setup_env.sh [환경타입]"
    echo ""
    echo "환경타입:"
    echo "  local   - 로컬 개발 환경 (.env.local)"
    echo "  dev     - 개발 서버 환경 (.env.dev)"
    echo "  prod    - 운영 서버 환경 (.env.prod)"
    echo ""
    echo "예시:"
    echo "  ./scripts/setup_env.sh local"
    echo "  ./scripts/setup_env.sh dev"
    echo "  ./scripts/setup_env.sh prod"
}

# 환경변수 파일 생성 함수
create_env_file() {
    local env_type=$1
    local env_file=".env.${env_type}"
    
    print_info "환경변수 파일 생성 중: ${env_file}"
    
    # .env.example 파일이 존재하는지 확인
    if [ ! -f ".env.example" ]; then
        print_error ".env.example 파일이 존재하지 않습니다."
        exit 1
    fi
    
    # .env.example 파일 내용 읽기
    envContent=$(cat .env.example)
    
    # 환경별 설정 적용
    if [ "$env_type" = "local" ]; then
        envContent=$(echo "$envContent" | sed \
            -e 's/DJANGO_ENV=.*/DJANGO_ENV=local/' \
            -e 's/SECRET_KEY=.*/SECRET_KEY=local-development-secret-key-change-in-production/' \
            -e 's/DEBUG=.*/DEBUG=True/' \
            -e 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0/' \
            -e 's/DB_NAME=.*/DB_NAME=fablink_local_db/' \
            -e 's/DB_USER=.*/DB_USER=fablink_user/' \
            -e 's/DB_PASSWORD=.*/DB_PASSWORD=local123/' \
            -e 's/DB_HOST=.*/DB_HOST=localhost/' \
            -e 's/DB_PORT=.*/DB_PORT=5432/' \
            -e 's/USE_DYNAMODB=.*/USE_DYNAMODB=False/' \
            -e 's/DYNAMODB_TABLE_PREFIX=.*/DYNAMODB_TABLE_PREFIX=fablink_local/' \
            -e 's/CORS_ALLOWED_ORIGINS=.*/CORS_ALLOWED_ORIGINS=http:\/\/localhost:3000,http:\/\/127.0.0.1:3000/' \
            -e 's/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=local-jwt-secret-key/' \
            -e 's/USE_S3=.*/USE_S3=False/' \
            -e 's/AWS_STORAGE_BUCKET_NAME=.*/AWS_STORAGE_BUCKET_NAME=fablink-local-uploads/' \
            -e 's/LOG_LEVEL=.*/LOG_LEVEL=DEBUG/' \
            -e 's/ENABLE_SQL_LOGGING=.*/ENABLE_SQL_LOGGING=True/' \
            -e 's/ENABLE_DEBUG_TOOLBAR=.*/ENABLE_DEBUG_TOOLBAR=True/' \
            -e 's/ENABLE_EXPERIMENTAL_FEATURES=.*/ENABLE_EXPERIMENTAL_FEATURES=True/' \
            -e 's/MOCK_EXTERNAL_APIS=.*/MOCK_EXTERNAL_APIS=True/' \
            -e 's/SENTRY_ENVIRONMENT=.*/SENTRY_ENVIRONMENT=local/' \
            -e 's/OPENAI_API_KEY=.*/OPENAI_API_KEY=test-openai-key/' \
            -e 's/PAYMENT_GATEWAY_API_KEY=.*/PAYMENT_GATEWAY_API_KEY=test-payment-key/' \
            -e 's/PAYMENT_GATEWAY_SECRET=.*/PAYMENT_GATEWAY_SECRET=test-payment-secret/' \
            -e 's|MONGODB_URI=.*|MONGODB_URI=mongodb://localhost:9000|' \
            -e 's/MONGODB_DB=.*/MONGODB_DB=fablink/' \
            -e 's/MONGODB_COLLECTION_DESIGNER=.*/MONGODB_COLLECTION_DESIGNER=designer_orders/' \
            -e 's/MONGODB_COLLECTION_FACTORY=.*/MONGODB_COLLECTION_FACTORY=factory_orders/' )
            
    elif [ "$env_type" = "dev" ]; then
        envContent=$(echo "$envContent" | sed \
            -e 's/DJANGO_ENV=.*/DJANGO_ENV=dev/' \
            -e 's/SECRET_KEY=.*/SECRET_KEY=dev-secret-key-change-in-production/' \
            -e 's/DEBUG=.*/DEBUG=True/' \
            -e 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=dev-api.fablink.com,.amazonaws.com/' \
            -e 's/DB_NAME=.*/DB_NAME=fablink_dev_db/' \
            -e 's/DB_USER=.*/DB_USER=fablink_dev_user/' \
            -e 's/DB_PASSWORD=.*/DB_PASSWORD=dev-aurora-password/' \
            -e 's/DB_HOST=.*/DB_HOST=fablink-dev-aurora-cluster.cluster-xxxxx.ap-northeast-2.rds.amazonaws.com/' \
            -e 's/DB_PORT=.*/DB_PORT=5432/' \
            -e 's/USE_DYNAMODB=.*/USE_DYNAMODB=True/' \
            -e 's/DYNAMODB_REGION=.*/DYNAMODB_REGION=ap-northeast-2/' \
            -e 's/DYNAMODB_TABLE_PREFIX=.*/DYNAMODB_TABLE_PREFIX=fablink_dev/' \
            -e 's/CORS_ALLOWED_ORIGINS=.*/CORS_ALLOWED_ORIGINS=https:\/\/dev.fablink.com/' \
            -e 's/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=dev-jwt-secret-key/' \
            -e 's/USE_S3=.*/USE_S3=True/' \
            -e 's/AWS_STORAGE_BUCKET_NAME=.*/AWS_STORAGE_BUCKET_NAME=fablink-dev-uploads/' \
            -e 's/AWS_S3_REGION_NAME=.*/AWS_S3_REGION_NAME=ap-northeast-2/' \
            -e 's/LOG_LEVEL=.*/LOG_LEVEL=INFO/' \
            -e 's/ENABLE_SQL_LOGGING=.*/ENABLE_SQL_LOGGING=False/' \
            -e 's/ENABLE_DEBUG_TOOLBAR=.*/ENABLE_DEBUG_TOOLBAR=True/' \
            -e 's/ENABLE_EXPERIMENTAL_FEATURES=.*/ENABLE_EXPERIMENTAL_FEATURES=True/' \
            -e 's/MOCK_EXTERNAL_APIS=.*/MOCK_EXTERNAL_APIS=False/' \
            -e 's/SENTRY_ENVIRONMENT=.*/SENTRY_ENVIRONMENT=development/')
            
    elif [ "$env_type" = "prod" ]; then
        envContent=$(echo "$envContent" | sed \
            -e 's/DJANGO_ENV=.*/DJANGO_ENV=prod/' \
            -e 's/SECRET_KEY=.*/SECRET_KEY=super-secret-production-key-change-this/' \
            -e 's/DEBUG=.*/DEBUG=False/' \
            -e 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=api.fablink.com,.amazonaws.com/' \
            -e 's/DB_NAME=.*/DB_NAME=fablink_prod_db/' \
            -e 's/DB_USER=.*/DB_USER=fablink_prod_user/' \
            -e 's/DB_PASSWORD=.*/DB_PASSWORD=super-secure-aurora-password/' \
            -e 's/DB_HOST=.*/DB_HOST=fablink-prod-aurora-cluster.cluster-xxxxx.ap-northeast-2.rds.amazonaws.com/' \
            -e 's/DB_PORT=.*/DB_PORT=5432/' \
            -e 's/USE_DYNAMODB=.*/USE_DYNAMODB=True/' \
            -e 's/DYNAMODB_REGION=.*/DYNAMODB_REGION=ap-northeast-2/' \
            -e 's/DYNAMODB_TABLE_PREFIX=.*/DYNAMODB_TABLE_PREFIX=fablink_prod/' \
            -e 's/CORS_ALLOWED_ORIGINS=.*/CORS_ALLOWED_ORIGINS=https:\/\/fablink.com/' \
            -e 's/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=super-secure-jwt-key/' \
            -e 's/USE_S3=.*/USE_S3=True/' \
            -e 's/AWS_STORAGE_BUCKET_NAME=.*/AWS_STORAGE_BUCKET_NAME=fablink-prod-uploads/' \
            -e 's/AWS_S3_REGION_NAME=.*/AWS_S3_REGION_NAME=ap-northeast-2/' \
            -e 's/LOG_LEVEL=.*/LOG_LEVEL=ERROR/' \
            -e 's/SECURE_SSL_REDIRECT=.*/SECURE_SSL_REDIRECT=True/' \
            -e 's/SECURE_HSTS_SECONDS=.*/SECURE_HSTS_SECONDS=31536000/' \
            -e 's/SECURE_HSTS_INCLUDE_SUBDOMAINS=.*/SECURE_HSTS_INCLUDE_SUBDOMAINS=True/' \
            -e 's/SECURE_HSTS_PRELOAD=.*/SECURE_HSTS_PRELOAD=True/' \
            -e 's/SESSION_COOKIE_SECURE=.*/SESSION_COOKIE_SECURE=True/' \
            -e 's/CSRF_COOKIE_SECURE=.*/CSRF_COOKIE_SECURE=True/' \
            -e 's/SENTRY_ENVIRONMENT=.*/SENTRY_ENVIRONMENT=production/' \
            -e 's|MONGODB_URI=.*|MONGODB_URI=mongodb://localhost:9000|' \
            -e 's/MONGODB_DB=.*/MONGODB_DB=fablink/' \
            -e 's/MONGODB_COLLECTION_DESIGNER=.*/MONGODB_COLLECTION_DESIGNER=designer_orders/' \
            -e 's/MONGODB_COLLECTION_FACTORY=.*/MONGODB_COLLECTION_FACTORY=factory_orders/' )
    fi
    
    # 파일 생성
    echo "$envContent" > "$env_file"


    print_success "${env_file} 파일이 생성되었습니다."
    
    # 파일 권한 설정 (보안을 위해 소유자만 읽기/쓰기 가능)
    chmod 600 "$env_file"
    
    print_info "파일 권한이 600으로 설정되었습니다."
}

# 메인 실행 부분
main() {
    # 인자 확인
    if [ $# -eq 0 ]; then
        print_error "환경 타입을 지정해주세요."
        show_help
        exit 1
    fi
    
    env_type=$1
    
    # 도움말 요청 확인
    if [ "$env_type" = "-h" ] || [ "$env_type" = "--help" ]; then
        show_help
        exit 0
    fi
    
    # 유효한 환경 타입인지 확인
    if [ "$env_type" != "local" ] && [ "$env_type" != "dev" ] && [ "$env_type" != "prod" ]; then
        print_error "유효하지 않은 환경 타입입니다: $env_type"
        print_info "사용 가능한 환경 타입: local, dev, prod"
        exit 1
    fi
    
    # 프로젝트 루트 디렉토리로 이동
    cd "$(dirname "$0")/.."
    
    print_info "FabLink Backend 환경변수 설정을 시작합니다..."
    print_info "환경 타입: $env_type"
    
    # 환경변수 파일 생성
    create_env_file "$env_type"
    
    print_success "환경변수 설정이 완료되었습니다!"
    print_info "생성된 파일: .env.${env_type}"
    print_warning "⚠️  실제 운영에서는 보안을 위해 환경변수 값들을 변경해주세요."
}

# 스크립트 실행
main "$@"
