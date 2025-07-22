from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'company', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'company')
    
    # 기존 UserAdmin의 fieldsets에 추가 필드 포함
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {
            'fields': ('user_type', 'phone', 'company'),
        }),
    )
    
    # 사용자 추가 시 보여줄 필드
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('추가 정보', {
            'fields': ('user_type', 'phone', 'company'),
        }),
    )