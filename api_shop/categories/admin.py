from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active", "is_hidden", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active", "is_hidden")
