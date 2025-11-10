from django.core.exceptions import ValidationError
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Vehiculo, Chofer, Combustible, Mantencion, Mecanico, Usuario, TipoVehiculo


def debug_users(request):
    """Vista temporal para diagnosticar usuarios"""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    print("=== DEBUG USUARIOS ===")
    print("Usuarios en auth:")
    for user in User.objects.all():
        print(f"- {user.username} (cargo: {getattr(user, 'cargo', 'NO TIENE')})")
    
    print("\nUsuario actual:", request.user if request.user.is_authenticated else "No autenticado")
    
    return redirect('login')

# ================================================================
# 🔒 DECORADORES PERSONALIZADOS
# ================================================================

def requiere_autenticacion(view_func):
    """Verifica si hay sesión activa en request.session"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_autenticado'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def requiere_tipo_usuario(tipos_permitidos):
    """Restringe el acceso según el tipo de usuario"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            tipo_usuario = request.session.get('tipo_usuario')
            if tipo_usuario not in tipos_permitidos:
                return HttpResponse("No tienes permisos para acceder a esta página", status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ================================================================
# 🧩 LOGIN
# ================================================================

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            try:
                usuario_personalizado = Usuario.objects.get(username=username)
                
                # ✅ VERIFICAR Y CREAR CHOFER SI NO EXISTE (CON CAMPOS CORRECTOS)
                if usuario_personalizado.cargo == 'chofer':
                    try:
                        # Intentar encontrar el chofer
                        chofer = Chofer.objects.get(usuario=usuario_personalizado)
                        print(f"✅ Chofer encontrado: {chofer.Nombre}")
                    except Chofer.DoesNotExist:
                        print(f"⚠️ Chofer no encontrado, creando uno...")
                        # Crear chofer automáticamente con campos CORRECTOS
                        chofer = Chofer.objects.create(
                            usuario=usuario_personalizado,
                            RUT_Chofer=f"11.111.111-{usuario_personalizado.username[:1]}",  # RUT temporal
                            Nombre=usuario_personalizado.first_name or usuario_personalizado.username,
                            Telefono="+56912345678",  # Teléfono temporal
                            Estado='Activo',
                            Taller='Principal',
                            Horas='0'
                        )
                        print(f"✅ Chofer creado: {chofer.Nombre}")
                
            except Usuario.DoesNotExist:
                messages.error(request, 'Error en la base de datos de usuarios.')
                return redirect('login')
            
            request.session['usuario_autenticado'] = True
            request.session['nombre_usuario'] = usuario_personalizado.first_name or usuario_personalizado.username
            request.session['tipo_usuario'] = usuario_personalizado.cargo
            request.session['username'] = username

            # Redirigir según el cargo
            if usuario_personalizado.cargo == 'admin':
                return redirect('admin_dashboard')
            elif usuario_personalizado.cargo == 'chofer':
                return redirect('chofer_dashboard')
            elif usuario_personalizado.cargo == 'mecanico':
                return redirect('mecanico_dashboard')
            else:
                messages.error(request, f'Cargo no reconocido: {usuario_personalizado.cargo}')
                return redirect('login')

        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return redirect('login')

    return render(request, 'TemplatesFlota/login.html')


# ================================================================
# 🧭 DASHBOARDS
# ================================================================

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_dashboard(request):
    # Obtener datos dinámicos para el dashboard
    vehiculos_activos = Vehiculo.objects.count()
    conductores_ruta = Chofer.objects.filter(Estado='Activo').count()
    
    context = {
        'nombre_usuario': request.session.get('nombre_usuario'),
        'vehiculos_activos': vehiculos_activos,
        'conductores_ruta': conductores_ruta,
        'title': 'Dashboard - ControlFlota'
    }
    return render(request, 'TemplatesFlota/admin_dashboard.html', context)


@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_dashboard(request):
    """Dashboard principal para el chofer"""
    try:
        # Obtener el usuario actual
        usuario_actual = request.user
        
        # Buscar el chofer relacionado con este usuario
        try:
            chofer = Chofer.objects.get(usuario=usuario_actual)
        except Chofer.DoesNotExist:
            # Si no existe, crear uno automáticamente con campos CORRECTOS
            chofer = Chofer.objects.create(
                usuario=usuario_actual,
                RUT_Chofer=f"11.111.111-{usuario_actual.username[:1]}",  # RUT temporal
                Nombre=usuario_actual.first_name or usuario_actual.username,
                Telefono="+56912345678",
                Estado='Activo',
                Taller='Principal', 
                Horas='0'
            )
            print(f"✅ Chofer creado automáticamente: {chofer.Nombre}")
        
        # Obtener vehículos asignados a este chofer
        vehiculos = Vehiculo.objects.filter(chofer_asignado=chofer)
        total_vehiculos = vehiculos.count()
        
        # Contar vehículos con documentación al día
        vehiculos_documentados = vehiculos.filter(
            seguro=True,
            revision_tecnica=True,
            permiso_circulacion=True
        ).count()
        
        context = {
            'chofer': chofer,
            'total_vehiculos': total_vehiculos,
            'vehiculos_documentados': vehiculos_documentados,
            'vehiculos': vehiculos
        }
        return render(request, 'TemplatesFlota/chofer_dashboard.html', context)
        
    except Exception as e:
        print(f"❌ Error en chofer_dashboard: {str(e)}")
        messages.error(request, f'❌ Error al cargar el dashboard: {str(e)}')
        return redirect('login')

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_dashboard(request):
    return render(request, 'TemplatesFlota/mecanico_dashboard.html', {
        'nombre_usuario': request.session.get('nombre_usuario')
    })


# ================================================================
# 🚪 LOGOUT
# ================================================================

def logout_view(request):
    """Cierra sesión completamente"""
    request.session.flush()
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')


# ================================================================
# 🔧 VISTAS DE ADMIN
# ================================================================

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_agregar_chofer(request):
    """Vista para agregar un nuevo chofer y su cuenta de usuario."""
    context = {
        'today': timezone.now().date()
    }
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email_usuario = request.POST.get('email_usuario')
        nombre = request.POST.get('nombre')  # Este es el nombre del chofer
        rut_chofer = request.POST.get('RUTChofer')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        telefono = request.POST.get('telefono')
        estado = request.POST.get('estado')
        horas = request.POST.get('horas')

        try:
            # ✅ CORREGIDO: Usar first_name en lugar de nombre
            nuevo_usuario = Usuario.objects.create_user(
                username=username,
                password=password,
                email=email_usuario,
                first_name=nombre,  # ← CAMBIA 'nombre' por 'first_name'
                cargo='chofer'
            )
            
            chofer = Chofer(
                usuario=nuevo_usuario,
                RUTChofer=rut_chofer,
                Nombre=nombre,  # ← Este sí se queda igual (es del modelo Chofer)
                Fecha_Nacimiento=fecha_nacimiento,
                Telefono=telefono,
                Estado=estado,
                Horas=horas,
            )
            
            chofer.full_clean()
            chofer.save()
            
            messages.success(request, 'Chofer y cuenta de usuario creados correctamente')
            return redirect('admin_ver_chofers')
        
        except IntegrityError:
            messages.error(request, f'Error: El nombre de usuario "{username}" ya existe.')
        except ValidationError as e:
            for field, errors in e.error_dict.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        except Exception as e:
            messages.error(request, f'Error al agregar chofer: {e}')
            pass

    return render(request, 'TemplatesFlota/admin_agregar_chofer.html', context)


@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_chofers(request):
    chofers = Chofer.objects.all()
    
    try:
        conductores_activos = chofers.filter(Estado='Activo').count()
        conductores_viaje = chofers.filter(Estado='En Viaje').count()
    except:
        conductores_activos = chofers.count()
        conductores_viaje = 0
    
    context = {
        'chofers': chofers,
        'conductores_activos': conductores_activos,
        'conductores_viaje': conductores_viaje,
        'vehiculos_sin_conductor': Vehiculo.objects.filter(chofer_asignado__isnull=True).count(),
    }
    return render(request, 'TemplatesFlota/admin_ver_chofers.html', context)


@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_agregar_vehiculo(request):
    from datetime import datetime
    from django.core.exceptions import ValidationError
    from django.db import IntegrityError
    import re
    
    # Calcular año máximo para el template
    max_year = datetime.now().year + 2
    
    if request.method == 'POST':
        print("🔍 DEBUG: Iniciando procesamiento POST")
        
        # INICIALIZAR TODAS LAS VARIABLES AL PRINCIPIO
        patente = vin = marca = modelo = motor = ""
        año_int = kilometraje_int = 0
        estanque_float = tonelaje_float = None
        seguro_val = revision_val = permiso_val = gps_val = False
        tipo_obj = chofer_obj = None
        
        try:
            # Obtener TODOS los datos del formulario primero
            patente = request.POST.get('patente', '').upper().strip()
            vin = request.POST.get('vin', '').upper().strip()
            marca = request.POST.get('marca', '').strip()
            modelo = request.POST.get('modelo', '').strip()
            año = request.POST.get('año')
            motor = request.POST.get('motor', '').strip()
            kilometraje = request.POST.get('kilometraje') or 0
            estanque = request.POST.get('estanque')
            tonelaje = request.POST.get('tonelaje')
            tipo_id = request.POST.get('tipo')
            chofer_id = request.POST.get('chofer_asignado')

            # Procesar checkboxes
            seguro_val = request.POST.get('seguro') == 'on'
            revision_val = request.POST.get('revision_tecnica') == 'on'
            permiso_val = request.POST.get('permiso_circulacion') == 'on'
            gps_val = request.POST.get('gps') == 'on'
            
            print(f"🔍 DEBUG: Datos recibidos - Patente: {patente}, VIN: {vin}, Marca: {marca}, Modelo: {modelo}, Año: {año}, Estanque: {estanque}")

            # Validaciones básicas
            if not patente:
                messages.error(request, '❌ La patente es obligatoria')
                raise ValidationError('Patente requerida')
                
            if not vin:
                messages.error(request, '❌ El VIN es obligatorio')
                raise ValidationError('VIN requerido')
                
            if not marca:
                messages.error(request, '❌ La marca es obligatoria')
                raise ValidationError('Marca requerida')
                
            if not modelo:
                messages.error(request, '❌ El modelo es obligatorio')
                raise ValidationError('Modelo requerido')
                
            if not año:
                messages.error(request, '❌ El año es obligatorio')
                raise ValidationError('Año requerido')
                
            if not estanque:
                messages.error(request, '❌ La capacidad del estanque es obligatoria')
                raise ValidationError('Estanque requerido')
                
            if not tipo_id:
                messages.error(request, '❌ El tipo de vehículo es obligatorio')
                raise ValidationError('Tipo de vehículo requerido')

            # Validar formato de patente CHILENA (4 letras + 2 números)
            patente_pattern = r'^[A-Z]{4}\d{2}$'
            if not re.match(patente_pattern, patente):
                messages.error(request, '❌ Formato de patente inválido. Use: ABCD12 (4 letras + 2 números)')
                raise ValidationError('Formato de patente inválido')

            # Validar formato de VIN
            vin_pattern = r'^[A-HJ-NPR-Z0-9]{17}$'
            if not re.match(vin_pattern, vin):
                messages.error(request, '❌ VIN debe tener 17 caracteres alfanuméricos (excluyendo I, O, Q)')
                raise ValidationError('Formato de VIN inválido')

            # Validar año
            try:
                año_int = int(año)
                if año_int < 1900 or año_int > max_year:
                    messages.error(request, f'❌ El año debe estar entre 1900 y {max_year}')
                    raise ValidationError('Año fuera de rango')
            except ValueError:
                messages.error(request, '❌ El año debe ser un número válido')
                raise ValidationError('Año inválido')

            # Validar capacidad estanque
            try:
                estanque_float = float(estanque)
                if estanque_float < 1 or estanque_float > 500:
                    messages.error(request, '❌ La capacidad del estanque debe estar entre 1 y 500 litros')
                    raise ValidationError('Capacidad de estanque fuera de rango')
            except ValueError:
                messages.error(request, '❌ La capacidad del estanque debe ser un número válido')
                raise ValidationError('Estanque inválido')

            # Validar kilometraje
            try:
                kilometraje_int = int(kilometraje)
                if kilometraje_int < 0 or kilometraje_int > 1000000:
                    messages.error(request, '❌ El kilometraje debe estar entre 0 y 1,000,000 km')
                    raise ValidationError('Kilometraje fuera de rango')
            except ValueError:
                messages.error(request, '❌ El kilometraje debe ser un número válido')
                raise ValidationError('Kilometraje inválido')

            # Validar tonelaje si se proporciona
            if tonelaje:
                try:
                    tonelaje_float = float(tonelaje)
                    if tonelaje_float < 0.1 or tonelaje_float > 100:
                        messages.error(request, '❌ El tonelaje debe estar entre 0.1 y 100 toneladas')
                        raise ValidationError('Tonelaje fuera de rango')
                except ValueError:
                    messages.error(request, '❌ El tonelaje debe ser un número válido')
                    raise ValidationError('Tonelaje inválido')

            # Obtener objetos relacionados
            tipo_obj = TipoVehiculo.objects.get(pk=tipo_id)
            
            if chofer_id:
                chofer_obj = Chofer.objects.get(pk=chofer_id)

            # Verificar si la patente ya existe
            if Vehiculo.objects.filter(patente=patente).exists():
                messages.error(request, f'❌ Ya existe un vehículo con la patente {patente}')
                raise ValidationError('Patente duplicada')

            # Verificar si el VIN ya existe
            if Vehiculo.objects.filter(VIN=vin).exists():
                messages.error(request, '❌ Ya existe un vehículo con este VIN')
                raise ValidationError('VIN duplicado')

            print("🔍 DEBUG: Todas las validaciones pasaron")
            
            # Crear el vehículo
            vehiculo = Vehiculo(
                patente=patente,
                VIN=vin,
                marca=marca,
                modelo=modelo,
                año=año_int,
                motor=motor,
                kilometraje=kilometraje_int,
                estanque=estanque_float,
                tonelaje=tonelaje_float,
                
                seguro=seguro_val,
                revision_tecnica=revision_val,
                permiso_circulacion=permiso_val,
                gps=gps_val,

                Tipo=tipo_obj,
                chofer_asignado=chofer_obj
            )

            print("🔍 DEBUG: Objeto Vehiculo creado, intentando guardar...")
            
            # Validar el modelo antes de guardar
            vehiculo.full_clean()
            vehiculo.save()
            
            print("🔍 DEBUG: ✅ Vehículo guardado exitosamente en la base de datos")
            
            messages.success(request, f'✅ Vehículo {patente} agregado correctamente')
            return redirect('admin_ver_vehiculos')
        
        except ValidationError as e:
            print(f"🔍 DEBUG: ❌ Error de validación: {str(e)}")
            # Los mensajes ya se agregaron arriba
            pass
        except TipoVehiculo.DoesNotExist:
            messages.error(request, '❌ El tipo de vehículo seleccionado no existe')
            print("🔍 DEBUG: ❌ Tipo de vehículo no existe")
        except Chofer.DoesNotExist:
            messages.error(request, '❌ El chofer seleccionado no existe')
            print("🔍 DEBUG: ❌ Chofer no existe")
        except IntegrityError as e:
            print(f"🔍 DEBUG: ❌ Error de integridad: {str(e)}")
            if 'patente' in str(e).lower():
                messages.error(request, f'❌ Ya existe un vehículo con la patente {patente}')
            elif 'vin' in str(e).lower():
                messages.error(request, '❌ Ya existe un vehículo con este VIN')
            else:
                messages.error(request, f'❌ Error de integridad en la base de datos: {str(e)}')
        except Exception as e:
            print(f"🔍 DEBUG: ❌ Error inesperado: {str(e)}")
            print(f"🔍 DEBUG: Tipo de error: {type(e).__name__}")
            messages.error(request, f'❌ Error al agregar vehículo: {str(e)}')

    context = {
        'tipos_vehiculo': TipoVehiculo.objects.all(),
        'choferes': Chofer.objects.all(),
        'max_year': max_year,
    }
    return render(request, 'TemplatesFlota/admin_agregar_vehiculo.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_vehiculos(request):
    vehiculos = Vehiculo.objects.select_related('Tipo', 'chofer_asignado').all()
    
    context = {
        'vehiculos': vehiculos,
        'total_vehiculos': vehiculos.count(),
        'vehiculos_con_chofer': vehiculos.filter(chofer_asignado__isnull=False).count(),
        'vehiculos_sin_chofer': vehiculos.filter(chofer_asignado__isnull=True).count(),
        'vehiculos_con_seguro': vehiculos.filter(seguro=True).count(),
    }
    return render(request, 'TemplatesFlota/admin_ver_vehiculos.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_combustible(request):
    combustibles = Combustible.objects.select_related('vehiculo').all()
    
    total_litros = 0
    for c in combustibles:
        if c.Cantidad_Estanque:
            try:
                total_litros += float(c.Cantidad_Estanque)
            except (TypeError, ValueError):
                pass
    
    context = {
        'combustibles': combustibles,
        'total_litros': total_litros,
        'recargas_mes': combustibles.filter(Fecha_Recarga__month=timezone.now().month).count(),
        'vehiculos_activos': Vehiculo.objects.filter(chofer_asignado__isnull=False).count(),
    }
    return render(request, 'TemplatesFlota/admin_ver_combustible.html', context)


@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_mantenciones(request):
    from datetime import date
    
    mantenciones = Mantencion.objects.all().order_by('-Fecha')
    
    # Estadísticas
    total_mantenciones = mantenciones.count()
    mantenciones_preventivas = mantenciones.filter(Tipo_Mantencion='Preventiva').count()
    mantenciones_mes = mantenciones.filter(
        Fecha__month=date.today().month,
        Fecha__year=date.today().year
    ).count()
    
    context = {
        'mantenciones': mantenciones,
        'total_mantenciones': total_mantenciones,
        'mantenciones_preventivas': mantenciones_preventivas,
        'mantenciones_mes': mantenciones_mes,
    }
    return render(request, 'TemplatesFlota/admin_ver_mantenciones.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_editar_mantencion(request, id):
    mantencion = get_object_or_404(Mantencion, ID_Mantencion=id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            vehiculo_patente = request.POST.get('vehiculo')
            mecanico_rut = request.POST.get('mecanico')
            tipo_mantencion = request.POST.get('Tipo_Mantencion')
            fecha = request.POST.get('Fecha')
            lugar = request.POST.get('Lugar', '').strip()
            descripcion = request.POST.get('Descripcion', '').strip()

            # Validaciones
            if not descripcion:
                messages.error(request, '❌ La descripción es obligatoria')
                raise ValidationError('Descripción requerida')

            # Validar longitud de descripción
            if len(descripcion) < 10:
                messages.error(request, '❌ La descripción debe tener al menos 10 caracteres')
                raise ValidationError('Descripción muy corta')

            # Obtener objetos relacionados
            vehiculo = Vehiculo.objects.get(patente=vehiculo_patente)
            mecanico = Mecanico.objects.get(RUT_Mecanico=mecanico_rut)

            # Actualizar mantencion
            mantencion.vehiculo = vehiculo
            mantencion.mecanico = mecanico
            mantencion.Tipo_Mantencion = tipo_mantencion
            mantencion.Fecha = fecha
            mantencion.Lugar = lugar
            mantencion.Descripcion = descripcion
            
            mantencion.full_clean()
            mantencion.save()
            
            messages.success(request, f'✅ Mantención actualizada correctamente')
            return redirect('admin_ver_mantenciones')
        
        except Vehiculo.DoesNotExist:
            messages.error(request, '❌ El vehículo seleccionado no existe')
        except Mecanico.DoesNotExist:
            messages.error(request, '❌ El mecánico seleccionado no existe')
        except ValidationError as e:
            print(f"🔍 DEBUG: ❌ Error de validación: {str(e)}")
        except Exception as e:
            print(f"🔍 DEBUG: ❌ Error inesperado: {str(e)}")
            messages.error(request, f'❌ Error al actualizar mantencion: {str(e)}')

    context = {
        'mantencion': mantencion,
        'vehiculos': Vehiculo.objects.all(),
        'mecanicos': Mecanico.objects.all(),
        'tipos_mantencion': ['Preventiva', 'Correctiva', 'Predictiva', 'Programada']
    }
    return render(request, 'TemplatesFlota/admin_editar_mantencion.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_eliminar_mantencion(request, id):
    mantencion = get_object_or_404(Mantencion, ID_Mantencion=id)
    
    if request.method == 'POST':
        try:
            mantencion.delete()
            messages.success(request, '✅ Mantención eliminada correctamente')
            return redirect('admin_ver_mantenciones')
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar mantencion: {str(e)}')
    
    context = {'mantencion': mantencion}
    return render(request, 'TemplatesFlota/admin_eliminar_mantencion.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_agregar_mantencion(request):
    from django.core.exceptions import ValidationError
    from datetime import date
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            vehiculo_patente = request.POST.get('vehiculo')
            mecanico_rut = request.POST.get('mecanico')
            tipo_mantencion = request.POST.get('Tipo_Mantencion')
            fecha = request.POST.get('Fecha')
            lugar = request.POST.get('Lugar', '').strip()
            descripcion = request.POST.get('Descripcion', '').strip()

            print(f"🔍 DEBUG: Creando mantencion - Vehículo: {vehiculo_patente}, Mecánico: {mecanico_rut}")

            # Validaciones básicas
            if not vehiculo_patente:
                messages.error(request, '❌ El vehículo es obligatorio')
                raise ValidationError('Vehículo requerido')
                
            if not mecanico_rut:
                messages.error(request, '❌ El mecánico es obligatorio')
                raise ValidationError('Mecánico requerido')
                
            if not tipo_mantencion:
                messages.error(request, '❌ El tipo de mantencion es obligatorio')
                raise ValidationError('Tipo de mantencion requerido')
                
            if not fecha:
                messages.error(request, '❌ La fecha es obligatoria')
                raise ValidationError('Fecha requerida')
                
            if not descripcion:
                messages.error(request, '❌ La descripción es obligatoria')
                raise ValidationError('Descripción requerida')

            # Validar longitud de descripción
            if len(descripcion) < 10:
                messages.error(request, '❌ La descripción debe tener al menos 10 caracteres')
                raise ValidationError('Descripción muy corta')

            # Obtener objetos relacionados
            vehiculo = Vehiculo.objects.get(patente=vehiculo_patente)
            mecanico = Mecanico.objects.get(RUT_Mecanico=mecanico_rut)

            print("🔍 DEBUG: Todas las validaciones pasadas")
            
            # Crear la mantencion
            mantencion = Mantencion(
                vehiculo=vehiculo,
                mecanico=mecanico,
                Tipo_Mantencion=tipo_mantencion,
                Fecha=fecha,
                Lugar=lugar,
                Descripcion=descripcion
            )

            print("🔍 DEBUG: Objeto Mantencion creado, intentando guardar...")
            
            # Validar el modelo antes de guardar
            mantencion.full_clean()
            mantencion.save()
            
            print("🔍 DEBUG: ✅ Mantencion guardada exitosamente")
            
            messages.success(request, f'✅ Mantención agregada correctamente')
            return redirect('admin_ver_mantenciones')
        
        except Vehiculo.DoesNotExist:
            messages.error(request, '❌ El vehículo seleccionado no existe')
            print("🔍 DEBUG: ❌ Vehículo no existe")
        except Mecanico.DoesNotExist:
            messages.error(request, '❌ El mecánico seleccionado no existe')
            print("🔍 DEBUG: ❌ Mecánico no existe")
        except ValidationError as e:
            print(f"🔍 DEBUG: ❌ Error de validación: {str(e)}")
            pass
        except Exception as e:
            print(f"🔍 DEBUG: ❌ Error inesperado: {str(e)}")
            messages.error(request, f'❌ Error al agregar mantencion: {str(e)}')

    context = {
        'vehiculos': Vehiculo.objects.all(),
        'mecanicos': Mecanico.objects.filter(Estado='Activo'),
        'tipos_mantencion': ['Preventiva', 'Correctiva', 'Predictiva', 'Programada'],
        'fecha_hoy': date.today().strftime('%Y-%m-%d')
    }
    return render(request, 'TemplatesFlota/admin_agregar_mantencion.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_agregar_mecanico(request):
    from django.core.exceptions import ValidationError
    from datetime import datetime
    import re
    
    if request.method == 'POST':
        try:
            # Datos de cuenta (Usuario)
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            email = request.POST.get('email', '').strip()
            
            # Datos personales (Mecánico)
            rut = request.POST.get('RUT_Mecanico', '').upper().strip()
            nombre = request.POST.get('Nombre', '').strip()
            fecha_nacimiento = request.POST.get('Fecha_Nacimiento')
            telefono = request.POST.get('Telefono', '').strip()
            estado = request.POST.get('Estado')
            taller = request.POST.get('Taller', '').strip()
            horas = request.POST.get('Horas', '0').strip()

            print(f"🔍 DEBUG: Creando mecánico - Usuario: {username}, RUT: {rut}")

            # Validaciones de cuenta
            if not username:
                messages.error(request, '❌ El username es obligatorio')
                raise ValidationError('Username requerido')
                
            if not password or len(password) < 8:
                messages.error(request, '❌ La contraseña debe tener al menos 8 caracteres')
                raise ValidationError('Contraseña inválida')

            # Validaciones de mecánico
            if not rut:
                messages.error(request, '❌ El RUT es obligatorio')
                raise ValidationError('RUT requerido')
                
            if not nombre:
                messages.error(request, '❌ El nombre es obligatorio')
                raise ValidationError('Nombre requerido')

            # Verificar si el username ya existe
            if Usuario.objects.filter(username=username).exists():
                messages.error(request, f'❌ Ya existe un usuario con el username {username}')
                raise ValidationError('Username duplicado')

            # Verificar si el RUT ya existe
            if Mecanico.objects.filter(RUT_Mecanico=rut).exists():
                messages.error(request, f'❌ Ya existe un mecánico con el RUT {rut}')
                raise ValidationError('RUT duplicado')

            print("🔍 DEBUG: Todas las validaciones pasadas")
            
            # Crear el Usuario primero - VERSIÓN CORREGIDA
            usuario = Usuario.objects.create_user(
                username=username,
                password=password,
                email=email if email else None  # Email opcional
            )
            
            # Si tu modelo Usuario tiene un campo para tipo, actualízalo aquí
            # Por ejemplo, si tienes un campo 'rol' o 'tipo':
            # usuario.rol = 'mecanico'
            # usuario.save()
            
            # Crear el Mecánico vinculado al Usuario
            mecanico = Mecanico(
                usuario=usuario,  # Vinculamos el usuario creado
                RUT_Mecanico=rut,
                Nombre=nombre,
                Fecha_Nacimiento=fecha_nacimiento,
                Telefono=telefono,
                Estado=estado,
                Taller=taller,
                Horas=horas
            )

            print("🔍 DEBUG: Objetos creados, intentando guardar...")
            
            # Validar y guardar
            mecanico.full_clean()
            mecanico.save()
            
            print("🔍 DEBUG: ✅ Mecánico y Usuario creados exitosamente")
            
            messages.success(request, f'✅ Mecánico {nombre} agregado correctamente')
            return redirect('admin_ver_mecanicos')
        
        except ValidationError as e:
            print(f"🔍 DEBUG: ❌ Error de validación: {str(e)}")
            pass
        except IntegrityError as e:
            print(f"🔍 DEBUG: ❌ Error de integridad: {str(e)}")
            messages.error(request, f'❌ Error de integridad en la base de datos: {str(e)}')
        except Exception as e:
            print(f"🔍 DEBUG: ❌ Error inesperado: {str(e)}")
            print(f"🔍 DEBUG: Tipo de error: {type(e).__name__}")
            import traceback
            print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
            messages.error(request, f'❌ Error al agregar mecánico: {str(e)}')

    # Calcular fechas para el template
    from datetime import date
    hoy = date.today()
    max_date = hoy.replace(year=hoy.year - 18)  # Mínimo 18 años
    min_date = hoy.replace(year=hoy.year - 80)  # Máximo 80 años

    context = {
        'max_date': max_date,
        'min_date': min_date,
        'estados': ['Activo', 'Inactivo', 'Vacaciones', 'Licencia']
    }
    return render(request, 'TemplatesFlota/admin_agregar_mecanico.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_ver_mecanicos(request):
    mecanicos = Mecanico.objects.all()
    
    # Estadísticas
    total_mecanicos = mecanicos.count()
    mecanicos_activos = mecanicos.filter(Estado='Activo').count()
    # Para total_mantenimientos necesitaríamos el modelo Mantenimiento
    
    context = {
        'mecanicos': mecanicos,
        'total_mecanicos': total_mecanicos,
        'mecanicos_activos': mecanicos_activos,
        'total_mantenimientos': 0,  # Temporal hasta tener modelo Mantenimiento
    }
    return render(request, 'TemplatesFlota/admin_ver_mecanicos.html', context)


@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_editar_mecanico(request, rut):
    mecanico = get_object_or_404(Mecanico, RUT_Mecanico=rut)
    
    if request.method == 'POST':
        try:
            import re
            # Obtener datos del formulario
            nombre = request.POST.get('Nombre', '').strip()
            fecha_nacimiento = request.POST.get('Fecha_Nacimiento')
            telefono = request.POST.get('Telefono', '').strip()
            estado = request.POST.get('Estado')
            taller = request.POST.get('Taller', '').strip()
            horas = request.POST.get('Horas', '0').strip()

            # Validaciones
            if not nombre:
                messages.error(request, '❌ El nombre es obligatorio')
                raise ValidationError('Nombre requerido')
                
            if not fecha_nacimiento:
                messages.error(request, '❌ La fecha de nacimiento es obligatoria')
                raise ValidationError('Fecha de nacimiento requerida')

            # Validar formato de teléfono
            telefono_pattern = r'^\+56 9 \d{4} \d{4}$|^9\d{8}$|^\d{9}$'
            if telefono and not re.match(telefono_pattern, telefono):
                messages.error(request, '❌ Formato de teléfono inválido. Use: 912345678 o +56 9 1234 5678')
                raise ValidationError('Teléfono inválido')

            # Validar horas
            horas_pattern = r'^\d{1,3}$'
            if horas and not re.match(horas_pattern, horas):
                messages.error(request, '❌ Las horas deben ser un número entre 0 y 999')
                raise ValidationError('Horas inválidas')

            # Actualizar mecánico
            mecanico.Nombre = nombre
            mecanico.Fecha_Nacimiento = fecha_nacimiento
            mecanico.Telefono = telefono
            mecanico.Estado = estado
            mecanico.Taller = taller
            mecanico.Horas = horas
            
            mecanico.full_clean()
            mecanico.save()
            
            messages.success(request, f'✅ Mecánico {nombre} actualizado correctamente')
            return redirect('admin_ver_mecanicos')
        
        except ValidationError as e:
            print(f"🔍 DEBUG: ❌ Error de validación: {str(e)}")
        except Exception as e:
            print(f"🔍 DEBUG: ❌ Error inesperado: {str(e)}")
            messages.error(request, f'❌ Error al actualizar mecánico: {str(e)}')

    # Calcular fechas para el template
    from datetime import date
    hoy = date.today()
    max_date = hoy.replace(year=hoy.year - 18)
    min_date = hoy.replace(year=hoy.year - 80)

    context = {
        'mecanico': mecanico,
        'max_date': max_date,
        'min_date': min_date,
        'estados': ['Activo', 'Inactivo', 'Vacaciones', 'Licencia']
    }
    return render(request, 'TemplatesFlota/admin_editar_mecanico.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_eliminar_mecanico(request, rut):
    mecanico = get_object_or_404(Mecanico, RUT_Mecanico=rut)
    
    if request.method == 'POST':
        try:
            nombre = mecanico.Nombre
            mecanico.delete()
            messages.success(request, f'✅ Mecánico {nombre} eliminado correctamente')
            return redirect('admin_ver_mecanicos')
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar mecánico: {str(e)}')
    
    context = {'mecanico': mecanico}
    return render(request, 'TemplatesFlota/admin_eliminar_mecanico.html', context)


@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_agregar_tipo_vehiculo(request):
    if request.method == 'POST':
        nombre_tipo = request.POST.get('nombre')
        
        if nombre_tipo:
            try:
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
    tipos_vehiculo = TipoVehiculo.objects.all().order_by('nombre')
    
    # Estadísticas
    total_tipos = tipos_vehiculo.count()
    
    # Contar vehículos por tipo
    vehiculos_por_tipo = {}
    total_vehiculos = 0
    
    for tipo in tipos_vehiculo:
        count = tipo.vehiculos.count()
        vehiculos_por_tipo[tipo.nombre] = count
        total_vehiculos += count
    
    context = {
        'tipos_vehiculo': tipos_vehiculo,
        'total_tipos': total_tipos,
        'total_vehiculos': total_vehiculos,
        'vehiculos_por_tipo': vehiculos_por_tipo,
    }
    return render(request, 'TemplatesFlota/admin_ver_tipos_vehiculo.html', context)


# ================================================================
# 👨‍✈️ VISTAS DE CHOFER
# ================================================================

@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_ver_vehiculos(request):
    """Vista para que el chofer vea sus vehículos asignados"""
    try:
        # Obtener el chofer asociado al usuario
        chofer = request.user.chofer
        # Obtener vehículos asignados a este chofer
        vehiculos = Vehiculo.objects.filter(chofer_asignado=chofer)
        
        context = {
            'vehiculos': vehiculos,
            'chofer': chofer
        }
        return render(request, 'TemplatesFlota/chofer_ver_vehiculos.html', context)
        
    except Chofer.DoesNotExist:
        messages.error(request, '❌ No se encontró información del chofer')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'❌ Error al cargar los vehículos: {str(e)}')
        return redirect('login')
    
@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_ver_detalle_vehiculo(request, patente):
    """Vista para que el chofer vea los detalles de un vehículo específico"""
    try:
        chofer = request.user.chofer
        # Verificar que el vehículo esté asignado a este chofer
        vehiculo = get_object_or_404(Vehiculo, patente=patente, chofer_asignado=chofer)
        
        context = {
            'vehiculo': vehiculo,
            'chofer': chofer
        }
        return render(request, 'TemplatesFlota/chofer_detalle_vehiculo.html', context)
        
    except Vehiculo.DoesNotExist:
        messages.error(request, '❌ Vehículo no encontrado o no asignado a usted')
        return redirect('chofer_ver_vehiculos')


@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_agregar_combustible(request):
    vehiculos_del_chofer = []
    try:
        username = request.session.get('username')
        usuario_actual = Usuario.objects.get(username=username)
        chofer_actual = usuario_actual.chofer
        vehiculos_del_chofer = chofer_actual.vehiculos_asignados.all()
    except (Usuario.DoesNotExist, Chofer.DoesNotExist, AttributeError):
        messages.error(request, 'No se pudo encontrar su perfil de chofer.')
        return redirect('chofer_dashboard')

    if request.method == 'POST':
        tipo_combustible = request.POST.get('tipo_combustible')
        fecha_recarga = request.POST.get('fecha_recarga')
        lugar = request.POST.get('lugar')
        patente_vehiculo = request.POST.get('vehiculo')
        cantidad_estanque = request.POST.get('cantidad_estanque')
        recargar = request.POST.get('recargar')

        if not patente_vehiculo:
            messages.error(request, 'Debe seleccionar un vehículo.')
        else:
            try:
                vehiculo_obj = Vehiculo.objects.get(patente=patente_vehiculo)
                
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
        ).order_by('-Fecha_Recarga')
        
    except (Usuario.DoesNotExist, Chofer.DoesNotExist):
        messages.error(request, 'No se pudo encontrar tu perfil de chofer.')
    
    context = {
        'combustibles': lista_combustibles
    }
    return render(request, 'TemplatesFlota/chofer_ver_combustible.html', context)


# ================================================================
# 🔧 VISTAS DE MECÁNICO
# ================================================================

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


# ================================================================
# 🔧 VISTAS PARA EDITAR Y ELIMINAR
# ================================================================


# VEHÍCULOS - Editar

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_editar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, patente=pk)
    
    if request.method == 'POST':
        try:
            print("🔍 DEBUG: Iniciando edición de vehículo")
            print("🔍 DEBUG: Datos POST recibidos:", request.POST.dict())
            
            # Obtener y validar el tipo de vehículo primero
            tipo_id = request.POST.get('tipo')
            print(f"🔍 DEBUG: Tipo ID recibido: '{tipo_id}' (tipo: {type(tipo_id)})")
            
            if not tipo_id:
                messages.error(request, '❌ El tipo de vehículo es obligatorio')
                # Debug adicional
                print("🔍 DEBUG: Todos los campos recibidos:")
                for key, value in request.POST.items():
                    print(f"  {key}: {value}")
                raise ValueError('Tipo de vehículo requerido')
            
            # Obtener el objeto TipoVehiculo
            tipo_obj = TipoVehiculo.objects.get(pk=tipo_id)
            print(f"🔍 DEBUG: Tipo objeto encontrado: {tipo_obj.nombre}")
            
            # Procesar chofer (puede ser None)
            chofer_id = request.POST.get('chofer_asignado')
            chofer_obj = None
            if chofer_id:
                chofer_obj = Chofer.objects.get(pk=chofer_id)

            # Procesar checkboxes
            seguro_val = request.POST.get('seguro') == 'on'
            revision_val = request.POST.get('revision_tecnica') == 'on'
            permiso_val = request.POST.get('permiso_circulacion') == 'on'
            gps_val = request.POST.get('gps') == 'on'
            
            # Validar campos numéricos
            kilometraje = request.POST.get('kilometraje') or 0
            estanque = request.POST.get('estanque')
            tonelaje = request.POST.get('tonelaje')
            
            if not estanque:
                messages.error(request, '❌ La capacidad del estanque es obligatoria')
                raise ValueError('Estanque requerido')
            
            # Convertir y validar valores numéricos
            try:
                kilometraje_int = int(kilometraje)
                estanque_float = float(estanque)
                tonelaje_float = float(tonelaje) if tonelaje else None
            except (ValueError, TypeError) as e:
                messages.error(request, '❌ Error en los valores numéricos')
                raise ValueError('Valores numéricos inválidos')

            # Actualizar vehículo
            vehiculo.VIN = request.POST.get('vin', '').upper().strip()
            vehiculo.marca = request.POST.get('marca', '').strip()
            vehiculo.modelo = request.POST.get('modelo', '').strip()
            vehiculo.año = request.POST.get('año')
            vehiculo.motor = request.POST.get('motor', '').strip()
            vehiculo.kilometraje = kilometraje_int
            vehiculo.estanque = estanque_float
            vehiculo.tonelaje = tonelaje_float
            
            vehiculo.seguro = seguro_val
            vehiculo.revision_tecnica = revision_val
            vehiculo.permiso_circulacion = permiso_val
            vehiculo.gps = gps_val

            vehiculo.Tipo = tipo_obj
            vehiculo.chofer_asignado = chofer_obj
            
            print("🔍 DEBUG: Todos los datos procesados correctamente")
            
            # Validar el modelo antes de guardar
            vehiculo.full_clean()
            vehiculo.save()
            
            print("🔍 DEBUG: ✅ Vehículo actualizado exitosamente")
            
            messages.success(request, '✅ Vehículo actualizado correctamente')
            return redirect('admin_ver_vehiculos')
        
        except TipoVehiculo.DoesNotExist:
            messages.error(request, '❌ El tipo de vehículo seleccionado no existe')
            print("🔍 DEBUG: ❌ TipoVehiculo.DoesNotExist")
        except Chofer.DoesNotExist:
            messages.error(request, '❌ El chofer seleccionado no existe')
            print("🔍 DEBUG: ❌ Chofer.DoesNotExist")
        except ValueError as e:
            print(f"🔍 DEBUG: ❌ Error de valor: {str(e)}")
            # Los mensajes ya se agregaron arriba
        except Exception as e:
            print(f"🔍 DEBUG: ❌ Error inesperado: {str(e)}")
            print(f"🔍 DEBUG: Tipo de error: {type(e).__name__}")
            messages.error(request, f'❌ Error al actualizar vehículo: {str(e)}')

    # Calcular año máximo para el template
    from datetime import datetime
    max_year = datetime.now().year + 2
    
    # Debug en el contexto - CORREGIDO
    print(f"🔍 DEBUG [GET]: Vehiculo Tipo: {vehiculo.Tipo}")
    print(f"🔍 DEBUG [GET]: Vehiculo Tipo PK: {vehiculo.Tipo.pk}")
    
    context = {
        'vehiculo': vehiculo,
        'tipos_vehiculo': TipoVehiculo.objects.all(),
        'choferes': Chofer.objects.all(),
        'max_year': max_year,
    }
    return render(request, 'TemplatesFlota/admin_editar_vehiculo.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_eliminar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, patente=pk)
    
    if request.method == 'POST':
        try:
            patente = vehiculo.patente
            vehiculo.delete()
            messages.success(request, f'✅ Vehículo {patente} eliminado correctamente')
            return redirect('admin_ver_vehiculos')
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar vehículo: {str(e)}')
    
    context = {'vehiculo': vehiculo}
    return render(request, 'TemplatesFlota/admin_eliminar_vehiculo.html', context)

# CONDUCTORES - Editar y Eliminar

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_editar_chofer(request, pk):
    chofer = get_object_or_404(Chofer, pk=pk)
    usuario = chofer.usuario
    
    if request.method == 'POST':
        try:
            # Actualizar usuario
            usuario.username = request.POST.get('username')
            usuario.email = request.POST.get('email_usuario')
            usuario.first_name = request.POST.get('nombre')
            usuario.save()
            
            # Actualizar chofer
            chofer.RUTChofer = request.POST.get('RUTChofer')
            chofer.Nombre = request.POST.get('nombre')
            chofer.Fecha_Nacimiento = request.POST.get('fecha_nacimiento')
            chofer.Telefono = request.POST.get('telefono')
            chofer.Estado = request.POST.get('estado')
            chofer.Horas = request.POST.get('horas')
            chofer.save()
            
            messages.success(request, '✅ Chofer actualizado correctamente')
            return redirect('admin_ver_chofers')
        
        except Exception as e:
            messages.error(request, f'❌ Error al actualizar chofer: {str(e)}')

    context = {'chofer': chofer}
    return render(request, 'TemplatesFlota/admin_editar_chofer.html', context)

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_eliminar_chofer(request, pk):
    chofer = get_object_or_404(Chofer, pk=pk)
    
    if request.method == 'POST':
        try:
            nombre = chofer.Nombre
            # Verificar si el chofer tiene vehículos asignados
            if chofer.vehiculos_asignados.exists():
                vehiculos = chofer.vehiculos_asignados.all()
                messages.error(request, f'❌ No se puede eliminar el chofer porque tiene {vehiculos.count()} vehículo(s) asignado(s)')
                return redirect('admin_ver_chofers')
            
            # Eliminar usuario (esto eliminará el chofer por CASCADE)
            chofer.usuario.delete()
            messages.success(request, f'✅ Chofer {nombre} eliminado correctamente')
            return redirect('admin_ver_chofers')
        
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar chofer: {str(e)}')
    
    context = {'chofer': chofer}
    return render(request, 'TemplatesFlota/admin_eliminar_chofer.html', context)

# TIPOS DE VEHÍCULO - Editar
@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_editar_tipo_vehiculo(request, id):
    tipo_vehiculo = get_object_or_404(TipoVehiculo, ID_Tipo=id)
    
    if request.method == 'POST':
        nuevo_nombre = request.POST.get('nombre', '').strip()
        
        if nuevo_nombre:
            try:
                # Validar longitud del nombre
                if len(nuevo_nombre) < 2:
                    messages.error(request, '❌ El nombre debe tener al menos 2 caracteres')
                elif len(nuevo_nombre) > 45:
                    messages.error(request, '❌ El nombre no puede exceder los 45 caracteres')
                else:
                    # Verificar si el nombre ya existe (excluyendo el actual)
                    if TipoVehiculo.objects.exclude(ID_Tipo=id).filter(nombre=nuevo_nombre).exists():
                        messages.error(request, f'❌ El tipo de vehículo "{nuevo_nombre}" ya existe')
                    else:
                        tipo_vehiculo.nombre = nuevo_nombre
                        tipo_vehiculo.save()
                        messages.success(request, f'✅ Tipo actualizado correctamente a "{nuevo_nombre}"')
                        return redirect('admin_ver_tipos_vehiculo')
                        
            except Exception as e:
                messages.error(request, f'❌ Error al actualizar: {str(e)}')
        else:
            messages.error(request, '❌ El nombre no puede estar vacío')
    
    context = {
        'tipo_vehiculo': tipo_vehiculo
    }
    return render(request, 'TemplatesFlota/admin_editar_tipo_vehiculo.html', context)

# TIPOS DE VEHÍCULO - Eliminar
@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_eliminar_tipo_vehiculo(request, id):
    tipo_vehiculo = get_object_or_404(TipoVehiculo, ID_Tipo=id)
    
    if request.method == 'POST':
        try:
            nombre_tipo = tipo_vehiculo.nombre
            
            # Verificar si hay vehículos asociados a este tipo
            if tipo_vehiculo.vehiculos.exists():
                messages.error(request, f'❌ No se puede eliminar "{nombre_tipo}" porque tiene vehículos asociados')
                return redirect('admin_ver_tipos_vehiculo')
            
            tipo_vehiculo.delete()
            messages.success(request, f'✅ Tipo "{nombre_tipo}" eliminado correctamente')
            return redirect('admin_ver_tipos_vehiculo')
            
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar: {str(e)}')
    
    context = {
        'tipo_vehiculo': tipo_vehiculo
    }
    return render(request, 'TemplatesFlota/admin_eliminar_tipo_vehiculo.html', context)