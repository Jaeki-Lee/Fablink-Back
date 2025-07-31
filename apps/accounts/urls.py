from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 인증 관련
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', views.token_refresh_view, name='token_refresh'),
    
    # 사용자 정보 관련
    path('user/', views.user_info_view, name='user_info'),
    path('profile/', views.user_profile_update_view, name='profile_update'),
    path('password/change/', views.password_change_view, name='password_change'),
    
    # 유틸리티
    path('check-user-id/', views.check_user_id_view, name='check_user_id'),
    
    # 관리자용
    path('users/', views.user_list_view, name='user_list'),
]
