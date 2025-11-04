from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Vehiculo, Chofer, Combustible, Mantencion, Mecanico, Usuario
from .forms import VehiculoForm, ChoferForm, CombustibleForm, MantencionForm, UsuarioForm
from django.db import transaction

# --- Vistas de Login y Dashboards (Sin cambios) ---

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            usuario = Usuario.objects.get(username=username, password=password)
            
            # Login exitoso
            request.session['usuario_autenticado'] = True
            request.session['tipo_usuario'] = usuario.cargo
            request.session['username'] = usuario.username
            request.session['nombre_usuario'] = usuario.nombre
            
            if usuario.cargo == 'admin':
                return redirect('admin_dashboard')
            elif usuario.cargo == 'chofer':
                # NOTA: Tu template original de agregar combustible usaba 
                # request.session.Vehiculo
                # Debes agregar la lógica para guardar el vehículo del chofer en la sesión aquí.
                # Ejemplo (si el chofer solo tiene UN vehículo):
                try:
                    chofer_obj = Chofer.objects.get(usuario=usuario)
                    vehiculo = Vehiculo.objects.filter(chofer_asignado=chofer_obj).first()
                    if vehiculo:
                        request.session['Vehiculo'] = vehiculo.patente
                except Chofer.DoesNotExist:
                    pass # El chofer no existe como tal en la tabla Chofer

                return redirect('chofer_dashboard')
            elif usuario.cargo == 'mecanico':
                return redirect('mecanico_dashboard')
                
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'TemplatesFlota/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def requiere_autenticacion(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_autenticado'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def requiere_tipo_usuario(tipos_permitidos):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            tipo_usuario = request.session.get('tipo_usuario')
            if tipo_usuario not in tipos_permitidos:
                return HttpResponse("No tienes permisos para acceder a esta página", status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# --- Vistas de Dashboard (Sin cambios) ---

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_dashboard(request):
    return render(request, 'TemplatesFlota/admin_dashboard.html', {
        'nombre_usuario': request.session.get('nombre_usuario')
    })

@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_dashboard(request):
    return render(request, 'TemplatesFlota/chofer_dashboard.html', {
        'nombre_usuario': request.session.get('nombre_usuario')
    })

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_dashboard(request):
    return render(request, 'TemplatesFlota/mecanico_dashboard.html', {
        'nombre_usuario': request.session.get('nombre_usuario')
    })

# ==========================================================
# VISTAS "AGREGAR" REFACTORIZADAS
# ==========================================================

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
@transaction.atomic # Asegura que se cree el Usuario y el Chofer, o ninguno
def admin_agregar_chofer(request):
    # El modelo Chofer depende del modelo Usuario (es su Llave Primaria)
    # Necesitamos dos formularios: uno para Usuario y otro para Chofer.
    
    if request.method == 'POST':
        # Pasamos el prefijo para que Django sepa qué datos van a qué formulario
        usuario_form = UsuarioForm(request.POST, prefix='usuario')
        chofer_form = ChoferForm(request.POST, prefix='chofer')

        if usuario_form.is_valid() and chofer_form.is_valid():
            # Creamos el objeto Usuario primero
            nuevo_usuario = usuario_form.save(commit=False)
            nuevo_usuario.cargo = 'chofer' # Asignamos el cargo
            nuevo_usuario.save()
            
            # Creamos el objeto Chofer, asignando el usuario recién creado
            nuevo_chofer = chofer_form.save(commit=False)
            nuevo_chofer.usuario = nuevo_usuario # Asignamos el Usuario
            nuevo_chofer.save()
            
            messages.success(request, 'Chofer agregado correctamente')
            return redirect('admin_ver_chofers')
        else:
            messages.error(request, 'Error al agregar chofer. Revisa los campos.')
    else:
        usuario_form = UsuarioForm(prefix='usuario')
        chofer_form = ChoferForm(prefix='chofer')

    return render(request, 'TemplatesFlota/admin_agregar_chofer.html', {
        'usuario_form': usuario_form,
        'chofer_form': chofer_form
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_chofers(request):
    chofers = Chofer.objects.all()
    return render(request, 'TemplatesFlota/admin_ver_chofers.html', {
        'chofers': chofers
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_agregar_vehiculo(request):
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save() # Guarda el objeto directamente
            messages.success(request, 'Vehículo agregado correctamente')
            return redirect('admin_ver_vehiculos')
        else:
            messages.error(request, 'Error al agregar vehículo. Revisa los campos.')
    else:
        form = VehiculoForm()
    
    return render(request, 'TemplatesFlota/admin_agregar_vehiculo.html', {
        'form': form
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_vehiculos(request):
    vehiculos = Vehiculo.objects.all()
    return render(request, 'TemplatesFlota/admin_ver_vehiculos.html', {
        'vehiculos': vehiculos
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_combustible(request):
    combustibles = Combustible.objects.all()
    return render(request, 'TemplatesFlota/admin_ver_combustible.html', {
        'combustibles': combustibles
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_mantenciones(request):
    mantenciones = Mantencion.objects.all()
    return render(request, 'TemplatesFlota/admin_ver_mantenciones.html', {
        'mantenciones': mantenciones
    })

# --- Funciones para Chofer ---

@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_ver_vehiculos(request):
    vehiculos = Vehiculo.objects.all()
    return render(request, 'TemplatesFlota/chofer_ver_vehiculos.html', {
        'vehiculos': vehiculos
    })

@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_agregar_combustible(request):
    # Tu template original ponía el vehículo en modo "readonly"
    # Usaremos el ModelForm, que mostrará un dropdown.
    # Si quieres que se auto-asigne, la lógica debe cambiar.
    
    if request.method == 'POST':
        form = CombustibleForm(request.POST)
        if form.is_valid():
            # Nota: El campo 'Encargado' ya no existe en el modelo,
            # por lo que el ModelForm no intentará guardarlo.
            form.save()
            messages.success(request, 'Registro de combustible agregado correctamente')
            return redirect('chofer_ver_combustible')
        else:
            messages.error(request, 'Error al agregar el registro.')
    else:
        # Intentamos pre-seleccionar el vehículo guardado en la sesión
        vehiculo_patente = request.session.get('Vehiculo', None)
        initial_data = {}
        if vehiculo_patente:
            try:
                vehiculo_obj = Vehiculo.objects.get(patente=vehiculo_patente)
                initial_data['vehiculo'] = vehiculo_obj
            except Vehiculo.DoesNotExist:
                pass # Si el vehículo no existe, simplemente no lo pre-llenamos
        
        form = CombustibleForm(initial=initial_data)
    
    return render(request, 'TemplatesFlota/chofer_agregar_combustible.html', {
        'form': form
    })

@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_ver_combustible(request):
    combustibles = Combustible.objects.all()
    return render(request, 'TemplatesFlota/chofer_ver_combustible.html', {
        'combustibles': combustibles
    })

# --- Funciones para Mecánico ---

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_ver_vehiculos(request):
    vehiculos = Vehiculo.objects.all()
    return render(request, 'TemplatesFlota/mecanico_ver_vehiculos.html', {
        'vehiculos': vehiculos
    })

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_agregar_combustible(request):
    # Esta vista es para el mecánico, por lo que tiene sentido
    # que pueda elegir cualquier vehículo.
    if request.method == 'POST':
        form = CombustibleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro de combustible agregado correctamente')
            return redirect('mecanico_ver_combustible')
        else:
            messages.error(request, 'Error al agregar el registro.')
    else:
        form = CombustibleForm()
    
    return render(request, 'TemplatesFlota/mecanico_agregar_combustible.html', {
        'form': form
    })

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_ver_combustible(request):
    combustibles = Combustible.objects.all()
    return render(request, 'TemplatesFlota/mecanico_ver_combustible.html', {
        'combustibles': combustibles
    })

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_agregar_mantencion(request):
    # Tu vista original no asignaba 'vehiculo' ni 'mecanico',
    # lo cual causaría un error. El ModelForm requiere estos campos.
    
    if request.method == 'POST':
        form = MantencionForm(request.POST)
        if form.is_valid():
            # Ya no es necesario calcular el ID, el AutoField lo hace solo.
            form.save()
            messages.success(request, 'Mantención agregada correctamente')
            return redirect('mecanico_ver_mantenciones')
        else:
            messages.error(request, 'Error al agregar la mantención.')
    else:
        # Intentamos pre-seleccionar al mecánico que está logueado
        initial_data = {}
        try:
            usuario_obj = Usuario.objects.get(username=request.session['username'])
            mecanico_obj = Mecanico.objects.get(usuario=usuario_obj)
            initial_data['mecanico'] = mecanico_obj
        except (Usuario.DoesNotExist, Mecanico.DoesNotExist):
            pass # Si no se encuentra, el usuario deberá seleccionarlo manualmente
            
        form = MantencionForm(initial=initial_data)
    
    return render(request, 'TemplatesFlota/mecanico_agregar_mantencion.html', {
        'form': form
    })

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_ver_mantenciones(request):
    mantenciones = Mantencion.objects.all()
    return render(request, 'TemplatesFlota/mecanico_ver_mantenciones.html', {
        'mantenciones': mantenciones
    })

# --- Clases de los models (Sin cambios) ---

def ChoferData(request):
    Choferes = Chofer.objects.all() # Corregido: el modelo es Chofer
    data = {'Choferes' : Choferes} # Corregido: la variable en el template es Choferes
    return render(request, 'chofer.html', data)

def MantencionData(request):
    Mantenciones = Mantencion.objects.all() # Corregido: variable plural
    data = {'Mantencion' : Mantenciones} # La variable en el template puede ser otra
    return render(request, 'mantencion.html', data)

def CombustibleData(request):
    Combustibles = Combustible.objects.all() # Corregido: variable plural
    data = {'Combustible' : Combustibles}
    return render(request, 'combustible.html', data)

def MecanicoData(request):
    Mecanicos = Mecanico.objects.all() # Corregido: variable plural
    data = {'Mecanico' : Mecanicos}
    return render(request, 'mecanico.html', data)

# Error en tu código original: 'Tipo_Vehiculo' no está definido. 
# El modelo es 'TipoVehiculo'
from .models import TipoVehiculo 
def Tipo_VehiculoData(request):
    Tipo_Vehiculos = TipoVehiculo.objects.all() # Corregido: Modelo y variable
    data = {'Tipo_Vehiculo' : Tipo_Vehiculos}
    return render(request, 'tipoVehiculo.html', data)