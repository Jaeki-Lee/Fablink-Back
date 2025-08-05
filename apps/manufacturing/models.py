from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

# accounts 앱의 User 모델 import
from apps.accounts.models import User

class Product(models.Model):
    """제품 모델"""
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
    
    designer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name="디자이너",
        limit_choices_to={'user_type': 'designer'}
    )
    name = models.CharField(max_length=100, verbose_name="제품명")
    season = models.CharField(max_length=20, choices=SEASON_CHOICES, verbose_name="시즌")
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, verbose_name="타겟 고객층")
    concept = models.TextField(verbose_name="컨셉 설명")
    image_path = models.ImageField(upload_to='design_image/', null=True, blank=True, verbose_name="디자인 이미지")
    detail = models.TextField(blank=True, null=True, verbose_name="포인트 부위 설명")
    size = models.CharField(max_length=20, null=True, blank=True, verbose_name="사이즈")
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], 
        null=True, 
        blank=True, 
        verbose_name="수량"
    )
    fabric = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name="원단 정보",
        help_text="원단 종류, 무게, 신축성 등의 정보를 JSON 형태로 저장"
    )
    material = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name="부자재 정보",
        help_text="단추, 지퍼, 라이닝 등의 정보를 JSON 형태로 저장"
    ) 
    due_date = models.DateField(null=True, blank=True, verbose_name="납기일")
    memo = models.TextField(null=True, blank=True, verbose_name="메모")
    work_sheet_path = models.FileField(
        upload_to='worksheets/', 
        null=True, 
        blank=True, 
        verbose_name="작업지시서"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = 'products'
        verbose_name = "제품"
        verbose_name_plural = "제품들"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.designer.name}"


class Order(models.Model):
    """주문 모델"""
    STATUS_CHOICES = (
        ('pending', '대기중'),
        ('confirmed', '확인됨'),
        ('in_production', '생산중'),
        ('completed', '완료'),
        ('cancelled', '취소됨'),
    )
    
    order_id = models.CharField(max_length=50, unique=True, verbose_name="주문 번호")
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name="제품"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name="주문 상태"
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="주문 수량"
    )
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="단가"
    )
    total_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="총 금액"
    )
    receipt_path = models.FileField(
        upload_to='orders/receipts/', 
        null=True, 
        blank=True, 
        verbose_name="영수증"
    )
    notes = models.TextField(null=True, blank=True, verbose_name="주문 메모")
    
    # 고객 정보 (Product의 designer와 다를 수 있음)
    customer_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="고객명")
    customer_contact = models.CharField(max_length=50, null=True, blank=True, verbose_name="고객 연락처")
    
    # 배송 정보
    shipping_address = models.TextField(null=True, blank=True, verbose_name="배송 주소")
    shipping_method = models.CharField(max_length=50, null=True, blank=True, verbose_name="배송 방법")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="배송비")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = 'orders'
        verbose_name = "주문"
        verbose_name_plural = "주문들"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_id} - {self.product.name}"

    def save(self, *args, **kwargs):
        # 주문 번호 자동 생성
        if not self.order_id:
            self.order_id = f"ORD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # 총 금액 자동 계산
        if self.unit_price and self.quantity:
            self.total_price = self.unit_price * self.quantity
            
        super().save(*args, **kwargs)