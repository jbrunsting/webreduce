from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    path('create', views.create_plugin),
    path('edit/<plugin_id>', views.edit_plugin),
    path('publish/<plugin_id>', views.publish_plugin),
]
