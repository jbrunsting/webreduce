from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('feed/', include('feed.urls')),
    path('admin/', admin.site.urls),
]
