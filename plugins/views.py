from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import Plugin, PluginVersion


@login_required
@require_http_methods(["GET"])
def home(request):
    plugins = {}
    owned_plugins = Plugin.objects.filter(owners=request.user.id)
    for plugin in owned_plugins:
        plugins[plugin] = plugin.pluginversion_set.all()

    return render(
        request,
        'plugins/home.html', {
            'username': request.user.username,
            'plugins': plugins,
        })


class CreatePluginForm(forms.ModelForm):
    class Meta:
        model = Plugin
        fields = [
            'name',
            'description',
        ]


def get_create_plugin(request):
    return render(request, 'plugins/create.html', {
        'form': CreatePluginForm(),
    })


def post_create_plugin(request):
    form = CreatePluginForm(request.POST)
    error = None
    form.is_valid()
    if form.is_valid():
        if Plugin.objects.filter(name=form.cleaned_data['name']).exists():
            error = "Plugin with that name already exists"
        else:
            plugin = form.save(commit=False)
            plugin.save()
            plugin.owners.add(request.user)
            plugin.save()
            return redirect('/plugins')
    else:
        error = "Form invalid"

    return render(request, 'plugins/create.html', {
        'form': form,
        'error': error,
    })


@login_required
@require_http_methods(["GET", "POST"])
def create_plugin(request):
    if request.method == "GET":
        return get_create_plugin(request)

    return post_create_plugin(request)


class EditVersionForm(forms.ModelForm):
    class Meta:
        model = PluginVersion
        fields = [
            'code',
        ]


def get_edit_version(request, version, error=None):
    form = EditVersionForm(instance=version)

    return render(request, 'plugins/edit.html', {
        'version': version,
        'form': form,
        'error': error,
    })


def post_edit_version(request, version_id):
    version = PluginVersion.objects.get(pk=version_id)
    form = EditVersionForm(request.POST, instance=version)
    # TODO: Use django permissions to guard against this
    if not version.plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': version.plugin.name,
            'plugin_owners': version.plugin.owners.all(),
        })

    error = None
    if version.published:
        error = "Plugin already published"
    elif form.is_valid():
        form.save()
    else:
        error = "Invalid form"

    return render(request, 'plugins/edit.html', {
        'version': version,
        'form': form,
        'error': error,
    })


@login_required
@require_http_methods(["GET", "POST"])
def edit_version(request, version_id):
    if not PluginVersion.objects.filter(pk=version_id).exists():
        return render(request, 'plugins/not_found.html', {
            'version_id': version_id,
        })

    version = PluginVersion.objects.get(pk=version_id)
    # TODO: Use django permissions to guard against this
    if not version.plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': version.plugin.name,
            'plugin_owners': version.plugin.owners.all(),
        })

    if request.method == "GET":
        return get_edit_version(request, version)

    return post_edit_version(request, version_id)


@login_required
@require_http_methods(["POST"])
def publish_version(request, version_id):
    version = PluginVersion.objects.get(pk=version_id)
    # TODO: Use django permissions to guard against this
    if not version.plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': version.plugin.name,
            'plugin_owners': version.plugin.owners.all(),
        })

    version.published = True
    version.save()

    return redirect('/plugins')
