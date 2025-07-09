from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from datetime import date, datetime, time
from django.utils.html import escape
from django.core import serializers
from django.contrib import messages
from django.template import loader
from django.db import transaction
from proveedores.models import *
from django.urls import reverse
from email.mime import message
from django import forms
from logging import info
from .models import *
from .forms import *
import re

#Función para llenar el formulario de registro
def signup(request):
    seccion1 = ProveedorForm_(request.POST or None, prefix='seccion1')
    ca = forms.formset_factory(composicion_accionaria_, extra=1, max_num=8)
    seccion2 = ca(request.POST or None, prefix='seccion2')
    seccion3 = informacion_financiera_(request.POST or None, prefix='seccion3')
    seccion4 = informacion_tributaria_(request.POST or None, prefix='seccion4')
    resolucion_formset = seccion4.resolucionT(request.POST or None, prefix='seccion4', initial=[
        {'Tcontribuyente': 'T03'}, {'Tcontribuyente': 'T04'}
    ])
    seccion5 = informacion_pagos_contable_(request.POST or None, prefix='seccion5')
    certificados = forms.formset_factory(certificacion_ or None, extra=8, max_num=8)
    seccion6 = certificados(request.POST or None, request.FILES or None, initial=[
        {'certificacion': 20, 'nombre': 'ISO 28000'},
        {'certificacion': 21, 'nombre': 'ISO 27000'},
        {'certificacion': 22, 'nombre': 'API'},
        {'certificacion': 23, 'nombre': 'OHSAS 18001'},
        {'certificacion': 2, 'nombre': 'ISO 14000'},
        {'certificacion': 1, 'nombre': 'ISO 9001'},
        {'certificacion': 19, 'nombre': 'RUC'},
        {'certificacion': 24, 'nombre': 'OEA'}
    ], prefix='seccion6')
    doc = forms.formset_factory(documentos_requeridos_, extra=1, max_num=8)
    seccion7 = doc(request.POST or None, request.FILES or None, initial=[
        {'documento': 26}, {'documento': 27}, {'documento': 28},
        {'documento': 29}, {'documento': 30}, {'documento': 31},
        {'documento': 46}, {'documento': 33}, {'documento': 32}
    ], prefix='seccion7')
    seccion8 = condiciones_pago_catalogo_(request.POST or None, request.FILES or None, prefix='seccion8')
    seccion9 = declaracion_(request.POST or None, request.FILES or None, prefix='seccion9')

    if request.method == "POST":
        try:
            formularios = [
                seccion1, seccion2, seccion3, seccion4,
                resolucion_formset, seccion5, seccion6,
                seccion7, seccion8, seccion9
            ]

            if request.user.is_authenticated:
                if registro_formulario.objects.filter(usuario=request.user).exists():
                    return redirect('users:profile')

            if all(formulario.is_valid() for formulario in formularios):
                with transaction.atomic():

                    # Crear o asignar usuario
                    if request.user.is_authenticated:
                        user = request.user
                    else:
                        email = formularios[0].cleaned_data['email']
                        documento = formularios[0].cleaned_data['documento']
                        user = User.objects.create_user(username=documento, password='12345678', email=email)

                        grupo, _ = Group.objects.get_or_create(name='Proveedor')
                        user.groups.add(grupo)
                        login(request, user)

                    # Crear registro principal
                    registro = registro_formulario.objects.create(usuario=user, **formularios[0].cleaned_data)

                    # Guardar subsecciones
                    for f in formularios[1]:
                        if f.cleaned_data and f.cleaned_data['tipo_identificacion']:
                            composicion_accionaria.objects.create(id_registro=registro, **f.cleaned_data)

                    info_financiera.objects.create(id_registro=registro, **formularios[2].cleaned_data)

                    cleaned_data = formularios[3].cleaned_data.copy()
                    Tcontribuyente = cleaned_data.pop('tipo_contribuyente')
                    tribu = info_tributaria.objects.create(id_registro=registro, **cleaned_data)

                    for data in Tcontribuyente:
                        if data.codigo != 'T03' and data.codigo != 'T04':
                            resolucion.objects.create(id_trib=tribu, Tcontribuyente=data)
                        else:
                            for f in formularios[4]:
                                if f.cleaned_data and f.cleaned_data['Tcontribuyente']:
                                    resolucion.objects.create(id_trib=tribu, **f.cleaned_data)

                    info_pago.objects.create(id_registro=registro, **formularios[5].cleaned_data)

                    for f in formularios[6]:
                        if f.cleaned_data and f.cleaned_data['file']:
                            f.cleaned_data.pop('nombre', None)
                            certificaciones_proveedores.objects.create(id_registro=registro, **f.cleaned_data)

                    for f in formularios[7]:
                        if f.cleaned_data and f.cleaned_data['file']:
                            documentos_requeridos.objects.create(id_registro=registro, **f.cleaned_data)

                    productos_servicios_condiciones.objects.create(id_registro=registro, **formularios[8].cleaned_data)
                    declaracion.objects.create(id_registro=registro, **formularios[9].cleaned_data)
                    homologacion.objects.create(id_registro=registro)

                    messages.success(request, '¡Registro exitoso! Ya puedes ver tu perfil.')
                    return redirect('users:profile')

            else:
                text = "Error al registrar el formulario, por favor intente nuevamente"
                url = reverse('users:signup')
                errores_form = [f.errors for f in formularios if f.errors]
                error = f"Error en el formulario: {errores_form}"
                return render(request, "error.html", {'texto': text, 'url': url, 'error': error})

        except Exception as e:
            text = "Error al registrar el formulario, por favor revise bien los datos e intente nuevamente"
            url = reverse('users:signup')
            print(e)
            return render(request, "error.html", {'texto': text, 'url': url, 'error': e})

    return render(request, "users/register/signup.html", {
        'seccion1': seccion1, 'seccion2': seccion2, 'seccion3': seccion3,
        'seccion4': seccion4, 'seccion5': seccion5, 'seccion6': seccion6,
        'seccion7': seccion7, 'seccion8': seccion8, 'seccion9': seccion9
    })

#Funcion para mostrarv la actividad economica en el formulario
def actividad_economica(request):
    codigo = request.GET.get('ciiu', None)
    if codigo:
        try:
            actividad = actividad_eco_clase.objects.get(codigo=codigo)
            act_data = serializers.serialize('json', [actividad,])
            return JsonResponse({'actividad': act_data}, status=200)
            
        except actividad_eco_clase.DoesNotExist:
            return JsonResponse({'error': 'Actividad no encontrada'}, status=404)
    else:
        return JsonResponse({'error': 'Código no Proporcionado'}, status=400)

#Función para traer los municipios de la base de datos
def get_municipios(request):
    departamento_id = request.GET.get('departamento_id', None)
    if departamento_id:
        municipios = Municipio.objects.filter(departamento_id_id=departamento_id).order_by('nombre')
        mun_data = serializers.serialize('json', municipios)
        return JsonResponse({'municipios': mun_data}, status=200)
    else:
        return JsonResponse({'error': 'Departamento no proporcionado'}, status=400)

#Función para iniciar sesion
def login_(request):
    if request.user.is_authenticated and request.user.groups.filter(name='Proveedor').exists():
        return redirect('proveedor:dashboard')
    elif request.user.is_authenticated and request.user.groups.filter(name='compras').exists():
        return redirect('compras:dashboard')
    
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    if not user.is_active:
                        messages.error(request, 'Usuario inactivo.')
                        return render(request, 'users/register/login.html', {'form': form})
                    
                    login(request, user)

                    if user.groups.filter(name='Proveedor').exists():
                        return redirect('proveedor:dashboard')
                    elif user.groups.filter(name='compras').exists():
                        return redirect('compras:dashboard')
                    elif user.is_superuser:
                        return redirect('/admin/')
                    else:
                        messages.error(request, 'Tu cuenta aún no tiene un rol asignado.')
                        return render(request, 'users/register/login.html', {'form': form})
                else:
                    messages.error(request, 'Usuario o contraseña incorrectos.')
            except User.DoesNotExist:
                messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'users/register/login.html', {'form': form})

#Función para cerrar sesión
def logout_(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # con esto los marcas como "leídos"
    logout(request)
    return redirect('users:login')

#Función para ver el perfil del proveedor
def profile(request):
    registro = registro_formulario.objects.filter(usuario=request.user).first()
    
    if not registro:
        messages.warning(request, 'Aun no tienes datos registrados como proveedor.')
        return redirect('users:signup') 

    if request.method == 'POST':
        form = PerfilProveedorForm(request.POST, request.FILES, instance=registro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Los cambios fueron guardados correctamente')
            return redirect('users:profile')
        else:
            messages.error(request, 'Error al guardar los cambios. Por favor, corrige los errores.')
    else:
        form = PerfilProveedorForm(instance=registro)

    # Cargar documentos asociados al proveedor
    docs = documentos_requeridos.objects.filter(id_registro=registro)
    certs = certificaciones_proveedores.objects.filter(id_registro=registro)

    return render(request, 'users/profile/profile.html', {
        'form': form,
        'registro': registro,
        'documentos': docs,
        'certificaciones': certs,
    })