# Generated by Django 4.0.6 on 2022-08-07 18:36
# added manually - add_first_category

from django.db import migrations, models


def add_first_category(apps, schema_editor):
    Category = apps.get_model('app_lessons', 'Category')
    Category.objects.create(name='default')


class Migration(migrations.Migration):

    dependencies = [
        ('app_lessons', '0005_course_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ['ordering']},
        ),
        migrations.RunPython(add_first_category),
    ]