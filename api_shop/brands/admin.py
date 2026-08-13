from django.contrib import admin

from api_shop.admin import CustomModelAdmin
from .models import Brand

@admin.register(Brand)
class BrandAdmin(CustomModelAdmin):
    list_display = ("id", "name", "slug", "is_active")
    search_fields = ("name", "slug")
    list_filter = ("is_active", "is_hidden")
