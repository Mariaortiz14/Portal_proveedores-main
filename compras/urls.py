from django.urls import path
from . import views
from .views import cambiar_estado_propuesta
# pyright: reportCallIssue=false

app_name = 'compras'
urlpatterns = [
      path('mis_solicitudes/<str:id>/comentario/<int:parent_id>/', views.agregar_comentario, name='agregar_comentario'),   
      path('tareas/asignar/', views.asignar_tarea_doc, name='asignar_tarea_doc'), 
      path('mis_proveedores/proveedor/<str:id_registro>/homologa/',views.homologacion_proveedor , name='homologa'), 
      path('mis_proveedores/proveedor/<str:id_registro>/aprobacion/',views.aprobar_documento , name='aprobacion'),
      path('mis_proveedores/proveedor/<str:id_registro>/familia/',views.asigancion_familia , name='familia'),
      path('mis_solicitudes/<str:id>/comentario/', views.agregar_comentario, name='agregar_comentario'),
      path('mis_solicitudes/<str:id>/chart/', views.get_propuestas_chart, name='get_propuestas_chart'),
      path('mis_solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
      path('mis_solicitudes/editar/', views.editar_solicitud_modal, name='editar_solicitud_modal'), # type: ignore
      path('mis_solicitudes/', views.mis_solicitudes, name='missolicitudes'),
      path('mis_solicitudes/<str:id>/eliminar/', views.eliminar_solicitud, name='eliminar_sol'),   
      path('propuestas/<int:id>/cambiar_estado/<str:accion>/', cambiar_estado_propuesta, name='cambiar_estado_propuesta'),
      path('mis_proveedores/proveedor/<str:id_registro>/', views.Proveedor, name='proveedor'),
      path('tablas/<str:tablas>/crear_editar/', views.Crear_editar, name='crear_editar'),
      path('mis_solicitudes/crear/', views.crear_solicitudes, name='crear_solicitudes'),
      path('tablas/<str:tablas>/eliminar/<str:id>/', views.eliminar, name='eliminar'),
      path('tablas/matriz/<str:familia>/', views.matriz_info, name='info_matriz'),
      path('mis_solicitudes/<str:id>/', views.solicitud_id, name='solicitud_id'),
      path('dashboard/data/', views.get_dashboard_data, name='dashboard_data'),
      path('mis_proveedores/', views.Misproveedores, name='misproveedores'),
      path('mis_solicitudes/', views.mis_solicitudes, name='missolicitudes'),
      path('dashboard/', views.dashboard_compras, name='dashboard'),
      path('perfil/', views.perfil_comprador, name='perfil'), 
      path('tablas/matriz/', views.matriz, name='matriz'),       
      path('tablas/<str:t>/', views.tablas, name='tablas'),
      path('tablas/', views.t_basicas, name='t_basicas'),
      path('tareas/', views.tareas, name='tareas'),
  #   path('mis_proveedores/proveedor/<str:id_registro>/reporte/',views.generar_pdf , name='reporte'),     
]
