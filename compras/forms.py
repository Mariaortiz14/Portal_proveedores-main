from logging import PlaceHolder
from mimetypes import init
from pydoc import doc
import re
from django import contrib, forms
from django.forms import formset_factory
from datetime import date
from django.contrib.auth.models import User
from .models import *
from proveedores.models import plazos, familias
from django import forms
from .models import solicitud

class SolicitudForm(forms.ModelForm):
    class Meta:
        model = solicitud
        fields = ['descripcion', 'observaciones', 'estado']

class Evaluacion_inicial(forms.Form):
    option_calidad={
        ('', 'Selecciona una opción'),
        (20, 'Esta certificado en un sistema de gestión de calidad'),
        (10, 'Posee un sistema de gestión de calidad el cual no se encuentra certificado.'),
        (5, 'Posee procedimientos internos alineados bajo los estándares de FEPCO Zona Franca SAS.'),
        (0, 'No posee sistema de gestión ni procedimientos internos.')
    }
    
    option_experiencia={
        ('', 'Selecciona una opción'),
        (20, 'Entre 10 - 14 años'),
        (10, 'Entre 5 - 9 años'),
        (5, 'Entre 1 - 4 años'),
        (0, 'Menos de 1 año')
    }
    
    option_matriz={
        ('', 'Selecciona una opción'),
        (40, 'El proveedor anexo toda la documentación solicitada en la MATRIZ PARA SELECCIÓN DE PROVEEDORES DE SSTA (M-E-01)'),
        (20, 'El proveedor anexo parte de la documentación solicitada en la MATRIZ PARA SELECCIÓN DE PROVEEDORES DE SSTA (M-E-01)'),
        (0, 'El proveedor no anexo la documentación solicitada en la MATRIZ PARA SELECCIÓN DE PROVEEDORES DE SSTA (M-E-01)')
    }
    
    option_extra={
        ('', 'Selecciona una opción'),
        (5, 'El proveedor SÍ realiza prácticas de Responsabilidad Social Empresarial con sus grupos de interés.'),
        (0, 'El proveedor NO realiza prácticas de Responsabilidad Social Empresarial con sus grupos de interés.')
    }
   
    s_calidad = forms.ChoiceField(choices=option_calidad, initial=None ,widget=forms.Select(attrs={'class': 'form-control '}))
    descripcion_s = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control ', 'rows': 1, 'placeholder': 'Descripción'}))
    experiencia= forms.ChoiceField(choices=option_experiencia, initial=None, widget=forms.Select(attrs={'class': 'form-control '}))
    descripcion_e = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control ', 'rows': 1, 'placeholder': 'Descripción'}))
    forma_pago= forms.ModelChoiceField(queryset=plazos.objects.all(), initial=None, widget=forms.Select(attrs={'class': 'form-control '}))
    descripcion_f= forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control ', 'rows': 1, 'placeholder': 'Descripción'}))
    matriz= forms.ChoiceField(choices=option_matriz, initial=None, widget=forms.Select(attrs={'class': 'form-control '}))
    descripcion_m= forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control ', 'rows': 1, 'placeholder': 'Descripción'}))
    oea= forms.BooleanField(required=False)
    descripcion_o = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control ', 'rows': 1, 'placeholder': 'Descripción'}))
    validacion= forms.BooleanField(required=False)
    descripcion_v= forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control ', 'rows': 1, 'placeholder': 'Descripción'}))
    extra= forms.ChoiceField(choices=option_extra, initial=None, widget=forms.Select(attrs={'class': 'form-control '}))
    descripcion_ex= forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control ', 'rows': 1, 'placeholder': 'Descripción'}))
    
    
class caracteristicas(forms.Form):
    caracteristica= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'Característica'}))
    
    
class crear_solicitud(forms.Form):
    solicitud= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'Solicitud'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control ', 'rows': 4, 'placeholder': 'Descripción'}))
    carasteristicas= formset_factory(caracteristicas, extra=1)
    familia = forms.ModelChoiceField(queryset=familias.objects.all(), widget=forms.Select(attrs={'class': 'form-control '}))
    cantidad = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control ', 'placeholder': 'Cantidad'}))
    
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = comentarios
        fields = ['comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'class': 'form-control ','rows': 3, 'placeholder': 'Escribe un comentario...'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        # Omite la validación de los campos 'solicitud' y 'usuario'
        cleaned_data.pop('solicitud', None)
        cleaned_data.pop('usuario', None)
        return cleaned_data