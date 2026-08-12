from django.urls import resolve, reverse

from users.views import (
    ActivateUserView,
    CurrentUserView,
    GoogleAuthView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegistrationView,
    ResendActivationCodeView,
)


def test_google_auth_url():
    url = reverse("google-auth")
    assert resolve(url).func.view_class is GoogleAuthView


def test_register_url():
    url = reverse("register")
    assert resolve(url).func.view_class is RegistrationView


def test_activate_user_url():
    url = reverse("activate-user")
    assert resolve(url).func.view_class is ActivateUserView


def test_resend_activation_code_url():
    url = reverse("resend-activation-code")
    assert resolve(url).func.view_class is ResendActivationCodeView


def test_current_user_url():
    url = reverse("current-user")
    assert resolve(url).func.view_class is CurrentUserView


def test_password_reset_url():
    url = reverse("password_reset")
    assert resolve(url).func.view_class is PasswordResetRequestView


def test_password_reset_confirm_url():
    url = reverse("password_reset_confirm")
    assert resolve(url).func.view_class is PasswordResetConfirmView


def test_password_change_url():
    url = reverse("password_change")
    assert resolve(url).func.view_class is PasswordChangeView