from django.db import models

from addons.mixins import TimeStampMixin


class Kind(models.TextChoices):
    CLOTHING = "clothing", "Clothing"
    SHOES = "shoes", "Shoes"
    ACCESSORIES = "accessories", "Accessories"


class Size(TimeStampMixin):
    name = models.CharField(
        max_length=20,
        unique=True,
    )

    size_type = models.CharField(
        max_length=20,
        choices=Kind.choices,
    )

    sort_order = models.PositiveIntegerField(
        default=0,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Size"
        verbose_name_plural = "Sizes"
        ordering = ["sort_order"]