from django.contrib.auth.models import User
from django.db import models
from plugins.models import PluginVersion


class ConfiguredPlugin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plugin_version = models.ForeignKey(PluginVersion, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'plugin_version')
