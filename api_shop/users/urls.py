from django.urls import path
from users.views import (
    ActivateUserView,
    CurrentUserView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegistrationView
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path(
        "activate/<uidb64>/<token>/",
        ActivateUserView.as_view(),
        name="activate-user",
    ),
    path("current-user/", CurrentUserView.as_view(), name="current-user"),
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset-confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-change/",
        PasswordChangeView.as_view(),
        name="password_change",
    ),
]
