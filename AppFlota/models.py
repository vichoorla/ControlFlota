from django.db import models

class Vehiculo(models.Model):
   patente = models.CharField(max_length=6)
   VIN = models.CharField(max_length=17)
   marca = models.CharField(max_length=50)
   modelo = models.CharField(max_length=50)
   año = models.CharField(max_length=4)
   motor = models.CharField(max_length=50)
   seguro = models.BooleanField(default=True)
   revision_tecnica = models.BooleanField(default=True)
   permiso_circulacion = models.BooleanField(default=True)
   gps = models.BooleanField(default=True)
   kilometraje = models.PositiveBigIntegerField(default=0)
   estanque = models.DecimalField(max_digits=5, decimal_places=2,
    help_text="Capacidad en litros")
   tonelaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
   asignacion = models.CharField(max_length=50)