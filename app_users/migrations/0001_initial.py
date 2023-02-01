# Generated by Django 4.0.6 on 2023-02-01 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=10, unique=True, verbose_name='Название параметра')),
                ('value', models.CharField(max_length=100, verbose_name='Значение параметра')),
            ],
        ),
    ]
