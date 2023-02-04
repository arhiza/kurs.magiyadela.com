from django.urls import path

from .views import restore_password, login_view, LogoutView, UserUpdateView

urlpatterns = [
    path('restore_password', restore_password, name="restore_password"),
    path('login', login_view, name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('lk/', UserUpdateView.as_view(), name="cabinet"),
]
