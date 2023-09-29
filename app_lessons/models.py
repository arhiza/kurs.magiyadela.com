import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models import Max
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.core.exceptions import ValidationError

from app_emails.services import mail_about_answered_comment


class Category(models.Model):
    name = models.CharField(max_length=50)
    ordering = models.PositiveIntegerField(default=0, verbose_name="Сортировка")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['ordering']
        verbose_name_plural = 'Категории'
        verbose_name = 'Категория'


class Course(models.Model):
    OK = 'OK'
    NEW = 'NEW'
    PROMO = 'FLY'  # butterfly :)
    STATUS_CHOICES = [
        (OK, 'Готово'),
        (NEW, 'Редактируется'),
        (PROMO, 'Новый (Промо)'),
    ]
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default=NEW,
    )
    category = models.ForeignKey('Category', default=1, on_delete=models.SET_DEFAULT,
                                 related_name="courses", verbose_name="Категория")
    name = models.CharField(max_length=100, verbose_name="Название курса")
    url = models.SlugField(null=True, unique=True, verbose_name="Название-урл")
    picture = models.ForeignKey('FilePicture', related_name="course", null=True,
                                blank=True, on_delete=models.SET_NULL, verbose_name="Файл с иллюстрацией")
    about = models.TextField(verbose_name="Описание")
    is_free = models.BooleanField(default=False, verbose_name="Курс бесплатный")
    price = models.CharField(blank=True, null=True, max_length=200, verbose_name="Цена")
    link = models.URLField(blank=True, null=True, max_length=200, verbose_name="Ссылка на магазин, где купить")
    ordering = models.PositiveIntegerField(default=0, verbose_name="Сортировка")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('course', args=[self.url])

    def save(self, *args, **kwargs):
        if self.ordering == 0:
            max_ordering = self.category.courses.all().aggregate(Max('ordering'))['ordering__max']
            if max_ordering:
                self.ordering = max_ordering + 10
            else:
                self.ordering = 10
        super(Course, self).save(*args, **kwargs)

    class Meta:
        ordering = ['ordering']
        verbose_name_plural = 'Курсы'
        verbose_name = 'Курс'


class Lesson(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE,
                               related_name="lessons", verbose_name="Часть какого курса")
    name = models.CharField(max_length=100, verbose_name="Название урока")
    url = models.SlugField(null=True, unique=True, verbose_name="Название-урл")
    is_intro = models.BooleanField(default=False, verbose_name="Вводный урок")
    is_child = models.BooleanField(default=False, verbose_name="Дочерний урок")
    picture = models.ForeignKey('FilePicture', related_name="lesson", null=True,
                                blank=True, on_delete=models.SET_NULL, verbose_name="Файл с иллюстрацией")
    info = models.TextField(verbose_name="Основная часть урока")
    video = models.URLField(blank=True, null=True, verbose_name="Видео на ютубе, если есть")
    questions = models.TextField(blank=True, null=True, verbose_name="Вопросы для домашней работы")
    ordering = models.PositiveIntegerField(default=0, verbose_name="Порядок уроков в курсе")

    def published_comments(self):
        return self.comments.filter(is_published=True)

    def view_comments(self, cur_user):
        if cur_user.has_perm('app_lessons.change_comment'):
            return self.comments
        else:
            return self.comments.filter(Q(is_published=True) | Q(user=cur_user))

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
        return reverse('lesson', args=[self.url])

    def get_add_comment_url(self):
        return reverse('comment', args=[self.url])

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
        verbose_name_plural = 'Уроки'
        verbose_name = 'Урок'


class CoursesForUsers(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, verbose_name="курс", related_name="to_users")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="пользователь", related_name="to_courses")
    is_active = models.BooleanField(default=False, verbose_name="On|Off")
    info = models.CharField(max_length=200, blank=True, null=True, verbose_name="примечание")

    def to_mail(self):
        if self.is_active and hasattr(self.user, "profile"):
            if self.user.profile.is_verified:
                from app_emails.services import mail_about_approved_order
                mail_about_approved_order(self)

    def save(self, *args, **kwargs):
        super(CoursesForUsers, self).save(*args, **kwargs)
        self.to_mail()

    class Meta:
        verbose_name_plural = "Подключенные курсы"
        verbose_name = 'Подключенный курс'
        unique_together = ['course', 'user']


class FilePicture(models.Model):
    file = models.FileField(upload_to="tmp", verbose_name='файл с картинкой')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')

    @receiver(post_save, sender=Course)
    def upd_path_with_course(sender, instance, **kwargs):
        pic = instance.picture
        if pic:
            pic.check_path(instance.id)

    @receiver(post_save, sender=Lesson)
    def upd_path_with_lesson(sender, instance, **kwargs):
        pic = instance.picture
        if pic:
            pic.check_path(instance.course.id)

    def check_path(self, course_id):
        ''' переместить картинку в папку того курса, для которого картинку загрузили '''
        if self.file.name.startswith('tmp'):  # or len(self.file.name.split('/')) < 3:
            initial_path = self.file.path
            filename = self.file.name.split('/')[-1]
            path = 'courses/' + str(course_id)
            new_name = os.path.join(path, filename)
            new_path = os.path.join(settings.MEDIA_ROOT, new_name)
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            os.rename(initial_path, new_path)
            # Update the file field
            self.file.name = new_name
            self.save()

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name_plural = 'Картинки'
        verbose_name = 'Картинка'


class Comment(models.Model):
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE,
                               related_name="comments", verbose_name="урок")
    is_published = models.BooleanField(default=False, verbose_name="опубликовано")
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL,
                             verbose_name="пользователь", related_name="user_comments")
    text_question = models.TextField(verbose_name="вопрос", blank=True, null=True)
    text_answer = models.TextField(verbose_name="ответ", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created at')
    modified_at = models.DateTimeField(auto_now=True, verbose_name='modified_at')
    
    @property
    def adresates(self):
        if self.is_published:
            # всем, кто записан на курс и у кого включены уведомления о новых уроках и подтверждены емейлы
            users = self.lesson.course.to_users.filter(is_active=True)
            res = []
            for cfu in users:
                user = cfu.user
                if hasattr(user, "profile") and user.profile.is_verified and user.profile.say_about_new_comments:
                    res.append(user.email)
            return res
        else:
            # только автору комментария, если подтвержден емейл
            if self.user and hasattr(self.user, "profile") and self.user.profile.is_verified:
                return [self.user.email]
            return None

    def clean(self):
        if not self.text_question and not self.text_answer:
            raise ValidationError('Нужно заполнить вопрос или ответ')

    def save(self, *args, **kwargs):
        super(Comment, self).save(*args, **kwargs)
        if self.is_published or (self.text_answer and self.user and hasattr(self.user, "profile") and self.user.profile.is_verified):
            mail_about_answered_comment(self)
            # при публикации комментария админом отправить уведомления заинтересованным лицам

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
