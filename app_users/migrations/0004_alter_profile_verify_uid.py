# Generated by Django 4.0.6 on 2023-02-12 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_users', '0003_alter_profile_name_hint_alter_profile_name_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='verify_uid',
            field=models.CharField(max_length=70, verbose_name='код для ссылки подтверждения мыла'),
        ),
    ]
