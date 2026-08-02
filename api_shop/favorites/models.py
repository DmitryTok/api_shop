from django.conf import settings
from django.db import models

from addons.mixins import TimeStampMixin
from product_variants.models import ProductVariant


class Favorite(TimeStampMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
    )

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="favorites",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product_variant"],
                name="unique_user_product_variant_favorite",
            )
        ]
