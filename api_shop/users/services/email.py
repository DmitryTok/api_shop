from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from users.utils import gen_activation_user_code


def generate_uid_token(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def send_activation_email(user, request):
    code = gen_activation_user_code(user.id)
    subject = "Activate your account"
    message = f"Hello {user.email},\n\n" f"Here your activation code: {code}"

    return send_mail(
        subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]
    )


def send_password_reset_email(user, request):
    FRONTEND_URL = None
    uid, token = generate_uid_token(user)
    reset_link = (
        f"{FRONTEND_URL.rstrip('/')}/password-reset-confirm/{uid}/{token}/"
    )

    subject = "Change password request"
    message = (
        f"Hello {user.email}, click here to change your password: {reset_link}"
    )

    return send_mail(
        subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]
    )
