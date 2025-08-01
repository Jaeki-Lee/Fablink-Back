from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, user_id, password=None, **extra_fields):
        if not user_id:
            raise ValueError('User ID는 필수입니다.')
        
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, user_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(user_id, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('designer', '디자이너'),
        ('factory', '공장주'),
    )
    
    # id는 자동으로 PK가 됨 (Django 기본) # id 필드 따로 존재
    user_id = models.CharField(max_length=20, unique=True)  # unique 필드
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='designer')
    name = models.CharField(max_length=20, default="")
    contact = models.CharField(max_length=20, default="")
    address = models.TextField(default="")
    
    # 관리자 권한용
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.user_id} - {self.name} ({self.get_user_type_display()})"


class Designer(models.Model):
    """디자이너 모델"""
    user_id = models.CharField(max_length=50, unique=True, verbose_name="사용자 ID")
    password = models.CharField(max_length=255, verbose_name="비밀번호")
    name = models.CharField(max_length=100, verbose_name="이름")
    profile_image = models.ImageField(
        upload_to='profiles/designers/', 
        null=True, 
        blank=True, 
        verbose_name="프로필 이미지"
    )
    contact = models.CharField(max_length=50, null=True, blank=True, verbose_name="연락처")
    address = models.TextField(null=True, blank=True, verbose_name="주소")
    is_active = models.BooleanField(default=True, verbose_name="활성 상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = 'designers'
        verbose_name = "디자이너"
        verbose_name_plural = "디자이너들"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user_id})"


class Factory(models.Model):
    """공장 모델"""
    user_id = models.CharField(max_length=50, unique=True, verbose_name="사용자 ID")
    password = models.CharField(max_length=255, verbose_name="비밀번호")
    name = models.CharField(max_length=100, verbose_name="공장명")
    profile_image = models.ImageField(
        upload_to='profiles/factories/', 
        null=True, 
        blank=True, 
        verbose_name="프로필 이미지"
    )
    contact = models.CharField(max_length=50, null=True, blank=True, verbose_name="연락처")
    address = models.TextField(null=True, blank=True, verbose_name="주소")
    is_active = models.BooleanField(default=True, verbose_name="활성 상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = 'factory'
        verbose_name = "공장"
        verbose_name_plural = "공장들"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user_id})"