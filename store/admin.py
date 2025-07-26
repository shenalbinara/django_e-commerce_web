from django.contrib import admin
from .models import Product  # or Product if you decide to rename it later


class ProductAdmin(admin.ModelAdmin):  # <-- FIXED HERE
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug' : ('product_name',)}

admin.site.register(Product, ProductAdmin)
