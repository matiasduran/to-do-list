# Generated by Django 3.2.6 on 2021-09-25 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_app', '0010_auto_20210923_0249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='task',
        ),
        migrations.AddField(
            model_name='task',
            name='tag',
            field=models.ManyToManyField(related_name='task_tag', to='task_app.Tag'),
        ),
    ]
