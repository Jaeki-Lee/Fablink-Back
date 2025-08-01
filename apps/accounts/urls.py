from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.user_info_view, name='user_info'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
