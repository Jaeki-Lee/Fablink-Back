from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, user_id, name, user_type='designer', password=None, **extra_fields):
        if not user_id:
            raise ValueError('사용자 ID는 필수입니다')
        
        user = self.model(
            user_id=user_id,
            name=name,
            user_type=user_type,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(user_id, name, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('designer', '디자이너'),
        ('factory', '공장주'),
    ]
    
    user_id = models.CharField(max_length=20, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='designer')
    name = models.CharField(max_length=20, default='')
    contact = models.CharField(max_length=20, default='')
    address = models.TextField(default='')
    
    # 권한 관련 필드
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.user_id})"
    
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'