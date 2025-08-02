from django.db import models
from django.conf import settings

class Product(models.Model):

    SIZE_CHOICES = (
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('Free Size', 'Free Size'),
    )

    SEASON_CHOICES = (
        ('spring', '봄'),
        ('summer', '여름'),
        ('autumn', '가을'),
        ('winter', '겨울'),
        ('all-season', '사계절'),
    )
    
    TARGET_CHOICES = (
        ('teens', '10대'),
        ('twenties', '20대'),
        ('thirties', '30대'),
        ('forties', '40대'),
        ('fifties-plus', '50대 이상'),
        ('all-ages', '전 연령'),
    )
    
    designer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    target_customer = models.CharField(max_length=20, choices=TARGET_CHOICES)
    concept = models.TextField()
    detail = models.TextField(blank=True, null=True)                                            # 포인트 부위 설명 추가
    image_path = models.ImageField(upload_to='design_image/', blank=True, null=True)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, null=True)         # 수량 및 일정 관련 필드 추가
    quantity = models.PositiveIntegerField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ProductionOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', '대기중'),
        ('in_progress', '진행중'),
        ('completed', '완료'),
        ('cancelled', '취소'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='manufacturing_orders'
    )
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}개"