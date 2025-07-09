from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class SolicitudIngreso(models.Model):
    proveedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_ingreso')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(verbose_name="Motivo de ingreso")
    documento_seguro = models.FileField(upload_to='ingresos/seguros/')
    codigo_ingreso = models.CharField(max_length=20, blank=True, null=True, unique=True)
    identificacion_productos = models.FileField(upload_to='ingresos/productos/')
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada')
    ], default='pendiente')
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Ingreso de {self.proveedor.username} - {self.estado}"

def generar_codigo_ingreso():
    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ING-{fecha}"