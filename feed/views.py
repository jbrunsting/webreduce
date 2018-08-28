from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from plugins.models import Plugin, PluginVersion

from .models import ConfiguredPlugin


# Assumes there is at least one plugin version
def newest_version(plugin_version):
    max_version = plugin_version
    for version in max_version.plugin.pluginversion_set.all():
        if (version.major_version > max_version.major_version
                or version.major_version == max_version.major_version
                and version.minor_version > max_version.minor_version):
            max_version = version

    return max_version


def get_updates(versions):
    updates = []
    for version in versions:
        newest = newest_version(version)
        if newest != version:
            updates.append((version, newest))

    return updates


@login_required
@require_http_methods(["GET"])
def home(request):
    subscriptions = ConfiguredPlugin.objects.filter(user=request.user)
    versions = [s.plugin_version for s in subscriptions]
    updates = get_updates(versions)
    return render(request, 'feed/home.html', {
        'subscriptions': versions,
        'updates': updates
    })


class SearchForm(forms.Form):
    search_term = forms.CharField()


def newest_versions(versions):
    newest_versions = {}
    for version in versions:
        if version.plugin in newest_versions:
            newest = newest_versions[version.plugin]
            if (version.major_version > newest.major_version
                    or version.major_version == newest.major_version
                    and version.minor_version > newest.minor_version):
                newest_versions[version.plugin] = version
        else:
            newest_versions[version.plugin] = version
    return newest_versions.values()


def get_search_results(search_term, user_id):
    # TODO: Use a better search algorithm - when using postgres there are
    # better fuzzy search options
    approved_versions = PluginVersion.objects.filter(approved=True)
    owned_versions = PluginVersion.objects.filter(plugin__owners=user_id)
    valid_versions = approved_versions | owned_versions
    search_results = valid_versions.filter(
        Q(plugin__name__icontains=search_term)
        | Q(plugin__description__icontains=search_term))
    return newest_versions(search_results)


@login_required
@require_http_methods(["POST", "GET"])
def search(request):
    search_term = ""
    form = None
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search_term = form.cleaned_data['search_term']
    else:
        form = SearchForm()

    results = []
    if len(search_term) >= 3:
        results = get_search_results(search_term, request.user.id)

    subscriptions = ConfiguredPlugin.objects.filter(user=request.user).all()

    return render(
        request, 'feed/search.html', {
            'user': request.user,
            'results': results,
            'subscribed': [s.plugin_version.plugin for s in subscriptions],
            'form': form
        })


@login_required
@require_http_methods(["POST"])
def subscribe(request, plugin_version_id):
    if not PluginVersion.objects.filter(pk=plugin_version_id).exists():
        return render(request, 'plugins/version_not_found.html', {
            'plugin_version_id': plugin_version_id,
        })

    plugin_version = PluginVersion.objects.get(pk=plugin_version_id)
    if ConfiguredPlugin.objects.filter(plugin_version=plugin_version).exists():
        return redirect('/feed')

    configured_plugin = ConfiguredPlugin(
        user=request.user, plugin_version=plugin_version)
    configured_plugin.save()
    return redirect('/feed')


@login_required
@require_http_methods(["POST"])
def unsubscribe(request, plugin_version_id):
    if not PluginVersion.objects.filter(pk=plugin_version_id).exists():
        return render(request, 'plugins/version_not_found.html', {
            'plugin_version_id': plugin_version_id,
        })

    plugin_version = PluginVersion.objects.get(pk=plugin_version_id)
    candidates = ConfiguredPlugin.objects.filter(
        user=request.user, plugin_version=plugin_version)
    if candidates.exists():
        candidates.first().delete()
    return redirect('/feed')


@login_required
@require_http_methods(["POST"])
def update(request, plugin_version_id):
    if not PluginVersion.objects.filter(pk=plugin_version_id).exists():
        return render(request, 'plugins/version_not_found.html', {
            'plugin_version_id': plugin_version_id,
        })

    new_version = PluginVersion.objects.get(pk=plugin_version_id)
    configurations = ConfiguredPlugin.objects.filter(
        user=request.user, plugin_version__plugin=new_version.plugin)
    if configurations.exists():
        configuration = configurations.first()
        configuration.plugin_version = new_version
        configuration.save()
    return redirect('/feed')
