from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

handler404 = views.handler404
handler500 = views.handler500

urlpatterns = [
    path('registration/', include('registration.urls')),
    path('feed/', include('feed.urls')),
    path('plugins/', include('plugins.urls')),
    path('registration/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
] + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT)
