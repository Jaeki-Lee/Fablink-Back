# FabLink Backend 🚀

AI 기반 맞춤형 의류 제작 플랫폼 FabLink의 Django REST API 서버입니다.

## 📌 목차
1. [환경별 설정 가이드](#-환경별-설정-가이드)
2. [빌드 가이드](#-빌드-가이드)
3. [새 기능 개발 가이드](#-새-기능-개발-가이드)

## 🔧 환경별 설정 가이드

### 공통 준비사항

```bash
# 1. 저장소 클론
git clone https://github.com/your-username/Fablink-Back.git
cd Fablink-Back

# 2. 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 스크립트 실행 안될시
```bash
1. 스크립트 디렉토리로 이동후 모든 스크립트 들의 줄 끝의 r 문자 제거 및 권한 부여
cd /scripts
for file in *.sh; do sed -i 's/\r$//' "$file"; chmod +x "$file"; done
2.fix_scripts 실행
```

### 환경별 초기 설정

각 환경(local/dev/prod)별로 다음 3단계를 순서대로 실행합니다:

1. **환경변수 설정** (setup_env.sh)
2. **데이터베이스 설정** (setup_postgresql_[env].sh)
3. **최초 빌드 실행** (first_build.sh)

#### 로컬 환경 설정
```bash
# 1. 환경변수 설정
./scripts/setup_env.sh local
# => .env.local 파일 생성
# => 기본 환경변수 설정

# 2. PostgreSQL 설치 및 DB 설정
./scripts/setup_postgresql_local.sh
# => PostgreSQL 설치 (없는 경우)
# => 로컬 DB 및 사용자 생성
# => 기본 DB: fablink_local_db
# => 기본 사용자: fablink_user

# 3. 최초 빌드 실행
./scripts/first_build.sh local
# => 패키지 설치
# => DB 마이그레이션
# => 기본 관리자 계정 생성
```

#### 개발 서버 환경 설정
```bash
# 1. 환경변수 설정
./scripts/setup_env.sh dev
# => .env.dev 파일 생성
# => 개발 서버용 환경변수 설정

# 2. PostgreSQL 설정 (AWS RDS)
./scripts/setup_postgresql_dev.sh
# => RDS 엔드포인트 입력 필요
# => DB 접속 정보 입력 필요
# => 개발용 DB 및 사용자 생성

# 3. 최초 빌드 실행
./scripts/first_build.sh dev
# => 개발 서버용 패키지 설치
# => DB 마이그레이션
# => 정적 파일 수집
```

#### 운영 서버 환경 설정
```bash
# 1. 환경변수 설정
./scripts/setup_env.sh prod
# => .env.prod 파일 생성
# => 운영 서버용 환경변수 설정

# 2. PostgreSQL 설정 (AWS RDS)
./scripts/setup_postgresql_prod.sh
# => 운영 RDS 엔드포인트 입력
# => 보안 정보 입력
# => 운영용 DB 및 사용자 생성

# 3. 최초 빌드 실행
./scripts/first_build.sh prod
# => 운영 서버용 패키지 설치
# => DB 마이그레이션
# => 정적 파일 수집
# => 보안 설정 적용
```

## 🚀 빌드 가이드

### 빌드 타입 개요

| 빌드 타입 | 설명 | 사용 시나리오 |
|-----------|------|---------------|
| normal | 일반 빌드 | 코드 수정 후 |
| model | 모델 변경 빌드 | DB 모델 변경 시 |
| rebuild | DB 재구성 빌드 | DB 완전 초기화 필요 시 |

### 일반 빌드 (normal)

코드 수정 후 일반적인 빌드를 실행할 때 사용합니다.

```bash
# 기본 사용법
./scripts/build.sh [환경] normal

# 예시
./scripts/build.sh local normal
./scripts/build.sh dev normal
./scripts/build.sh prod normal
```

### 모델 변경 빌드 (model)

Django 모델 변경 시 사용하며, 여러 옵션을 제공합니다.

```bash
# 1. 전체 앱 마이그레이션
./scripts/build.sh local model

# 2. 특정 앱만 마이그레이션
./scripts/build.sh local model --app accounts

# 3. 데이터 삭제 후 마이그레이션
./scripts/build.sh local model --flush  # local/dev만 가능
```

#### 모델 변경 시나리오별 가이드

1. **새 필드 추가** (기존 데이터 유지)
   ```python
   # models.py
   class User(AbstractUser):
       name = models.CharField(max_length=100)
       phone = models.CharField(max_length=20, null=True)  # 새 필드
   ```
   ```bash
   ./scripts/build.sh local model  # flush 불필요
   ```

2. **필수 필드 추가** (기존 데이터 삭제 필요)
   ```python
   # models.py
   class User(AbstractUser):
       phone = models.CharField(max_length=20)  # 필수 필드
   ```
   ```bash
   ./scripts/build.sh local model --flush
   ```

### DB 재구성 빌드 (rebuild)

데이터베이스를 완전히 초기화해야 할 때 사용합니다.

```bash
# ⚠️ 주의: 모든 데이터가 삭제됩니다!
./scripts/build.sh local rebuild

# 개발 서버 (DBA 승인 필요)
./scripts/build.sh dev rebuild

# 운영 서버에서는 사용 불가
./scripts/build.sh prod rebuild  # ❌ 에러 발생
```

## 🛠 새 기능 개발 가이드

### 새 앱 생성

`create_app.sh` 스크립트를 사용하여 새로운 Django 앱을 생성합니다.

```bash
# 기본 사용법
./scripts/create_app.sh [앱이름] [옵션]

# 예시
./scripts/create_app.sh payments                    # 일반 앱 생성
./scripts/create_app.sh analytics --api-only        # API 전용 앱 생성
./scripts/create_app.sh reviews --no-auto-config    # 수동 설정 앱 생성
```

### 생성되는 앱 구조

```
apps/your_app/
├── __init__.py
├── admin.py              # 관리자 페이지 설정
├── apps.py              # 앱 설정
├── models.py            # 데이터 모델
├── serializers.py       # DRF 시리얼라이저
├── services.py          # 비즈니스 로직
├── permissions.py       # 권한 설정
├── urls.py              # URL 라우팅
├── views.py            # API 뷰
├── viewsets.py         # API ViewSets (--api-only)
├── filters.py          # 필터링 (--api-only)
└── tests/              # 테스트 코드
    ├── __init__.py
    ├── test_models.py
    ├── test_api.py
    └── test_services.py
```

### 옵션 설명

| 옵션 | 설명 | 예시 |
|------|------|------|
| --api-only | API 전용 앱 생성 | ./scripts/create_app.sh payments --api-only |
| --no-auto-config | 자동 설정 건너뛰기 | ./scripts/create_app.sh reviews --no-auto-config |

### 앱 생성 후 작업

1. **모델 정의**
   ```python
   # apps/payments/models.py
   from django.db import models
   
   class Payment(models.Model):
       amount = models.DecimalField(max_digits=10, decimal_places=2)
       # ... 필요한 필드 추가
   ```

2. **마이그레이션 생성 및 적용**
   ```bash
   ./scripts/build.sh local model --app payments
   ```

3. **API 구현**
   ```python
   # apps/payments/views.py 또는 viewsets.py
   from rest_framework import viewsets
   from .models import Payment
   from .serializers import PaymentSerializer
   
   class PaymentViewSet(viewsets.ModelViewSet):
       queryset = Payment.objects.all()
       serializer_class = PaymentSerializer
   ```

4. **URL 설정**
   ```python
   # apps/payments/urls.py
   from django.urls import path, include
   from rest_framework.routers import DefaultRouter
   from . import viewsets
   
   router = DefaultRouter()
   router.register(r'payments', viewsets.PaymentViewSet)
   
   urlpatterns = [
       path('', include(router.urls)),
   ]
   ```

### 테스트 작성

```python
# apps/payments/tests/test_api.py
from rest_framework.test import APITestCase
from django.urls import reverse

class PaymentAPITest(APITestCase):
    def test_create_payment(self):
        url = reverse('payments-list')
        data = {'amount': '100.00'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
```

## ⚠️ 주의사항

1. **운영 환경 작업 시**
   - 데이터 삭제 작업 불가 (--flush, rebuild 옵션 사용 불가)
   - 항상 백업 필요
   - DBA와 사전 협의 필수

2. **개발 서버 작업 시**
   - 테스트 완료 후 배포
   - 다른 개발자와 동시 작업 주의

3. **로컬 환경 작업 시**
   - 가상환경 활성화 상태 확인
   - 최신 코드 동기화 확인
   - 브랜치 확인

## 🔍 환경별 접속 정보

### 로컬 환경
- http://localhost:8000/
- http://localhost:8000/admin/
- http://localhost:8000/api/

### 개발 서버
- https://dev-api.fablink.com/
- https://dev-api.fablink.com/admin/
- https://dev-api.fablink.com/api/

### 운영 서버
- https://api.fablink.com/
- https://api.fablink.com/admin/
- https://api.fablink.com/api/
