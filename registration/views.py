from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from .models import User


@require_http_methods(["GET"])
def home(request):
    return render(request, 'registration/home.html')


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", )


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/feed')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


def logoutUser(request):
    logout(request)
    return redirect('/login')
