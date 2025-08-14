FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# 애플리케이션 코드 복사
COPY . .

# 정적 파일 수집 (운영환경에서 실행)
# RUN python manage.py collectstatic --noinput --settings=fablink_project.settings.prod

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "fablink_project.wsgi:application"]