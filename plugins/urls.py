from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    path('create', views.create_plugin),
    path('edit/<version_id>', views.edit_version),
    path('publish/<version_id>', views.publish_version),
]
