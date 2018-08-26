from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    path('search', views.search),
    path('subscribe/<plugin_version_id>', views.subscribe),
    path('unsubscribe/<plugin_version_id>', views.unsubscribe),
]
