from celery import shared_task
from django.contrib.auth import get_user_model

from users.services.email import send_email_code

User = get_user_model()


@shared_task
def send_email_code_task(user_id: int, task_type: str):
    user = User.objects.get(pk=user_id)
    send_email_code(user, task_type)
