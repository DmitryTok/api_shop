from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from users.utils import gen_code


def generate_uid_token(user):

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def send_email_code(user, task_type: str, request=None):
    try:
        code = gen_code(user.id, task_type)

        if code is None:
            return

        match task_type:
            case "activation":
                subject = "Activate your account"
                message = f"Hello {user.email},\n\nHere your activation code: {code}"
            case "password_reset":
                subject = "Reset your password"
                message = f"Hello {user.email},\n\nYour password reset code is: {code}"
            case _:
                return

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

    except Exception:
        cache.delete(f"lock:{task_type}:{user.id}")
