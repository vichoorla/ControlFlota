# Crear el archivo vichoorla/controlflota/ControlFlota-f4e1bdf3b225366621209ad7308075e779a94958/AppFlota/forms.py

from material import forms
from .models import Vehiculo, Combustible, Mantencion, Chofer

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = [
            'patente', 'VIN', 'marca', 'modelo', 'año', 'motor', 
            'seguro', 'revision_tecnica', 'permiso_circulacion', 'gps',
            'kilometraje', 'estanque', 'tonelaje', 'Tipo', 'chofer_asignado'
        ]

class ChoferForm(forms.ModelForm):
    class Meta:
        model = Chofer
        fields = [
            'RUTChofer', 'Nombre', 'Fecha_Nacimiento', 
            'Telefono', 'Estado', 'Horas', 'Email'
        ]
        # Nota: 'usuario' no se incluye, se maneja en la vista.

class CombustibleForm(forms.ModelForm):
    class Meta:
        model = Combustible
        fields = [
            'vehiculo', 'Tipo_Combustible', 'Fecha_Recarga', 
            'Lugar', 'Cantidad_Estanque', 'Recargar'
        ]
        # 'Encargado' fue eliminado en la migración 0002

class MantencionForm(forms.ModelForm):
    class Meta:
        model = Mantencion
        fields = [
            'vehiculo', 'mecanico', 'Tipo_Mantencion', 
            'Fecha', 'Lugar', 'Descripcion'
        ]