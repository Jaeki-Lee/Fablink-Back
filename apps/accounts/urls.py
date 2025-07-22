from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'accounts'

router = DefaultRouter()
# router.register(r'users', UserViewSet)  # 나중에 추가

urlpatterns = [
    path('', include(router.urls)),
    # path('login/', LoginView.as_view(), name='login'),  # 나중에 추가
    # path('logout/', LogoutView.as_view(), name='logout'),
]
