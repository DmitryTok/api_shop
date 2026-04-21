from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import validate_email
from django.db import models


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', False)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Term(models.Model):
    version = models.CharField(max_length=20, unique=True)
    text = models.TextField(max_length=2000)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Terms {self.version}"


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, validators=[validate_email])
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'


class UserTermsAcceptance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    terms = models.ForeignKey(Term, on_delete=models.CASCADE)
    accepted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Acceptance by {self.user.email} ({self.accepted_at.strftime('%d/%m/%Y')})"

    class Meta:
        unique_together = ('user', 'terms')
