import os

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def generate_activation_link(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_path = reverse(
        "activate-user", kwargs={"uidb64": uid, "token": token}
    )
    return request.build_absolute_uri(activation_path)


def generate_password_reset_link(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_path = reverse(
        "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
    )
    return request.build_absolute_uri(reset_path)


def send_activation_email(user, request):
    frontend_url = os.getenv("ACTIVATION_LINK", "http://localhost:3000")

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_link = f"{frontend_url.rstrip('/')}/activate/{uidb64}/{token}/"

    subject = "Activate your account"
    message = (
        f"Hello {user.email},\n\n"
        f"Click here to activate your account: {activation_link}"
    )

    return send_mail(
        subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]
    )


def send_password_reset_email(user, request):
    link = generate_password_reset_link(user, request)
    subject = "Change password request"
    message = f"Hello {user.email}, click here to change your password: {link}"
    return send_mail(
        subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]
    )
