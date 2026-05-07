from django.db import models
from django.utils.text import slugify
from addons.mixins import TimeStampMixin

class Category(TimeStampMixin):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.name:
           self.name = self.name.strip()

        if not self.slug:
           base_slug = slugify(self.name)
           slug = base_slug
           counter = 1

           while Category.objects.filter(slug=slug).exists():
               slug = f"{base_slug}-{counter}"
               counter += 1

           self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
         verbose_name = "Category"
         verbose_name_plural = "Categories"
         ordering = ["-created_at"]