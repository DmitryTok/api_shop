from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def generate_activation_link(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = (
        f"{request.scheme}://{request.get_host()}/activate/{uid}/{token}/"
    )
    return activation_link


def generate_password_reset_link(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = f"{request.scheme}://{request.get_host()}/password-reset-confirm/{uid}/{token}/"
    return reset_link


def send_activation_email(user, request):
    link = generate_activation_link(user, request)
    subject = "Activate your account"
    message = (
        f"Hello {user.email}, click here to activate your account: {link}"
    )
    send_mail(subject, message, 'no-reply@example.com', [user.email])


def send_password_reset_email(user, request):
    link = generate_password_reset_link(user, request)
    subject = "Change password request"
    message = f"Hello {user.email}, click here to change your password: {link}"
    send_mail(subject, message, 'no-reply@example.com', [user.email])
