import uuid

from django.db import models

from registration.models import User
from plugins.models import Plugin, PluginVersion


class ConfiguredPlugin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plugin_version = models.ForeignKey(PluginVersion, on_delete=models.CASCADE)
    config = models.TextField()

    class Meta:
        unique_together = ('user', 'plugin_version')


class ExternalRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE)
    url = models.TextField()
    body = models.TextField()
