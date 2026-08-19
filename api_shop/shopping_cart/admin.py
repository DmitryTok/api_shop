from django.contrib import admin

from api_shop.admin import CustomModelAdmin
from shopping_cart.models import CartItem, ShoppingCart


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(ShoppingCart)
class ShoppingCartAdmin(CustomModelAdmin):
    list_display = ("id", "user", "created_at", "updated_at")
    search_fields = ("user__email",)
    inlines = (CartItemInline,)


@admin.register(CartItem)
class CartItemAdmin(CustomModelAdmin):
    list_display = (
        "id",
        "cart",
        "product_variant",
        "quantity",
        "created_at",
        "updated_at",
    )
    search_fields = ("cart__user__email",)
