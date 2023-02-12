from django.db import models
from django.contrib.auth.models import User
import secrets, string


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name_hint = models.CharField(max_length=50, verbose_name="Кто же это", blank=True)
    name_note = models.CharField(max_length=200, verbose_name="Примечание", blank=True)
    
    is_verified = models.BooleanField(default=False, verbose_name="Емейл подтвержден")
    verify_uid = models.CharField(max_length=200, verbose_name="код для ссылки подтверждения мыла")
    
    def _get_new_params_for_confirm(self):
        if self.user.username == self.user.email:
            chars=string.ascii_uppercase + string.ascii_lowercase + string.digits
            self.verify_uid = "".join(secrets.choice(chars) for _ in range(180))
            self.save()
            params = [f"email={self.user.email}", f"confirm={self.verify_uid}"]
            return "?"+"&".join(params)
        else:
            return ""
    get_new_params_for_confirm = property(_get_new_params_for_confirm)
    
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

