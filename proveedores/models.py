from math import e
from sys import api_version
from django.db import models
from users.models import Departamento, Municipio
from compras.models import *
from django.contrib.auth.models import User

# Create your models here.
class plazos(models.Model):
    id = models.AutoField(primary_key=True)
    valor = models.IntegerField()
    descripcion = models.CharField(max_length=100)
    
    def __str__(self):
        return self.descripcion

def id_documentos_directory_path(instance, filename):
    id_registro = instance.id_registro.identificador
    return f'{id_registro}/Documentos/{filename}' 

def id_solicitudes_directory_path(instance, filename):
    id_registro = instance.id_homologacion.id_registro.identificador
    return f'{id_registro}/Solicitudes/{filename}' 

def id_propuestas_directory_path(instance, filename):
    id_sol = instance.id_solicitud.identificador
    return f'{id_sol}/Propuestas/{filename}'

def id_declaracion_directory_path(instance, filename):
    id_registro = instance.id_registro.identificador
    return f'{id_registro}/Declaracion/{filename}' 
class actividad_eco_seccion(models.Model):
    codigo = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=180)

    def __str__(self):
        return (self.codigo + " - " + self.descripcion)

class actividad_eco_division(models.Model):
    codigo = models.CharField(max_length=5, primary_key=True)
    descripcion = models.CharField(max_length=230)
    seccion = models.ForeignKey(actividad_eco_seccion, on_delete=models.CASCADE)

    def __str__(self):
        return (self.codigo + " - " + self.descripcion)

class actividad_eco_grupo(models.Model):
    codigo= models.CharField(max_length=4, primary_key=True)
    descripcion = models.CharField(max_length=300)
    division = models.ForeignKey(actividad_eco_division, on_delete=models.CASCADE)

    def __str__(self):
        return (self.codigo + " - " + self.descripcion)   

class  actividad_eco_clase(models.Model):
    codigo = models.CharField(max_length=5, primary_key=True)
    descripcion = models.CharField(max_length=300)
    grupo = models.ForeignKey(actividad_eco_grupo, on_delete=models.CASCADE)

    def __str__(self):
        return (self.codigo + " - " + self.descripcion)    

class tipo_persona(models.Model):
    codigo = models.CharField(max_length=5, primary_key=True)
    descripcion = models.CharField(max_length=300)

    def __str__(self):
        return (self.descripcion)
    
class tipo_identificacion(models.Model):
    codigo = models.CharField(max_length=5, primary_key=True)
    descripcion = models.CharField(max_length=300)

    def __str__(self):
        return (self.descripcion)

class tipo_contribuyente(models.Model):
    codigo = models.CharField(max_length=5, primary_key=True)
    descripcion = models.CharField(max_length=300)

    def __str__(self):
        return (self.descripcion)   
    
class registro_formulario(models.Model):
    id_registro = models.AutoField(primary_key=True)
    identificador = models.CharField(max_length=12)
    tipo_persona = models.CharField(max_length=10)
    tipo_proveedor = models.CharField(max_length=20)
    dian = models.CharField(max_length=2)
    razon_social = models.CharField(max_length=300)
    sigla = models.CharField(max_length=100)
    matricula_mercantil = models.CharField(max_length=100)
    tipo_documento = models.CharField(max_length=3)
    documento = models.CharField(max_length=20)
    dv = models.CharField(max_length=2)
    ciiu = models.ForeignKey(actividad_eco_clase, on_delete=models.CASCADE, )
    direccion = models.CharField(max_length=300)
    telefono = models.CharField(max_length=20)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    email  = models.CharField(max_length=100)
    representante_legal = models.CharField(max_length=150)
    identificacion_representante = models.CharField(max_length=20, null=True)
    pertenece_grupo = models.CharField(max_length=2, null=True)
    nombre_grupo = models.CharField(max_length=300, null=True)
    tiene_trabajo_figura_publica = models.CharField(max_length=2, null=True)
    nombre_trabajo_figura_publica = models.CharField(max_length=150, null=True)
    cargo_trabajo_figura_publica = models.CharField(max_length=150, null=True)  
    responsabilidad_social = models.BooleanField()
    evidencia_RS = models.FileField(upload_to=id_documentos_directory_path, null=True)
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            last = registro_formulario.objects.all().last()
            if not  last:
                self.identificador = 'REG000001'                
            else:
                last =  last.identificador
                num = int(last[3:])
                new_num = num + 1
                new_id = 'REG' + str(new_num).zfill(6)
                self.identificador = new_id
            super().save(*args, **kwargs)

class info_financiera(models.Model):
    id = models.AutoField(primary_key=True)
    id_registro = models.ForeignKey(registro_formulario, on_delete=models.CASCADE)
    total_pasivos = models.CharField(max_length=100)
    total_activos = models.CharField(max_length=100)
    patrimonio = models.CharField(max_length=100)
    ingresos_mensuales = models.CharField(max_length=100)
    egresos_mensuales = models.CharField(max_length=100)
    otros_ingresos = models.CharField(max_length=100)
    otros_egresos = models.CharField(max_length=100)
    ventas_anuales = models.CharField(max_length=100)
    tipo_empresa = models.CharField(max_length=100)
    otro_tipo_empresa = models.CharField(max_length=100)
    num_empleados = models.CharField(max_length=100)
    

class composicion_accionaria(models.Model):
    id = models.AutoField(primary_key=True)
    id_registro = models.ForeignKey(registro_formulario, on_delete=models.CASCADE)
    nombre_razon_social = models.CharField(max_length=300)
    tipo_identificacion = models.CharField(max_length=2)
    identificacion = models.CharField(max_length=11)
    porcentaje = models.CharField(max_length=3)
    
    
def id_certificacion_directory_path(instance, filename):
    # Aquí se obtiene el id del registro
    id_registro = instance.id_registro.id_registro
    # Se construye la ruta completa
    return f'{id_registro}/certificaciones/{filename}' 

class familias(models.Model):
    id = models.AutoField(primary_key=True)
    nombre =  models.CharField(max_length=50)  
          
    def __str__(self):
        return self.nombre
     

class matriz_doc(models.Model):
    id = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=3)
    nombre = models.CharField(max_length=300)
    
class FamiliaDocumento(models.Model):
    OBLIGATORIEDAD_CHOICES = [
        ('', 'No especificado'),
        ('x', 'Obligatorio'),
        ('*', 'Para el caso de los proveedores de servicios en Seguridad y Salud y Medio Ambiente se solicitará esta documentación si el proveedor no es enviado por ARL.'),
        ('**', 'Se solicitará afiliación a la seguridad social cuando los servicios se presten en obra o en las instalaciones de FEPCO ZONA FRANCA S.A.S.'),
        ('***', 'En caso de que el Subcontratista no posea esta documentación se acogerá a la establecida por FEPCO ZONA FRANCA S.A.S.'),
        ('****', 'El proveedor y/o contratista NO está obligado a suministrar dichas certificaciones, pero si cuenta con ellas se tendrá en cuenta para su evaluación, en el criterio de calificación extra de Responsabilidad Social Empresarial.'),
    ]

    familia = models.ForeignKey(familias, on_delete=models.CASCADE)
    documento = models.ForeignKey(matriz_doc, on_delete=models.CASCADE)
    obligatoriedad = models.CharField(max_length=4, choices=OBLIGATORIEDAD_CHOICES, default='')
        
class certificaciones_proveedores(models.Model):
    id = models.AutoField(primary_key=True)
    id_registro = models.ForeignKey(registro_formulario, on_delete=models.CASCADE)
    certificacion = models.ForeignKey(matriz_doc, on_delete=models.CASCADE)
    fecha = models.DateField(null=True)
    numero_certificacion = models.CharField(max_length=300)
    file = models.FileField(upload_to=id_certificacion_directory_path, null=True)


class documentos_requeridos(models.Model):
    id = models.AutoField(primary_key=True)
    id_registro = models.ForeignKey(registro_formulario, on_delete=models.CASCADE)
    documento = models.ForeignKey(matriz_doc, on_delete=models.CASCADE)
    file = models.FileField(upload_to=id_documentos_directory_path, null=True)
    
    
class info_tributaria(models.Model):
    id = models.AutoField(primary_key=True)
    id_registro = models.ForeignKey(registro_formulario, on_delete=models.CASCADE)
    regimen = models.CharField(max_length=50)
    responsable_iva = models.CharField(max_length=2)
    contribuyente_impuesto_renta = models.CharField(max_length=2)
    responsable_ica = models.CharField(max_length=2)
    codigo_actividad_economica_p = models.ForeignKey(actividad_eco_clase, on_delete=models.CASCADE, related_name='codigo_actividad_p', null=True)
    codigo_actividad_economica_s = models.ForeignKey(actividad_eco_clase, on_delete=models.CASCADE, related_name='codigo_actividad_s', null=True)
    
        
class resolucion(models.Model):
    id = models.AutoField(primary_key=True)
    id_trib = models.ForeignKey(info_tributaria, on_delete=models.CASCADE)
    Tcontribuyente = models.ForeignKey(tipo_contribuyente, on_delete=models.CASCADE)
    fecha = models.DateField(null=True)
    resolucion = models.CharField(max_length=300, null=True)
    

class info_pago(models.Model):
    id = models.AutoField(primary_key=True)
    id_registro = models.ForeignKey(registro_formulario, on_delete=models.CASCADE)
    nombre_contable = models.CharField(max_length=100)
    apellido_contable = models.CharField(max_length=100)
    cargo_contable = models.CharField(max_length=100)
    telefono_contable = models.CharField(max_length=30)
    email_contable = models.CharField(max_length=150)
    direccion_contable = models.CharField(max_length=150)
    municipio_contable = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    departamento_contable = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    

    
class productos_servicios_condiciones(models.Model):
    id = models.AutoField(primary_key=True)
    id_registro = models.ForeignKey(registro_formulario, on_delete=models.CASCADE)
    credito = models.CharField(max_length=2)
    plazo = models.ForeignKey(plazos, on_delete=models.CASCADE)
    forma_pago = models.CharField(max_length=25)
    periodo_consignacion = models.CharField(max_length=100)
    describa_productos = models.CharField(max_length=300)
    
class declaracion(models.Model):
    id = models.AutoField(primary_key=True)
    id_registro = models.ForeignKey(registro_formulario, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    file = models.FileField(upload_to=id_declaracion_directory_path)
    
    
class homologacion(models.Model):
    id = models.AutoField(primary_key=True)
    id_registro = models.ForeignKey(registro_formulario, on_delete=models.CASCADE)
    familia = models.ForeignKey(familias, on_delete=models.CASCADE, null = True)
    usuario_hologa = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
    estado = models.CharField(max_length=10)
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            self.estado = 'Pendiente'
        super().save(*args, **kwargs)
     
class aprobacion_doc(models.Model):
    documento = models.ForeignKey(documentos_requeridos, on_delete=models.CASCADE, null=True)
    certificados = models.ForeignKey(certificaciones_proveedores, on_delete=models.CASCADE, null=True)
    tipo = models.CharField(max_length=4)
    fecha_apr = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null = True)
    aprobado= models.BooleanField()
    descripcion = models.CharField(max_length=300)
    
    
class evaluacion_inicial(models.Model):
    calidad = models.IntegerField()
    descripcion_c= models.CharField(max_length=300)
    experiencia= models.IntegerField()
    descripcion_e = models.CharField(max_length=300)
    pago= models.ForeignKey(plazos, on_delete=models.CASCADE)
    descripcion_p = models.CharField(max_length=300)
    martriz=models.IntegerField()
    descripcion_m=models.CharField(max_length=300)
    oea=models.IntegerField()
    descripcion_o=models.CharField(max_length=300)
    validacion=models.IntegerField()
    descripcion_v=models.CharField(max_length=300)
    extra = models.IntegerField()
    descripcion_ex=models.CharField(max_length=300)
    id_registro = models.ForeignKey(registro_formulario, on_delete=models.CASCADE)
    
    
class propuestas_sol(models.Model):
    id = models.AutoField(primary_key=True)
    id_homologacion = models.ForeignKey(homologacion, on_delete=models.CASCADE)
    id_solicitud = models.ForeignKey(solicitud, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    file = models.FileField(upload_to=id_solicitudes_directory_path)
    descripcion = models.CharField(max_length=300)
    valor_t = models.FloatField()
    garantia = models.CharField(max_length=300)
    moneda = models.CharField(max_length=3)
    tiempo_entrega_min = models.IntegerField(help_text="Ingrese el tiempo mínimo de entrega en días.")
    tiempo_entrega_max = models.IntegerField(null=True, blank=True, help_text="Ingrese el tiempo máximo de entrega en días (opcional).")
    t_pago = models.CharField(max_length=50)
    validez = models.IntegerField(null=True, blank=True)
    conteo = models.IntegerField()
    
    def save(self, *args, **kwargs):
        ultimo = propuestas_sol.objects.filter(id=self.id, id_homologacion=self.id_homologacion ).last()
        if not ultimo:
            self.conteo = 1
        else:
            self.conteo = ultimo.conteo + 1
            
class TipoTarea(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
class Tarea(models.Model):
    tipo = models.ForeignKey(TipoTarea, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    hecha = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_vencimiento = models.DateTimeField()
    datos_adicionales = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.tipo.nombre} - {'Hecha' if self.hecha else 'No hecha'}"
    
    def save(self, *args, **kwargs):
        if self.tipo.id == 1:
            self.titulo = "Carga de documento"
        elif self.tipo.id == 2:
            self.titulo = "Presentar evaluacion"  
    
    
    
    