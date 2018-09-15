import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    temporary = models.BooleanField(default=False)


class DefaultPlugin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plugin_version = models.ForeignKey(
        'plugins.PluginVersion', on_delete=models.CASCADE)
