from addons.mixins import TimeStampMixin
from django.db import models


class Brand(TimeStampMixin):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"
        ordering = ["-created_at"]
