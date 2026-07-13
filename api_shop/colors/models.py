from django.db import models

from addons.mixins import TimeStampMixin


class Color(TimeStampMixin):
    name = models.CharField(
        max_length=50,
        unique=True,
    )

    hex_code = models.CharField(
        max_length=7,
        unique=True,
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colors"
        ordering = ["name"]


