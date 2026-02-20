from django.urls import path
from users.views import ActivateUserView, CurrentUserView, RegistrationView

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path(
        "activate/<uidb64>/<token>/",
        ActivateUserView.as_view(),
        name="activate-user",
    ),
    path("current-user/", CurrentUserView.as_view(), name="current-user"),
]
