from django.contrib import admin
from .models import Usuario, Chofer, Vehiculo, Combustible, Mantencion, Mecanico, TipoVehiculo

# Registrar todos los modelos
admin.site.register(Usuario)
admin.site.register(Chofer)
admin.site.register(Vehiculo)
admin.site.register(Combustible)
admin.site.register(Mantencion)
admin.site.register(Mecanico)
admin.site.register(TipoVehiculo)