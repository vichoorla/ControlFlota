from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import IntegrityError
from .models import Vehiculo, Chofer, Combustible, Mantencion, Mecanico, Usuario, TipoVehiculo


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
    nombre_usuario = request.session.get('nombre_usuario')
    username = request.session.get('username')
    
    vehiculos_del_chofer = []
    
    try:
        # se busca al usuario
        usuario_actual = Usuario.objects.get(username=username)
        
        # se busca al chofer asignado
        chofer_actual = usuario_actual.chofer 
        
        # se busca el vehiculo asignado
        vehiculos_del_chofer = chofer_actual.vehiculos_asignados.all()
        
    except (Usuario.DoesNotExist, Chofer.DoesNotExist, AttributeError):
        pass 

    context = {
        'nombre_usuario': nombre_usuario,
        'vehiculos': vehiculos_del_chofer 
    }
    return render(request, 'TemplatesFlota/chofer_dashboard.html', context)


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
        username = request.POST.get('username')
        password = request.POST.get('password')
        email_usuario = request.POST.get('email_usuario')
        nombre = request.POST.get('nombre')
        

        rut_chofer = request.POST.get('RUTChofer')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        telefono = request.POST.get('telefono')
        estado = request.POST.get('estado')
        horas = request.POST.get('horas')

        try:
            nuevo_usuario = Usuario.objects.create(
                username=username,
                password=password,
                nombre=nombre,
                email=email_usuario,
                cargo='chofer'
            )
            
            # crear el chofer y enlazarlo al usuario
            Chofer.objects.create(
                usuario=nuevo_usuario,
                RUTChofer=rut_chofer,
                Nombre=nombre,
                Fecha_Nacimiento=fecha_nacimiento,
                Telefono=telefono,
                Estado=estado,
                Horas=horas,
            )
            
            messages.success(request, 'Chofer y cuenta de usuario creados correctamente')
            return redirect('admin_ver_chofers')
        
        except IntegrityError:
            messages.error(request, f'Error: El nombre de usuario "{username}" ya existe.')
        except Exception as e:
            messages.error(request, f'Error al agregar chofer: {e}')

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
        tipo_id = request.POST.get('tipo')
        chofer_id = request.POST.get('chofer_asignado')

        seguro_val = request.POST.get('seguro') == 'on'
        revision_val = request.POST.get('revision_tecnica') == 'on'
        permiso_val = request.POST.get('permiso_circulacion') == 'on'
        gps_val = request.POST.get('gps') == 'on'
        
        try:
            tipo_obj = TipoVehiculo.objects.get(pk=tipo_id)
            
            chofer_obj = None
            if chofer_id:
                chofer_obj = Chofer.objects.get(pk=chofer_id)

            Vehiculo.objects.create(
                patente=request.POST.get('patente'),
                VIN=request.POST.get('vin'),
                marca=request.POST.get('marca'),
                modelo=request.POST.get('modelo'),
                año=request.POST.get('año'),
                motor=request.POST.get('motor'),
                kilometraje=request.POST.get('kilometraje'),
                estanque=request.POST.get('estanque'),
                tonelaje=request.POST.get('tonelaje') or None,
                
                seguro=seguro_val,
                revision_tecnica=revision_val,
                permiso_circulacion=permiso_val,
                gps=gps_val,

                Tipo=tipo_obj,
                chofer_asignado=chofer_obj
            )
            messages.success(request, 'Vehículo agregado correctamente')
            return redirect('admin_ver_vehiculos')
        
        except TipoVehiculo.DoesNotExist:
             messages.error(request, 'Error: El tipo de vehículo seleccionado no es válido.')
        except Chofer.DoesNotExist:
             messages.error(request, 'Error: El chofer seleccionado no es válido.')
        except Exception as e:
            messages.error(request, f'Error al agregar vehículo: {e}')
    
    context = {
        'tipos_vehiculo': TipoVehiculo.objects.all(),
        'choferes': Chofer.objects.all()
    }
    return render(request, 'TemplatesFlota/admin_agregar_vehiculo.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_vehiculos(request):
    vehiculos = Vehiculo.objects.select_related('Tipo', 'chofer_asignado').all()
    return render(request, 'TemplatesFlota/admin_ver_vehiculos.html', {
        'vehiculos': vehiculos
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_combustible(request):
    combustibles = Combustible.objects.select_related('vehiculo').all()
    return render(request, 'TemplatesFlota/admin_ver_combustible.html', {
        'combustibles': combustibles
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_mantenciones(request):
    mantenciones = Mantencion.objects.select_related('vehiculo', 'mecanico').all()
    return render(request, 'TemplatesFlota/admin_ver_mantenciones.html', {
        'mantenciones': mantenciones
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_agregar_mecanico(request):
    if request.method == 'POST':
        # campos del modelo usuario
        username = request.POST.get('username')
        password = request.POST.get('password')
        email_usuario = request.POST.get('email_usuario')
        nombre = request.POST.get('nombre') 
        # campos del modelo mecanico
        rut_mecanico = request.POST.get('RUT_Mecanico')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        telefono = request.POST.get('telefono')
        estado = request.POST.get('estado')
        taller = request.POST.get('taller')
        horas = request.POST.get('horas')

        try:
            nuevo_usuario = Usuario.objects.create(
                username=username,
                password=password,
                nombre=nombre,
                email=email_usuario,
                cargo='mecanico'
            )
            
            Mecanico.objects.create(
                usuario=nuevo_usuario,
                RUT_Mecanico=rut_mecanico,
                Nombre=nombre,
                Fecha_Nacimiento=fecha_nacimiento,
                Telefono=telefono,
                Estado=estado,
                Taller=taller,
                Horas=horas
            )
            messages.success(request, 'Mecánico y Usuario creados correctamente')
            return redirect('admin_ver_mecanicos')
        
        except IntegrityError:
            messages.error(request, f'Error: El username "{username}" o el RUT "{rut_mecanico}" ya existen.')
        except Exception as e:
            messages.error(request, f'Error al agregar mecánico: {e}')

    return render(request, 'TemplatesFlota/admin_agregar_mecanico.html')

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_mecanicos(request):
    mecanicos = Mecanico.objects.select_related('usuario').all()
    return render(request, 'TemplatesFlota/admin_ver_mecanicos.html', {
        'mecanicos': mecanicos
    })

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_agregar_tipo_vehiculo(request):
    if request.method == 'POST':
        nombre_tipo = request.POST.get('nombre')
        
        if nombre_tipo:
            try:
                # El modelo TipoVehiculo tiene 'nombre' como 'unique=True'
                # por eso usamos IntegrityError.
                TipoVehiculo.objects.create(nombre=nombre_tipo)
                messages.success(request, f'Tipo "{nombre_tipo}" agregado correctamente.')
                return redirect('admin_ver_tipos_vehiculo')
            except IntegrityError:
                messages.error(request, f'El tipo de vehículo "{nombre_tipo}" ya existe.')
            except Exception as e:
                messages.error(request, f'Ocurrió un error: {e}')
        else:
            messages.error(request, 'El nombre no puede estar vacío.')
            
    return render(request, 'TemplatesFlota/admin_agregar_tipo_vehiculo.html')

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_tipos_vehiculo(request):
    tipos = TipoVehiculo.objects.all()
    return render(request, 'TemplatesFlota/admin_ver_tipos_vehiculo.html', {
        'tipos_vehiculo': tipos
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
    
    # Obtener los vehículos del chofer
    vehiculos_del_chofer = []
    try:
        username = request.session.get('username')
        usuario_actual = Usuario.objects.get(username=username)
        chofer_actual = usuario_actual.chofer
        vehiculos_del_chofer = chofer_actual.vehiculos_asignados.all()
    except (Usuario.DoesNotExist, Chofer.DoesNotExist, AttributeError):
        messages.error(request, 'No se pudo encontrar su perfil de chofer.')
        return redirect('chofer_dashboard')

    # Lógica de cuando se envía el formulario
    if request.method == 'POST':
        tipo_combustible = request.POST.get('tipo_combustible')
        fecha_recarga = request.POST.get('fecha_recarga')
        lugar = request.POST.get('lugar')
        
        # Se obtiene la patente
        patente_vehiculo = request.POST.get('vehiculo') 
        
        cantidad_estanque = request.POST.get('cantidad_estanque')
        recargar = request.POST.get('recargar')

        if not patente_vehiculo:
            messages.error(request, 'Debe seleccionar un vehículo.')
        else:
            try:
                vehiculo_obj = Vehiculo.objects.get(patente=patente_vehiculo)
                
                # se asegura que el auto sea del chofer
                if vehiculo_obj in vehiculos_del_chofer:
                    Combustible.objects.create(
                        vehiculo=vehiculo_obj, 
                        Tipo_Combustible=tipo_combustible,
                        Fecha_Recarga=fecha_recarga,
                        Lugar=lugar,
                        Cantidad_Estanque=cantidad_estanque,
                        Recargar=recargar
                    )
                    messages.success(request, 'Registro de combustible agregado correctamente')
                    return redirect('chofer_ver_combustible')
                else:
                    messages.error(request, 'El vehículo seleccionado no está asignado a usted.')
                    
            except Vehiculo.DoesNotExist:
                messages.error(request, 'El vehículo seleccionado no existe.')
            except Exception as e:
                messages.error(request, f'Ocurrió un error inesperado: {e}')

    context = {
        'vehiculos_asignados': vehiculos_del_chofer
    }
    return render(request, 'TemplatesFlota/chofer_agregar_combustible.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_ver_combustible(request):
    
    lista_combustibles = []
    
    try:
        username = request.session.get('username')
        usuario_actual = Usuario.objects.get(username=username)
        chofer_actual = usuario_actual.chofer
        
        vehiculos_del_chofer = chofer_actual.vehiculos_asignados.all()
        
        lista_combustibles = Combustible.objects.filter(
            vehiculo__in=vehiculos_del_chofer
        ).order_by('-Fecha_Recarga') # se ordena por la fecha mas nueva
        
    except (Usuario.DoesNotExist, Chofer.DoesNotExist):
        messages.error(request, 'No se pudo encontrar tu perfil de chofer.')
    
    context = {
        'combustibles': lista_combustibles
    }
    return render(request, 'TemplatesFlota/chofer_ver_combustible.html', context)

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
        patente_vehiculo = request.POST.get('vehiculo') 
        
        tipo_combustible = request.POST.get('tipo_combustible')
        fecha_recarga = request.POST.get('fecha_recarga')
        lugar = request.POST.get('lugar')
        cantidad_estanque = request.POST.get('cantidad_estanque')
        recargar = request.POST.get('recargar')

        if not patente_vehiculo:
            messages.error(request, 'Debe seleccionar un vehículo.')
        else:
            try:
                vehiculo_obj = Vehiculo.objects.get(patente=patente_vehiculo)
                
                Combustible.objects.create(
                    vehiculo=vehiculo_obj,
                    Tipo_Combustible=tipo_combustible,
                    Fecha_Recarga=fecha_recarga,
                    Lugar=lugar,
                    Cantidad_Estanque=cantidad_estanque,
                    Recargar=recargar
                )
                messages.success(request, 'Registro de combustible agregado correctamente')
                return redirect('mecanico_ver_combustible')

            except Vehiculo.DoesNotExist:
                messages.error(request, 'El vehículo seleccionado no existe.')
            except Exception as e:
                messages.error(request, f'Ocurrió un error inesperado: {e}')

    context = {
        'todos_los_vehiculos': Vehiculo.objects.all()
    }
    return render(request, 'TemplatesFlota/mecanico_agregar_combustible.html', context)

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
    
    mecanico_actual = None
    try:
        username = request.session.get('username')
        usuario_actual = Usuario.objects.get(username=username)
        mecanico_actual = usuario_actual.mecanico 
    except (Usuario.DoesNotExist, Mecanico.DoesNotExist, AttributeError):
        messages.error(request, 'No se pudo encontrar tu perfil de mecánico.')
        return redirect('mecanico_dashboard')

    if request.method == 'POST':
        patente_vehiculo = request.POST.get('vehiculo')
        tipo_mantencion = request.POST.get('tipo_mantencion')
        fecha = request.POST.get('fecha')
        lugar = request.POST.get('lugar')
        descripcion = request.POST.get('descripcion')

        if not patente_vehiculo:
            messages.error(request, 'Debes seleccionar un vehículo.')
        else:
            try:
                vehiculo_obj = Vehiculo.objects.get(patente=patente_vehiculo)
                
                Mantencion.objects.create(
                    vehiculo=vehiculo_obj,
                    mecanico=mecanico_actual,
                    Tipo_Mantencion=tipo_mantencion,
                    Lugar=lugar,
                    Fecha=fecha,
                    Descripcion=descripcion
                )
                messages.success(request, 'Mantención agregada correctamente')
                return redirect('mecanico_ver_mantenciones')
            
            except Vehiculo.DoesNotExist:
                 messages.error(request, 'El vehículo seleccionado no existe.')
            except Exception as e:
                 messages.error(request, f'Ocurrió un error inesperado: {e}')
    
    context = {
        'todos_los_vehiculos': Vehiculo.objects.all()
    }
    return render(request, 'TemplatesFlota/mecanico_agregar_mantencion.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_ver_mantenciones(request):
    
    lista_mantenciones = []
    
    try:
        username = request.session.get('username')
        usuario_actual = Usuario.objects.get(username=username)
        mecanico_actual = usuario_actual.mecanico
        
        lista_mantenciones = Mantencion.objects.filter(
            mecanico=mecanico_actual
        ).select_related('vehiculo').order_by('-Fecha')
        
    except (Usuario.DoesNotExist, Mecanico.DoesNotExist, AttributeError):
        messages.error(request, 'No se pudo encontrar tu perfil de mecánico.')
        return redirect('mecanico_dashboard')

    context = {
        'mantenciones': lista_mantenciones
    }
    return render(request, 'TemplatesFlota/mecanico_ver_mantenciones.html', context)

# Clases de los models.

def ChoferData(request):
    Chofer = Chofer.objects.all()
    data = {'Chofer' : Chofer}
    return render(request, 'chofer.html', data)

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

