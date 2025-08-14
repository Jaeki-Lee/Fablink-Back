#!/bin/bash

# 간단한 Django Docker 테스트 스크립트

echo "🧪 Django Docker 테스트"
echo "======================"

# 1. 간단한 Dockerfile로 테스트
echo "1. 간단한 이미지 빌드 중..."
docker build -t fablink-test:latest -f Dockerfile.simple .

# 2. 컨테이너 실행 (SQLite 사용)
echo "2. 테스트 컨테이너 실행 중..."
docker run --rm -it \
    -p 8000:8000 \
    -e USE_SQLITE=True \
    -e DEBUG=True \
    -e ALLOWED_HOSTS=* \
    fablink-test:latest

echo "✅ 테스트 완료!"
