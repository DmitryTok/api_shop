from addons.mixins import TimeStampMixin
from django.db import models
from product_variants.models import ProductVariant


class Discount(TimeStampMixin):
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="discounts",
    )

    discount_type = models.CharField(max_length=20)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    start_at = models.DateTimeField()

    end_at = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.discount_type} - {self.amount}"

    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["start_at"]),
            models.Index(fields=["end_at"]),
        ]
