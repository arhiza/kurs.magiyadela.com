from django.urls import path

from .views import restore_password

urlpatterns = [
    path('restore_password', restore_password, name="restore_password")
]
