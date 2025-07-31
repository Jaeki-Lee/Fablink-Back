from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    # 목록 페이지에서 보여줄 필드들
    list_display = ('user_id', 'name', 'user_type', 'is_active', 'is_staff', 'created_at')
    list_filter = ('user_type', 'is_active', 'is_staff', 'created_at')
    search_fields = ('user_id', 'name', 'contact')
    ordering = ('-created_at',)

    # 상세 페이지 필드 구성
    fieldsets = (
        (None, {'fields': ('user_id', 'password')}),
        ('개인정보', {'fields': ('name', 'user_type', 'contact', 'address')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요 일자', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')

    # 새 사용자 추가 시 필드 구성
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_id', 'name', 'user_type', 'contact', 'address', 'password1', 'password2'),
        }),
    )

    # 검색 및 필터링을 위한 설정
    filter_horizontal = ('groups', 'user_permissions')
    
    # AbstractBaseUser를 사용하므로 기본 UserAdmin의 일부 설정을 오버라이드
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                'is_superuser',
                'user_permissions',
                'groups',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form
