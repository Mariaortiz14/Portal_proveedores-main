from django.urls import path
from . import views

app_name = 'administracion'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
]
