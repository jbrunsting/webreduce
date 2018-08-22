from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Plugin


@login_required
def home(request):
    return render(
        request,
        'plugins/home.html', {
            'username': request.user.username,
            'plugins': Plugin.objects.filter(owners=request.user.id),
        })


@login_required
def edit_plugin(request, plugin_id):
    if not Plugin.objects.filter(pk=plugin_id).exists():
        return render(request, 'plugins/not_found.html', {
            'plugin_id': plugin_id,
        })

    plugin = Plugin.objects.get(pk=plugin_id)
    if plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/edit.html', {
            'plugin': plugin,
        })
    else:
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': plugin.id,
            'plugin_owners': plugin.owners.all(),
        })
