import json

from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from plugins.models import Plugin, PluginVersion

from .models import ConfiguredPlugin


def newest_version(plugin_version):
    max_version = plugin_version
    for version in max_version.plugin.pluginversion_set.filter(
            approved=True).all():
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
    plugin_versions = [s.plugin_version for s in subscriptions]
    updates = get_updates(plugin_versions)
    return render(
        request, 'feed/home.html', {
            'subscriptions': subscriptions,
            'updates': updates,
            'divide_into_pages': False,
        })


class SearchForm(forms.Form):
    search_term = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Search',
        }), label='')


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
    return list(newest_versions.values())


def get_search_results(search_term, user_id):
    # TODO: Use a better search algorithm - when using postgres there are
    # better fuzzy search options
    approved_versions = PluginVersion.objects.filter(approved=True)
    search_results = approved_versions.filter(
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

    top_plugins = ConfiguredPlugin.objects.values(
        'plugin_version__plugin').annotate(
            plugin_count=Count('plugin_version__plugin')).order_by(
                '-plugin_count')[:10]

    top_versions = []
    for plugin_info in top_plugins:
        plugin_pk = plugin_info['plugin_version__plugin']
        plugin = Plugin.objects.get(pk=plugin_pk)
        approved = plugin.pluginversion_set.filter(approved=True)
        if approved.exists():
            top_versions.append(newest_versions(approved.all())[0])

    return render(
        request, 'feed/search.html', {
            'searching': search_term != "",
            'user': request.user,
            'results': results,
            'subscribed': [s.plugin_version.plugin for s in subscriptions],
            'top_versions': top_versions,
            'form': form,
        })


@login_required
@require_http_methods(["POST"])
def subscribe(request, plugin_version_id):
    plugin_version = get_object_or_404(PluginVersion, pk=plugin_version_id)

    if not plugin_version.approved and not request.user in plugin_version.plugin.owners.all(
    ):
        return redirect('/feed')

    if ConfiguredPlugin.objects.filter(
            user=request.user, plugin_version=plugin_version).exists():
        return redirect('/feed')

    if ConfiguredPlugin.objects.filter(
            user=request.user,
            plugin_version__plugin=plugin_version.plugin).exists():
        configuration = get_object_or_404(
            ConfiguredPlugin,
            user=request.user,
            plugin_version__plugin=plugin_version.plugin)
        configuration.plugin_version = plugin_version
        configuration.save()
        return redirect('/feed')

    configured_plugin = ConfiguredPlugin(
        user=request.user, plugin_version=plugin_version)
    configured_plugin.save()

    return redirect('/feed?configure=' + str(configured_plugin.id))


@login_required
@require_http_methods(["POST"])
def unsubscribe(request, plugin_version_id):
    plugin_version = get_object_or_404(PluginVersion, pk=plugin_version_id)

    candidates = ConfiguredPlugin.objects.filter(
        user=request.user, plugin_version=plugin_version)
    if candidates.exists():
        candidates.first().delete()

    return redirect('/feed')


@login_required
@require_http_methods(["POST"])
def configure(request, configuration_id):
    configuration = get_object_or_404(ConfiguredPlugin, pk=configuration_id)
    configuration.config = request.body.decode('utf-8')
    configuration.save()

    return redirect('/feed')


@csrf_exempt
@require_http_methods(["GET", "POST"])
def external(request, plugin_name):
    if request.method == "POST":
        if not Plugin.objects.filter(name=plugin_name).exists():
            return HttpResponse(status=404)

        external_request = ExternalRequest(
            plugin=Plugin.objects.get(name=plugin_name),
            url=request.build_absolute_uri(),
            body=request.body.decode('utf-8'))

        return HttpResponse(status=200)

    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    if not Plugin.objects.filter(name=plugin_name).exists():
        return HttpResponse(status=404)

    plugin = Plugin.objects.get(name=plugin_name)

    if not ExternalRequest.objects.filter(plugin=plugin).exists():
        return HttpResponse(status=404)

    external_request = ExternalRequest.objects.get(plugin=plugin)

    return JsonResponse({
        'timestamp': external_request.timestamp,
        'url': external_request.url,
        'body': external_request.body,
    })
