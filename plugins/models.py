from django.db import models
from django.contrib.auth.models import User


class Plugin(models.Model):
    approved = models.BooleanField(default=False)
    owners = models.ManyToManyField(User)
    code = models.CharField(max_length=5000)
    major_version = models.IntegerField()
    minor_version = models.IntegerField()
