from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Chofer, Mecanico

class UsuarioAdminForm(UserCreationForm):
    cargo = forms.ChoiceField(
        choices=[
            ('admin', 'Administrador'),
            ('chofer', 'Chofer'),
            ('mecanico', 'Mecánico')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'cargo', 'password1', 'password2']

class ChoferForm(forms.ModelForm):
    class Meta:
        model = Chofer
        fields = ['RUTChofer', 'Nombre', 'Fecha_Nacimiento', 'Telefono', 'Estado', 'Horas']
        widgets = {
            'Fecha_Nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'RUTChofer': forms.TextInput(attrs={'placeholder': '12.345.678-9', 'class': 'form-control'}),
            'Nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'Telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'Estado': forms.Select(attrs={'class': 'form-control'}),
            'Horas': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MecanicoForm(forms.ModelForm):
    class Meta:
        model = Mecanico
        fields = ['RUT_Mecanico', 'Nombre', 'Fecha_Nacimiento', 'Telefono', 'Estado', 'Taller', 'Horas']
        widgets = {
            'Fecha_Nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'RUT_Mecanico': forms.TextInput(attrs={'placeholder': '12.345.678-9', 'class': 'form-control'}),
            'Nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'Telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'Estado': forms.Select(attrs={'class': 'form-control'}),
            'Taller': forms.TextInput(attrs={'class': 'form-control'}),
            'Horas': forms.TextInput(attrs={'class': 'form-control'}),
        }