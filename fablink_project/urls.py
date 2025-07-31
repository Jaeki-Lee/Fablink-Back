from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    """API 루트 엔드포인트"""
    return JsonResponse({
        'message': 'FabLink API Server',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'accounts': '/api/accounts/',
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    # API 엔드포인트들
    path('api/auth/', include('apps.accounts.urls')),
    # path('api/manufacturing/', include('apps.manufacturing.urls')),
    # path('api/orders/', include('apps.orders.urls')),
    # path('api/notifications/', include('apps.notifications.urls')),
    # path('api/files/', include('apps.files.urls')),
=======
    path('api/accounts/', include('apps.accounts.urls')),
>>>>>>> e33323476e2dd02895507acc67ffce896ce6cd48
]

# Debug Toolbar URLs (로컬 환경에서만)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# 정적 파일 서빙 (로컬 환경에서만)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

