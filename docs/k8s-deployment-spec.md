# Fablink Backend Kubernetes 배포 기술 명세서

## 📋 프로젝트 개요

**프로젝트명**: Fablink Backend K8s 배포  
**버전**: v1.0.1  
**배포 환경**: AWS EKS + Aurora PostgreSQL  
**작성일**: 2025-08-14  

## 🏗️ 아키텍처 구성

### 인프라 구성요소
- **EKS 클러스터**: `fablink-cluster-dev`
- **Aurora DB**: `fablink-aurora-cluster` (PostgreSQL 15.4)
- **ECR 리포지토리**: `853963783084.dkr.ecr.ap-northeast-2.amazonaws.com/fablink-backend`
- **LoadBalancer**: AWS ELB (Classic)

### 애플리케이션 스택
- **Backend Framework**: Django 4.2.7
- **WSGI Server**: Gunicorn 21.2.0
- **Database**: Aurora PostgreSQL
- **Container Runtime**: Docker
- **Orchestration**: Kubernetes (EKS)

## 🔧 기술 스펙

### Docker 이미지
```dockerfile
FROM python:3.11-slim
# 주요 패키지
- Django==4.2.7
- djangorestframework==3.14.0
- psycopg2-binary==2.9.9
- gunicorn==21.2.0
```

### Kubernetes 리소스
```yaml
# Deployment
- Replicas: 2
- Image: fablink-backend:latest
- Resources: 512Mi/250m (request), 1Gi/500m (limit)

# Service
- Type: LoadBalancer
- Port: 80 -> 8000
```

### 환경변수
| 변수명 | 값 | 설명 |
|--------|----|----|
| DJANGO_SETTINGS_MODULE | fablink_project.settings.k8s | Django 설정 모듈 |
| DJANGO_ENV | production | 환경 구분 |
| DEBUG | False | 디버그 모드 |
| DB_HOST | fablink-aurora-cluster.cluster-cr2c0e2q6qeb.ap-northeast-2.rds.amazonaws.com | Aurora 엔드포인트 |
| DB_NAME | fablink | 데이터베이스명 |
| DB_USER | fablinkadmin | DB 사용자 |
| DB_PASSWORD | fablink123! | DB 비밀번호 |

## 🌐 엔드포인트

### LoadBalancer URL
```
http://ab936d849f5784e168ee84b50b7d0e21-1046340646.ap-northeast-2.elb.amazonaws.com
```

### API 엔드포인트
- **메인**: `/` - API 정보
- **헬스체크**: `/health/` - 서비스 상태 확인
- **DB 체크**: `/db-check/` - 데이터베이스 연결 확인
- **관리자**: `/admin/` - Django 관리자 페이지

## 🔍 모니터링 및 로깅

### Health Check
```yaml
livenessProbe:
  httpGet:
    path: /health/
    port: 8000
  initialDelaySeconds: 60
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health/
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

### 로그 확인 명령어
```bash
# Pod 로그 확인
kubectl logs -l app=fablink-backend --tail=50

# 실시간 로그 모니터링
kubectl logs -l app=fablink-backend -f
```

## 🚨 알려진 이슈

### 현재 문제점
1. **ALLOWED_HOSTS 오류**: Pod IP가 ALLOWED_HOSTS에 포함되지 않음
2. **DB 마이그레이션**: auth_user 테이블 누락
3. **Health Check 실패**: ALLOWED_HOSTS 문제로 인한 헬스체크 실패

### 해결 방안
1. Django 설정에서 ALLOWED_HOSTS = ['*'] 설정
2. 초기 마이그레이션 실행 필요
3. 프로브 설정 조정

## 📊 성능 지표

### 리소스 사용량
- **CPU**: 250m (request) / 500m (limit)
- **Memory**: 512Mi (request) / 1Gi (limit)
- **Replicas**: 2개

### 예상 처리량
- **동시 연결**: ~100 connections
- **응답 시간**: < 200ms (정상 상태)
- **처리량**: ~1000 req/min

## 🔐 보안 고려사항

### 현재 보안 설정
- **CORS**: 모든 오리진 허용 (개발용)
- **HTTPS**: 미설정 (추후 구현 필요)
- **Secret 관리**: 환경변수로 관리 (개선 필요)

### 보안 개선 계획
- [ ] Kubernetes Secrets 사용
- [ ] HTTPS/TLS 설정
- [ ] CORS 정책 강화
- [ ] 네트워크 정책 적용
