from django.urls import path
from . import views

app_name = 'administracion'

urlpatterns = [
    path('', views.dashboard_admin, name='dashboard'),
    path('usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('grupos/', views.gestionar_grupos, name='gestionar_grupos'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
]
