from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ==================== 통합 인증 ====================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', views.token_refresh_view, name='token_refresh'),
    
    # ==================== 디자이너 관련 ====================
    path('designer/profile/', views.designer_profile_view, name='designer_profile'),
    
    # ==================== 공장주 관련 ====================
    path('factory/profile/', views.factory_profile_view, name='factory_profile'),
]
