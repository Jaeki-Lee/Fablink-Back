from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class DesignerManager(BaseUserManager):
    """디자이너 매니저"""
    def create_user(self, user_id, password=None, **extra_fields):
        if not user_id:
            raise ValueError('사용자 ID는 필수입니다.')
        
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, user_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(user_id, password, **extra_fields)

class Designer(AbstractBaseUser, PermissionsMixin):
    """디자이너 모델"""
    user_id = models.CharField(max_length=50, unique=True, verbose_name="사용자 ID")
    name = models.CharField(max_length=100, verbose_name="이름")
    profile_image = models.ImageField(
        upload_to='profiles/designers/', 
        null=True, 
        blank=True, 
        verbose_name="프로필 이미지"
    )
    contact = models.CharField(max_length=50, null=True, blank=True, verbose_name="연락처")
    address = models.TextField(null=True, blank=True, verbose_name="주소")
    
    # Django 인증 시스템 필수 필드
    is_active = models.BooleanField(default=True, verbose_name="활성 상태")
    is_staff = models.BooleanField(default=False, verbose_name="스태프 권한")
    
    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    objects = DesignerManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'designers'
        verbose_name = "디자이너"
        verbose_name_plural = "디자이너들"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user_id})"

    def get_full_name(self):
        """전체 이름 반환"""
        return self.name

    def get_short_name(self):
        """짧은 이름 반환"""
        return self.name


class FactoryManager(BaseUserManager):
    """공장주 매니저"""
    def create_user(self, user_id, password=None, **extra_fields):
        if not user_id:
            raise ValueError('사용자 ID는 필수입니다.')
        
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, user_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(user_id, password, **extra_fields)

class Factory(AbstractBaseUser, PermissionsMixin):
    """공장주 모델"""
    user_id = models.CharField(max_length=50, unique=True, verbose_name="사용자 ID")
    name = models.CharField(max_length=100, verbose_name="이름")
    company_name = models.CharField(max_length=200, verbose_name="회사명")
    business_license = models.CharField(max_length=50, null=True, blank=True, verbose_name="사업자등록번호")
    profile_image = models.ImageField(
        upload_to='profiles/factories/', 
        null=True, 
        blank=True, 
        verbose_name="프로필 이미지"
    )
    contact = models.CharField(max_length=50, null=True, blank=True, verbose_name="연락처")
    address = models.TextField(null=True, blank=True, verbose_name="주소")
    
    # 공장 특화 정보
    production_capacity = models.IntegerField(null=True, blank=True, verbose_name="생산 능력 (월)")
    specialties = models.TextField(null=True, blank=True, verbose_name="전문 분야")
    
    # Django 인증 시스템 필수 필드
    is_active = models.BooleanField(default=True, verbose_name="활성 상태")
    is_staff = models.BooleanField(default=False, verbose_name="스태프 권한")
    
    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    objects = FactoryManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['name', 'company_name']

    class Meta:
        db_table = 'factories'
        verbose_name = "공장주"
        verbose_name_plural = "공장주들"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.company_name} ({self.user_id})"

    def get_full_name(self):
        """전체 이름 반환"""
        return f"{self.name} ({self.company_name})"

    def get_short_name(self):
        """짧은 이름 반환"""
        return self.name


# 기존 User 모델과의 호환성을 위한 별칭 (Designer를 기본으로)
User = Designer
