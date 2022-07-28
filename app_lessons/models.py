from django.db import models
from django.db.models import Max


class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название курса")
    about = models.TextField(verbose_name="Описание")
    price = models.CharField(blank=True, null=True, max_length=20, verbose_name="Цена, с пометкой, в какой валюте")
    link = models.URLField(blank=True, null=True, max_length=200, verbose_name="Ссылка на магазин, где купить")

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="lessons", verbose_name="Часть какого курса")
    name = models.CharField(max_length=100, verbose_name="Название урока")
    info = models.TextField(verbose_name="Основная часть урока")
    video = models.URLField(blank=True, null=True, verbose_name="Видео на ютубе, если есть")
    questions = models.TextField(blank=True, null=True, verbose_name="Вопросы для домашней работы")
    ordering = models.PositiveIntegerField(default=0, verbose_name="Порядок уроков в курсе")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.ordering == 0:
            max_ordering = self.course.lessons.all().aggregate(Max('ordering'))['ordering__max']
            if max_ordering:
                self.ordering = max_ordering + 10
            else:
                self.ordering = 10
        super(Lesson, self).save(*args, **kwargs)
