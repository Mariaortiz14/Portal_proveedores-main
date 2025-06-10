from email.mime import message
import re
from datetime import date, datetime, time
from logging import info
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import render, redirect
from .forms import *
from .models import *
from proveedores.models import *
from django.core import serializers
from django.utils.html import escape
from django import forms
from django.urls import reverse
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


def signup(request):   
    seccion1 = ProveedorForm_(request.POST or None , prefix='seccion1')
    ca = forms.formset_factory(composicion_accionaria_ , extra=1, max_num=8)
    seccion2 = ca(request.POST or None, prefix='seccion2')
    seccion3 = informacion_financiera_(request.POST or None, prefix='seccion3')
    seccion4 = informacion_tributaria_(request.POST or None, prefix='seccion4')
    resolucion_formset = seccion4.resolucionT(request.POST or None, prefix='seccion4', initial=[{'Tcontribuyente': 'T03'}, {'Tcontribuyente': 'T04'}])
    seccion5 = informacion_pagos_contable_(request.POST or None, prefix='seccion5')
    certificados = forms.formset_factory(certificacion_ or None, extra=8, max_num=8)
    seccion6 = certificados(request.POST or None, request.FILES or None, initial=[{'certificacion': 20,'nombre': 'ISO 28000' }, {'certificacion': 21,'nombre': 'ISO 27000'}, {'certificacion': 22,'nombre': 'API'}, {'certificacion': 23,'nombre': 'OHSAS 18001'}, {'certificacion': 2,'nombre': 'ISO 14000'}, {'certificacion': 1,'nombre': 'ISO 9001'}, {'certificacion': 19,'nombre': 'RUC'}, {'certificacion': 24,'nombre': 'OEA'}], prefix='seccion6')
    doc = forms.formset_factory(documentos_requeridos_, extra=1, max_num=8)
    seccion7 = doc(request.POST or None, request.FILES or None,initial=[{'documento':26}, {'documento': 27}, {'documento':28},{'documento':29}, {'documento':30}, {'documento':31}, {'documento':46},{'documento':33},{'documento':32}], prefix='seccion7')
    seccion8 = condiciones_pago_catalogo_(request.POST or None, request.FILES or None, prefix='seccion8')
    seccion9 = declaracion_(request.POST or None, request.FILES or None, prefix='seccion9')
    if request.method == "POST":
        try:
            formularios = [seccion1, seccion2, seccion3, seccion4, resolucion_formset, seccion5, seccion6, seccion7, seccion8, seccion9]
            if all(formulario.is_valid() for formulario in formularios):
                with transaction.atomic():
                    registro = registro_formulario.objects.create(**formularios[0].cleaned_data)
                    for f in formularios[1]:
                        if f.cleaned_data and f.cleaned_data['tipo_identificacion']!=None:
                            composicion_accionaria.objects.create(id_registro=registro, **f.cleaned_data)
                    info_financiera.objects.create(id_registro=registro, **formularios[2].cleaned_data)
                    cleaned_data = formularios[3].cleaned_data.copy() 
                    Tcontribuyente = cleaned_data['tipo_contribuyente']
                    cleaned_data.pop('tipo_contribuyente')
                    tribu= info_tributaria.objects.create(id_registro=registro, **cleaned_data)
                    for data in Tcontribuyente:
                        if data.codigo!='T03' and data.codigo!='T04':
                            resolucion.objects.create(id_trib=tribu, Tcontribuyente=data)
                        else:
                            for f in formularios[4]:
                                
                                if f.cleaned_data and f.cleaned_data['Tcontribuyente'] != None:
                                    resolucion.objects.create(id_trib=tribu, **f.cleaned_data)
                    info_pago.objects.create(id_registro=registro, **formularios[5].cleaned_data)
                    for f in formularios[6]:
                        if f.cleaned_data and f.cleaned_data['file'] != None:
                            f.cleaned_data.pop('nombre')
                            certificaciones_proveedores.objects.create(id_registro=registro, **f.cleaned_data)
                    for f in formularios[7]:
                        if f.cleaned_data and f.cleaned_data['file'] != None:
                            print(f.cleaned_data)
                            documentos_requeridos.objects.create(id_registro=registro, **f.cleaned_data) 
                        
                    productos_servicios_condiciones.objects.create(id_registro=registro, **formularios[8].cleaned_data)    
                    declaracion.objects.create(id_registro=registro, **formularios[9].cleaned_data)
                    homologacion.objects.create(id_registro=registro)
            else: 
                text = "Error al registrar el formulario, por favor intente nuevamente."
                url = reverse('users:signup')
                errores_form = [f.errors for f in formularios if f.errors]
                error = f"Error en el formulario: {errores_form}"
                return render(request, "error.html", {'texto': text, 'url': url, 'error': error})
            
        except Exception as e:
            text = "Error al registrar el formulario, por favor intente nuevamente."
            url = reverse('users:signup')
            print(e)
            return render(request, "error.html", {'texto': text, 'url': url, 'error': e})
         
    return render(request, "users/register/signup.html", {'seccion1': seccion1, 'seccion2': seccion2, 'seccion3': seccion3, 
                                                    'seccion4': seccion4, 'seccion5': seccion5, 'seccion6': seccion6, 
                                                    'seccion7': seccion7, 'seccion8': seccion8, 'seccion9': seccion9})

def actividad_economica(request):
    codigo = request.GET.get('ciiu', None)
    if codigo:
        try:
            actividad = actividad_eco_clase.objects.get(codigo=codigo)
            act_data = serializers.serialize('json', [actividad,])
            return JsonResponse({'actividad': act_data}, status=200)
            
        except actividad_eco_clase.DoesNotExist:
            return JsonResponse({'error': 'Actividad no Encontrada '}, status=404)
    else:
        return JsonResponse({'error': 'Código no Proporcionado'}, status=400)

def get_municipios(request):
    departamento_id = request.GET.get('departamento_id', None)
    if departamento_id:
        municipios = Municipio.objects.filter(departamento_id_id=departamento_id).order_by('nombre')
        mun_data = serializers.serialize('json', municipios)
        return JsonResponse({'municipios': mun_data}, status=200)
    else:
        return JsonResponse({'error': 'Departamento no proporcionado'}, status=400)

def login_(request):
    if request.user.is_authenticated and request.user.groups.filter(name='Proveedor').exists():
        return redirect('proveedor:dashboard')
    elif request.user.is_authenticated and request.user.groups.filter(name='compras').exists():
        return redirect('compras:dashboard')
  
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if User.objects.filter(username=user).exists():
                user = User.objects.get(username=user)
                if user.check_password(password):
                    login(request, user)
                    if user.groups.filter(name='Proveedor').exists():
                        return redirect('proveedor:dashboard')
                    elif user.groups.filter(name='compras').exists():
                        return redirect('compras:dashboard')
                    
                else:
                    messages.error(request, 'Usuario o contraseña incorrectos')
                    return render(request, 'users/register/login.html', {'form': form})
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
                return render(request, 'users/register/login.html', {'form': form})
    
    
    return render(request, 'users/register/login.html', {'form': form})


def logout_(request):
    logout(request)
    return redirect('users:login')

def profile(request):
    
    return render(request, 'users/profile/profile.html')
