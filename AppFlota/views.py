from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Vehiculo, Chofer, Combustible, Mantencion, Mecanico, Usuario


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
def admin_agregar_chofer(request):
    if request.method == 'POST':
        but_chofer = request.POST.get('but_chofer')
        nombre = request.POST.get('nombre')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        telefono = request.POST.get('telefono')
        estado = request.POST.get('estado')
        horas = request.POST.get('horas')

        try:
            Chofer.objects.create(
                RUTChofer=but_chofer,
                Nombre=nombre,
                Fecha_Nacimiento=fecha_nacimiento,
                Telefono=telefono,
                Estado=estado,
                Horas=horas
            )
            messages.success(request, 'Chofer agregado correctamente')
            return redirect('admin_ver_chofers')
        except:
            messages.error(request, 'Error al agregar chofer')

    return render(request, 'TemplatesFlota/admin_agregar_chofer.html')

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
        kilometraje = request.POST.get('kilometraje')
        estanque = request.POST.get('estanque')
        tonelaje = request.POST.get('tonelaje')
        asignacion = request.POST.get('asignacion')
        
        try:
            Vehiculo.objects.create(
                Patente=patente,
                VIN=vin,
                Marca=marca,
                Modelo=modelo,
                Año=año,
                Motor=motor,
                Seguro=seguro,
                Revision_Tecnica=revision_tecnica,
                Permiso_Circulacion=permiso_circulacion,
                GPS=gps,
                kilometraje=kilometraje,
                estanque=estanque,
                tonelaje=tonelaje,
                asignacion=asignacion
            )
            messages.success(request, 'Vehículo agregado correctamente')
            return redirect('admin_ver_vehiculos')
        except:
            messages.error(request, 'Error al agregar vehículo')
    
    return render(request, 'TemplatesFlota/admin_agregar_vehiculo.html')

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

# Funciones para Chofer
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
    if request.method == 'POST':
        tipo_combustible = request.POST.get('tipo_combustible')
        fecha_recarga = request.POST.get('fecha_recarga')
        lugar = request.POST.get('lugar')
        encargado = request.POST.get('encargado')
        cantidad_estanque = request.POST.get('cantidad_estanque')
        recargar = request.POST.get('recargar')

        Combustible.objects.create(
            Tipo_Combustible=tipo_combustible,
            Fecha_Recarga=fecha_recarga,
            Lugar=lugar,
            Encargado=encargado,
            Cantidad_Estanque=cantidad_estanque,
            Recargar=recargar
        )
        messages.success(request, 'Registro de combustible agregado correctamente')
        return redirect('chofer_ver_combustible')
    
    return render(request, 'TemplatesFlota/chofer_agregar_combustible.html')

@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_ver_combustible(request):
    combustibles = Combustible.objects.all()
    return render(request, 'TemplatesFlota/chofer_ver_combustible.html', {
        'combustibles': combustibles
    })

# Funciones para Mecánico
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
    if request.method == 'POST':
        tipo_combustible = request.POST.get('tipo_combustible')
        fecha_recarga = request.POST.get('fecha_recarga')
        lugar = request.POST.get('lugar')
        encargado = request.POST.get('encargado')
        cantidad_estanque = request.POST.get('cantidad_estanque')
        recargar = request.POST.get('recargar')

        Combustible.objects.create(
            Tipo_Combustible=tipo_combustible,
            Fecha_Recarga=fecha_recarga,
            Lugar=lugar,
            Encargado=encargado,
            Cantidad_Estanque=cantidad_estanque,
            Recargar=recargar
        )
        messages.success(request, 'Registro de combustible agregado correctamente')
        return redirect('mecanico_ver_combustible')
    
    return render(request, 'TemplatesFlota/mecanico_agregar_combustible.html')

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
    if request.method == 'POST':
        tipo_mantencion = request.POST.get('tipo_mantencion')
        fecha = request.POST.get('fecha')
        lugar = request.POST.get('lugar')
        descripcion = request.POST.get('descripcion')

        # último ID + 1
        ultima_mantencion = Mantencion.objects.order_by('-ID_Mantencion').first()
        nuevo_id = ultima_mantencion.ID_Mantencion + 1 if ultima_mantencion else 1

        Mantencion.objects.create(
            ID_Mantencion=nuevo_id,
            Tipo_Mantencion=tipo_mantencion,
            Lugar=lugar,
            Fecha=fecha,
            Descripcion=descripcion
        )
        messages.success(request, 'Mantención agregada correctamente')
        return redirect('mecanico_ver_mantenciones')
    
    return render(request, 'TemplatesFlota/mecanico_agregar_mantencion.html')

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_ver_mantenciones(request):
    mantenciones = Mantencion.objects.all()
    return render(request, 'TemplatesFlota/mecanico_ver_mantenciones.html', {
        'mantenciones': mantenciones
    })