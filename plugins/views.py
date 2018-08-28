from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
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

    return render(request, 'plugins/home.html', {
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
            return redirect('/plugins/update/' + str(plugin.id))
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


class CreateVersionForm(forms.ModelForm):
    class Meta:
        model = PluginVersion
        fields = [
            'code',
            'major_version',
            'minor_version',
        ]


def get_create_version(request, plugin):
    code = ""
    major_version = 1
    minor_version = 0
    for version in plugin.pluginversion_set.all():
        if (version.major_version > major_version
                or version.major_version == major_version
                and version.minor_version >= minor_version):
            code = version.code
            major_version = version.major_version
            minor_version = version.minor_version + 1

    form = CreateVersionForm({
        'code': code,
        'major_version': major_version,
        'minor_version': minor_version,
    })

    return render(request, 'plugins/update.html', {
        'form': form,
    })


def post_create_version(request, plugin):
    form = CreateVersionForm(request.POST)
    error = None
    form.is_valid()
    if form.is_valid():
        # TODO: Gross, clean up
        version = form.save(commit=False)
        version_set = plugin.pluginversion_set.all()
        if version_set.filter(major_version__gt=version.major_version).exists():
            error = "A larger major version already exists, incriment major version number"
        elif version_set.filter(
                major_version=version.major_version,
                minor_version=version.minor_version):
            error = "Version already exists, incriment major or minor version number"
        elif (not version.major_version == 1 and not version_set.filter(
                major_version=version.major_version).exists()
              and not version_set.filter(major_version=version.major_version -
                                         1).exists()):
            error = "Major version number skipped, decriment major version number"
        elif (version_set.filter(major_version=version.major_version).exists()
              and not version_set.filter(
                  major_version=version.major_version,
                  minor_version=version.minor_version - 1).exists()):
            error = "Minor version number skipped, decriment minor version number"
        elif (not version_set.filter(
                major_version=version.major_version).exists()
              and version.minor_version != 0):
            error = "The first minor version for a new major version must be 0"
        else:
            version.plugin = plugin
            version.save()
            return redirect('/plugins')
    else:
        error = "Form invalid"

    return render(request, 'plugins/create.html', {
        'form': form,
        'error': error,
    })


@login_required
@require_http_methods(["GET", "POST"])
def create_version(request, plugin_id):
    if not Plugin.objects.filter(pk=plugin_id).exists():
        return render(request, 'plugins/plugin_not_found.html', {
            'plugin_id': plugin_id,
        })

    plugin = Plugin.objects.get(pk=plugin_id)
    # TODO: Use django permissions to guard against this
    if not plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': plugin.name,
            'plugin_owners': plugin.owners.all(),
        })

    if request.method == "GET":
        return get_create_version(request, plugin)

    return post_create_version(request, plugin)


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
        return render(
            request, 'plugins/not_owner.html', {
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
        return render(request, 'plugins/version_not_found.html', {
            'version_id': version_id,
        })

    version = PluginVersion.objects.get(pk=version_id)
    # TODO: Use django permissions to guard against this
    if not version.plugin.owners.filter(pk=request.user.pk).exists():
        return render(
            request, 'plugins/not_owner.html', {
                'plugin_name': version.plugin.name,
                'plugin_owners': version.plugin.owners.all(),
            })

    if request.method == "GET":
        return get_edit_version(request, version)

    return post_edit_version(request, version_id)


@login_required
@require_http_methods(["POST"])
def publish_version(request, version_id):
    if not PluginVersion.objects.filter(pk=version_id).exists():
        return render(request, 'plugins/version_not_found.html', {
            'version_id': version_id,
        })

    version = PluginVersion.objects.get(pk=version_id)
    # TODO: Use django permissions to guard against this
    if not version.plugin.owners.filter(pk=request.user.pk).exists():
        return render(
            request, 'plugins/not_owner.html', {
                'plugin_name': version.plugin.name,
                'plugin_owners': version.plugin.owners.all(),
            })

    version.published = True
    version.save()

    return redirect('/plugins')


@login_required
@require_http_methods(["GET"])
def view_version(request, version_id):
    if not PluginVersion.objects.filter(pk=version_id).exists():
        return render(request, 'plugins/version_not_found.html', {
            'version_id': version_id,
        })

    version = PluginVersion.objects.get(pk=version_id)
    if not version.plugin.owners.filter(
            pk=request.user.pk).exists() and not version.plugin.approved:
        return render(
            request, 'plugins/not_owner.html', {
                'plugin_name': version.plugin.name,
                'plugin_owners': version.plugin.owners.all(),
            })

    return render(request, 'plugins/view_version.html', {
        'plugin_version': version,
    })


class RejectionForm(forms.Form):
    rejection_reason = forms.CharField(max_length=2048)


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["GET"])
def approvals(request):
    versions = PluginVersion.objects.filter(
        published=True, approved=False, rejected=False)
    return render(request, 'plugins/approvals.html', {
        'versions': versions,
        'rejection_form': RejectionForm(),
    })


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def approve(request, version_id):
    if not PluginVersion.objects.filter(pk=version_id).exists():
        return render(request, 'plugins/version_not_found.html', {
            'version_id': version_id,
        })

    version = PluginVersion.objects.get(pk=version_id)
    version.approved = True
    version.save()

    return redirect('/plugins/approvals')


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def reject(request, version_id):
    if not PluginVersion.objects.filter(pk=version_id).exists():
        return render(request, 'plugins/version_not_found.html', {
            'version_id': version_id,
        })

    rejection_form = RejectionForm(request.POST)

    if not rejection_form.is_valid():
        return redirect('/plugins/approvals')

    version = PluginVersion.objects.get(pk=version_id)
    version.rejected = True
    version.rejection_reason = rejection_form.cleaned_data['rejection_reason']
    version.save()

    return redirect('/plugins/approvals')
