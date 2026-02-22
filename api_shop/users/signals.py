from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from profiles.models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_on_activation(sender, instance, created, **kwargs):
    if created:
        print(instance.id)
        Profile.objects.get_or_create(id=instance.id, user=instance)
