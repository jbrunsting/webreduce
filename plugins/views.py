from django import forms
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


class EditPluginForm(forms.ModelForm):
    extra_field = forms.CharField(label='Name of Institution') # TODO: Make this edit the owners

    class Meta:
        model = Plugin
        fields = [
            'name',
            'code',
            'major_version',
            'minor_version',
        ]

    def __init__(self, *args, **kwargs):
        super(EditPluginForm, self).__init__(*args, **kwargs)
        self.fields['extra_field'].initial = 'harvard'


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
    return get_edit_plugin(request, plugin)


@login_required
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
