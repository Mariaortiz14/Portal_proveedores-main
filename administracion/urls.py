from django.urls import path
from . import views
from .views import estadisticas_dashboard_admin

app_name = 'administracion'
urlpatterns = [
    path('', views.dashboard_admin, name='dashboard'),
    path('usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('grupos/', views.gestionar_grupos, name='gestionar_grupos'),
    path('perfil/', views.perfil_admin, name='perfil'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('administracion/', estadisticas_dashboard_admin, name='estadisticas_dashboard_admin'),
]