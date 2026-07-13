from django.db import models

from addons.mixins import TimeStampMixin
from brands.models import Brand
from categories.models import Subcategory


class Product(TimeStampMixin):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="products",
    )

    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name="products",
    )

    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]

# Create your models here.
