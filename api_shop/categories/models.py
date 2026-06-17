from django.db import models
from addons.mixins import TimeStampMixin


class Category(TimeStampMixin):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)

   

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["-created_at"]


class Subcategory(TimeStampMixin):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories"
    )

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)

   

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        ordering = ["-created_at"]