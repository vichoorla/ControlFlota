from django.db import models

# Create your models here.
class Chofer(models.Model):
    Rut = models.CharField(max_length=10)
    Nombre = models.CharField(max_length=50)
    Fecha_Nacimiento = models.CharField(max_length=10)
    Telefono = models.CharField(max_length=10)
    Estado = models.BooleanField(default=True)
    Horas = models.CharField(max_length=30)
    Email = models.EmailField()

class Combustible(models.Model):
    Tipo_Combustible = models.CharField(max_length=45)
    Fecha_Recarga = models.CharField(max_length=10)
    Lugar = models.CharField(max_length=55)
    Encargado = models.CharField(max_length=40)
    Cantidad_Estanque = models.CharField(max_length=40)
    Recargar = models.CharField(max_length=40)

class Mantencion(models.Model):
    Tipo_Mantencion = models.CharField(max_length=50)
    Fecha_Mantencion = models.CharField(max_length=20)
    Lugar = models.CharField(max_length=60)
    Detalle = models.CharField(max_length=100)

class Mecanico(models.Model):
    Rut = models.CharField(max_length=10)
    Fecha_Nacimiento = models.CharField(max_length=10)
    Telefono = models.CharField(max_length=10)
    Email = models.EmailField()
    Estado = models.BooleanField(default=True)
    Taller = models.CharField(max_length=50)
    Horas = models.CharField(max_length=100)
    Empresa = models.CharField(max_length=100)

class Tipo_Vehiculo(models.Model):
    Tipo = models.CharField(max_length=40)