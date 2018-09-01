from django.contrib.auth.models import User
from django.db import models


class Plugin(models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.CharField(max_length=2048)
    owners = models.ManyToManyField(User)


class PluginVersion(models.Model):
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE)
    code = models.CharField(max_length=4096)
    major_version = models.IntegerField()
    minor_version = models.IntegerField()
    published = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    rejection_reason = models.CharField(max_length=2048)

    class Meta:
        unique_together = ('plugin', 'major_version', 'minor_version')
