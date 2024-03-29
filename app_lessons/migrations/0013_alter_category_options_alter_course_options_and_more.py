# Generated by Django 4.0.6 on 2022-08-25 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_lessons', '0012_alter_course_picture_alter_lesson_picture'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'verbose_name': 'Курс', 'verbose_name_plural': 'Курсы'},
        ),
        migrations.AlterModelOptions(
            name='coursesforusers',
            options={'verbose_name': 'Подключенный курс', 'verbose_name_plural': 'Подключенные курсы'},
        ),
        migrations.AlterModelOptions(
            name='filepicture',
            options={'verbose_name': 'Картинка', 'verbose_name_plural': 'Картинки'},
        ),
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ['ordering'], 'verbose_name': 'Урок', 'verbose_name_plural': 'Уроки'},
        ),
    ]
