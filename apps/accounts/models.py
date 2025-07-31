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
