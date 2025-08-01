from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'designer', 'season', 'target_customer', 'created_at')
    list_filter = ('season', 'target_customer')
    search_fields = ('name', 'designer__username')