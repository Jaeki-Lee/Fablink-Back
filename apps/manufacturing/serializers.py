from rest_framework import serializers
from .models import Product, Order
from apps.accounts.serializers import UserSerializer

class ProductSerializer(serializers.ModelSerializer):
    """제품 시리얼라이저"""
    designer_info = UserSerializer(source='designer', read_only=True)
    image_url = serializers.SerializerMethodField()
    work_sheet_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'season', 'target', 'concept', 'detail', 
            'image_path', 'image_url', 'size', 'quantity', 'fabric', 
            'material', 'due_date', 'memo', 'work_sheet_path', 'work_sheet_url',
            'designer', 'designer_info', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'designer', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        """이미지 URL 반환"""
        if obj.image_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_path.url)
            return obj.image_path.url
        return None
    
    def get_work_sheet_url(self, obj):
        """작업지시서 URL 반환"""
        if obj.work_sheet_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.work_sheet_path.url)
            return obj.work_sheet_path.url
        return None


class ProductCreateSerializer(serializers.ModelSerializer):
    """제품 생성용 시리얼라이저"""
    target_customer = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'season', 'target', 'target_customer', 'concept', 'detail', 
            'image_path', 'size', 'quantity', 'fabric', 
            'material', 'due_date', 'memo', 'work_sheet_path'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'image_path': {'required': False},
            'target': {'required': False}
        }
    
    def validate_name(self, value):
        """제품명 검증"""
        if not value or not value.strip():
            raise serializers.ValidationError("제품명은 필수입니다.")
        return value.strip()
    
    def validate_season(self, value):
        """시즌 검증"""
        valid_seasons = ['spring', 'summer', 'autumn', 'winter', 'all-season']
        if value not in valid_seasons:
            raise serializers.ValidationError(f"유효한 시즌을 선택해주세요: {', '.join(valid_seasons)}")
        return value
    
    def validate_target(self, value):
        """타겟 고객층 검증"""
        valid_targets = ['teens', 'twenties', 'thirties', 'forties', 'fifties-plus', 'all-ages']
        if value not in valid_targets:
            raise serializers.ValidationError(f"유효한 타겟 고객층을 선택해주세요: {', '.join(valid_targets)}")
        return value
    
    def validate_concept(self, value):
        """컨셉 검증"""
        if not value or not value.strip():
            raise serializers.ValidationError("컨셉 설명은 필수입니다.")
        return value.strip()
    
    def validate_quantity(self, value):
        """수량 검증"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("수량은 1 이상이어야 합니다.")
        return value
    
    def validate(self, attrs):
        """전체 데이터 검증"""
        # target_customer를 target으로 매핑
        if 'target_customer' in attrs:
            attrs['target'] = attrs.pop('target_customer')
        
        # 필수 필드 검증
        required_fields = ['name', 'season', 'target', 'concept']
        for field in required_fields:
            if field not in attrs or not attrs[field]:
                raise serializers.ValidationError(f"{field} 필드는 필수입니다.")
        
        return attrs


class ProductListSerializer(serializers.ModelSerializer):
    """제품 목록용 간단한 시리얼라이저"""
    designer_name = serializers.CharField(source='designer.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    work_sheet_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'season', 'target', 'concept', 'detail',
            'image_path', 'image_url', 'quantity', 'due_date', 'fabric',
            'material', 'memo', 'work_sheet_path', 'work_sheet_url',
            'designer', 'designer_name', 'created_at'
        ]
    
    def get_image_url(self, obj):
        """이미지 URL 반환"""
        if obj.image_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_path.url)
            return obj.image_path.url
        return None
    
    def get_work_sheet_url(self, obj):
        """작업지시서 URL 반환"""
        if obj.work_sheet_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.work_sheet_path.url)
            return obj.work_sheet_path.url
        return None


class OrderSerializer(serializers.ModelSerializer):
    """주문 시리얼라이저"""
    product_info = ProductListSerializer(source='product', read_only=True)
    receipt_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'product', 'product_info', 'status', 
            'quantity', 'unit_price', 'total_price', 'receipt_path', 
            'receipt_url', 'notes', 'customer_name', 'customer_contact', 
            'shipping_address', 'shipping_method', 
            'shipping_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_id', 'total_price', 'created_at', 'updated_at']
    
    def get_receipt_url(self, obj):
        """영수증 URL 반환"""
        if obj.receipt_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.receipt_path.url)
            return obj.receipt_path.url
        return None


class OrderCreateSerializer(serializers.ModelSerializer):
    """주문 생성용 시리얼라이저"""
    
    class Meta:
        model = Order
        fields = [
            'product', 'quantity', 'unit_price', 'receipt_path', 'notes',
            'customer_name', 'customer_contact',
            'shipping_address', 'shipping_method', 'shipping_cost'
        ]
    
    def validate_quantity(self, value):
        """수량 검증"""
        if value <= 0:
            raise serializers.ValidationError("수량은 1 이상이어야 합니다.")
        return value
    
    def validate_unit_price(self, value):
        """단가 검증"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("단가는 0보다 커야 합니다.")
        return value