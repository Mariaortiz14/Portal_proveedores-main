from proveedores.models import actividad_eco_clase, matriz_doc, tipo_contribuyente, plazos, propuestas_sol,registro_formulario
from django.contrib.auth.models import User
from .models import Departamento, Municipio
from django.forms import formset_factory
from django import contrib, forms
from mimetypes import init
from datetime import date
from pydoc import doc
import re

#Clase para el formulario del proveedor
class ProveedorForm_(forms.Form):
    tipo_persona = forms.ChoiceField(choices=[('', 'Seleccione uno'),('Natural', 'Natural'), ('Jurídica', 'Jurídica')], initial=None ,widget=forms.Select(attrs={'class': 'form-control '}))
    tipo_proveedor = forms.ChoiceField(choices=[('', 'Seleccione uno'),('Fabricante', 'Fabricante'), ('Comercializador', 'Comercializador')], initial=None ,widget=forms.Select(attrs={'class': 'form-control'}))
    dian= forms.ChoiceField(choices=[('', 'Seleccione uno'),('S', 'Si'), ('N', 'No')], widget=forms.Select(attrs={'class': 'form-control'}))
    razon_social = forms.CharField(max_length=300, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sigla = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    matricula_mercantil = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipo_documento = forms.ChoiceField(choices=[('', 'Seleccione uno'),('CC', 'Cédula de Ciudadanía'), ('CE', 'Cédula de Extranjería'), ('NIT', 'NIT')],initial=None, widget=forms.Select(attrs={'class': 'form-control'}))
    documento = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control' ,'type':'number','min': '0','onfocusout':'codigo_dv()'}))
    dv = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control','readonly': 'true' }))
    ciiu= forms.ModelChoiceField(queryset=actividad_eco_clase.objects.all(), widget=forms.Select(attrs={'class': 'form-control select2'})) 
    direccion= forms.CharField(max_length=100, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':'4'}))
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(),empty_label="Seleccione un Departamento", widget=forms.Select(attrs={'class': 'form-select single select2'}))
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all(), widget=forms.Select(attrs={'class': 'form-select single select2 '}))
    telefono = forms.CharField(max_length=10,widget=forms.TextInput(attrs={'class': 'form-control','type': 'number','pattern': '[0-9]{10}','min': '1000000000','max': '9999999999',}))
    email = forms.EmailField( widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'email'}))
    representante_legal = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    identificacion_representante = forms.CharField(max_length=12, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0'}))
    pertenece_grupo = forms.ChoiceField(choices=[('', 'Seleccione uno'),('S', 'Si'), ('N', 'No')], widget=forms.Select(attrs={'class': 'form-control'}))
    nombre_grupo = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    tiene_trabajo_figura_publica = forms.ChoiceField(choices=[('', 'Seleccione uno'),('S', 'Si'), ('N', 'No')], widget=forms.Select(attrs={'class': 'form-control'}))
    nombre_trabajo_figura_publica = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    cargo_trabajo_figura_publica = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    responsabilidad_social = forms.ChoiceField(choices=[('', 'Seleccione uno'),('True', 'Si'), ('False', 'No')], widget=forms.Select(attrs={'class': 'form-control'}))
    evidencia_RS = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}),required=False  )

#Clase de composicion de acciones 
class composicion_accionaria_(forms.Form):
    nombre_razon_social = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), required=False )
    tipo_identificacion = forms.ChoiceField(choices=[('', 'Seleccione uno'),('CC', 'Cédula de Ciudadanía'), ('CE', 'Cédula de Extranjería'), ('NIT', 'NIT')], widget=forms.Select(attrs={'class': 'form-control'}),  required=False)
    identificacion = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control','min':'0'}),  required=False)
    porcentaje = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'type':'number', 'min':'5', 'step': '0.1' , 'max':'100', 'onfocusout':'if(this.value>100){this.value="100";}else if(this.value<5){this.value="5";}'}),  required=False)

#Clse de información financiera
class informacion_financiera_(forms.Form):
    total_pasivos = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'type':'number','min':'0'}))
    total_activos = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'type':'number','min':'0'}))
    patrimonio = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'type':'number','min':'0'}))
    ingresos_mensuales = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control',  'type':'number','min':'0'}))
    egresos_mensuales = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control',  'type':'number','min':'0'}) )
    otros_ingresos = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control',  'type':'number','min':'0'}))
    otros_egresos = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class': 'form-control',  'type':'number','min':'0'}))
    ventas_anuales = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'type':'number','min':'0'}))
    tipo_empresa = forms.ChoiceField(choices=[('', 'Seleccione uno'),('publica', 'Pública'), ('privada', 'Privada'), ('mixta', 'Mixta'), ('otra', 'Otra')], widget=forms.Select(attrs={'class': 'form-control'}) )
    otro_tipo_empresa = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    num_empleados = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control',  'type':'number','min':'0'}))

#Clase para la resolución
class resolucion_(forms.Form):
    resolucion = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control hidden'}), required=False)
    fecha = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control hidden', 'type':'date'}), required=False)
    Tcontribuyente = forms.ModelChoiceField(queryset=tipo_contribuyente.objects.all(), widget=forms.Select(attrs={'class': 'form-control hidden'}), required=False)

#Clase para la información tributaria
class informacion_tributaria_(forms.Form):
    tipo_contribuyente = forms.ModelMultipleChoiceField(queryset=tipo_contribuyente.objects.all(),widget=forms.SelectMultiple(attrs={'class': 'form-control js-contribuyente-basic-multiple', 'multiple':'multiple', 'data-placeholder': 'Seleccione uno'}))
    resolucionT= forms.formset_factory(resolucion_, extra=2, max_num=2)
    resolucion = resolucionT(initial=[{'Tcontribuyente': 'T03'}, {'Tcontribuyente': 'T04'}], prefix="seccion4")
    regimen = forms.ChoiceField(choices=[('', 'Seleccione uno'),('comun', 'Común'), ('simplificado', 'Simplificado')], widget=forms.Select(attrs={'class': 'form-control'}) )
    responsable_iva = forms.ChoiceField(choices=[('', 'Seleccione uno'),('S', 'Si'), ('N', 'No')], widget=forms.Select(attrs={'class': 'form-control'}) )
    contribuyente_impuesto_renta = forms.ChoiceField(choices=[('', 'Seleccione uno'),('S', 'Si'), ('N', 'No')], widget=forms.Select(attrs={'class': 'form-control'}) )
    responsable_ica = forms.ChoiceField(choices=[('', 'Seleccione uno'),('S', 'Si'), ('N', 'No')], widget=forms.Select(attrs={'class': 'form-control'}) )
    codigo_actividad_economica_p = forms.ModelChoiceField(queryset=actividad_eco_clase.objects.all(), widget=forms.Select(attrs={'class': 'form-control select2'}))
    codigo_actividad_economica_s = forms.ModelChoiceField(queryset=actividad_eco_clase.objects.all(), widget=forms.Select(attrs={'class': 'form-control select2'}), required=False)

#Clase de información de pagis contables
class informacion_pagos_contable_(forms.Form):
    nombre_contable = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido_contable = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    cargo_contable = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono_contable = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email_contable = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion_contable = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':'4'}))
    municipio_contable = forms.ModelChoiceField(queryset=Municipio.objects.all(), widget=forms.Select(attrs={'class': 'form-control select2'}))
    departamento_contable = forms.ModelChoiceField(queryset=Departamento.objects.all(), widget=forms.Select(attrs={'class': 'form-control select2'}))

#Clase para la certificación de la empresa
class certificacion_(forms.Form):
    nombre= forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control','disabled': 'disabled'}), required=False)
    certificacion = forms.ModelChoiceField(queryset=matriz_doc.objects.all(), widget=forms.HiddenInput())
    numero_certificacion = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)
    fecha = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type':'date', 'min':'2000-01-01', 'max':'2030-12-31'}),required=False)
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=False )

#Clase de los documentos requeridos para la creación de los registros
class documentos_requeridos_(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=False) 
    documento = forms.ModelChoiceField(queryset=matriz_doc.objects.all(), widget=forms.HiddenInput())
    
#Clase de las condiciones de pago
class condiciones_pago_catalogo_(forms.Form):
    credito = forms.ChoiceField(choices=[('', 'Seleccione uno'),('S', 'Si'), ('N', 'No')], widget=forms.Select(attrs={'class': 'form-control'}))
    plazo = forms.ModelChoiceField(queryset=plazos.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    forma_pago = forms.ChoiceField(choices=[('', 'Seleccione uno'),('contado', 'Contado'), ('consignación', 'Consignación')], widget=forms.Select(attrs={'class': 'form-control'}))
    periodo_consignacion = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    describa_productos = forms.CharField(max_length=300, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':'4', 'placeholder': 'Describa los productos que ofrece'}))

#Clase de la declaracion de la empresa
class declaracion_(forms.Form):
    fecha = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1999-01-01', 'max': '2040-12-31'}),initial=date.today().strftime('%Y-%m-%d'),disabled=True)
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))

#Clase para el inicio del formulario de registro  
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control form-control-user', 'placeholder':'Usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-user', 'placeholder':'Contraseña'}) )
    
    class Meta:
        model = User
        fields = ['username', 'password']

#Clase para el perfil del proveedor
class PerfilProveedorForm(forms.ModelForm):
    class Meta:
        model = registro_formulario
        fields = ['razon_social', 'documento', 'email', 'telefono', 'direccion','foto']
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }