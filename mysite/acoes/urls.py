from django.urls import path
from . import views

app_name = 'acoes'
urlpatterns = [
    path('', views.index, name='index'),
    path('test-api/', views.test_api_view, name='test_api'),
    #path('toggle_favorite/<str:papel>/', views.toggle_favorite, name='toggle_favorite'),
    #path('acao/<str:papel>/', views.acao, name='acao'),
]