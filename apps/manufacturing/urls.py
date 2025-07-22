from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'manufacturing'

router = DefaultRouter()
# router.register(r'orders', ManufacturingOrderViewSet)  # 나중에 추가

urlpatterns = [
    path('', include(router.urls)),
]
