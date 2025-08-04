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
    
    class Meta:
        model = Product
        fields = [
            'name', 'season', 'target', 'concept', 'detail', 
            'image_path', 'size', 'quantity', 'fabric', 
            'material', 'due_date', 'memo', 'work_sheet_path'
        ]
    
    def validate_quantity(self, value):
        """수량 검증"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("수량은 1 이상이어야 합니다.")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """제품 목록용 간단한 시리얼라이저"""
    designer_name = serializers.CharField(source='designer.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'season', 'target', 'concept', 
            'image_path', 'image_url', 'quantity', 'due_date',
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


class OrderSerializer(serializers.ModelSerializer):
    """주문 시리얼라이저"""
    product_info = ProductListSerializer(source='product', read_only=True)
    receipt_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'product', 'product_info', 'status', 
            'quantity', 'unit_price', 'total_price', 'receipt_path', 
            'receipt_url', 'notes', 'created_at', 'updated_at'
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
            'product', 'quantity', 'unit_price', 'receipt_path', 'notes'
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