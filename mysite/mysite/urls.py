import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('fiis/', include('fiis.urls')),
    path('acoes/', include('acoes.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Add this to serve admin static files in development
    urlpatterns += static(settings.STATIC_URL + 'admin/', document_root=os.path.join(settings.STATIC_ROOT, 'admin'))
