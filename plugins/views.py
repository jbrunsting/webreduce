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


class CreatePluginForm(forms.ModelForm):
    class Meta:
        model = Plugin
        fields = [
            'name',
            'code',
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
            plugin.major_version = 1
            plugin.minor_version = 0
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


class EditPluginForm(forms.ModelForm):
    class Meta:
        model = Plugin
        fields = [
            'code',
        ]


def get_edit_plugin(request, plugin, error=None):
    form = EditPluginForm(instance=plugin)

    return render(request, 'plugins/edit.html', {
        'plugin': plugin,
        'form': form,
        'error': error,
    })


def post_edit_plugin(request, plugin_id):
    plugin = Plugin.objects.get(pk=plugin_id)
    form = EditPluginForm(request.POST, instance=plugin)
    # TODO: Use django permissions to guard against this
    if not plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': plugin.id,
            'plugin_owners': plugin.owners.all(),
        })

    error = None
    if plugin.published:
        error = "Plugin already published"
    elif form.is_valid():
        form.save()
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
