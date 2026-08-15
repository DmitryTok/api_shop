from enum import IntEnum

from addons.int_enum import BaseIntEnumMixin
from django.contrib.auth import get_user_model
from django.db import models

from profiles.validators import validate_birthday, validate_phone

User = get_user_model()


class Gender(BaseIntEnumMixin, IntEnum):
    MALE = 1
    FEMALE = 2


class ClothingSize(BaseIntEnumMixin, IntEnum):
    XS = 1
    S = 2
    M = 3
    L = 4
    XL = 5
    XXl = 6


class Profile(models.Model):
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    surname = models.CharField(max_length=30, null=True, blank=True)
    gender = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
        choices=Gender.choices(),
    )
    clothing_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
        choices=ClothingSize.choices(),
    )
    shoe_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
    )
    birthday = models.DateField(null=True, blank=True, validators=[validate_birthday])
    phone = models.CharField(
        max_length=15, null=True, blank=True, validators=[validate_phone]
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return f"{self.user.email}"
