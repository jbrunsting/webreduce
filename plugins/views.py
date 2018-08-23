from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import Plugin


@login_required
@require_http_methods(["GET"])
def home(request):
    return render(
        request,
        'plugins/home.html', {
            'username': request.user.username,
            'plugins': Plugin.objects.filter(owners=request.user.id),
        })


class EditPluginForm(forms.ModelForm):
    class Meta:
        model = Plugin
        fields = [
            'name',
            'code',
            'major_version',
            'minor_version',
        ]


def get_edit_plugin(request, plugin, error=None):
    form = EditPluginForm({
        'name': plugin.name,
        'owners': plugin.owners.all(),
        'code': plugin.code,
        'major_version': plugin.major_version,
        'minor_version': plugin.minor_version,
    })

    return render(request, 'plugins/edit.html', {
        'plugin': plugin,
        'form': form,
        'error': error,
    })


def post_edit_plugin(request, plugin_id):
    form = EditPluginForm(request.POST)
    plugin = Plugin.objects.get(pk=plugin_id)
    # TODO: Use django permissions to guard against this
    if not plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': plugin.id,
            'plugin_owners': plugin.owners.all(),
        })

    error = None
    if form.is_valid():
        form_data = form.cleaned_data
        if (plugin.major_version == form_data['major_version']
                and plugin.minor_version == form_data['minor_version']):
            if plugin.published:
                error = "Version already published, incriment major or minor version"
            else:
                plugin.name = form_data['name']
                plugin.code = form_data['code']
                plugin.major_version = form_data['major_version']
                plugin.minor_version = form_data['minor_version']
                plugin.save()
        else:
            new_plugin = Plugin()
            new_plugin.name = form_data['name']
            new_plugin.code = form_data['code']
            new_plugin.major_version = form_data['major_version']
            new_plugin.minor_version = form_data['minor_version']
            new_plugin.save()
            new_plugin.owners.add(request.user)
            new_plugin.save()
    else:
        error = "Invalid form"

    return render(request, 'plugins/edit.html', {
        'plugin': plugin,
        'form': form,
        'error': error,
    })


@login_required
@require_http_methods(["GET", "POST"])
def edit_plugin(request, plugin_id):
    if not Plugin.objects.filter(pk=plugin_id).exists():
        return render(request, 'plugins/not_found.html', {
            'plugin_id': plugin_id,
        })

    plugin = Plugin.objects.get(pk=plugin_id)
    # TODO: Use django permissions to guard against this
    if not plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': plugin.id,
            'plugin_owners': plugin.owners.all(),
        })

    if request.method == "GET":
        return get_edit_plugin(request, plugin)

    return post_edit_plugin(request, plugin_id)


@login_required
@require_http_methods(["POST"])
def publish_plugin(request, plugin_id):
    plugin = Plugin.objects.get(pk=plugin_id)
    # TODO: Use django permissions to guard against this
    if not plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': plugin.id,
            'plugin_owners': plugin.owners.all(),
        })

    plugin.published = True
    plugin.save()

    return redirect('/plugins')
