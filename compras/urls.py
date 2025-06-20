from django.urls import path
from . import views

app_name = 'compras'
urlpatterns = [
    path('dashboard/', views.dashboardc , name='dashboard'),
    path('mis_proveedores/', views.Misproveedores, name='misproveedores'),
    path('mis_proveedores/proveedor/<str:id_registro>/', views.Proveedor, name='proveedor'),
    path('mis_proveedores/proveedor/<str:id_registro>/familia/',views.asigancion_familia , name='familia'), 
    path('mis_proveedores/proveedor/<str:id_registro>/aprobacion/',views.aprobar_documento , name='aprobacion'),
    path('mis_proveedores/proveedor/<str:id_registro>/homologa/',views.homologacion_proveedor , name='homologa'), 
  #  path('mis_proveedores/proveedor/<str:id_registro>/reporte/',views.generar_pdf , name='reporte'), 
    path('mis_proveedores/proveedor/<str:id_registro>/tareas/',views.asignar_tarea_doc , name='tareas_proveedor'),
    path('mis_solicitudes/', views.MisSolicitudes, name='missolicitudes'),
    path('mis_solicitudes/crear/', views.crear_solicitudes, name='crear_solicitudes'),
    path('mis_solicitudes/<str:id>/eliminar/', views.eliminar_solicitud, name='eliminar_sol'),
    path('mis_solicitudes/<str:id>/', views.solicitud_id, name='solicitud_id'),
    path('mis_solicitudes/<str:id>/comentario/', views.agregar_comentario, name='agregar_comentario'),
    path('mis_solicitudes/<str:id>/comentario/<int:parent_id>/', views.agregar_comentario, name='agregar_comentario'),
    path('mis_solicitudes/<str:id>/chart/', views.get_propuestas_chart, name='get_propuestas_chart'),
    path('mis_solicitudes/<str:id>/editar/', views.editar_solicitud, name='editar_solicitud'),
    path('tablas/', views.t_basicas, name='t_basicas'),
    path('tablas/matriz/', views.matriz, name='matriz'),
    path('tablas/<str:t>/', views.tablas, name='tablas'),
    path('tablas/<str:tablas>/eliminar/<str:id>/', views.eliminar, name='eliminar'),
    path('tablas/<str:tablas>/crear_editar/', views.Crear_editar, name='crear_editar'),
    path('tablas/matriz/<str:familia>/', views.matriz_info, name='info_matriz'),
    path('tareas/', views.tareas, name='tareas'),
    path('perfil/', views.perfil_comprador, name='perfil'),
    
    
]
