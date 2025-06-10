from django.db import models

# Create your models here.


class Departamento(models.Model):
    codigo = models.CharField(max_length=4, primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Municipio(models.Model):
    codigo = models.CharField(max_length=6, primary_key=True)
    nombre = models.CharField(max_length=100)
    departamento_id = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
class tipo_retenedor(models.Model):
    codigo = models.CharField(max_length=1, primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    

