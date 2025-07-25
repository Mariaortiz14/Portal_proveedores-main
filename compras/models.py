from django.contrib.auth.models import User
from django.db import models
from django.apps import apps
from turtle import mode

# Clase de la tabla de los proveedores
class solicitud(models.Model):
    id = models.AutoField(primary_key=True)
    identificador = models.CharField(max_length=12, unique=True)
    TSolicitud = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=400)
    cantidad = models.IntegerField()
    familia = models.ForeignKey('proveedores.familias', on_delete=models.CASCADE)
    estado = models.CharField(max_length=50)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_final = models.DateField(null=True)
    observaciones = models.CharField(max_length=400)

    def save(self, *args, **kwargs):
        if self._state.adding and not self.identificador:
            last = self.__class__.objects.order_by('-id').first()
            if not last:
                new_id = 'SOL000001'
            else:
                last_num = int(last.identificador[3:])
                new_num = last_num + 1
                new_id = 'SOL' + str(new_num).zfill(6)

            while self.__class__.objects.filter(identificador=new_id).exists():
                new_num += 1
                new_id = 'SOL' + str(new_num).zfill(6)

            self.identificador = new_id

        super(solicitud, self).save(*args, **kwargs)

# Clase de la caracteristica de la solicitud
class caracteristicas_solicitud(models.Model):
    id = models.AutoField(primary_key=True)
    solicitud = models.ForeignKey(solicitud, on_delete=models.CASCADE)
    caracteristica = models.CharField(max_length=100)
    
    def __str__(self):
        return self.caracteristica
    
#Clase de los comentarios de la solicitud       
class comentarios(models.Model):
    homologacion = models.ForeignKey('proveedores.homologacion', null=True, blank=True, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    solicitud = models.ForeignKey(solicitud, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=400)
    fecha = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f'{self.usuario}: {self.comentario}'

    @property
    def is_reply(self):
        return self.parent is not None
    
#clase para evaluar a un proveedor
class EvaluacionProveedor(models.Model):
    proveedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluaciones_recibidas')
    evaluador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluaciones_realizadas')
    fecha_evaluacion = models.DateField(auto_now_add=True)

    PUNTAJE_CHOICES = [(i, str(i)) for i in range(1, 6)]
    puntualidad = models.PositiveSmallIntegerField(choices=PUNTAJE_CHOICES, verbose_name="Puntualidad en entregas")
    calidad = models.PositiveSmallIntegerField(choices=PUNTAJE_CHOICES, verbose_name="Calidad del producto/servicio")
    comunicacion = models.PositiveSmallIntegerField(choices=PUNTAJE_CHOICES, verbose_name="Comunicación y respuesta")
    cumplimiento = models.PositiveSmallIntegerField(choices=PUNTAJE_CHOICES, verbose_name="Cumplimiento de tareas")

    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Evaluación de proveedor"
        verbose_name_plural = "Evaluaciones de proveedores"

    def __str__(self):
        return f"Evaluación a {self.proveedor.username} por {self.evaluador.username}"