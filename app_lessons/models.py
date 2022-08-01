from django.db import models
from django.db.models import Max
from django.urls import reverse


class Course(models.Model):
    OK = 'OK'
    NEW = 'NEW'
    STATUS_CHOICES = [
        (OK, 'Готово'),
        (NEW, 'Редактируется'),
    ]
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default=NEW,
    )
    name = models.CharField(max_length=100, verbose_name="Название курса")
    about = models.TextField(verbose_name="Описание")
    price = models.CharField(blank=True, null=True, max_length=20, verbose_name="Цена, с пометкой, в какой валюте")
    link = models.URLField(blank=True, null=True, max_length=200, verbose_name="Ссылка на магазин, где купить")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('course', args=[str(self.id)])


class Lesson(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="lessons", verbose_name="Часть какого курса")
    name = models.CharField(max_length=100, verbose_name="Название урока")
    info = models.TextField(verbose_name="Основная часть урока")
    video = models.URLField(blank=True, null=True, verbose_name="Видео на ютубе, если есть")
    questions = models.TextField(blank=True, null=True, verbose_name="Вопросы для домашней работы")
    ordering = models.PositiveIntegerField(default=0, verbose_name="Порядок уроков в курсе")

    def _code_video(self):
        # из ссылки типа такой https://www.youtube.com/watch?v=8HDXSmDJ6Kw&list=LL
        # надо достать параметр 8HDXSmDJ6Kw, чтобы встроить в проигрыватель на странице
        if self.video:
            tmp = self.video.split("?")[1]
            tmp = tmp.split("v=")[1]
            tmp = tmp.split("&")[0]
            return tmp
        return None
    code_video = property(_code_video)

    def _prev_lesson(self):
        # ближайший урок этого же курса, в сторону начала
        tmp = Lesson.objects.filter(ordering__lt=self.ordering, course=self.course).order_by("-ordering").first()
        return tmp
    prev_lesson = property(_prev_lesson)

    def _next_lesson(self):
        # ближайший урок этого же курса, в сторону конца
        tmp = Lesson.objects.filter(ordering__gt=self.ordering, course=self.course).order_by("ordering").first()
        return tmp
    next_lesson = property(_next_lesson)

    def get_absolute_url(self):
        return reverse('lesson', args=[str(self.id)])

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

    class Meta:
        ordering = ['ordering']
