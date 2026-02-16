from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, validators=[validate_email])
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
