from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product, ProductionOrder

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'designer', 'season', 'target_customer', 'created_at')
    list_filter = ('season', 'target_customer')
    search_fields = ('name', 'designer__username')

@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'manufacturer', 'quantity', 'status', 'delivery_date')
    list_filter = ('status', 'delivery_date')
    search_fields = ('product__name', 'manufacturer__username')