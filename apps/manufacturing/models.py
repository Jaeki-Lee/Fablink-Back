from django.db import models
from django.conf import settings

class Product(models.Model):
    SEASON_CHOICES = (
        ('spring', '봄'),
        ('summer', '여름'),
        ('autumn', '가을'),
        ('winter', '겨울'),
    )
    
    TARGET_CHOICES = (
        ('child', '아동'),
        ('teen', '청소년'),
        ('adult', '성인'),
        ('senior', '시니어'),
    )
    
    designer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    target_customer = models.CharField(max_length=20, choices=TARGET_CHOICES)
    concept = models.TextField()
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