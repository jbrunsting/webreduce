from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    path('edit/<plugin_id>', views.edit_plugin),
]
