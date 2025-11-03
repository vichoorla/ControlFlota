from rest_framework import serializers
from .models import Vehiculo,Mantencion,Mecanico,Combustible,Chofer

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['patente','VIN','marca','modelo','año','motor','seguro','revision_tecnica','permiso_circulacion','gps','kilometraje','estanque','tonelaje','asignacion']

class MantencionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mantencion
        fields = ['Tipo_Mantencion','Fecha','Lugar','Descripcion']

class MecanicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mecanico
        fields = ['RUT_Mecanico','Nombre','Fecha_Nacimiento','Telefono','Email','Estado','Taller','Horas']

class CombustibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Combustible
        fields = ['Tipo_Combustible','Fecha_Recarga','Lugar','Encargado','Cantidad_Estanque','Recargar']

class ChoferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chofer
        fields = ['RUTChofer','Nombre','Fecha_Nacimiento','Telefono','Estado','Horas','Email']