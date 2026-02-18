from django.db import models
from django.contrib.auth import get_user_model
from profiles.validators import validate_birthday, validate_phone

User = get_user_model()


class Profile(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birthday = models.DateField(
        null=True, blank=True, validators=[validate_birthday]
    )
    phone = models.CharField(
        max_length=15, null=True, blank=True, validators=[validate_phone]
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
