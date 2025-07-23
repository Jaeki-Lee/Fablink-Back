from django.urls import path
from .views import LoginView, UserInfoView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    # JWT 패키지가 설치되면 아래 주석을 해제하세요
    # from rest_framework_simplejwt.views import TokenRefreshView
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserInfoView.as_view(), name='user_info'),
]