from django.conf import settings
from django.db import models

from addons.mixins import TimeStampMixin
from product_variants.models import ProductVariant


class ShoppingCart(TimeStampMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
    )

    def __str__(self):
        return f"Shopping cart of {self.user.email}"
    
    
class CartItem(TimeStampMixin):
    cart = models.ForeignKey(
        ShoppingCart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    def __str__(self):
        return f"{self.product_variant.sku} x {self.quantity}"  


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product_variant"],
                name="unique_cart_product_variant",
            )
        ]
          