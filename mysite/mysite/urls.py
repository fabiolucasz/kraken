from django.contrib import admin
from django.urls import path
from . import views
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('fiis/', include('fiis.urls')),
    path('acoes/', include('acoes.urls')),
]
