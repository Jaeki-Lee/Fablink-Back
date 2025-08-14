#!/bin/bash

# Fablink Backend Docker 실행 스크립트

echo "🐳 Fablink Backend Docker 실행 스크립트"
echo "=================================="

# 1. 기존 컨테이너 정리
echo "1. 기존 컨테이너 정리 중..."
docker stop fablink-backend 2>/dev/null || true
docker rm fablink-backend 2>/dev/null || true

# 2. 이미지 빌드
echo "2. Docker 이미지 빌드 중..."
docker build -t fablink-backend:latest -f Dockerfile.dev .

if [ $? -ne 0 ]; then
    echo "❌ Docker 이미지 빌드 실패!"
    exit 1
fi

# 3. 환경변수 파일 확인
if [ ! -f ".env.local" ]; then
    echo "⚠️  .env.local 파일이 없습니다. .env.example을 복사합니다..."
    cp .env.example .env.local
    echo "📝 .env.local 파일을 수정해주세요!"
fi

# 4. SQLite 모드로 컨테이너 실행 (DB 연결 문제 방지)
echo "3. Docker 컨테이너 실행 중..."
docker run -d \
    --name fablink-backend \
    -p 8000:8000 \
    -e DJANGO_SETTINGS_MODULE=fablink_project.settings.dev \
    -e USE_SQLITE=True \
    -e DEBUG=True \
    -e ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0 \
    -v $(pwd):/app \
    fablink-backend:latest

if [ $? -eq 0 ]; then
    echo "✅ 컨테이너가 성공적으로 시작되었습니다!"
    echo ""
    echo "🌐 접속 URL: http://localhost:8000"
    echo "📋 관리자 페이지: http://localhost:8000/admin"
    echo ""
    echo "📊 컨테이너 상태 확인:"
    docker ps | grep fablink-backend
    echo ""
    echo "📝 로그 확인: docker logs fablink-backend"
    echo "🛑 중지: docker stop fablink-backend"
else
    echo "❌ 컨테이너 실행 실패!"
    exit 1
fi
