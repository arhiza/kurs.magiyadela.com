# Generated by Django 4.0.6 on 2022-08-29 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_lessons', '0015_alter_lesson_is_intro'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='is_child',
            field=models.BooleanField(default=False, verbose_name='Дочерний урок'),
        ),
    ]