from django.urls import path
from . import views

app_name = 'acoes'
urlpatterns = [
    path('', views.index, name='index'),
    path('toggle_favorite/<str:papel>/', views.toggle_favorite, name='toggle_favorite'),
]