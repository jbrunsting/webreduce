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
