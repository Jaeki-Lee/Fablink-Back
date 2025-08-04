from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ==================== 통합 인증 ====================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', views.token_refresh_view, name='token_refresh'),
    
    # ==================== 사용자 프로필 ====================
    path('profile/', views.user_profile_view, name='user_profile'),
]