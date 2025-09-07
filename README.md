# ControlFlota
Proyecto de aplicacion a la gestion de flota.

Documentación del Sistema de Gestión de Flota (ControlFlota)

Descripción General
Sistema web desarrollado en Django para la gestión de flotas vehiculares, que incluye módulos para administradores, choferes y mecánicos.

Estructura del Proyecto

Archivos Principales del Proyecto

1. settings.py
- Configuración principal de Django
- Templates configurados en directorio 'Templates'


2. urls.py
- Configuración de rutas URL
- Rutas principales:
  - /admin/ - Panel de administración Django
  - /inicio/ - Página de bienvenida
  - /chofer/ - Agregar chofer
  - /login/ - Inicio de sesión
  - /logout/ - Cerrar sesión
  - Dashboards para cada tipo de usuario

3. views.py (AppFlota)
- Lógica principal de la aplicación

Sistema de Autenticación
- Usuarios predefinidos:
  - admin/admin123 (Administrador)
  - chofer/chofer123 (Chofer)
  - mecanico/mecanico123 (Mecánico)

- Decoradores de seguridad:
  - @requiere_autenticacion - Verifica sesión activa
  - @requiere_tipo_usuario - Control de permisos por rol

Roles y Permisos

1. Administrador
- Funciones:
  - Gestión de choferes (agregar/ver)
  - Gestión de vehículos (agregar/ver)
  - Visualización de registros de combustible
  - Visualización de mantenciones

2. Chofer
- Funciones:
  - Visualización de vehículos
  - Registro de combustible
  - Visualización de registros de combustible

3. Mecánico
- Funciones:
  - Visualización de vehículos
  - Registro de combustible
  - Visualización de registros de combustible
  - Gestión de mantenciones (agregar/ver)

Modelos de Datos (Almacenamiento en Memoria)

Vehículos
- Campos: patente, VIN, marca, modelo, año, motor, seguro, revisión técnica, permiso circulación, GPS

Choferes
- Campos: nombre, fecha nacimiento, teléfono, estado, horas

Combustible
- Campos: tipo, fecha recarga, lugar, encargado, cantidad, vehículo, registrado por

Mantenciones
- Campos: tipo, fecha, descripción, vehículo, realizado por

Templates HTML Disponibles

1. Autenticación
- login.html - Formulario de inicio de sesión

2. Dashboards
- admin_dashboard.html - Panel administrador
- chofer_dashboard.html - Panel chofer
- mecanico_dashboard.html - Panel mecánico
- administracion.html - Panel administración (alternativo)

3. Páginas de Gestión
- Múltiples templates para CRUD de cada entidad


Ejecutar
   python manage.py runserver

3. Acceso:
   - URL: http://localhost:8000/login/
   - Usar credenciales predefinidas

Consideraciones

- Almacenamiento en memoria: Los datos se pierden al reiniciar el servidor
- Modo desarrollo: No usar en producción (DEBUG = True)
- Seguridad: Implementar base de datos real para entorno productivo
- Validaciones: Añadir validaciones adicionales para datos de entrada

Próximos Pasos Recomendados

1. Implementar modelos Django con base de datos real
2. Añadir validaciones de formularios
3. Implementar tests automatizados
4. Mejorar interfaz de usuario
5. Añadir sistema de reportes
6. Implementar API REST