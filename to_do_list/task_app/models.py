from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

# Create your models here.

class Tag(models.Model):

    name = models.CharField(max_length=300, unique=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        # sets unique values to pair of fields
        unique_together = ('author', 'name',)

    def __str__(self):
        return self.name

class Task(models.Model):
    PRIORITIES = (
        ('1', 'High'),
        ('2', 'Medium'),
        ('3', 'Low'),
    )

    STATUSES = (
        ('b', 'BACKLOG'),
        ('bb', 'BOTTOM BACKLOG'),
        ('wip', 'WIP'),
        ('d', 'DONE'),
        ('a', 'ARCHIVED'),
    )

    description = models.CharField(max_length=300)
    priority = models.CharField(max_length=1, choices=PRIORITIES)
    status = models.CharField(max_length=3, choices=STATUSES, default='b')
    is_blocked = models.BooleanField(default=False)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    last_working_time = models.DateTimeField(auto_now_add=True)
    spent_time = models.DurationField(
        default = timedelta(days=0)
    )

    tag = models.ManyToManyField(
        Tag,
        related_name='task_tag',
        blank=False
    )

    """
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('images:detail', args=[self.id, self.slug])
    """
    def __str__(self):
        return self.description
