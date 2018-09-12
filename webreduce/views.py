from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def handler404(request):
    return render(request, 'webreduce/404.html')


@require_http_methods(["GET"])
def handler500(request):
    return render(request, 'webreduce/500.html')
