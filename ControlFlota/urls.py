from django.contrib import admin
from django.urls import path, include
from AppFlota import views

urlpatterns = [
    # 🔧 ADMIN DE DJANGO - Solo para /admin/
    path('admin/', admin.site.urls),
    
    # 🚗 TUS URLs PERSONALIZADAS
    path('flota/ver-vehiculos/', views.admin_ver_vehiculos, name='admin_ver_vehiculos'),
    path('flota/agregar-vehiculo/', views.admin_agregar_vehiculo, name='admin_agregar_vehiculo'),
    
    path('flota/ver-chofers/', views.admin_ver_chofers, name='admin_ver_chofers'),
    path('flota/agregar-chofer/', views.admin_agregar_chofer, name='admin_agregar_chofer'),
    
    path('flota/ver-mantenciones/', views.admin_ver_mantenciones, name='admin_ver_mantenciones'),
    path('flota/ver-combustible/', views.admin_ver_combustible, name='admin_ver_combustible'),
    path('flota/inventario/', views.admin_ver_inventario, name='admin_ver_inventario'),
    path('flota/ver-mecanicos/', views.admin_ver_mecanicos, name='admin_ver_mecanicos'),
    path('flota/agregar-mecanico/', views.admin_agregar_mecanico, name='admin_agregar_mecanico'),
    
    path('flota/ver-tipos-vehiculo/', views.admin_ver_tipos_vehiculo, name='admin_ver_tipos_vehiculo'),
    path('flota/agregar-tipo-vehiculo/', views.admin_agregar_tipo_vehiculo, name='admin_agregar_tipo_vehiculo'),
    
    # 📊 Dashboards
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('chofer-dashboard/', views.chofer_dashboard, name='chofer_dashboard'),
    path('mecanico-dashboard/', views.mecanico_dashboard, name='mecanico_dashboard'),
    
    # 🔐 Autenticación
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # 👨‍✈️ URLs de Chofer
    path('chofer/ver-vehiculos/', views.chofer_ver_vehiculos, name='chofer_ver_vehiculos'),
    path('chofer/agregar-combustible/', views.chofer_agregar_combustible, name='chofer_agregar_combustible'),
    path('chofer/ver-combustible/', views.chofer_ver_combustible, name='chofer_ver_combustible'),
    
    # 🔧 URLs de Mecánico
    path('mecanico/ver-vehiculos/', views.mecanico_ver_vehiculos, name='mecanico_ver_vehiculos'),
    path('mecanico/agregar-combustible/', views.mecanico_agregar_combustible, name='mecanico_agregar_combustible'),
    path('mecanico/ver-combustible/', views.mecanico_ver_combustible, name='mecanico_ver_combustible'),
    path('mecanico/agregar-mantencion/', views.mecanico_agregar_mantencion, name='mecanico_agregar_mantencion'),
    path('mecanico/ver-mantenciones/', views.mecanico_ver_mantenciones, name='mecanico_ver_mantenciones'),
    
    # 🛠️ URLs para CRUD completo (AGREGA ESTAS)
    path('flota/editar-vehiculo/<str:pk>/', views.admin_editar_vehiculo, name='admin_editar_vehiculo'),
    path('flota/eliminar-vehiculo/<str:pk>/', views.admin_eliminar_vehiculo, name='admin_eliminar_vehiculo'),
    
    path('flota/editar-chofer/<str:pk>/', views.admin_editar_chofer, name='admin_editar_chofer'),
    path('flota/eliminar-chofer/<str:pk>/', views.admin_eliminar_chofer, name='admin_eliminar_chofer'),
    
    path('flota/editar-tipo-vehiculo/<int:pk>/', views.admin_editar_tipo_vehiculo, name='admin_editar_tipo_vehiculo'),
    path('flota/eliminar-tipo-vehiculo/<int:pk>/', views.admin_eliminar_tipo_vehiculo, name='admin_eliminar_tipo_vehiculo'),

    # 🛠️ URLs para CRUD completo
    path('flota/editar-vehiculo/<str:pk>/', views.admin_editar_vehiculo, name='admin_editar_vehiculo'),
    path('flota/eliminar-vehiculo/<str:pk>/', views.admin_eliminar_vehiculo, name='admin_eliminar_vehiculo'),

    path('flota/editar-chofer/<str:pk>/', views.admin_editar_chofer, name='admin_editar_chofer'),
    path('flota/eliminar-chofer/<str:pk>/', views.admin_eliminar_chofer, name='admin_eliminar_chofer'),

    path('flota/editar-mecanico/<str:pk>/', views.admin_editar_mecanico, name='admin_editar_mecanico'),
    path('flota/eliminar-mecanico/<str:pk>/', views.admin_eliminar_mecanico, name='admin_eliminar_mecanico'),

    path('flota/editar-tipo-vehiculo/<int:pk>/', views.admin_editar_tipo_vehiculo, name='admin_editar_tipo_vehiculo'),
    path('flota/eliminar-tipo-vehiculo/<int:pk>/', views.admin_eliminar_tipo_vehiculo, name='admin_eliminar_tipo_vehiculo'),
    path('mecanicos/', views.admin_ver_mecanicos, name='admin_ver_mecanicos'),
    path('mecanicos/agregar/', views.admin_agregar_mecanico, name='admin_agregar_mecanico'),
    path('mecanicos/editar/<str:rut>/', views.admin_editar_mecanico, name='admin_editar_mecanico'),
    path('mecanicos/eliminar/<str:rut>/', views.admin_eliminar_mecanico, name='admin_eliminar_mecanico'),
    path('mecanicos/', views.admin_ver_mecanicos, name='admin_ver_mecanicos'),
    path('mecanicos/agregar/', views.admin_agregar_mecanico, name='admin_agregar_mecanico'),
    path('mecanicos/editar/<str:rut>/', views.admin_editar_mecanico, name='admin_editar_mecanico'),
    path('mecanicos/eliminar/<str:rut>/', views.admin_eliminar_mecanico, name='admin_eliminar_mecanico'),
    # Mantenciones
    path('mantenciones/', views.admin_ver_mantenciones, name='admin_ver_mantenciones'),
    path('mantenciones/agregar/', views.admin_agregar_mantencion, name='admin_agregar_mantencion'),
    path('mantenciones/editar/<int:id>/', views.admin_editar_mantencion, name='admin_editar_mantencion'),
    path('mantenciones/eliminar/<int:id>/', views.admin_eliminar_mantencion, name='admin_eliminar_mantencion'),

    # Tipos de Vehículo
    path('tipos-vehiculo/', views.admin_ver_tipos_vehiculo, name='admin_ver_tipos_vehiculo'),
    path('tipos-vehiculo/agregar/', views.admin_agregar_tipo_vehiculo, name='admin_agregar_tipo_vehiculo'),
    path('tipos-vehiculo/editar/<int:id>/', views.admin_editar_tipo_vehiculo, name='admin_editar_tipo_vehiculo'),
    path('tipos-vehiculo/eliminar/<int:id>/', views.admin_eliminar_tipo_vehiculo, name='admin_eliminar_tipo_vehiculo'),

    # Vistas para Chofer
    path('chofer-dashboard/', views.chofer_dashboard, name='chofer_dashboard'),
    path('chofer/vehiculos/', views.chofer_ver_vehiculos, name='chofer_ver_vehiculos'),
    path('chofer/vehiculos/<str:patente>/', views.chofer_ver_detalle_vehiculo, name='chofer_detalle_vehiculo'),

    path('debug-users/', views.debug_users, name='debug_users'),
]