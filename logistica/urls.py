from django.urls import path
from . import views

app_name = 'logistica'

urlpatterns = [
    path('crear/', views.crear_solicitud_ingreso, name='crear_solicitud'),
    path('panel/', views.panel_logistica, name='panel'),
    path('gestionar/<int:solicitud_id>/', views.gestionar_solicitud, name='gestionar'),
    path('dashboard/', views.dashboard_logistica, name='dashboard'),
    path('mis-solicitudes/', views.mis_solicitudes_ingreso, name='mis_solicitudes'),

]
