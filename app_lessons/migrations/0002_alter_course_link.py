# Generated by Django 4.0.6 on 2022-07-28 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_lessons', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='link',
            field=models.URLField(blank=True, null=True, verbose_name='Ссылка на магазин, где купить'),
        ),
    ]
