# Generated by Django 3.2.6 on 2021-09-23 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_app', '0007_auto_20210914_2224'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('task', models.ManyToManyField(blank=True, related_name='tag_task', to='task_app.Task')),
            ],
        ),
    ]
