# fablink_project/urls_k8s.py
# Kubernetes 배포용 URL 설정

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

def health_check(request):
    """헬스체크 엔드포인트"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Fablink Backend is running on Kubernetes!',
        'version': '1.0.0',
        'environment': 'k8s',
        'database': 'aurora-postgresql'
    })

def api_info(request):
    """API 정보 엔드포인트"""
    return JsonResponse({
        'name': 'Fablink Backend API',
        'version': '1.0.0',
        'description': 'AI 기반 맞춤형 의류 제작 플랫폼',
        'environment': 'kubernetes',
        'database': {
            'type': 'Aurora PostgreSQL',
            'host': os.getenv('DB_HOST', 'aurora-cluster'),
            'name': os.getenv('DB_NAME', 'fablink')
        },
        'endpoints': {
            '/': 'API 정보',
            '/health/': '헬스체크',
            '/admin/': '관리자 페이지',
        }
    })

def db_check(request):
    """데이터베이스 연결 확인"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
        
        return JsonResponse({
            'status': 'connected',
            'database': 'Aurora PostgreSQL',
            'version': db_version,
            'host': os.getenv('DB_HOST'),
            'name': os.getenv('DB_NAME')
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'database': 'Aurora PostgreSQL',
            'host': os.getenv('DB_HOST'),
            'name': os.getenv('DB_NAME')
        }, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('db-check/', db_check, name='db_check'),
    path('', api_info, name='api_info'),
]
