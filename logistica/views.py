from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import *

# funcion ´para crear una solicitud de ingreso
@login_required
def crear_solicitud_ingreso(request):
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        documento_seguro = request.FILES.get('documento_seguro')
        identificacion_productos = request.FILES.get('identificacion_productos')

        if not documento_seguro or not identificacion_productos:
            messages.error(request, "Debes adjuntar ambos documentos.")
            return redirect('logistica:crear_solicitud')

        SolicitudIngreso.objects.create(
            proveedor=request.user,
            motivo=motivo,
            documento_seguro=documento_seguro,
            identificacion_productos=identificacion_productos
        )
        messages.success(request, "Solicitud enviada correctamente.")
        return redirect('proveedores:tareas')  

    return render(request, 'logistica/crear_solicitud.html')

# funcion para verificar si el usuario es del grupo de logistica para asi mismo mostrar el panel correspondiente
def es_logistica(user):
    return user.groups.filter(name='Logística').exists()

# vista general del panel de logistica
@user_passes_test(es_logistica)
def panel_logistica(request):
    solicitudes = SolicitudIngreso.objects.all().order_by('-fecha_solicitud')
    return render(request, 'logistica/panel.html', {'solicitudes': solicitudes})

# vista para gestionar una solicitud de ingreso
def gestionar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudIngreso, id=solicitud_id)

    if request.method == 'POST':
        accion = request.POST.get('accion')
        observacion = request.POST.get('observacion', '')

        if accion == 'aprobar':
            solicitud.estado = 'aprobada'
        if not solicitud.codigo_ingreso:
            from logistica.models import generar_codigo_ingreso
            solicitud.codigo_ingreso = generar_codigo_ingreso()


        solicitud.observacion = observacion
        solicitud.save()
        messages.success(request, f"Solicitud {accion} correctamente.")
        return redirect('logistica:panel')

    return redirect('logistica:panel')

#funcion para mostrar el dashboard de logistica
def dashboard_logistica(request):
    pendientes = SolicitudIngreso.objects.filter(estado='pendiente').count()
    aprobadas = SolicitudIngreso.objects.filter(estado='aprobada').count()
    rechazadas = SolicitudIngreso.objects.filter(estado='rechazada').count()
    
    return render(request, 'logistica/dashboard/index.html', {
        'pendientes': pendientes,
        'aprobadas': aprobadas,
        'rechazadas': rechazadas,
    })

# vista para ver las solicitudes de ingreso que he hecho con mi usuario
def mis_solicitudes_ingreso(request):
    solicitudes = SolicitudIngreso.objects.filter(proveedor=request.user).order_by('-fecha_solicitud')
    return render(request, 'logistica/proveedor/mis_solicitudes.html', {'solicitudes': solicitudes})

#funcion para mirar los datos del perfil del usuario logistica
@login_required
def perfil_logistica(request):
   return render(request, 'users/profile/logistica.html', {
        'usuario': request.user
    })