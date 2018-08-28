from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    path('create', views.create_plugin),
    path('update/<plugin_id>', views.create_version),
    path('edit/<version_id>', views.edit_version),
    path('publish/<version_id>', views.publish_version),
    path('view/<version_id>', views.view_version),
    path('approvals', views.approvals),
    path('approve/<version_id>', views.approve),
    path('reject/<version_id>', views.reject),
]
