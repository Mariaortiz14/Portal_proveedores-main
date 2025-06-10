from django.urls import path
from . import views

app_name = 'proveedor'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('doc/', views.doc, name='doc'),
    path('p/', views.doc, name='p'),
    path('descargar_archivo/<str:path>/', views.descargar_archivo, name='descargar_archivo'),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('solicitudes/<str:id>/', views.solicitud_id, name='solicitud_id'),
    path('solicitud/<str:id>/comentario/', views.agregar_comentario, name='agregar_comentario'),
    path('solicitud/<str:id>/comentario/<int:parent_id>/', views.agregar_comentario, name='agregar_comentario'),
    path('tareas/', views.tareas, name='tareas'),
    path('propuestas/', views.propuestas, name='propuestas'),
]
