from django.urls import path
from users.views import (
    ActivateUserView,
    CurrentUserView,
    GoogleAuthView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegistrationView,
    ResendActivationCodeView
)

urlpatterns = [
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'),
    path("register/", RegistrationView.as_view(), name="register"),
    path(
        "activate/",
        ActivateUserView.as_view(),
        name="activate-user",
    ),
    path(
        "resend_activation_code/",
        ResendActivationCodeView.as_view(),
        name="resend-activation-code",
    ),
    path("current-user/", CurrentUserView.as_view(), name="current-user"),
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-change/",
        PasswordChangeView.as_view(),
        name="password_change",
    ),
]
