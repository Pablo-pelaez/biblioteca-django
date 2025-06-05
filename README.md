# Sistema de Usuarios

Autenticación completa: Registro, login, logout
Roles diferenciados:

Usuario Regular: Puede buscar libros, tomar préstamos y ver su historial
Administrador: Gestión completa de libros, usuarios y sistema



# Gestión de Libros

CRUD completo de libros (Crear, Leer, Actualizar, Eliminar)
Información detallada: título, autor, año de publicación, ISBN, descripción
Control de inventario con cantidad de stock
Sistema de disponibilidad en tiempo real
Búsqueda avanzada por título, autor o ISBN

# Sistema de Préstamos

Préstamo y devolución de libros
Seguimiento de fechas límite
Historial completo de préstamos
Control automático de disponibilidad

# Interfaz de Usuario

Vista de grilla y lista para catálogo
Dashboard con estadísticas
Mensajes informativos y confirmaciones

# API REST

Endpoints para todas las operaciones CRUD
Autenticación y autorización por roles
Documentación automática
Compatible con Postman

# Tecnologías Utilizadas

Backend: Django 5.0.1
Base de Datos: SQLite (desarrollo)
API: Django REST Framework
Autenticación: Sistema de usuarios de Django personalizado


# Requisitos del Sistema

Python 3.12+
Django 5.0.1
Django REST Framework

##---------------------------------------------------------------------------------

# Instalación y Configuración
1. Clonar el Repositorio
bashgit clone <url-del-repositorio>
cd BIBLIOTECA
2. Crear Entorno Virtual
bash# En Windows
python -m venv venv
venv\Scripts\activate

En macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. Instalar Dependencias
bashpip install -r requirements.txt
4. Configurar la Base de Datos
bash# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
5. Crear Superusuario
bashpython manage.py createsuperuser
6. Ejecutar el Servidor de Desarrollo
bashpython manage.py runserver
El proyecto estará disponible en: http://127.0.0.1:8000/ || <url-de-heroku>

##-----------------------------------------------------------------------

# Configuración
Variables de Entorno

Para producción, configura las siguientes variables de entorno:
SECRET_KEY=django-key-2025
DEBUG=True