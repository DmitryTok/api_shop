from django.contrib import admin

from api_shop.admin import CustomModelAdmin
from .models import Category, Subcategory


@admin.register(Category)
class CategoryAdmin(CustomModelAdmin):
    list_display = ("id", "name", "slug", "is_active", "is_hidden", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active", "is_hidden")

@admin.register(Subcategory)
class SubcategoryAdmin(CustomModelAdmin):
    list_display = ("id", "name", "slug", "category")
    search_fields = ("name", "slug")
