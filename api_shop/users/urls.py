from django.urls import path
from users.views import RegistrationView, CurrentUserView

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("current-user/", CurrentUserView.as_view(), name="current-user"),
]
