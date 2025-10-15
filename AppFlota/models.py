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

class Usuario(models.Model):
    # ID auto-incremental (interno, no se usa para login)
    id = models.AutoField(primary_key=True)
    
    # Campos para login
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    
    # Información personal
    nombre = models.CharField(max_length=60)
    email = models.CharField(max_length=80)
    cargo = models.CharField(max_length=20, choices=[
        ('admin', 'Administrador'),
        ('chofer', 'Chofer'), 
        ('mecanico', 'Mecánico')
    ])

    class Meta:
        db_table = 'appflota_usuario'

    def __str__(self):
        return self.username

class Mantencion(models.Model):
    ID_Mantencion = models.IntegerField(primary_key=True)
    Tipo_Mantencion = models.CharField(max_length=45)
    Fecha = models.CharField(max_length=45)
    Lugar = models.CharField(max_length=50)
    Descripcion = models.CharField(max_length=45)

class Mecanico(models.Model):
    RUT_Mecanico = models.IntegerField(primary_key=True)
    Nombre = models.CharField(max_length=45)
    Fecha_Nacimiento = models.CharField(max_length=45)
    Telefono = models.CharField(max_length=45)
    Email = models.CharField(max_length=45)
    Estado = models.CharField(max_length=45)
    Taller = models.CharField(max_length=45)
    Horas = models.CharField(max_length=45)

class TipoVehiculo(models.Model):
    ID_Tipo = models.IntegerField(primary_key=True)
    Tipo = models.CharField(max_length=45)

class Combustible(models.Model):
    Tipo_Combustible = models.CharField(max_length=45)
    Fecha_Recarga = models.CharField(max_length=45)
    Lugar = models.CharField(max_length=45)
    Encargado = models.CharField(max_length=45)
    Cantidad_Estanque = models.CharField(max_length=45)
    Recargar = models.CharField(max_length=45)

class Chofer(models.Model):
    RUTChofer = models.IntegerField(primary_key=True)
    Nombre = models.CharField(max_length=45)
    Fecha_Nacimiento = models.CharField(max_length=45)
    Telefono = models.CharField(max_length=45)
    Estado = models.CharField(max_length=45)
    Horas = models.CharField(max_length=45)
    Email = models.CharField(max_length=45)
