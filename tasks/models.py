from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser


class Task(models.Model):
    title = models.CharField(_('task name'), max_length=90, unique=True)
    description = models.TextField(_('task description'), max_length=255)
    created_by = models.ForeignKey(
        CustomUser, related_name='user_created', on_delete=models.DO_NOTHING
    )
    assigned_to = models.ForeignKey(
        CustomUser, related_name='user_assigned', on_delete=models.DO_NOTHING
    )

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.title
