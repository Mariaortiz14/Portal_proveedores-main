from django.db.models import Count, Max, F, ExpressionWrapper, fields, DurationField, Value, OuterRef, Subquery, Q
from .forms import Evaluacion_inicial, caracteristicas, crear_solicitud, ComentarioForm, SolicitudForm, EvaluacionProveedorForm
from proveedores.models import Tarea, TipoTarea, homologacion, info_financiera
from django.shortcuts import render, redirect, get_object_or_404
from portal_proveedores.settings import DEFAULT_FROM_EMAIL as s
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import Group, User
from django.contrib.auth.models import User, Group
from django.db.models.functions import Coalesce
from django.template.loader import get_template
from datetime import date, timedelta, datetime
from django.contrib.auth.models import User
from proveedores.models import homologacion
from django.utils.timezone import now
from collections import defaultdict
from sqlalchemy import False_, desc
from django.contrib import messages
from django.template import loader
from django.db import transaction
from django.conf import settings
from proveedores.models import *
from django.db.models import Avg, F
from django.urls import reverse
from django.apps import apps
from compras.models import *
from .models import *
from .chart import *
import logging
import re
import os
#from weasyprint import HTML, CSS


logger = logging.getLogger(__name__)

# Funcion de vista de dashboard
def dashboard_compras(request):
    return render(request, 'compras/dashboard/index.html')

#Funcion de vista de dashboard
def get_dashboard_data(request):
    total_proveedores = homologacion.objects.count()
    proveedores_activos = homologacion.objects.filter(estado='activo').count()
    proveedores_inactivos = total_proveedores - proveedores_activos

    solicitudes_abiertas = solicitud.objects.filter(estado__in=['Nueva', 'Abierta']).count()
    solicitudes_revision = solicitud.objects.filter(estado='En revisión').count()
    solicitudes_cerradas = solicitud.objects.filter(estado='Cerrada').count()

    propuestas_aceptadas = propuestas_sol.objects.filter(estado='aceptada').count()
    propuestas_rechazadas = propuestas_sol.objects.filter(estado='rechazada').count()
    propuestas_enviadas = propuestas_sol.objects.exclude(estado__in=['aceptada', 'rechazada']).count()

    return JsonResponse({
        "proveedores": [proveedores_activos, proveedores_inactivos],
        "solicitudes": [solicitudes_abiertas, solicitudes_revision, solicitudes_cerradas],
        "propuestas": [propuestas_aceptadas, propuestas_rechazadas, propuestas_enviadas],
    })

#Función de tablas básicas
def t_basicas(request):
    return render(request, 'compras/tablas/t_basicas.html', {})

# funcion de vista de tablas
def tablas(request, t):
    app_config = apps.get_app_config('proveedores')
    
    tabla = None
    objetos = []
    nombre = ''
    nombre_t = ''

    for model in app_config.get_models():
        t_nombre = model.__name__
        if t == t_nombre:
            tabla = apps.get_model('proveedores', t)
            nombre = t_nombre.replace("_", " ")
            nombre_t = t_nombre
            objetos = tabla.objects.all()
            break  # Ya encontramos el modelo, no necesitamos seguir el loop

    if not tabla:
        messages.error(request, "No se encontró la tabla solicitada.")
    
    return render(request, 'compras/tablas/tablas.html', {
        't_nombre': nombre_t,
        'objetos': objetos,
        'nombre': nombre
    })

# Funcion de Eliminar tablas
def eliminar(request, tablas, id):
    tabla = apps.get_model('proveedores', tablas)
    tabla.objects.filter(id=id).delete()
    
    return redirect('compras:tablas', t=tablas)
# Funcion de crear tablas

def Crear_editar(request, tablas):
    tabla = apps.get_model('proveedores', tablas)
    id = request.POST['id']
    with transaction.atomic():
        if id == '':
            nombre_modelo = request.POST['nombre'] 
            tabla = apps.get_model('proveedores', tablas)
            objeto = tabla.objects.create(nombre=nombre_modelo)
            objeto.save()
        elif tabla.objects.filter(id=id):
            nombre_modelo = request.POST['nombre']
            id = request.POST['id']
            tabla = apps.get_model('proveedores', tablas)
            tabla.objects.filter(id=id).update(nombre=nombre_modelo)    

    return redirect('compras:tablas', t=tablas)
#Función de matriz de datos

def matriz(request):
    familias_= familias.objects.all()
    doc_generales = matriz_doc.objects.filter(tipo='DG')
    doc_certificados = matriz_doc.objects.filter(tipo='DC')
    doc_regla = matriz_doc.objects.filter(tipo='DR')
    doc_varios = matriz_doc.objects.filter(tipo='DV')
    doc_lic = matriz_doc.objects.filter(tipo='DL')
    doc_califi = matriz_doc.objects.filter(tipo='DCA')

    if request.method == 'POST':
        familia = familias.objects.get(id=request.POST['familia'])      
        print(request.POST)
        for key, value in request.POST.items():
            # Filtrar claves que no son números
            if not key.isdigit():
                continue
            if FamiliaDocumento.objects.filter(familia=familia, documento__id=key).exists():
                documento = matriz_doc.objects.get(id=key)
                if request.POST.get(key):
                    with transaction.atomic(): 
                        doc = FamiliaDocumento.objects.get(familia=familia, documento=documento)
                        doc.obligatoriedad = value
                        doc.save()
            elif matriz_doc.objects.filter(id=key).exists():
                documento = matriz_doc.objects.get(id=key)
                if request.POST.get(key):
                    with transaction.atomic(): 
                        FamiliaDocumento.objects.create(familia=familia, documento=documento, obligatoriedad=value)

    return render(request, 'compras/tablas/matriz.html', {'familias':familias_, 'doc_generales': doc_generales, 'doc_certificados': doc_certificados, 'doc_regla': doc_regla, 'doc_varios': doc_varios, 'doc_lic': doc_lic, 'doc_califi': doc_califi})

# Función de información de matriz
def matriz_info(request, familia):
    familia_doc = FamiliaDocumento.objects.filter(familia=familia).select_related('documento')
    
    if familia_doc.exists():
        documentos = [
            {
                'documento_id': fd.documento.id,
                'obligatoriedad': fd.obligatoriedad,
                'id': fd.pk
            }
            for fd in familia_doc
        ]
        return JsonResponse({'familia': familia, 'documentos': documentos})
    else:
        return JsonResponse({'familia': familia, 'documentos': 'No hay documentos asociados a esta familia'})

# Función de vista de proveedores-comprador
def Misproveedores(request):
    reg = registro_formulario.objects.all()
    registros = {}

    for r in reg:
        homologa = homologacion.objects.filter(id_registro=r.id_registro).first()
        if homologa:
            registros[r.id_registro] = [r, homologa]
        else:
            registros[r.id_registro] = [r, None]  # o puedes simplemente omitir si prefieres

    return render(request, 'compras/proveedores/index.html', {'registros': registros})

#Funcion de crear proveedores
def Proveedor(request, id_registro):
    registro = get_object_or_404(registro_formulario, id_registro=id_registro)
    homologa = get_object_or_404(homologacion, id_registro=id_registro)
    accionarios = composicion_accionaria.objects.filter(id_registro=id_registro)
    contable = info_pago.objects.get(id_registro=id_registro)

    try:
        financiera = info_financiera.objects.get(id_registro=id_registro)
    except info_financiera.DoesNotExist:
        financiera = None

    familias_ = familias.objects.all()
    documentos_g = documentos_requeridos.objects.filter(id_registro=id_registro)
    documentos_c = certificaciones_proveedores.objects.filter(id_registro=id_registro)

    cant_doc = documentos_g.count()
    cant_cer = documentos_c.count()
    total_doc = cant_doc + cant_cer

    documentos_aprobados = aprobacion_doc.objects.filter(documento__id_registro=id_registro).values('documento__id', 'aprobado')
    certifi_aprobados = aprobacion_doc.objects.filter(certificados__id_registro=id_registro).values('certificados__id', 'aprobado')
    todos_ids = documentos_aprobados.union(certifi_aprobados)

    doc_aceptados = sum(1 for doc in todos_ids if doc['aprobado'])
    doc_rechazados = sum(1 for doc in todos_ids if not doc['aprobado'])
    doc_pendientes = total_doc - (doc_aceptados + doc_rechazados)

    documentos_estado = {doc['documento__id']: doc['aprobado'] for doc in todos_ids}

    if aprobacion_doc.objects.filter(certificados__id='24'):
        oea_val = True
    else:
        oea_val = False
        if certificaciones_proveedores.objects.filter(id_registro=id_registro, certificacion_id='24'):
            mensaje_oea = "Documento no aprobado o rechazado"
        else:
            mensaje_oea = "Documento no subido"

    rse = 5 if registro.responsabilidad_social else 0
    plazos = productos_servicios_condiciones.objects.get(id_registro=id_registro)

    todos_documentos_aprobados = all(
        aprobacion_doc.objects.filter(documento__id=doc_id).exists()
        for doc_id in documentos_g.values_list('id', flat=True)
    )
    todos_certificados_aprobados = all(
        aprobacion_doc.objects.filter(certificados__id=cert_id).exists()
        for cert_id in documentos_c.values_list('id', flat=True)
    )
    condition = todos_documentos_aprobados and todos_certificados_aprobados

    if condition:
        condicion, faltantes, _ = verificar_documentos_y_certificados_por_familia(homologa.familia, id_registro)
        if condicion:
            matriz = all(
                aprobacion_doc.objects.filter(documento__id=doc_id, aprobado=True).exists()
                for doc_id in documentos_g.values_list('id', flat=True)
            ) and all(
                aprobacion_doc.objects.filter(certificados__id=cert_id, aprobado=True).exists()
                for cert_id in documentos_c.values_list('id', flat=True)
            )
            if matriz:
                valor_matriz = 40
                mensaje_matriz = "Todos los documentos y certificados requeridos han sido aprobados"
            else:
                valor_matriz = 20
                mensaje_matriz = "No todos los documentos y certificados requeridos han sido aprobados"
        else:
            valor_matriz = 20
            mensaje_matriz = "No todos los documentos y certificados requeridos han sido subidos"
    else:
        faltantes = []
        valor_matriz = 0
        mensaje_matriz = "No todos los documentos y certificados han sido aprobados"

    # Evaluación de homologación (documental)
    evaluacion_documentos = int(round((doc_aceptados / total_doc) * 100)) if total_doc > 0 else 0

    # Evaluación final (promedio de evaluaciones)
    evaluacion_final = EvaluacionProveedor.objects.filter(proveedor=registro.usuario).aggregate(
        promedio=Avg((F('puntualidad') + F('calidad') + F('comunicacion') + F('cumplimiento')) / 4.0)
    )['promedio'] or 0
    evaluacion_final = round(evaluacion_final, 1)

    form_homologacion = Evaluacion_inicial(initial={
        'oea': oea_val,
        'extra': rse,
        'forma_pago': plazos.plazo.id,
        'matriz': valor_matriz
    })

    evaluacion_form = EvaluacionProveedorForm()

    if request.method == 'POST':
        evaluacion_form = EvaluacionProveedorForm(request.POST)
        if evaluacion_form.is_valid():
            evaluacion_obj = evaluacion_form.save(commit=False)
            evaluacion_obj.proveedor = registro.usuario
            evaluacion_obj.evaluador = request.user
            evaluacion_obj.save()
            messages.success(request, "Evaluación registrada correctamente.")
            return redirect('compras:proveedor', id_registro=id_registro)

    return render(request, 'compras/proveedores/proveedor.html', {
        'registro': registro,
        'homologa': homologa,
        'contable': contable,
        'total': total_doc,
        'familias': familias_,
        'documentos_g': documentos_g,
        'documentos_c': documentos_c,
        'documentos_estado': documentos_estado,
        'form': form_homologacion,
        'evaluacion_form': evaluacion_form,
        'accionarios': accionarios,
        'mensaje_oea': mensaje_oea,
        'condition': condition,
        'faltantes': faltantes,
        'doc_pendientes': doc_pendientes,
        'doc_aceptados': doc_aceptados,
        'doc_rechazados': doc_rechazados,
        'mensaje_matriz': mensaje_matriz,
        'evaluacion': evaluacion_documentos,
        'evaluacion_final': evaluacion_final,
        'financiera': financiera,
    })

# Funcion de verificar documentos y certificados por familia
def verificar_documentos_y_certificados_por_familia(familia_id, id_registro):
    # Obtén todos los documentos requeridos para la familia
    documentos_matriz = FamiliaDocumento.objects.filter(familia_id=familia_id)

    # Obtén todos los documentos y certificados subidos
    documentos_subidos = documentos_requeridos.objects.filter(id_registro=id_registro)
    certificados_subidos = certificaciones_proveedores.objects.filter(id_registro=id_registro)

    # Verifica si todos los documentos y certificados requeridos han sido subidos
    documentos_faltantes = [doc_req for doc_req in documentos_matriz if doc_req.documento.id not in [doc_sub.documento.id for doc_sub in documentos_subidos]]
    certificados_faltantes = [cert_req for cert_req in documentos_matriz if cert_req.documento.id not in [cert_sub.certificacion.id for cert_sub in certificados_subidos]]

    # Verifica si todos los documentos y certificados obligatorios han sido subidos
    documentos_obligatorios_faltantes = [doc_req for doc_req in documentos_matriz if doc_req.documento.id not in [doc_sub.documento.id for doc_sub in documentos_subidos] and doc_req.obligatoriedad == '*']
    certificados_obligatorios_faltantes = [cert_req for cert_req in documentos_matriz if cert_req.documento.id not in [cert_sub.certificacion.id for cert_sub in certificados_subidos] and cert_req.obligatoriedad == '*']

    # Si todos los documentos y certificados obligatorios han sido subidos, condition es True. Si no, es False.
    condition = len(documentos_obligatorios_faltantes) == 0 and len(certificados_obligatorios_faltantes) == 0

    # Devuelve la condición y los arrays de documentos y certificados faltantes
    return condition, documentos_faltantes, certificados_faltantes

# Finción para aprobvar dovumentos
def aprobar_documento(request, id_registro):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                doc_id = request.POST['id']
                descripcion = request.POST['des']
                fecha_vencimiento = request.POST.get('fecha_ven') or None

                if 'aprobar' in request.POST:
                    if documentos_requeridos.objects.filter(id=doc_id).exists():
                        doc = documentos_requeridos.objects.get(id=doc_id)
                        aprobacion_doc.objects.create(documento=doc, aprobado=True, descripcion=descripcion, fecha_vencimiento=fecha_vencimiento)
                    elif certificaciones_proveedores.objects.filter(id=doc_id).exists():
                        cert = certificaciones_proveedores.objects.get(id=doc_id)
                        aprobacion_doc.objects.create(certificados=cert, aprobado=True, descripcion=descripcion, fecha_vencimiento=fecha_vencimiento)

                elif 'desaprobar' in request.POST:
                    if documentos_requeridos.objects.filter(id=doc_id).exists():
                        doc = documentos_requeridos.objects.get(id=doc_id)
                        aprobacion_doc.objects.create(documento=doc, aprobado=False, descripcion=descripcion)
                    elif certificaciones_proveedores.objects.filter(id=doc_id).exists():
                        cert = certificaciones_proveedores.objects.get(id=doc_id)
                        aprobacion_doc.objects.create(certificados=cert, aprobado=False, descripcion=descripcion)

                actualizar_estado_proveedor(id_registro)

        except Exception as e:
            print(e)

    return redirect('compras:proveedor', id_registro=id_registro)

#Funcion para la homologación de los proveedores
def homologacion_proveedor(request, id_registro):
    form = Evaluacion_inicial(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        homologa = evaluacion_inicial.objects.create(id_registro=id_registro, oea=form.cleaned_data['oea'],
                                                    descripcion_o=form.cleaned_data['descripcion_o'], validacion=form.cleaned_data['validacion'],
                                                    descripcion_v=form.cleaned_data['descripcion_v'], calidad=form.cleaned_data['calidad'],
                                                    descripcion_c=form.cleaned_data['descripcion_c'], extra=form.cleaned_data['extra'],
                                                    descripcion_ex=form.cleaned_data['descripcion_ex'], experiencia=form.cleaned_data['experiencia'],
                                                    descripcion_e=form.cleaned_data['descripcion_e'], matriz=form.cleaned_data['matriz'],
                                                    descripcion_m=form.cleaned_data['descripcion_m'], forma_pago=form.cleaned_data['forma_pago'],
                                                    descripcion_f=form.cleaned_data['descripcion_f'])
        homologa.save()
    return redirect('compras:proveedor', id_registro=id_registro)  
        #Funcion para asignarle familia a los proveedores desde la vista de comprador 
def asigancion_familia(request, id_registro):
    if request.method == 'POST':
        homo = homologacion.objects.get(id_registro=id_registro)
        familia = familias.objects.get(id=request.POST['familia'])
        homo.familia = familia

        if homo.id_registro and homo.id_registro.usuario:
            homo.usuario_hologa = homo.id_registro.usuario  

        homo.save()
    return redirect('compras:proveedor', id_registro=id_registro)

#Funcion para ver las solicitudes de ccompras de un proveedor 

def mis_solicitudes(request):
    hoy = date.today()
    solicitudes_raw = solicitud.objects.all()
    familias_ = familias.objects.all()

    solicitudes = []

    for s in solicitudes_raw:
        s.ocultar_estado = False  # type: ignore # Atributo temporal para la plantilla

        print(f"Solicitud ID: {s.id}")
        print(f"Estado: {s.estado}")
        print(f"Fecha de creación: {s.fecha_creacion}")

        if s.estado and s.estado.lower() == 'nueva' and s.fecha_creacion:
            dias_pasados = (hoy - s.fecha_creacion).days
            print(f"Días desde creación: {dias_pasados}")
            if s.fecha_creacion + timedelta(days=3) <= hoy:
                s.ocultar_estado = True # type: ignore
                print(f"✔ Estado será ocultado para la solicitud {s.id}")
            else:
                print(f"❌ Aún NO se oculta estado (menos de 3 días)")
        else:
            print(f"❌ No es 'nueva' o no tiene fecha de creación")

        if s.id and s.identificador and s.familia:
            solicitudes.append(s)

    return render(request, 'compras/solicitudes/solicitudes.html', {
        'solicitudes': solicitudes,
        'familias': familias_
    })

# Función de enviar email cuando se crea una solicitud de compra
def send_email_task(subject, recipient_list, template_name, context):
    try:        
        if not isinstance(recipient_list, (list, tuple)):
            recipient_list = [recipient_list]
        domain = f"{settings.SITE_DOMAIN}:{settings.SITE_PORT}"
        
        # Generar la URL completa
        solicitud_id = context.get('solicitud_id')
        if solicitud_id:
            relative_url = reverse('compras:solicitud_id', args=[solicitud_id])
            full_url = f"{settings.DEFAULT_HTTP_PROTOCOL}://{domain}{relative_url}"
            print(full_url)
            context['url'] = full_url
 
        print(context)
        # Renderizar la plantilla con el contexto proporcionado
        content = render_to_string(template_name, context)
        from_email = s  # Define el remitente correctamente
        
        # Crea el mensaje de correo electrónico
        message = EmailMultiAlternatives(
            subject,  # Título
            '',  # El cuerpo del mensaje en texto plano (puede estar vacío si solo enviarás HTML)
            from_email,  # Remitente
            [],
            bcc=recipient_list,# Destinatario(s)
        )
        
        # Adjunta el contenido HTML
        message.attach_alternative(content, 'text/html')
        
        # Envía el correo
        message.send()
    except Exception as e:
        print(e)
        logger.error(f"Error al enviar el correo: {e}")

#Función para crear solicitudes de compra desde la vista del proveedor
def crear_solicitudes(request):
    form = crear_solicitud(request.POST or None)
    if request.method=='POST':
        carac = form.carasteristicas(request.POST or None)
        try:
            with transaction.atomic():
                if form.is_valid() and carac.is_valid():
                    solicitud_ = solicitud.objects.create(
                        TSolicitud=form.cleaned_data['solicitud'],
                        descripcion=form.cleaned_data['descripcion'],
                        familia=form.cleaned_data['familia'],
                        cantidad=form.cleaned_data['cantidad'],
                        fecha_final=form.cleaned_data.get('fecha_final'),
                        estado='Nueva'
                    )
                    for c in carac.cleaned_data:
                        if 'caracteristica' in c and c['caracteristica'] != ' ':
                            caracteristica = c['caracteristica']
                            caracteristicas_solicitud.objects.create(
                                solicitud_id=solicitud_.id,
                                caracteristica=caracteristica
                            )
                    id = solicitud_.id
                    url = reverse('compras:solicitud_id', args=[id])
                    correos = homologacion.objects.filter(familia=solicitud_.familia).values_list('id_registro__email', flat=True)
                    if correos:
                        context = {
                            'titulo': solicitud_.TSolicitud,
                            'descripcion': solicitud_.descripcion,
                            'fecha_creacion': solicitud_.fecha_creacion,
                            'url': url,
                            'solicitud_id':id, 
                        }
                        send_email_task('Solicitud FEPCO', correos, 'compras/correo/email_notsoli.html', context)
                    else:
                        messages.error(request, 'No se envió correos porque no hay proveedores homologados para esta familia')
                        context = {
                            'solicitud': solicitud_.TSolicitud,
                            'descripcion': solicitud_.descripcion,
                            'fecha_creacion': solicitud_.fecha_creacion,
                            'error': 'No se envió correos porque no hay proveedores homologados para esta familia',
                            'url': url,
                            'solicitud_id': id,
                        }
                        send_email_task('error al enviar [Solicitud FEPCO]', 'ymorales@fepco.com.co', 'compras/correo/email_notsoli.html', context)
                    return redirect('compras:missolicitudes')
                else:
                    messages.error(request, 'Formulario inválido')
        except Exception as e:
            messages.error(request, f'Error al crear la solicitud: {str(e)}')
            return redirect('compras:crear_solicitud')

    return render(request, 'compras/solicitudes/crear_soli.html', {'form':form})

#Función para eliminar una solicitud desde la vista de proveedor
def eliminar_solicitud(request, id):
    solicitud.objects.filter(id=id).delete()
    return redirect('compras:missolicitudes')

#Función para mostrar las solicitudes de un proveedor individualemnte 
def solicitud_id(request, id):

    solicitudes = solicitud.objects.get(id=id)    
    subquery = propuestas_sol.objects.filter(
        id_homologacion=OuterRef('id_homologacion')
    ).values('id_homologacion').annotate(max_id=Max('id')).values('max_id')
    
    propuestas_ultimas = propuestas_sol.objects.filter(
        id__in=Subquery(subquery), id_solicitud_id=id
    )
    propuestas_ranking = propuestas_ultimas.annotate(
        tiempo_entrega=ExpressionWrapper(
            Coalesce(F('tiempo_entrega_max'), Value(0)) - F('tiempo_entrega_min'),
            output_field=DurationField()
        )
    ).order_by('valor_t', 'tiempo_entrega')
    form = ComentarioForm()                                                                                                                                                                                                                                                                                                                                                                         
    return render(request, 'compras/solicitudes/solicitud_id.html', {'solicitud': solicitudes, 'form_comentarios': form, 'propuestas_ultimas': propuestas_ultimas, 'propuestas_ranking': propuestas_ranking})

#Función para obtener las propuestas que tienen los mismos proveedores
def get_propuestas_chart(request, id):
    propuestas= propuestas_sol.objects.filter(id_solicitud_id=id)
 
    propuestas_por_homologacion = defaultdict(list)
    for propuesta in propuestas:
        propuestas_por_homologacion[propuesta.id_homologacion].append(propuesta)
        
    if propuestas:
        mx_conteo = max(p.conteo for p in propuestas)
    else:
        mx_conteo = 1  # o 0 según lo que tenga más sentido

      
    return JsonResponse({
        "title": f"Ranking propuestas por Proveedor",
        "data": {
            "labels": [num for num in range(1, mx_conteo + 1)],
            "datasets": [
                {
                    "label": f"Proveedor {id_homologacion.id_registro.sigla}",
                    "data": [propuesta.valor_t for propuesta in propuestas],
                    "fill": False,
                    "borderColor": generate_color_random(),
                    "tension": 0,
                }
                for id_homologacion, propuestas in propuestas_por_homologacion.items()
            ]
        },
    })

#Función para crear un comentario en una solicitud
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

                    comentario.save()  # Guardar siempre antes de cualquier otra acción

            except Exception as e:
                print("Error al guardar el comentario:", str(e))
                messages.error(request, 'Hubo un error al guardar el comentario.')

        else:
            messages.error(request, 'Formulario inválido. Revisa los campos.')

    return redirect('proveedor:solicitud_id', identificador=solicitud_obj.identificador)
  
#Función para crear tareas para los proveedores
def tareas(request):
    tareas = Tarea.objects.all()
    user_id = request.GET.get('user', '')
    status = request.GET.get('status', '')

    # Filtrar por usuario
    if user_id:
        tareas = tareas.filter(usuario__id=user_id)

    # Filtrar por estado
    if status == 'hecha':
        tareas = tareas.filter(hecha=True)
    elif status == 'no_hecha':
        tareas = tareas.filter(hecha=False)

    grupo_proveedor = Group.objects.get(name='Proveedor')
    users = User.objects.filter(groups=grupo_proveedor)
    homologaciones = homologacion.objects.select_related('id_registro').all()
    tipos_tarea = TipoTarea.objects.all()

    return render(request, 'compras/tareas/tareas.html', {
        'tareas': tareas,
        'users': users,
        'homologaciones': homologaciones,
        'tipos_tarea': tipos_tarea,
        'user_selected_id': user_id,
        'status_selected': status
    })


#Función para asignar una nueva tarea desde la interfaz de compras a proveedores
def asignar_tarea_doc(request):
    print("🚨 Entró a asignar_tarea_doc")
    if request.method == 'POST':
        try:
            with transaction.atomic():
                tipo_id = request.POST.get('tipo_id')
                tipo = TipoTarea.objects.get(id=tipo_id)

                user_id = request.POST.get('assigned_to')
                usuario = User.objects.get(id=user_id)

                homologacion_ = homologacion.objects.filter(usuario_hologa=usuario).first()
                if not homologacion_:
                    print("❌ No se encontró homologación")
                    messages.error(request, "El usuario seleccionado no tiene homologación válida.")
                    return redirect('compras:tareas')

                titulo = request.POST.get('title')
                descripcion = request.POST.get('description')
                fecha_vencimiento_raw = request.POST.get('due_date')
                fecha_vencimiento = datetime.strptime(fecha_vencimiento_raw, "%Y-%m-%d")

                print(f"📋 Campos recibidos: {titulo} {descripcion} {fecha_vencimiento} {usuario}")

                tarea = Tarea.objects.create(
                    titulo=titulo,
                    descripcion=descripcion,
                    fecha_vencimiento=fecha_vencimiento,
                    datos_adicionales="Asignada desde el panel de compras",
                    tipo=tipo,
                    usuario=usuario
                )

                print("✅ Tarea guardada con ID:", tarea.pk)
                messages.success(request, "Tarea asignada correctamente.")

        except Exception as e:
            print("❌ ERROR al crear tarea:", e)
            messages.error(request, "No se pudo asignar la tarea.")
    return redirect('compras:tareas')

#Función para general un pdf con la información de un registro de compras
'''def generar_pdf(request, id_registro):
    registro = get_object_or_404(registro_formulario, id_registro=id_registro)
    homologa = get_object_or_404(homologacion, id_registro=id_registro)
    accionarios = composicion_accionaria.objects.filter(id_registro=id_registro)
    contable = get_object_or_404(info_pago, id_registro=id_registro)
    financiera = get_object_or_404(info_financiera, id_registro=id_registro)
    tributaria = get_object_or_404(info_tributaria, id_registro=id_registro)
    resolucion_ = resolucion.objects.filter(id_trib=tributaria)
    # Renderizar el HTML con los datos
    html_string = render_to_string('compras/proveedores/contacto_report.html', {
        'registro': registro,
        'homologa': homologa,
        'contable': contable,
        'accionarios': accionarios,
        'financiera': financiera,
        'tributaria': tributaria,
    })

    # Crear el PDF
  html = HTML(string=html_string)
    bootstrap_css_path = os.path.join(settings.STATIC_ROOT, "bootstrap/css/bootstrap.min.css")
    pdf = html.write_pdf(stylesheets=[CSS(bootstrap_css_path)])
    
    # Devolver el PDF como respuesta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=registro_{id_registro}.pdf'
    return response'''

#Función para editar una solicitud de compras
def editar_solicitud_modal(request):
    if request.method == 'POST':
        id = request.POST.get('solicitud_id')
        tipo = request.POST.get('tipo')
        familia_id = request.POST.get('familia')
        fecha_final = request.POST.get('fecha_final')

        solicitud_ = get_object_or_404(solicitud, id=id)
        solicitud_.TSolicitud = tipo
        solicitud_.familia = familias.objects.get(id=familia_id)
        solicitud_.fecha_final = fecha_final if fecha_final else None
        solicitud_.save()
        messages.success(request, "Solicitud actualizada correctamente.")
        return redirect('compras:mis_solicitudes')

#Función para editar una solicitud de compras
def editar_solicitud(request, id):
    solicitud_ = get_object_or_404(solicitud, id=id)

    if request.method == 'POST':
        form = SolicitudForm(request.POST, instance=solicitud_)
        if form.is_valid():
            form.save()
            return redirect(reverse('detalle_solicitud', args=[solicitud_.id]))
    else:
        form = SolicitudForm(instance=solicitud_)

    return render(request, 'editar_solicitud.html', {'form': form, 'solicitud': solicitud_})

#Función para ver los datos del comprador en el apartado de mi cuenta
def perfil_comprador(request):
    # if not request.user.groups.filter(name='Comprador').exists():
    #     return render(request, 'compras/acceso_denegado.html')

    return render(request, 'users/profile/comprador.html', {
        'usuario': request.user
    })

#Función para ver los datos del comprador en el apartado de mi cuenta
def actualizar_estado_proveedor(id_registro):
    docs = documentos_requeridos.objects.filter(id_registro=id_registro)
    certs = certificaciones_proveedores.objects.filter(id_registro=id_registro)

    total = docs.count() + certs.count()
    if total == 0:
        return  # No hay documentos para evaluar

    aprobaciones = aprobacion_doc.objects.filter(
        Q(documento__id_registro=id_registro) | Q(certificados__id_registro=id_registro)
    )

    aprobados = aprobaciones.filter(aprobado=True).count()
    rechazados = aprobaciones.filter(aprobado=False).count()

    try:
        hom = homologacion.objects.get(id_registro=id_registro)
        if rechazados > 0:
            hom.estado = "Rechazado"
        elif aprobados == total:
            hom.estado = "Activo"
        else:
            hom.estado = "Pendiente"
        hom.save()
    except homologacion.DoesNotExist:
        pass
