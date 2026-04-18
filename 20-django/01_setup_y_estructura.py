# =============================================================================
# CAPÍTULO 20 — Django
# Archivo 01: Setup, estructura de proyecto y comandos esenciales
# =============================================================================
# Este archivo explica cómo instalar Django, crear un proyecto y
# entiende la estructura de archivos que genera.
#
# Instalación: pip install django
# =============================================================================

import subprocess  # Para ejecutar comandos del sistema
import sys         # Para acceder al ejecutable Python actual
import os          # Para verificar existencia de directorios

# =============================================================================
# SECCIÓN 1: Verificar instalación de Django
# =============================================================================

def verificar_django() -> bool:
    """
    Verifica si Django está instalado y muestra su versión.

    Por qué verificar primero: Django es un framework grande. Si no está
    instalado, los imports del resto del código fallarán con mensajes
    confusos. Mejor detectarlo y dar instrucciones claras.

    Returns:
        True si Django está instalado, False si no.
    """
    try:
        import django
        print(f"  Django instalado: versión {django.__version__}")

        # Verificamos también que django-admin esté disponible
        resultado = subprocess.run(
            [sys.executable, "-m", "django", "--version"],
            capture_output=True,
            text=True,
        )
        if resultado.returncode == 0:
            print(f"  django-admin disponible: {resultado.stdout.strip()}")
        return True

    except ImportError:
        print("  Django NO está instalado.")
        print("  Para instalar: pip install django")
        print("  Versión recomendada: pip install django>=4.2")
        return False


# =============================================================================
# SECCIÓN 2: Estructura completa de un proyecto Django explicada
# =============================================================================

def explicar_estructura_proyecto() -> None:
    """
    Explica cada archivo que Django genera al crear un nuevo proyecto.

    Por qué esto importa: entender para qué sirve cada archivo evita
    modificar el archivo equivocado y permite saber dónde poner código.
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║           ESTRUCTURA DE UN PROYECTO DJANGO                   ║
╚══════════════════════════════════════════════════════════════╝

mi_blog/                     ← Carpeta raíz (puede tener cualquier nombre)
│
├── manage.py                ← Script de gestión. NUNCA lo modifiques.
│                              Úsalo con: python manage.py <comando>
│
├── mi_blog/                 ← Paquete Python con la configuración central
│   │                          (mismo nombre que el proyecto)
│   │
│   ├── __init__.py          ← Hace que sea un paquete Python (vacío)
│   │
│   ├── settings.py          ← *** ARCHIVO MÁS IMPORTANTE ***
│   │                          Contiene toda la configuración:
│   │                          - BASE_DIR, SECRET_KEY, DEBUG
│   │                          - INSTALLED_APPS (apps activas)
│   │                          - DATABASES (conexión a la DB)
│   │                          - TEMPLATES (configuración de templates)
│   │                          - STATIC_URL, MEDIA_URL
│   │                          - MIDDLEWARE (capa de procesamiento)
│   │
│   ├── urls.py              ← URLs raíz del proyecto
│   │                          Conecta las URLs de cada app aquí:
│   │                          urlpatterns = [path('blog/', include('blog.urls'))]
│   │
│   ├── wsgi.py              ← Punto de entrada WSGI para producción sync
│   │                          (Gunicorn, uWSGI)
│   │
│   └── asgi.py              ← Punto de entrada ASGI para producción async
│                              (Daphne, Uvicorn con Django)
│
└── blog/                    ← Una "app" de Django (módulo reutilizable)
    │                          Cada funcionalidad independiente es una app:
    │                          blog, usuarios, tienda, comentarios...
    │
    ├── migrations/          ← Historial de cambios del schema de DB
    │   └── 0001_initial.py  ← Primera migración (creación de tablas)
    │
    ├── templates/           ← Archivos HTML de esta app
    │   └── blog/            ← Subcarpeta con el nombre de la app (convención)
    │       ├── base.html    ← Template base con bloques
    │       └── post_list.html
    │
    ├── static/              ← CSS, JS, imágenes de esta app
    │   └── blog/
    │       └── style.css
    │
    ├── __init__.py          ← Hace que sea un paquete Python
    ├── admin.py             ← Registro de modelos en el panel /admin/
    ├── apps.py              ← Configuración de la app (nombre, etc.)
    ├── models.py            ← Definición de modelos → tablas en la DB
    ├── forms.py             ← Formularios de la app
    ├── urls.py              ← URLs de esta app (se incluyen en el proyecto)
    ├── views.py             ← Lógica de las vistas (controladores)
    └── tests.py             ← Tests de la app
""")


# =============================================================================
# SECCIÓN 3: El archivo settings.py explicado
# =============================================================================

def explicar_settings() -> None:
    """
    Muestra un settings.py típico con explicación de cada sección.

    Por qué settings.py importa: es el cerebro de Django. Configurar mal
    DEBUG en producción, la SECRET_KEY o ALLOWED_HOSTS puede ser un
    problema de seguridad grave.
    """
    settings_ejemplo = '''
# ============================================================
# settings.py — Configuración del proyecto Django
# ============================================================

from pathlib import Path
import os

# BASE_DIR: ruta absoluta a la carpeta raíz del proyecto
# Se usa para construir rutas de templates, static files, etc.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY: clave criptográfica usada por Django para cookies,
# tokens CSRF, sesiones, etc.
# NUNCA la pongas en el código — usa variable de entorno en producción
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "clave-solo-para-desarrollo")

# DEBUG: True durante desarrollo, SIEMPRE False en producción
# Con DEBUG=True Django muestra stack traces detallados al usuario
# (peligroso en producción — revela estructura del código)
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# ALLOWED_HOSTS: dominios desde los que se puede acceder al proyecto
# En desarrollo puede ser [] o ["localhost", "127.0.0.1"]
# En producción: ["tudominio.com", "www.tudominio.com"]
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# INSTALLED_APPS: lista de apps activas en el proyecto
# El orden importa para algunos casos (templates, migrations)
INSTALLED_APPS = [
    "django.contrib.admin",        # Panel de administración /admin/
    "django.contrib.auth",         # Sistema de autenticación
    "django.contrib.contenttypes", # Framework de tipos de contenido
    "django.contrib.sessions",     # Manejo de sesiones
    "django.contrib.messages",     # Sistema de mensajes flash
    "django.contrib.staticfiles",  # Manejo de archivos estáticos
    # Apps propias del proyecto:
    "blog",                        # Nuestra app de blog
]

# DATABASES: configuración de la base de datos
# Por defecto SQLite — ideal para desarrollo
# Para producción usa PostgreSQL con psycopg2
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Para producción con PostgreSQL:
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.environ["DB_NAME"],
#         "USER": os.environ["DB_USER"],
#         "PASSWORD": os.environ["DB_PASSWORD"],
#         "HOST": os.environ["DB_HOST"],
#         "PORT": "5432",
#     }
# }

# TEMPLATES: cómo Django busca y renderiza templates HTML
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # DIRS: carpetas adicionales donde buscar templates (globales)
        "DIRS": [BASE_DIR / "templates"],
        # APP_DIRS: busca templates en cada app en carpeta templates/
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Archivos estáticos (CSS, JS, imágenes)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # Para collectstatic en producción

# Archivos subidos por usuarios (imágenes de perfil, documentos, etc.)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Configuración del idioma y zona horaria
LANGUAGE_CODE = "es-es"      # Idioma del admin y mensajes
TIME_ZONE = "America/Mexico_City"
USE_I18N = True               # Activar internacionalización
USE_TZ = True                 # Usar datetimes con timezone (recomendado)

# Campo por defecto para primary keys
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
'''
    print("\n--- Ejemplo de settings.py comentado ---")
    print(settings_ejemplo)


# =============================================================================
# SECCIÓN 4: Guía paso a paso de los comandos más usados
# =============================================================================

def mostrar_comandos_manage_py() -> None:
    """
    Guía completa de los comandos manage.py con explicación de cuándo usar cada uno.
    """
    comandos = [
        ("startproject nombre", "Crea un nuevo proyecto Django con la estructura base"),
        ("startapp nombre_app", "Crea una nueva app dentro del proyecto actual"),
        ("runserver", "Inicia servidor de desarrollo en http://127.0.0.1:8000"),
        ("runserver 0.0.0.0:8080", "Servidor accesible en red local, puerto 8080"),
        ("makemigrations", "Detecta cambios en models.py y crea archivos de migración"),
        ("makemigrations blog", "Crea migraciones solo para la app 'blog'"),
        ("migrate", "Aplica todas las migraciones pendientes a la DB"),
        ("migrate blog 0002", "Migra la app 'blog' hasta la migración 0002 (rollback)"),
        ("createsuperuser", "Crea usuario administrador para el panel /admin/"),
        ("shell", "Abre shell Python interactivo con Django configurado"),
        ("shell_plus", "Shell mejorado (requiere django-extensions)"),
        ("dbshell", "Abre la consola SQL de la base de datos"),
        ("showmigrations", "Lista todas las migraciones y su estado"),
        ("sqlmigrate blog 0001", "Muestra el SQL que ejecutará la migración"),
        ("test", "Ejecuta todos los tests del proyecto"),
        ("test blog", "Ejecuta solo los tests de la app 'blog'"),
        ("collectstatic", "Copia archivos estáticos a STATIC_ROOT (producción)"),
        ("check", "Verifica el proyecto en busca de problemas de configuración"),
        ("dumpdata blog", "Exporta datos de la app 'blog' a JSON (fixture)"),
        ("loaddata fixture.json", "Carga datos de un archivo JSON a la DB"),
    ]

    print("\n--- Comandos de manage.py ---")
    print(f"  {'Comando':<40} Descripción")
    print("  " + "-" * 70)
    for cmd, desc in comandos:
        print(f"  python manage.py {cmd:<24} {desc}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 65)
    print("DJANGO — SETUP, ESTRUCTURA Y COMANDOS ESENCIALES")
    print("=" * 65)

    print("\n[1] Verificando instalación de Django:")
    django_disponible = verificar_django()

    print("\n[2] Estructura de un proyecto Django:")
    explicar_estructura_proyecto()

    print("\n[3] El archivo settings.py:")
    explicar_settings()

    print("\n[4] Comandos de manage.py:")
    mostrar_comandos_manage_py()

    if not django_disponible:
        print("\n" + "!" * 65)
        print("Para seguir con los demás archivos, instala Django primero:")
        print("  pip install django djangorestframework")
        print("!" * 65)

    print("\n" + "=" * 65)
    print("Fin — siguiente: 02_modelos.py")
    print("=" * 65)
