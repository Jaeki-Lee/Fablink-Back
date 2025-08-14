# fablink_project/urls_minimal.py
# 최소한의 URL 설정 (테스트용)

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def health_check(request):
    """헬스체크 엔드포인트"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Fablink Backend is running!',
        'version': '1.0.0'
    })

def api_info(request):
    """API 정보 엔드포인트"""
    return JsonResponse({
        'name': 'Fablink Backend API',
        'version': '1.0.0',
        'description': 'AI 기반 맞춤형 의류 제작 플랫폼',
        'endpoints': {
            '/': 'API 정보',
            '/health/': '헬스체크',
            '/admin/': '관리자 페이지',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', api_info, name='api_info'),
]
