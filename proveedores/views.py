from proveedores.models import homologacion, propuestas_sol, documentos_requeridos, certificaciones_proveedores, registro_formulario
from compras.models import caracteristicas_solicitud, solicitud, comentarios
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from compras.models import solicitud as Solicitud
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from compras.forms import caracteristicas
from django.core.mail import EmailMessage
from compras.views import send_email_task
from compras.forms import ComentarioForm
from django.http import HttpResponse
from compras.models import solicitud
from django.contrib import messages
from django.template import loader
from .forms import form_propuesta
from django.db import transaction 
from django.conf import settings
from django.urls import reverse
from datetime import datetime, date , timedelta
from .models import *
import os



def agregar_comentario(request, id, parent_id=None):
    solicitud_obj = get_object_or_404(solicitud, id=id)

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    comentario = form.save(commit=False)
                    comentario.solicitud = solicitud_obj
                    comentario.usuario = request.user
                    if parent_id:
                        comentario.parent_id = parent_id
                    comentario.save()

                    messages.success(request, 'Comentario agregado correctamente.')

            except Exception as e:
                print("Error al guardar el comentario:", str(e))
                messages.error(request, 'No se pudo guardar el comentario. Intenta de nuevo.')
        else:
            messages.error(request, 'Formulario inválido. Revisa los campos.')

    return redirect('proveedor:solicitud_id', identificador=solicitud_obj.identificador)

#Funcion para mostrar el dashboard de proveedor
def dashboard(request):
    propuestas = []
    grafico_data = {
        'pendientes': 0,
        'aceptadas': 0,
        'rechazadas': 0,
    }
    solicitudes = []
    tareas = []

    try:
        homol = homologacion.objects.filter(usuario_hologa=request.user).first()
        propuestas = propuestas_sol.objects.filter(id_homologacion=homol)

        grafico_data = {
            'pendientes': propuestas.filter(estado='pendiente').count(),
            'aceptadas': propuestas.filter(estado='aceptada').count(),
            'rechazadas': propuestas.filter(estado='rechazada').count(),
        }

        # Obtener tareas asignadas al usuario autenticado
        tareas = Tarea.objects.filter(usuario=request.user).order_by('-fecha_vencimiento')

    except homologacion.DoesNotExist:
        pass

    solicitudes = solicitud.objects.filter(estado__in=['Nueva', 'Abierta'])

    context = {
        'propuestas': propuestas,
        'grafico_data': grafico_data,
        'solicitudes': solicitudes,
        'tareas': tareas,  
    }

    return render(request, 'proveedores/dashboard/index.html', context)

#Función para mostrar los documentos
def doc(request):
    if request.method == 'POST':
        file = request.FILES.get('file')

        if 'doc_id' in request.POST:
            doc_id = request.POST.get('doc_id')
            try:
                documento = documentos_requeridos.objects.get(id=doc_id)
                documento.file = file
                documento.estado = 'pendiente'  
                documento.save()
                messages.success(request, 'Documento cargado correctamente.')
            except documentos_requeridos.DoesNotExist:
                messages.error(request, 'El documento no existe.')

        elif 'cert_id' in request.POST:
            cert_id = request.POST.get('cert_id')
            try:
                cert = certificaciones_proveedores.objects.get(id=cert_id)
                cert.file = file
                cert.estado = 'pendiente'
                cert.save()
                messages.success(request, 'Certificación cargada correctamente.')
            except certificaciones_proveedores.DoesNotExist:
                messages.error(request, 'La certificación no existe.')

        return redirect('users:profile')

    registro = registro_formulario.objects.filter(usuario=request.user).first()
    documentos = documentos_requeridos.objects.filter(id_registro=registro)
    certificaciones = certificaciones_proveedores.objects.filter(id_registro=registro)

    aprobaciones = aprobacion_doc.objects.filter(documento__id_registro=registro)

    documentos_aprobados_ids = aprobaciones.filter(aprobado=True).values_list('documento__id', flat=True)
    documentos_rechazados_ids = aprobaciones.filter(aprobado=False).values_list('documento__id', flat=True)

    pendientes = documentos.exclude(id__in=documentos_aprobados_ids).exclude(id__in=documentos_rechazados_ids)
    aceptados = documentos.filter(id__in=documentos_aprobados_ids)
    rechazados = documentos.filter(id__in=documentos_rechazados_ids)

    # === Validación por tabla de aprobaciones para CERTIFICACIONES ===
    aprobaciones_cert = aprobacion_doc.objects.filter(certificados__id_registro=registro)

    certificados_aprobados_ids = aprobaciones_cert.filter(aprobado=True).values_list('certificados__id', flat=True)
    certificados_rechazados_ids = aprobaciones_cert.filter(aprobado=False).values_list('certificados__id', flat=True)

    cert_pendientes = certificaciones.exclude(id__in=certificados_aprobados_ids).exclude(id__in=certificados_rechazados_ids)
    cert_aceptados = certificaciones.filter(id__in=certificados_aprobados_ids)
    cert_rechazados = certificaciones.filter(id__in=certificados_rechazados_ids)



    context = {
    'pendientes': pendientes,
    'aceptados': aceptados,
    'rechazados': rechazados,
    'cert_pendientes': cert_pendientes,
    'cert_aceptados': cert_aceptados,
    'cert_rechazados': cert_rechazados,
    }


    return render(request, "proveedores/doc/documentos.html", context)


#Función para listar todos los archivos
def listar_archivos(request):
    media_path = os.path.join(settings.BASE_DIR, 'media')

    # Obtener una lista de archivos PDF en el directorio de medios
    pdf_files = [f for f in os.listdir(media_path) if f.endswith('.pdf')]
    print("Archivos PDF en el directorio de medios:", pdf_files)

    # Renderizar la plantilla con la lista de archivos PDF
    return render(request, 'proveedores/doc/documentos.html', {'pdf': pdf_files})

#Función para descargar los archivos pdf
def descargar_archivo(request, path):
    # Construir la ruta completa al archivo en el directorio MEDIA_ROOT
    ruta_completa = os.path.join(settings.MEDIA_ROOT, path)

    # Verificar si el archivo existe
    if os.path.exists(ruta_completa):
        # Abrir el archivo en modo binario
        with open(ruta_completa, 'rb') as archivo:
            # Crear una respuesta HTTP con el contenido del archivo
            response = HttpResponse(archivo.read(), content_type='application/pdf')

            # Configurar las cabeceras para la descarga
            response['Content-Disposition'] = f'inline; filename={os.path.basename(ruta_completa)}'

            return response
    else:
        # Manejar el caso en que el archivo no existe
        return HttpResponse("El archivo no existe", status=404)

#Función para listar las solicitudes
def solicitudes(request):
    homologacion_obj = homologacion.objects.filter(usuario_hologa=request.user.id).first()
    familia_ = homologacion_obj.familia if homologacion_obj else None

    solicitudes_raw = solicitud.objects.filter(familia=familia_.id) if familia_ else []
    solicitudes = []
    hoy = date.today()

    for s in solicitudes_raw:
        ocultar_estado = False
        if s.estado.lower() == 'nueva' and s.fecha_creacion:
            if s.fecha_creacion + timedelta(days=3) < hoy:
                ocultar_estado = True
        solicitudes.append({
            'solicitud': s,
            'ocultar_estado': ocultar_estado
        })

    return render(request, 'proveedores/solicitudes/solicitudes.html', {'solicitudes': solicitudes})

#Función para listar las solicitudes por identificador
def solicitud_id(request, identificador):
    solicitud_ = solicitud.objects.get(identificador=identificador)
    caracteristicas = caracteristicas_solicitud.objects.filter(solicitud=solicitud_)
    form = form_propuesta()
    form_comentario = ComentarioForm()
    comentarios_usuario = comentarios.objects.filter(solicitud=solicitud_, usuario=request.user).exclude(parent__isnull=False)

    # Buscar homologación válida para esta solicitud
    id_homolo = homologacion.objects.filter(
        usuario_hologa=request.user,
        familia=solicitud_.familia
    ).first()

    # Mostrar propuestas ya asociadas si existen
    propuestas_asociadas = propuestas_sol.objects.filter(
        id_solicitud=solicitud_,
        id_homologacion=id_homolo
    ) if id_homolo else []

    if request.method == 'POST':
        form = form_propuesta(request.POST, request.FILES)
        if not id_homolo:
            messages.error(request, 'No tienes una homologación válida para esta solicitud.')
            return redirect('proveedor:solicitud_id', identificador=identificador)

        if form.is_valid():
            try:
                print("📝 Homologación usada:", id_homolo)
                print("📄 Solicitud asociada:", solicitud_)
                print("📦 Datos del formulario:", form.cleaned_data)
                print("📎 Archivo recibido:", request.FILES.get('file'))

                # Crear manualmente la instancia de propuesta
                propuesta = propuestas_sol(
                    id_homologacion=id_homolo,
                    id_solicitud=solicitud_,
                    estado='pendiente',
                    **form.cleaned_data
                )
                if 'file' in request.FILES:
                    propuesta.file = request.FILES['file']
                propuesta.save()

                messages.success(request, 'Propuesta enviada con éxito.')
                return redirect('proveedor:solicitud_id', identificador=solicitud_.identificador)
            except Exception as e:
                print("❌ Error al guardar propuesta:", e)
                messages.error(request, 'Error al guardar la propuesta.')
        else:
            messages.error(request, 'Ocurrió un error al enviar la propuesta. Verifica los campos.')
            print(form.errors)

    return render(request, 'proveedores/solicitudes/solicitud_id.html', {
        'solicitud': solicitud_,
        'caracteristicas': caracteristicas,
        'form': form,
        'form_comentario': form_comentario,
        'Comentarios_usuario': comentarios_usuario,
        'propuestas': propuestas_asociadas
    })

#Funcion para listar las tareas que asignaron a proveedores
def tareas(request):
    tareas = Tarea.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'proveedores/tareas/tareas.html', {'tareas': tareas})


def marcar_tarea_hecha(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)

    if not tarea.hecha:
        tarea.hecha = True
        tarea.save()
        messages.success(request, "Tarea marcada como hecha.")
    else:
        messages.info(request, "Esta tarea ya está marcada como hecha.")

    return redirect('proveedores:tareas')

def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)

    if not tarea.hecha:
        messages.error(request, "No puedes eliminar una tarea que aún está pendiente.")
        return redirect('proveedores:tareas')

    tarea.delete()
    return redirect('proveedores:tareas')


def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)

    if request.method == 'POST':
        tarea.titulo = request.POST.get('titulo')
        tarea.descripcion = request.POST.get('descripcion')
        tarea.fecha_vencimiento = request.POST.get('fecha_vencimiento')
        tarea.save()
        messages.success(request, "Tarea actualizada correctamente.")
        return redirect('proveedores:tareas')

    return render(request, 'proveedores/tareas/editar_tarea.html', {'tarea': tarea})

#Funcion para listar las propuestas hechas por el proveedor
def propuestas(request):
    # Todas las homologaciones asociadas al usuario logueado
    homologaciones = homologacion.objects.filter(usuario_hologa=request.user)

    # Mostrar todas las propuestas vinculadas a cualquiera de esas homologaciones
    propuestas = propuestas_sol.objects.filter(
        id_homologacion__in=homologaciones
    ).order_by('-fecha')

    return render(request, 'proveedores/propuestas/propuestas.html', {
        'propuestas': propuestas
    })

