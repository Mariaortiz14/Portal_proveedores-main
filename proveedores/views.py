from proveedores.models import homologacion, propuestas_sol, documentos_requeridos, certificaciones_proveedores, registro_formulario
from compras.models import caracteristicas_solicitud, solicitud, comentarios
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string




from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from compras.forms import caracteristicas

from .forms import form_propuesta
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage
from compras.forms import ComentarioForm
from django.urls import reverse
from compras.views import send_email_task

from compras.models import solicitud as Solicitud

from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMessage

from django.contrib import messages
from .models import comentarios
from compras.models import solicitud
from django.db import transaction 
import os
from .models import *

def agregar_comentario(request, id, parent_id=None):
    solicitud_obj = get_object_or_404(solicitud, id=id)

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():  # 👈 NUEVO
                    comentario = form.save(commit=False)
                    comentario.solicitud = solicitud_obj
                    comentario.usuario = request.user
                    if parent_id:
                        comentario.parent_id = parent_id

                    # Construcción segura de la URL
                    protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')
                    domain = request.get_host()
                    full_url = f"{protocol}://{domain}{reverse('proveedor:solicitud_id', kwargs={'identificador': solicitud_obj.identificador})}"

                    subject = f"[Nuevo comentario] en la solicitud: {solicitud_obj.TSolicitud}"
                    context = {
                        'titulo': solicitud_obj.TSolicitud,
                        'url': full_url,
                        'solicitud_id': solicitud_obj.id,
                    }

                    html_content = render_to_string('compras/correo/email_comentario.html', context)

                    email = EmailMessage(
                        subject,
                        html_content,
                        settings.DEFAULT_FROM_EMAIL,
                        to=['ymorales@fepco.com.co', 'myito1612@gmail.com']
                    )
                    email.content_subtype = 'html'
                    email.send()  

                    comentario.save()  

                messages.success(request, 'Comentario agregado correctamente.')

            except Exception as e:
                print("Error al enviar el correo:", str(e))
                messages.error(request, 'No se pudo enviar el comentario. Intenta de nuevo.')

        else:
            messages.error(request, 'Formulario inválido. Revisa los campos.')

    return redirect('proveedor:solicitud_id', identificador=solicitud_obj.identificador)




def dashboard(request):
    propuestas = []
    grafico_data = {
        'pendientes': 0,
        'aceptadas': 0,
        'rechazadas': 0,
    }
    solicitudes = []

    try:
        homol = homologacion.objects.filter(usuario_hologa=request.user).first()
        propuestas = propuestas_sol.objects.filter(id_homologacion=homol)

        grafico_data = {
            'pendientes': propuestas.filter(estado='pendiente').count(),
            'aceptadas': propuestas.filter(estado='aceptada').count(),
            'rechazadas': propuestas.filter(estado='rechazada').count(),
        }

    except homologacion.DoesNotExist:
        pass

    # Obtener solicitudes activas
    solicitudes = solicitud.objects.filter(estado__in=['Nueva', 'Abierta'])

    context = {
        'propuestas': propuestas,
        'grafico_data': grafico_data,
        'solicitudes': solicitudes,
    }

    return render(request, 'proveedores/dashboard/index.html', context)


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

    estados = ['pendiente', 'aceptado', 'rechazado']
    documentos_por_estado = {estado: documentos.filter(estado=estado) for estado in estados}
    certificaciones_por_estado = {estado: certificaciones.filter(estado=estado) for estado in estados}

    context = {
        'documentos_por_estado': documentos_por_estado,
        'certificaciones_por_estado': certificaciones_por_estado,
    }

    return render(request, "proveedores/doc/documentos.html", context)


def listar_archivos(request):
    media_path = os.path.join(settings.BASE_DIR, 'media')

    # Obtener una lista de archivos PDF en el directorio de medios
    pdf_files = [f for f in os.listdir(media_path) if f.endswith('.pdf')]
    print("Archivos PDF en el directorio de medios:", pdf_files)

    # Renderizar la plantilla con la lista de archivos PDF
    return render(request, 'proveedores/doc/documentos.html', {'pdf': pdf_files})

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

def solicitudes(request):
    homologacion_obj = homologacion.objects.filter(usuario_hologa=request.user.id).first()
    familia_ = homologacion_obj.familia if homologacion_obj else None
    if familia_ is not None:
        solicitudes = solicitud.objects.filter(familia=familia_.id )
    else:
        solicitudes = []
    return render(request, 'proveedores/solicitudes/solicitudes.html', {'solicitudes':solicitudes})

def solicitud_id(request, identificador):
    solicitud_ = solicitud.objects.get(identificador=identificador)
    caracteristicas = caracteristicas_solicitud.objects.filter(solicitud=solicitud_)
    form = form_propuesta()
    form_comentario = ComentarioForm()
    comentarios_usuario = comentarios.objects.filter(solicitud=solicitud_, usuario=request.user).exclude(parent__isnull=False)  

    if request.method == 'POST':
        form = form_propuesta(request.POST, request.FILES)
        id_homolo = homologacion.objects.filter(
                     usuario_hologa=request.user,
                     familia=solicitud_.familia
                        ).first()
        if not id_homolo:
            messages.error(request, 'No tienes una homologación válida para esta solicitud.')
            return redirect('proveedor:solicitud_id', identificador=identificador)

        if form.is_valid():
            print("Homologación usada:", id_homolo)
            print("Solicitud asociada:", solicitud_)
            print("Datos del formulario:", form.cleaned_data)

            propuestas_sol.objects.create(
                id_homologacion=id_homolo,
                id_solicitud=solicitud_,
                **form.cleaned_data
            )
            messages.success(request, 'Propuesta enviada con éxito.')   
            return redirect('proveedor:solicitud_id', identificador=solicitud_.identificador)
        else:
            messages.error(request, 'Ocurrió un error al enviar la propuesta. Verifica los campos.')
            print(form.errors)

    return render(request, 'proveedores/solicitudes/solicitud_id.html', {
        'solicitud': solicitud_,
        'caracteristicas': caracteristicas,
        'form': form,
        'form_comentario': form_comentario,
        'Comentarios_usuario': comentarios_usuario
    })

def tareas(request):
    tareas_qs = Tarea.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    tareas = []
    for t in tareas_qs:
        tareas.append({
            'title': t.titulo,
            'description': t.descripcion,
            'due_date': t.fecha_vencimiento.strftime('%Y-%m-%d'),
            'status': 'Hecha' if t.hecha else 'Pendiente'
        })

    return render(request, 'proveedores/tareas/tareas.html', {'tareas': tareas})

def propuestas(request):
    from proveedores.models import propuestas_sol, homologacion

    homologaciones = homologacion.objects.filter(usuario_hologa=request.user)
    propuestas = propuestas_sol.objects.filter(id_homologacion__in=homologaciones).order_by('-fecha')

    print("Propuestas encontradas:", propuestas)

    return render(request, 'proveedores/propuestas/propuestas.html', {
        'propuestas': propuestas
    })
