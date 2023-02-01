from django.db import models


class SiteSettings(models.Model):
    key = models.CharField(max_length=10, verbose_name="Название параметра", unique=True)
    value = models.CharField(max_length=100, verbose_name="Значение параметра")
