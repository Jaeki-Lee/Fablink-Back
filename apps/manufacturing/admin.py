from django.contrib import admin
from .models import Product, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'designer', 'season', 'target', 'created_at')
    list_filter = ('season', 'target', 'created_at')
    search_fields = ('name', 'designer__name', 'designer__user_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'designer', 'season', 'target', 'concept')
        }),
        ('상세 정보', {
            'fields': ('detail', 'image_path', 'size', 'quantity')
        }),
        ('소재 정보', {
            'fields': ('fabric', 'material')
        }),
        ('일정 및 메모', {
            'fields': ('due_date', 'memo', 'work_sheet_path')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'product', 'status', 'quantity', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'product__name')
    readonly_fields = ('order_id', 'total_price', 'created_at', 'updated_at')
    
    fieldsets = (
        ('주문 정보', {
            'fields': ('order_id', 'product', 'status', 'quantity')
        }),
        ('가격 정보', {
            'fields': ('unit_price', 'total_price')
        }),
        ('추가 정보', {
            'fields': ('receipt_path', 'notes')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at')
        }),
    )