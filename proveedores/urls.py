from django.urls import path
from . import views

app_name = 'proveedor'
urlpatterns = [
    path('solicitud/<str:id>/cpmentario/<int:parent_id>/', views.agregar_comentario, name='agregar_comentario'),

    path('solicitud/<str:id>/comentario/', views.agregar_comentario, name='agregar_comentario'),
    path('descargar_archivo/<str:path>/', views.descargar_archivo, name='descargar_archivo'),
    path('solicitudes/<str:identificador>/', views.solicitud_id, name='solicitud_id'),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('propuestas/', views.propuestas, name='propuestas'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tareas/', views.tareas, name='tareas'),
    path('tareas/marcar-hecha/<int:tarea_id>/', views.marcar_tarea_hecha, name='marcar_tarea_hecha'),
    path('tareas/editar/<int:tarea_id>/', views.editar_tarea, name='editar_tarea'),
    path('tareas/eliminar/<int:tarea_id>/', views.eliminar_tarea, name='eliminar_tarea'),
    path('doc/', views.doc, name='doc'),
    path('p/', views.doc, name='p'),
]
