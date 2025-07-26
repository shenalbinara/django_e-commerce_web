from django.contrib import admin
from .models import Category

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}  # Use tuple
    list_display = ('category_name', 'slug')            # Use tuple

admin.site.register(Category, CategoryAdmin)
