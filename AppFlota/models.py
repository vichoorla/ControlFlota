from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import date, datetime
from django.core.validators import BaseValidator
import re

class EdadMinimaValidator(BaseValidator):
    def __init__(self, edad_minima):
        self.edad_minima = edad_minima
        message = f'La edad debe ser al menos {edad_minima} años'
        super().__init__(limit_value=edad_minima, message=message)

    def __call__(self, value):
        hoy = date.today()
        edad = hoy.year - value.year - ((hoy.month, hoy.day) < (value.month, value.day))
        if edad < self.edad_minima:
            raise ValidationError(self.message)

class EdadMaximaValidator(BaseValidator):
    def __init__(self, edad_maxima):
        self.edad_maxima = edad_maxima
        message = f'La edad no puede superar {edad_maxima} años'
        super().__init__(limit_value=edad_maxima, message=message)

    def __call__(self, value):
        hoy = date.today()
        edad = hoy.year - value.year - ((hoy.month, hoy.day) < (value.month, value.day))
        if edad > self.edad_maxima:
            raise ValidationError(self.message)

class NoFechaFuturaValidator(BaseValidator):
    def __init__(self):
        message = 'La fecha no puede ser futura'
        super().__init__(limit_value=None, message=message)

    def __call__(self, value):
        if value > date.today():
            raise ValidationError(self.message)
        
class RUTField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 12
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value:
            # Normaliza el RUT manteniendo el dígito verificador
            value = value.upper().replace('.', '').replace(' ', '')
            # Asegura de que tenga el formato correcto
            if '-' not in value and len(value) >= 8:
                cuerpo = value[:-1]
                dv = value[-1]
                value = f"{cuerpo}-{dv}"
            setattr(model_instance, self.attname, value)
        return value

class Vehiculo(models.Model):
   patente = models.CharField(
       max_length=6,
       validators=[
           RegexValidator(
               regex=r'^[A-Z]{2}\d{4}$|^[A-Z]{2}\d{3}[A-Z]{2}$',
               message='Formato de patente invalido. Use: AA1234 o AB1234CD'
           )
       ]
   )

   VIN = models.CharField(
       max_length=17,
       validators=[
           RegexValidator(
               regex=r'^[A-HJ-NPR-Z0-9]{17}$',
               message='VIN debe tener 17 caracteres alfanuméricos (excluyendo I, O, Q)'
           )
       ]
    )
   
   marca = models.CharField(max_length=50)
   modelo = models.CharField(max_length=50)

   año = models.CharField(
       max_length=4,
       validators=[
            RegexValidator(
                regex=r'^(19|20)\d{2}$',
                message='Año debe estar entre 1900 y 2099'
            )
       ]
   )
   motor = models.CharField(max_length=50)
   seguro = models.BooleanField(default=True)
   revision_tecnica = models.BooleanField(default=True)
   permiso_circulacion = models.BooleanField(default=True)
   gps = models.BooleanField(default=True)
   kilometraje = models.PositiveBigIntegerField(
        default=0,
        validators=[
            MaxValueValidator(1000000, message='Kilometraje no puede superar 1,000,000 km')
        ]
   )

   estanque = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[
            MinValueValidator(1, message='Capacidad mínima: 1 litro'),
            MaxValueValidator(500, message='Capacidad máxima: 500 litros')
        ],
        help_text="Capacidad en litros"
   )
   tonelaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[
            MinValueValidator(0.1, message='Tonelaje mínimo: 0.1 toneladas'),
            MaxValueValidator(100, message='Tonelaje máximo: 100 toneladas')
        ])
   asignacion = models.CharField(max_length=50)

   def clean(self):
       super().clean()

       # Validar que el año sea lógico (no futuro + 2 años)
       from datetime import datetime
       año_actual = datetime.now().year
       try:
           año_vehiculo = int(self.año)
           if año_vehiculo > (año_actual + 2):
               raise ValidationError({'año': f'El año no puede ser mayor a {año_actual + 2}'})
       except (ValueError, TypeError):
           raise ValidationError({'año': 'Año debe ser un número válido'})

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    
    username = models.CharField(
        max_length=50, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='Username solo puede contener letras, números, guiones y underscores'
            )
        ])
    
    password = models.CharField(        
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^.{8,}$',
                message='La contraseña debe tener al menos 8 caracteres'
            )
        ])
    
    nombre = models.CharField(        
        max_length=60,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
                message='Nombre solo puede contener letras y espacios'
            )
        ])
    
    email = models.CharField(       
        max_length=80,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                message='Formato de email inválido'
            )
        ])
    
    cargo = models.CharField(
        max_length=20, 
        choices=[
        ('admin', 'Administrador'),
        ('chofer', 'Chofer'), 
        ('mecanico', 'Mecánico')
    ])

    class Meta:
        db_table = 'appflota_usuario'

    def __str__(self):
        return self.username

class Mantencion(models.Model):
    ID_Mantencion = models.AutoField(primary_key=True)

    Tipo_Mantencion = models.CharField(        
        max_length=45,
        choices=[
            ('Preventiva', 'Preventiva'),
            ('Correctiva', 'Correctiva'),
            ('Predictiva', 'Predictiva'),
            ('Programada', 'Programada')
        ])
    
    Fecha = models.DateField()
    Lugar = models.CharField(max_length=50)

    Descripcion = models.CharField(        
        max_length=45,
        validators=[
            RegexValidator(
                regex=r'^.{10,}$',
                message='La descripción debe tener al menos 10 caracteres'
            )
        ])

class Mecanico(models.Model):
    RUT_Mecanico = RUTField(
        primary_key=True,
        validators=[
            RegexValidator(
                regex=r'^\d{1,2}\.\d{3}\.\d{3}-[0-9kK]$|^\d{7,8}-[0-9kK]$',
                message='Formato de RUT inválido. Use: 12.345.678-9 o 12345678-9'
            )
        ]
    )

    Nombre = models.CharField(        
        max_length=45,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
                message='Nombre solo puede contener letras y espacios'
            )
        ])
    
    Fecha_Nacimiento = models.DateField(
        validators=[
            NoFechaFuturaValidator(),
            EdadMinimaValidator(18),
            EdadMaximaValidator(80)
        ]
    )


    Telefono = models.CharField(
        max_length=45,
        validators=[
            RegexValidator(
                regex=r'^\+56 9 \d{4} \d{4}$|^9\d{8}$',
                message='Teléfono debe tener 9 dígitos comenzando con 9 o formato +56 9 XXXX XXXX'
            )
        ])
    
    Email = models.CharField(max_length=45)

    Estado = models.CharField(        
        max_length=45,
        choices=[
            ('Activo', 'Activo'),
            ('Inactivo', 'Inactivo'),
            ('Vacaciones', 'Vacaciones'),
            ('Licencia', 'Licencia')
        ])
    
    Taller = models.CharField(max_length=45)

    Horas = models.CharField(
        max_length=45,
        validators=[
            RegexValidator(
                regex=r'^\d{1,3}$',
                message='Horas debe ser un número entre 0 y 999'
            )
        ])
    
    def clean(self):
        super().clean()
        if self.RUT_Mecanico and not self.validar_rut_chileno(self.RUT_Mecanico):
            raise ValidationError({'RUT_Mecanico': 'RUT inválido o dígito verificador incorrecto'})
        
    def validar_rut_chileno(self, rut):
        try:
            # Limpiar el RUT
            rut = rut.upper().replace('.', '').replace(' ', '')
            
            # Si no tiene guión, asumir que el último carácter es el DV
            if '-' not in rut:
                if len(rut) < 8:
                    return False
                cuerpo = rut[:-1]
                dv = rut[-1]
            else:
                partes = rut.split('-')
                if len(partes) != 2:
                    return False
                cuerpo, dv = partes
            
            # Validar formato
            if not re.match(r'^\d{7,8}$', cuerpo) or not re.match(r'^[0-9K]$', dv):
                return False
            
            # Calcular dígito verificador
            suma = 0
            multiplo = 2
            
            for i in range(len(cuerpo)-1, -1, -1):
                suma += int(cuerpo[i]) * multiplo
                multiplo = 2 if multiplo == 7 else multiplo + 1
            
            dv_esperado = 11 - (suma % 11)
            if dv_esperado == 11: dv_esperado = '0'
            elif dv_esperado == 10: dv_esperado = 'K'
            else: dv_esperado = str(dv_esperado)
            
            return dv == dv_esperado
            
        except:
            return False
    
    def save(self, *args, **kwargs):
        if self.RUT_Mecanico:
            rut_limpio = self.RUT_Mecanico.upper().replace('.', '').replace(' ', '')
            if '-' not in rut_limpio and len(rut_limpio) >= 8:
                cuerpo = rut_limpio[:-1]
                dv = rut_limpio[-1]
                self.RUT_Mecanico = f"{cuerpo}-{dv}"
        
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Validar antes de guardar
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.RUT_Mecanico} - {self.Nombre}"

class TipoVehiculo(models.Model):
    ID_Tipo = models.IntegerField(primary_key=True)
    Tipo = models.CharField(max_length=45)

class Combustible(models.Model):
    Tipo_Combustible = models.CharField(        
        max_length=45,
        choices=[
            ('93', '93'),
            ('95', '95'),
            ('97', '97'),
            ('Diésel', 'Diésel'),
            ('Eléctrico', 'Eléctrico'),
            ('GLP', 'GLP')
        ])
    
    Fecha_Recarga = models.DateField()
    Lugar = models.CharField(max_length=45)
    Encargado = models.CharField(max_length=45)

    Cantidad_Estanque = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0.1, message='Cantidad mínima: 0.1 litros'),
            MaxValueValidator(500, message='Cantidad máxima: 500 litros')
        ])
    
    Recargar = models.CharField(        
        max_length=2,
        choices=[
            ('Si', 'Si'),
            ('No', 'No')
        ])

class Chofer(models.Model):
    RUTChofer = RUTField(
        primary_key=True,
        validators=[
            RegexValidator(
                regex=r'^\d{1,2}\.\d{3}\.\d{3}-[0-9kK]$|^\d{7,8}-[0-9kK]$',
                message='Formato de RUT inválido. Use: 12.345.678-9 o 12345678-9'
            )
        ]
    )
    Nombre = models.CharField(        
        max_length=45,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
                message='Nombre solo puede contener letras y espacios'
            )
        ])
    
    Fecha_Nacimiento = models.DateField(
        validators=[
            NoFechaFuturaValidator(),
            EdadMinimaValidator(21),
            EdadMaximaValidator(75)
        ]
    )


    Telefono = models.CharField(        
        max_length=45,
        validators=[
            RegexValidator(
                regex=r'^\+56 9 \d{4} \d{4}$|^9\d{8}$',
                message='Teléfono debe tener 9 dígitos comenzando con 9'
            )
        ])
    Estado = models.CharField(        
        max_length=45,
        choices=[
            ('Activo', 'Activo'),
            ('Inactivo', 'Inactivo'),
            ('Vacaciones', 'Vacaciones'),
            ('Licencia', 'Licencia'),
            ('Suspendido', 'Suspendido')
        ])
    
    Horas = models.CharField(        
        max_length=45,
        validators=[
            RegexValidator(
                regex=r'^\d{1,3}$',
                message='Horas debe ser un número entre 0 y 999'
            )
        ])
    
    Email = models.EmailField(max_length=45)

    def clean(self):
        super().clean()
        if self.RUTChofer and not self.validar_rut_chileno(self.RUTChofer):
            raise ValidationError({'RUTChofer': 'RUT inválido o dígito verificador incorrecto'})
        
    def validar_rut_chileno(self, rut):
        try:
            # Limpiar el RUT
            rut = rut.upper().replace('.', '').replace(' ', '')
            
            # Si no tiene guión, asumir que el último carácter es el DV
            if '-' not in rut:
                if len(rut) < 8:
                    return False
                cuerpo = rut[:-1]
                dv = rut[-1]
            else:
                partes = rut.split('-')
                if len(partes) != 2:
                    return False
                cuerpo, dv = partes
            
            # Validar formato
            if not re.match(r'^\d{7,8}$', cuerpo) or not re.match(r'^[0-9K]$', dv):
                return False
            
            # Calcular dígito verificador
            suma = 0
            multiplo = 2
            
            for i in range(len(cuerpo)-1, -1, -1):
                suma += int(cuerpo[i]) * multiplo
                multiplo = 2 if multiplo == 7 else multiplo + 1
            
            dv_esperado = 11 - (suma % 11)
            if dv_esperado == 11: dv_esperado = '0'
            elif dv_esperado == 10: dv_esperado = 'K'
            else: dv_esperado = str(dv_esperado)
            
            return dv == dv_esperado
            
        except:
            return False
    
    def save(self, *args, **kwargs):
        if self.RUTChofer:
            rut_limpio = self.RUTChofer.upper().replace('.', '').replace(' ', '')
            if '-' not in rut_limpio and len(rut_limpio) >= 8:
                cuerpo = rut_limpio[:-1]
                dv = rut_limpio[-1]
                self.RUTChofer = f"{cuerpo}-{dv}"

        self.full_clean()
        super().save(*args, **kwargs)
        
        # Validar antes de guardar
        self.full_clean()
        super().save(*args, **kwargs)
