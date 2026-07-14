from django.db import models

from addons.mixins import TimeStampMixin
from products.models import Product
from sizes.models import Size
from colors.models import Color

class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    UNISEX = "unisex", "Unisex"


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
        max_length=10,
        choices=Gender.choices,
        default=Gender.UNISEX,
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

        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["size"]),
            models.Index(fields=["color"]),
            models.Index(fields=["gender"]),
            models.Index(fields=["is_active"]),
        ]
