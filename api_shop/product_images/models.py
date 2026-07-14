from django.db import models

from addons.mixins import TimeStampMixin
from product_variants.models import ProductVariant


class ProductImage(TimeStampMixin):
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="products/",
    )

    is_main = models.BooleanField(
        default=False,
    )

    sort_order = models.PositiveIntegerField(
        default=0,
    )

    def __str__(self):
        return f"{self.product_variant.sku} Image"

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ["sort_order", "id"]

        indexes = [
            models.Index(fields=["product_variant"]),
        ]


