from django.db import models

from addons.mixins import TimeStampMixin
from products.models import Product
from sizes.models import Size
from colors.models import Color


class ProductVariant(TimeStampMixin):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )

    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        related_name="product_variants",
    )

    color = models.ForeignKey(
       Color,
       on_delete=models.CASCADE,
       related_name="product_variants",
   )

    sku = models.CharField(
        max_length=100,
        unique=True,
    )

    stock = models.PositiveIntegerField(
        default=0,
    )

    gender = models.CharField(
        max_length=20,
    )

    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.sku

    class Meta:
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"
        ordering = ["-created_at"]
