from django.contrib.auth.models import User
from django.db import models

from plugins.models import Plugin, PluginVersion


class ConfiguredPlugin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plugin_version = models.ForeignKey(PluginVersion, on_delete=models.CASCADE)
    config = models.TextField()

    class Meta:
        unique_together = ('user', 'plugin_version')


class ExternalRequest(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE)
    url = models.TextField()
    body = models.TextField()
