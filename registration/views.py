import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from feed.models import ConfiguredPlugin

from .models import DefaultPlugin, User


@require_http_methods(["GET"])
def home(request):
    if request.user.is_authenticated:
        return redirect('/feed')

    return render(request, 'registration/home.html')


def temporary(request):
    username = str(uuid.uuid4())
    password = str(uuid.uuid4())
    user = User(username=username, temporary=True)
    user.set_password(password)
    user.save()
    authenticated = authenticate(username=username, password=password)
    setup_defaults(user)
    login(request, authenticated)
    return redirect('/feed')


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')


def setup_defaults(user):
    for default in DefaultPlugin.objects.all():
        configured_plugin = ConfiguredPlugin(
            user=user, plugin_version=default.plugin_version)
        configured_plugin.save()


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(
                username=username, email=email, password=raw_password)
            setup_defaults(user)
            login(request, user)
            return redirect('/feed')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


def logoutUser(request):
    logout(request)
    return redirect('/login')
