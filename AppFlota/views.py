from django.shortcuts import render, redirect
from django.http import HttpResponse
# Create your views here.

# Usuarios para demostracion

USUARIOS_PRUEBA = {
    'admin': {'password': 'admin123','tipo': 'admin'},
    'chofer': {'password': 'chofer123','tipo':'chofer'},
    'mecanico': {'password': 'mecanico123','tipo':'mecanico'}
}

def bienvenida(request):
    return HttpResponse("<h1>Bienvenido/a a la página!</h1>")

def AgregarChofer(request):
    return render(request, 'TemplatesFlota/index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        #Verifica credenciales
        if username in USUARIOS_PRUEBA and USUARIOS_PRUEBA[username]['password'] == password:
            #Guardar en sesion
            request.session['usuario_autenticado'] = True
            request.session['tipo_usuario'] = USUARIOS_PRUEBA[username]['tipo']
            request.session['username'] = username

            #rEDIRIGIR SEGUN TIPO
            if USUARIOS_PRUEBA[username]['tipo'] == 'admin':
                return redirect('admin_dashboard')
            elif USUARIOS_PRUEBA[username]['tipo'] == 'chofer':
                return redirect('chofer_dashboard')
            elif USUARIOS_PRUEBA[username]['tipo'] == 'mecanico':
                return redirect('mecanico_dashboard')
        
        else:
            return render(request, 'TemplatesFlota/login.html', {'error': 'Usuario o contraseña incorrectas'})
        
    return render(request, 'TemplatesFlota/login.html')

def logout_view(request):
    #Acabar sesion
    request.session.flush()
    return redirect('inicio')

def requiere_autenticacion(view_funcion):
    #verifica autenticacion
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_autenticado'):
            return redirect('login')
        return view_funcion(request, *args, **kwargs)
    return wrapper

def requiere_tipo_usuario(tipo_permitidos):
    #verifica tipo de usuario
    def decorator(view_funcion):
        def wrapper(request, *args, **kwargs):
            if not request.session.get('usuario_autenticado'):
                return redirect('login')
            
            tipo_usuario = request.session.get('tipo_usuario')
            if tipo_usuario not in tipo_permitidos:
                return HttpResponse("No tienes permisos para acceder a esta pagina", status=403)
            
            return view_funcion(request, *args, **kwargs)
        return wrapper
    return decorator

#vistas protegidas

@requiere_autenticacion
@requiere_tipo_usuario(['admin'])
def admin_dashboard(request):
    return render(request, 'TemplatesFlota/admin_dashboard.html',
                  {'username': request.session.get('username')})


@requiere_autenticacion
@requiere_tipo_usuario(['chofer'])
def chofer_dashboard(request):
    return render(request, 'TemplatesFlota/chofer_dashboard.html',
                 {'username': request.session.get('username')})

@requiere_autenticacion
@requiere_tipo_usuario(['mecanico'])
def mecanico_dashboard(request):
    return render(request, 'TemplatesFlota/mecanico_dashboard.html',
                  {'username': request.session.get('username')})
