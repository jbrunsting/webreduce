from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    path('temporary', views.temporary),
    path('signup', views.signup),
    path('logout', views.logoutUser),
]
