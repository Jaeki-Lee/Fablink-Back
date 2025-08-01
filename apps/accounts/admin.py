from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Designer, Factory

@admin.register(Designer)
class DesignerAdmin(BaseUserAdmin):
    """디자이너 관리자 페이지"""
    
    # 목록 페이지에서 보여줄 필드들
    list_display = ('user_id', 'name', 'contact', 'profile_image_preview', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'created_at')
    search_fields = ('user_id', 'name', 'contact')
    ordering = ('-created_at',)

    # 상세 페이지 필드 구성
    fieldsets = (
        (None, {'fields': ('user_id', 'password')}),
        ('개인정보', {'fields': ('name', 'profile_image', 'contact', 'address')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요 일자', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')

    # 새 디자이너 추가 시 필드 구성
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_id', 'name', 'contact', 'address', 'profile_image', 'password1', 'password2'),
        }),
    )

    # 검색 및 필터링을 위한 설정
    filter_horizontal = ('groups', 'user_permissions')
    
    def profile_image_preview(self, obj):
        """프로필 이미지 미리보기"""
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_image.url
            )
        return "이미지 없음"
    profile_image_preview.short_description = "프로필 이미지"


@admin.register(Factory)
class FactoryAdmin(BaseUserAdmin):
    """공장주 관리자 페이지"""
    
    # 목록 페이지에서 보여줄 필드들
    list_display = ('user_id', 'name', 'company_name', 'business_license', 'contact', 'profile_image_preview', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'created_at')
    search_fields = ('user_id', 'name', 'company_name', 'business_license', 'contact')
    ordering = ('-created_at',)

    # 상세 페이지 필드 구성
    fieldsets = (
        (None, {'fields': ('user_id', 'password')}),
        ('개인정보', {'fields': ('name', 'profile_image', 'contact', 'address')}),
        ('회사정보', {'fields': ('company_name', 'business_license', 'production_capacity', 'specialties')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요 일자', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')

    # 새 공장주 추가 시 필드 구성
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_id', 'name', 'company_name', 'business_license', 'contact', 'address', 
                      'profile_image', 'production_capacity', 'specialties', 'password1', 'password2'),
        }),
    )

    # 검색 및 필터링을 위한 설정
    filter_horizontal = ('groups', 'user_permissions')
    
    def profile_image_preview(self, obj):
        """프로필 이미지 미리보기"""
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_image.url
            )
        return "이미지 없음"
    profile_image_preview.short_description = "프로필 이미지"
