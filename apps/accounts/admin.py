# apps/accounts/admin.py (현재 비어있음)
from django.contrib import admin
# Register your models here.

# 추가 필요:
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'company')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('user_type', 'phone', 'company')}),
    )