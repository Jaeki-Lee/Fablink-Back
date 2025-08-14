# Fablink Backend K8s 배포 체크리스트

## 🚀 배포 전 준비사항

### 인프라 확인
- [x] AWS 계정 및 권한 확인
- [x] EKS 클러스터 상태 확인 (`fablink-cluster-dev`)
- [x] Aurora DB 클러스터 상태 확인 (`fablink-aurora-cluster`)
- [x] ECR 리포지토리 확인 (`fablink-backend`)
- [x] kubectl 설정 및 연결 확인

### 코드 및 설정 준비
- [x] Django 설정 파일 작성 (`settings/k8s.py`)
- [x] URL 설정 파일 작성 (`urls_k8s.py`)
- [x] Dockerfile 작성 (`Dockerfile.k8s`)
- [x] K8s 매니페스트 작성 (`k8s-deployment.yaml`)

## 🔧 빌드 및 배포 단계

### Docker 이미지 빌드
- [x] 로컬 Docker 이미지 빌드
- [x] ECR 로그인
- [x] 이미지 태깅
- [x] ECR에 이미지 푸시

### Kubernetes 배포
- [x] kubectl 클러스터 연결 확인
- [x] 매니페스트 파일 적용
- [x] Deployment 생성 확인
- [x] Service 생성 확인
- [x] Pod 상태 확인

## 🔍 배포 후 검증

### 기본 상태 확인
- [x] Pod 실행 상태 확인
- [x] Service 엔드포인트 확인
- [x] LoadBalancer 외부 IP 할당 확인
- [ ] **Health Check 통과** ❌ (ALLOWED_HOSTS 문제)

### 데이터베이스 연결
- [x] Aurora DB 연결 성공
- [ ] **마이그레이션 완료** ❌ (auth_user 테이블 누락)
- [ ] 슈퍼유저 생성 완료

### API 엔드포인트 테스트
- [ ] **메인 API (/) 응답** ❌ (500 에러)
- [ ] **헬스체크 (/health/) 응답** ❌ (500 에러)
- [ ] **DB 체크 (/db-check/) 응답** ❌ (500 에러)
- [ ] 관리자 페이지 (/admin/) 접근

## 🚨 현재 이슈 및 해결 계획

### 긴급 해결 필요 (Priority 1)
- [ ] **ALLOWED_HOSTS 설정 수정**
  - 문제: Pod IP가 ALLOWED_HOSTS에 포함되지 않음
  - 해결: `ALLOWED_HOSTS = ['*']` 또는 동적 IP 추가
  - 담당자: DevOps
  - 예상 시간: 30분

- [ ] **Django 설정 파일 수정**
  - 문제: k8s.py 설정이 여전히 기본 설정을 import
  - 해결: 독립적인 설정 파일 생성
  - 담당자: Backend
  - 예상 시간: 20분

### 중요 해결 필요 (Priority 2)
- [ ] **데이터베이스 마이그레이션**
  - 문제: auth_user 테이블 누락
  - 해결: 초기 마이그레이션 실행
  - 담당자: Backend
  - 예상 시간: 15분

- [ ] **Health Check 프로브 조정**
  - 문제: 너무 짧은 초기 지연 시간
  - 해결: initialDelaySeconds 증가
  - 담당자: DevOps
  - 예상 시간: 10분

### 개선 사항 (Priority 3)
- [ ] **보안 강화**
  - Kubernetes Secrets 사용
  - CORS 정책 개선
  - HTTPS 설정

- [ ] **모니터링 설정**
  - CloudWatch 로그 연동
  - 메트릭 수집 설정
  - 알람 설정

## 📋 다음 작업 단계

### 즉시 실행 (오늘)
1. **ALLOWED_HOSTS 문제 해결**
   ```python
   ALLOWED_HOSTS = ['*']  # K8s 환경용
   ```

2. **새 이미지 빌드 및 배포**
   ```bash
   docker build -t fablink-backend:v1.0.2 .
   docker push ecr-repo/fablink-backend:v1.0.2
   kubectl set image deployment/fablink-backend django=ecr-repo/fablink-backend:v1.0.2
   ```

3. **API 엔드포인트 테스트**
   ```bash
   curl http://loadbalancer-url/health/
   ```

### 단기 계획 (이번 주)
- [ ] HTTPS 설정 (ALB + ACM)
- [ ] 모니터링 대시보드 구성
- [ ] 자동 스케일링 설정

### 중기 계획 (이번 달)
- [ ] CI/CD 파이프라인 구축
- [ ] 보안 정책 강화
- [ ] 성능 최적화

## 🔄 롤백 계획

### 롤백 시나리오
1. **새 배포 실패 시**
   ```bash
   kubectl rollout undo deployment/fablink-backend
   ```

2. **데이터베이스 문제 시**
   - Aurora 스냅샷 복원
   - 이전 버전 이미지로 롤백

3. **완전 장애 시**
   - 로컬 Docker 환경으로 임시 전환
   - 기존 안정 버전으로 복구

## 📞 연락처 및 책임자

- **DevOps**: EKS, 인프라 관리
- **Backend**: Django, 애플리케이션 코드
- **DBA**: Aurora DB 관리
- **보안**: 보안 정책 및 검토

## 📊 성공 기준

### 배포 성공 조건
- [ ] 모든 Pod가 Running 상태
- [ ] Health Check 통과 (200 OK)
- [ ] 모든 API 엔드포인트 정상 응답
- [ ] 데이터베이스 연결 및 쿼리 성공
- [ ] LoadBalancer를 통한 외부 접근 가능

### 성능 기준
- [ ] 응답 시간 < 500ms
- [ ] CPU 사용률 < 70%
- [ ] 메모리 사용률 < 80%
- [ ] 에러율 < 1%
