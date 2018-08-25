from django.contrib.auth.models import User
from django.db import models
from plugins.models import Plugin


class ConfiguredPlugin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'plugin')
