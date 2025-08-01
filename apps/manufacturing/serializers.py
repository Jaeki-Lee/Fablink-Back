from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'season', 'target_customer', 'concept', 'detail', 'image_path', 'designer', 'created_at', 'updated_at']
        read_only_fields = ['id', 'designer', 'created_at', 'updated_at']
