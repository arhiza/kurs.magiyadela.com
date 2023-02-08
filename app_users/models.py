from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name_hint = models.CharField(max_length=50, verbose_name="Кто же это", blank=True)
    name_note = models.CharField(max_length=200, verbose_name="Примечание", blank=True)
    
    is_verified = models.BooleanField(default=False, verbose_name="Емейл подтвержден")
    verify_uid = models.CharField(max_length=200, verbose_name="код для ссылки подтверждения мыла")
    
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Профили пользователей'
        verbose_name = 'Профиль пользователя'
    

class SiteSettings(models.Model):
    key = models.CharField(max_length=10, verbose_name="Название параметра", unique=True)
    value = models.CharField(max_length=100, verbose_name="Значение параметра")

    class Meta:
        verbose_name_plural = 'Настройки сайта'
        verbose_name = 'Настройка сайта'

