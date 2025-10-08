from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from AppFlota.models import Chofer, Combustible, Mantencion, Mecanico, Tipo_Vehiculo

vehiculos = {}
chofers = {}
mecanicos = {}
combustibles = {}
mantenciones = {}
usuarios = {
    'admin': {'password': 'admin123', 'tipo': 'admin', 'nombre': 'Administrador'},
    'chofer': {'password': 'chofer123', 'tipo': 'chofer', 'nombre': 'Juan Chofer'},
    'mecanico': {'password': 'mecanico123', 'tipo': 'mecanico', 'nombre': 'Pedro Mecánico'}
}

# Contadores para IDs
vehiculo_id_counter = 1
chofer_id_counter = 1
mecanico_id_counter = 1
combustible_id_counter = 1
mantencion_id_counter = 1

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username in usuarios and usuarios[username]['password'] == password:
            request.session['usuario_autenticado'] = True
            request.session['tipo_usuario'] = usuarios[username]['tipo']
            request.session['username'] = username
            request.session['nombre_usuario'] = usuarios[username]['nombre']
            
            if usuarios[username]['tipo'] == 'admin':
                return redirect('admin_dashboard')
            elif usuarios[username]['tipo'] == 'chofer':
                return redirect('chofer_dashboard')
            elif usuarios[username]['tipo'] == 'mecanico':
                return redirect('mecanico_dashboard')
        else:
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

# Vistas de dashboard
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

# Finciones para Admin
@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_agregar_chofer(request):
    global chofer_id_counter

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        telefono = request.POST.get('telefono')
        estado = request.POST.get('estado')
        horas = request.POST.get('horas')

        chofer_id = chofer_id_counter
        chofers[chofer_id] = {
            'id': chofer_id,
            'nombre': nombre,
            'fecha_nacimiento': fecha_nacimiento,
            'telefono': telefono,
            'estado': estado,
            'horas': horas,
            'imagen': 'images/fotoperfil.jpg'
        }
        chofer_id_counter += 1

        messages.success(request, 'Chofer agregado correctamente')
        return redirect('admin_ver_chofers')
    
    return render(request, 'TemplatesFlota/admin_agregar_chofer.html')

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_chofers(request):
    return render(request, 'TemplatesFlota/admin_ver_chofers.html', {
        'chofers': chofers
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_agregar_vehiculo(request):
    global vehiculo_id_counter

    if request.method == 'POST':
        patente = request.POST.get('patente')
        vin = request.POST.get('vin')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        año = request.POST.get('año')
        motor = request.POST.get('motor')
        seguro = request.POST.get('seguro')
        revision_tecnica = request.POST.get('revision_tecnica')
        permiso_circulacion = request.POST.get('permiso_circulacion')
        gps = request.POST.get('gps')
        
        vehiculo_id = vehiculo_id_counter
        vehiculos[vehiculo_id] = {
            'id': vehiculo_id,
            'patente': patente,
            'vin': vin,
            'marca': marca,
            'modelo': modelo,
            'año': año,
            'motor': motor,
            'seguro': seguro,
            'revision_tecnica': revision_tecnica,
            'permiso_circulacion': permiso_circulacion,
            'gps': gps
        }
        vehiculo_id_counter += 1

        messages.success(request, 'Vehículo agregado correctamente')
        return redirect('admin_ver_vehiculos')
    
    return render(request, 'TemplatesFlota/admin_agregar_vehiculo.html')

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_vehiculos(request):
    return render(request, 'TemplatesFlota/admin_ver_vehiculos.html',{
        'vehiculos': vehiculos
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_combustible(request):
    return render(request, 'TemplatesFlota/admin_ver_combustible.html', {
        'combustibles': combustibles
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_mantenciones(request):
    return render(request, 'TemplatesFlota/admin_ver_mantenciones.html', {
        'mantenciones': mantenciones
    })

# Funciones para Chofer
@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_ver_vehiculos(request):
    return render(request, 'TemplatesFlota/chofer_ver_vehiculos.html', {
        'vehiculos': vehiculos
    })

@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_agregar_combustible(request):
    global combustible_id_counter
    if request.method == 'POST':
        tipo_combustible = request.POST.get('tipo_combustible')
        fecha_recarga = request.POST.get('fecha_recarga')
        lugar = request.POST.get('lugar')
        encargado = request.POST.get('encargado')
        cantidad_estanque = request.POST.get('cantidad_estanque')
        recargar = request.POST.get('recargar')
        vehiculo_id = request.POST.get('vehiculo_id')

        combustible_id = combustible_id_counter
        combustibles[combustible_id] = {
            'id': combustible_id,
            'tipo_combustible': tipo_combustible,
            'fecha_recarga': fecha_recarga,
            'lugar': lugar,
            'encargado': encargado,
            'cantidad_estanque': cantidad_estanque,
            'recargar': recargar,
            'vehiculo_id': vehiculo_id,
            'registrado_por': request.session.get('nombre_usuario')
        }
        combustible_id_counter += 1

        messages.success(request, 'Registro de combustible agregado correctamente')
        return redirect('chofer_ver_combustible')
    
    return render(request, 'TemplatesFlota/chofer_agregar_combustible.html', {
        'vehiculos': vehiculos
    })

@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_ver_combustible(request):
    return render(request, 'TemplatesFlota/chofer_ver_combustible.html', {
        'combustibles': combustibles
    })

# Funciones para Mecánico
@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_ver_vehiculos(request):
    return render(request, 'TemplatesFlota/mecanico_ver_vehiculos.html', {
        'vehiculos': vehiculos
    })

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_agregar_combustible(request):
    global combustible_id_counter

    if request.method == 'POST':
        tipo_combustible = request.POST.get('tipo_combustible')
        fecha_recarga = request.POST.get('fecha_recarga')
        lugar = request.POST.get('lugar')
        encargado = request.POST.get('encargado')
        cantidad_estanque = request.POST.get('cantidad_estanque')
        recargar = request.POST.get('recargar')
        vehiculo_id = request.POST.get('vehiculo_id')

        combustible_id = combustible_id_counter
        combustibles[combustible_id] = {
            'id': combustible_id,
            'tipo_combustible': tipo_combustible,
            'fecha_recarga': fecha_recarga,
            'lugar': lugar,
            'encargado': encargado,
            'cantidad_estanque': cantidad_estanque,
            'recargar': recargar,
            'vehiculo_id': vehiculo_id,
            'registrado_por': request.session.get('nombre_usuario')
        }
        combustible_id_counter += 1

        messages.success(request, 'Registro de combustible agregado correctamente')
        return redirect('mecanico_ver_combustible')
    
    return render(request, 'TemplatesFlota/mecanico_agregar_combustible.html', {
        'vehiculos': vehiculos
    })

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_ver_combustible(request):
    return render(request, 'TemplatesFlota/mecanico_ver_combustible.html', {
        'combustibles': combustibles
    })

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_agregar_mantencion(request):
    global mantencion_id_counter

    if request.method == 'POST':
        tipo_mantencion = request.POST.get('tipo_mantencion')
        fecha = request.POST.get('fecha')
        descripcion = request.POST.get('descripcion')
        vehiculo_id = request.POST.get('vehiculo_id')

        mantencion_id = mantencion_id_counter
        mantenciones[mantencion_id] = {
            'id': mantencion_id,
            'tipo_mantencion': tipo_mantencion,
            'fecha': fecha,
            'descripcion': descripcion,
            'vehiculo_id': vehiculo_id,
            'realizado_por': request.session.get('nombre_usuario')
        }
        mantencion_id_counter += 1

        messages.success(request, 'Mantención agregada correctamente')
        return redirect('mecanico_ver_mantenciones')
    
    return render(request, 'TemplatesFlota/mecanico_agregar_mantencion.html', {
        'vehiculos': vehiculos
    })

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_ver_mantenciones(request):
    return render(request, 'TemplatesFlota/mecanico_ver_mantenciones.html', {
        'mantenciones': mantenciones
    })

# Clases de los models.

def ChoferData(request):
    Chofer = Chofer.objects.all()
    data = {'Chofer' : Chofer}
    return render(request, 'mhofer.html', data)

def MantencionData(request):
    Mantencion = Mantencion.objects.all()
    data = {'Mantencion' : Mantencion}
    return render(request, 'mantencion.html', data)

def CombustibleData(request):
    Combustible = Combustible.objects.all()
    data = {'Combustible' : Combustible}
    return render(request, 'combustible.html', data)

def MecanicoData(request):
    Mecanico = Mecanico.objects.all()
    data = {'Mecanico' : Mecanico}
    return render(request, 'mecanico.html', data)

def Tipo_VehiculoData(request):
    Tipo_Vehiculo = Tipo_Vehiculo.objects.all()
    data = {'Tipo_Vehiculo' : Tipo_Vehiculo}
    return render(request, 'tipoVehiculo.html', data)

