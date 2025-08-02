from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'season', 'target_customer', 'concept', 'detail', 
                 'image_path', 'size', 'quantity', 'due_date', 'designer', 'created_at', 'updated_at']
        read_only_fields = ['id', 'designer', 'created_at', 'updated_at']


class QuantityScheduleSerializer(serializers.ModelSerializer):      # 수량 및 일정 관련 필드만 포함
    class Meta:
        model = Product
        fields = ['size', 'quantity', 'due_date']
        
    def validate_quantity(self, value):
        if value is not None and value < 100:
            raise serializers.ValidationError("100개 이상 주문할 수 있습니다.")
        return value
        
    def validate_due_date(self, value):
        from datetime import date
        if value is not None and value <= date.today():
            raise serializers.ValidationError("희망 납기일은 오늘 이후여야 합니다.")
        return value