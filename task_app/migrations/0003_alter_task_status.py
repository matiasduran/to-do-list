# Generated by Django 3.2.6 on 2021-09-12 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_app', '0002_task_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('b', 'BACKLOG'), ('wip', 'WIP'), ('d', 'DONE'), ('a', 'ARCHIVED')], default='b', max_length=3),
        ),
    ]
