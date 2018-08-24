from django.contrib import admin

from .models import Plugin, PluginVersion

admin.site.register(Plugin)
admin.site.register(PluginVersion)
