from turtle import mode
from django.db import models
from django.apps import apps
from django.contrib.auth.models import User
# Create your models here.

class solicitud(models.Model):
    id = models.AutoField(primary_key=True)
    identificador = models.CharField(max_length=12)
    TSolicitud= models.CharField(max_length=50)
    descripcion = models.CharField(max_length=400)
    cantidad = models.IntegerField()
    familia = models.ForeignKey('proveedores.familias',  on_delete=models.CASCADE)
    estado= models.CharField(max_length=50)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_final = models.DateField(null=True)
    observaciones = models.CharField(max_length=400)
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            last = solicitud.objects.all().last()
            if not  last:
                self.identificador = 'SOL000001'
            else:
                last =  last.identificador
                num = int(last[3:])
                new_num = num + 1
                new_id = 'SOL' + str(new_num).zfill(6)
                self.identificador = new_id
            super().save(*args, **kwargs)
    
class caracteristicas_solicitud(models.Model):
    id = models.AutoField(primary_key=True)
    solicitud = models.ForeignKey(solicitud, on_delete=models.CASCADE)
    caracteristica = models.CharField(max_length=100)
    
    def __str__(self):
        return self.caracteristica
    

        
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
    
