import json

from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from plugins.models import Plugin, PluginVersion

from .models import ConfiguredPlugin


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
    updates = get_updates(plugin_versions)
    return render(request, 'feed/home.html', {
        'subscriptions': subscriptions,
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
    return list(newest_versions.values())


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

    top_plugins = ConfiguredPlugin.objects.values(
        'plugin_version__plugin').annotate(
            plugin_count=Count('plugin_version__plugin')).order_by(
                '-plugin_count')[:10]

    print(top_plugins)

    top_versions = []
    for plugin_info in top_plugins:
        plugin_pk = plugin_info['plugin_version__plugin']
        plugin = Plugin.objects.get(pk=plugin_pk)
        top_versions.append(newest_versions(plugin.pluginversion_set.all())[0])

    print(top_versions)

    return render(
        request, 'feed/search.html', {
            'user': request.user,
            'results': results,
            'subscribed': [s.plugin_version.plugin for s in subscriptions],
            'top_versions': top_versions,
            'form': form,
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


@login_required
@require_http_methods(["POST"])
def configure(request, configuration_id):
    if not ConfiguredPlugin.objects.filter(pk=configuration_id).exists():
        return render(request, 'feeds/configuration_not_found.html', {
            'configuration_id': configuration_id,
        })

    configuration = ConfiguredPlugin.objects.get(pk=configuration_id)
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
