from django.contrib import admin

from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product_variant",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__email",)
