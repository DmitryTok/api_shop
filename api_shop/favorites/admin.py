from django.contrib import admin

from api_shop.admin import CustomModelAdmin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(CustomModelAdmin):
    list_display = (
        "id",
        "user",
        "product_variant",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__email",)
