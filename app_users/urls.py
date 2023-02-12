from django.urls import path

from .views import restore_password, confirm, login_view, registration_view, LogoutView, UserUpdateView

urlpatterns = [
    path("restore_password", restore_password, name="restore_password"),
    path("confirm/", confirm, name="confirm"),
    path("login/", login_view, name="login"),
    path("registration/", registration_view, name="registration"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("lk/", UserUpdateView.as_view(), name="cabinet"),
]
