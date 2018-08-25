from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from plugins.models import Plugin

from .models import ConfiguredPlugin


@login_required
@require_http_methods(["GET"])
def home(request):
    subscriptions = ConfiguredPlugin.objects.filter(user=request.user)
    return render(request, 'feed/home.html',
                  {'subscriptions': [s.plugin for s in subscriptions]})


class SearchForm(forms.Form):
    search_term = forms.CharField()


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
        # TODO: Use a better search algorithm - when using postgres there are
        # better fuzzy search options
        results = Plugin.objects.filter(name__icontains=search_term).all()

    subscriptions = ConfiguredPlugin.objects.filter(user=request.user).all()

    return render(
        request, 'feed/search.html', {
            'user': request.user,
            'results': results,
            'subscribed': [s.plugin for s in subscriptions],
            'form': form
        })


@login_required
@require_http_methods(["POST"])
def subscribe(request, plugin_id):
    if not Plugin.objects.filter(pk=plugin_id).exists():
        return render(request, 'plugins/plugin_not_found.html', {
            'plugin_id': plugin_id,
        })

    plugin = Plugin.objects.get(pk=plugin_id)
    if ConfiguredPlugin.objects.filter(plugin=plugin).exists():
        return redirect('/feed')

    configured_plugin = ConfiguredPlugin(user=request.user, plugin=plugin)
    configured_plugin.save()
    return redirect('/feed')


@login_required
@require_http_methods(["POST"])
def unsubscribe(request, plugin_id):
    if not Plugin.objects.filter(pk=plugin_id).exists():
        return render(request, 'plugins/plugin_not_found.html', {
            'plugin_id': plugin_id,
        })

    plugin = Plugin.objects.get(pk=plugin_id)
    candidates = ConfiguredPlugin.objects.filter(
        user=request.user, plugin=plugin)
    if candidates.exists():
        candidates.first().delete()
    return redirect('/feed')
