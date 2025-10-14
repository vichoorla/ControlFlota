"""
URL configuration for ControlFlota project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from AppFlota import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('chofer-dashboard/', views.chofer_dashboard, name='chofer_dashboard'),
    path('mecanico-dashboard/', views.mecanico_dashboard, name='mecanico_dashboard'),
    
    # Funciones de Admin
    path('admin/agregar-chofer/', views.admin_agregar_chofer, name='admin_agregar_chofer'),
    path('admin/ver-chofers/', views.admin_ver_chofers, name='admin_ver_chofers'),
    path('admin/agregar-vehiculo/', views.admin_agregar_vehiculo, name='admin_agregar_vehiculo'),
    path('admin/ver-vehiculos/', views.admin_ver_vehiculos, name='admin_ver_vehiculos'),
    path('admin/ver-combustible/', views.admin_ver_combustible, name='admin_ver_combustible'),
    path('admin/ver-mantenciones/', views.admin_ver_mantenciones, name='admin_ver_mantenciones'),
    
    # Funciones de Chofer
    path('chofer/ver-vehiculos/', views.chofer_ver_vehiculos, name='chofer_ver_vehiculos'),
    path('chofer/agregar-combustible/', views.chofer_agregar_combustible, name='chofer_agregar_combustible'),
    path('chofer/ver-combustible/', views.chofer_ver_combustible, name='chofer_ver_combustible'),
    
    # Funciones de Mecánico
    path('mecanico/ver-vehiculos/', views.mecanico_ver_vehiculos, name='mecanico_ver_vehiculos'),
    path('mecanico/agregar-combustible/', views.mecanico_agregar_combustible, name='mecanico_agregar_combustible'),
    path('mecanico/ver-combustible/', views.mecanico_ver_combustible, name='mecanico_ver_combustible'),
    path('mecanico/agregar-mantencion/', views.mecanico_agregar_mantencion, name='mecanico_agregar_mantencion'),
    path('mecanico/ver-mantenciones/', views.mecanico_ver_mantenciones, name='mecanico_ver_mantenciones'),
]