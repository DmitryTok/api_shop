from django.db import models

from addons.mixins import TimeStampMixin
from product_variants.models import ProductVariant


class Currency(TimeStampMixin):
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="currencies",
    )

    currency_code = models.CharField(max_length=3)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.currency_code} - {self.amount}"

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
        ordering = ["-created_at"]

        indexes = [
             models.Index(fields=["amount"]),
        ]
