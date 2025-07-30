from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'

router = DefaultRouter()
# router.register(r'users', UserViewSet)  # 나중에 추가

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('login/', LoginView.as_view(), name='login'),  # 나중에 추가
    # path('logout/', LogoutView.as_view(), name='logout'),
]
