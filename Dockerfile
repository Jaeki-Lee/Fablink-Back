# 1단계: 빌드 환경
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 빌드에 필요한 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치 (requirements 캐시 활용)
COPY requirements/ requirements/
RUN pip install --upgrade pip && pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements/production.txt

# 2단계: 런타임 환경
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 런타임에 필요한 패키지 설치 (postgresql-client 등)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# wheel 파일만 복사 후 설치
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# 코드 복사
COPY . .

# 정적 파일 수집
RUN python manage.py collectstatic --noinput --settings=fablink_project.settings.prod

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "fablink_project.wsgi:application"]
