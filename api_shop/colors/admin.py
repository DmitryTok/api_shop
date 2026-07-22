from django.contrib import admin

from .models import Color


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "hex_code", "is_active")
    search_fields = ("name", "hex_code")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
