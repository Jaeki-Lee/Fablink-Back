from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # API 엔드포인트들
    path('api/auth/', include('apps.accounts.urls')),
    # path('api/manufacturing/', include('apps.manufacturing.urls')),
    # path('api/orders/', include('apps.orders.urls')),
    # path('api/notifications/', include('apps.notifications.urls')),
    # path('api/files/', include('apps.files.urls')),
]

# 개발환경에서 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
