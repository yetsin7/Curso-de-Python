"""
Guía Completa: Proyecto Django Profesional
============================================
Cubre todos los aspectos de un proyecto Django real:
  - Estructura de carpetas profesional
  - Settings por entorno (base / dev / prod)
  - Gestión de archivos estáticos y media
  - Django Signals (pre_save, post_save)
  - Custom management commands
  - Optimización de queries (select_related, prefetch_related)
  - Script verificador que muestra el árbol del proyecto tipo

Este archivo es ejecutable y no requiere Django instalado para
mostrar la guía estructural. Verifica Django solo cuando se ejecuta.
"""

import os
import sys
from pathlib import Path


# ===========================================================================
# Sección 1: Estructura de carpetas profesional
# ===========================================================================

ESTRUCTURA_PROYECTO = """
mi_proyecto/                    ← raíz del repositorio
│
├── config/                     ← paquete de configuración
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             ← settings comunes a todos los entornos
│   │   ├── dev.py              ← hereda base + DEBUG, SQLite local
│   │   └── prod.py             ← hereda base + PostgreSQL, S3, HTTPS
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── users/                  ← app de usuarios
│   │   ├── migrations/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── seed_users.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── signals.py          ← señales del modelo
│   │   ├── urls.py
│   │   └── views.py
│   │
│   └── blog/                   ← otra app de ejemplo
│       ├── migrations/
│       ├── admin.py
│       ├── models.py
│       ├── urls.py
│       └── views.py
│
├── templates/                  ← templates HTML globales
│   └── base.html
│
├── static/                     ← archivos estáticos del proyecto
│   ├── css/
│   ├── js/
│   └── img/
│
├── media/                      ← archivos subidos por usuarios (en .gitignore)
│
├── requirements/
│   ├── base.txt                ← dependencias comunes
│   ├── dev.txt                 ← dev: debug-toolbar, faker, etc.
│   └── prod.txt                ← prod: gunicorn, whitenoise, psycopg2
│
├── .env                        ← variables de entorno (en .gitignore)
├── .env.example                ← plantilla sin valores reales
├── manage.py
└── README.md
"""


# ===========================================================================
# Sección 2: Settings por entorno
# ===========================================================================

SETTINGS_BASE = '''
# config/settings/base.py
# Settings compartidos por todos los entornos.

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esto-en-produccion")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps propias
    "apps.users",
    "apps.blog",
    # Terceros
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # archivos estáticos en prod
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [...]},
}]

STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # destino de collectstatic
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
'''

SETTINGS_DEV = '''
# config/settings/dev.py
# Hereda base y agrega configuración de desarrollo.

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Debug toolbar
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE    += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
INTERNAL_IPS   = ["127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
'''

SETTINGS_PROD = '''
# config/settings/prod.py
# Hereda base y configura para producción segura.

from .base import *
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

SECRET_KEY = os.environ["SECRET_KEY"]   # obligatorio en prod

DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

# Archivos estáticos con whitenoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Archivos media en S3
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_STORAGE_BUCKET_NAME = os.environ["AWS_BUCKET_NAME"]

SECURE_HSTS_SECONDS         = 31536000
SECURE_SSL_REDIRECT         = True
SESSION_COOKIE_SECURE       = True
CSRF_COOKIE_SECURE          = True
'''


# ===========================================================================
# Sección 3: Django Signals
# ===========================================================================

SIGNALS_EJEMPLO = '''
# apps/users/signals.py
# Señales para el modelo User que se ejecutan automáticamente
# antes y después de guardar en base de datos.

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(pre_save, sender=User)
def normalizar_email(sender, instance, **kwargs):
    """
    Se ejecuta ANTES de guardar un usuario.
    Normaliza el email a minúsculas para evitar duplicados por capitalización.
    """
    if instance.email:
        instance.email = instance.email.lower().strip()


@receiver(post_save, sender=User, dispatch_uid="enviar_bienvenida")
def enviar_bienvenida(sender, instance, created, **kwargs):
    """
    Se ejecuta DESPUÉS de guardar un usuario.
    Solo cuando el usuario se crea por primera vez (created=True).
    Envía un email de bienvenida.
    """
    if created:
        from django.core.mail import send_mail
        send_mail(
            subject="¡Bienvenido!",
            message=f"Hola {instance.username}, tu cuenta fue creada.",
            from_email="noreply@ejemplo.com",
            recipient_list=[instance.email],
            fail_silently=True,
        )


# apps/users/apps.py — IMPORTANTE: registrar señales en AppConfig
class UsersConfig(AppConfig):
    name = "apps.users"

    def ready(self):
        import apps.users.signals  # noqa — activa el registro de señales
'''


# ===========================================================================
# Sección 4: Custom Management Commands
# ===========================================================================

MANAGEMENT_COMMAND = '''
# apps/users/management/commands/seed_users.py
# Comando personalizado ejecutable con:
#   python manage.py seed_users --count 50

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    """Crea usuarios de prueba para el entorno de desarrollo."""

    help = "Crea N usuarios de prueba con datos falsos"

    def add_arguments(self, parser):
        """Define los argumentos aceptados por el comando."""
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Cantidad de usuarios a crear (default: 10)"
        )

    def handle(self, *args, **options):
        """Lógica principal del comando."""
        count = options["count"]
        created = 0

        for i in range(1, count + 1):
            user, was_created = User.objects.get_or_create(
                username=f"usuario_{i:03d}",
                defaults={"email": f"usuario{i}@ejemplo.com"}
            )
            if was_created:
                user.set_password("password123")
                user.save()
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"✓ {created} usuario(s) creados de {count} solicitados")
        )
'''


# ===========================================================================
# Sección 5: Optimización de queries
# ===========================================================================

OPTIMIZACION_QUERIES = '''
# Optimización de queries en Django ORM
# =======================================
# Sin optimización → N+1 queries (desastre de rendimiento)
# Con optimización → 1-2 queries (eficiente)

from django.db.models import Prefetch
from apps.blog.models import Post, Comment

# ❌ MAL: N+1 queries — una query por cada post para obtener su autor
posts = Post.objects.all()
for post in posts:
    print(post.author.username)   # query extra por cada iteración

# ✅ BIEN: select_related → JOIN en una sola query (ForeignKey / OneToOne)
posts = Post.objects.select_related("author").all()
for post in posts:
    print(post.author.username)   # sin queries adicionales

# ✅ BIEN: prefetch_related → 2 queries con IN clause (ManyToMany / reverse FK)
posts = Post.objects.prefetch_related("comments").all()
for post in posts:
    for comment in post.comments.all():  # ya en memoria, sin queries
        print(comment.text)

# ✅ Prefetch con queryset personalizado (filtrar comentarios aprobados)
posts = Post.objects.prefetch_related(
    Prefetch("comments", queryset=Comment.objects.filter(approved=True))
)

# ✅ only() → trae solo columnas específicas (evita SELECT *)
posts = Post.objects.only("title", "created_at")

# ✅ defer() → excluye columnas pesadas (cuerpo largo, campos binarios)
posts = Post.objects.defer("body", "thumbnail")

# ✅ values() → retorna dicts en vez de instancias ORM (más rápido para lecturas)
titulos = Post.objects.values("title", "author__username")

# ✅ annotate() → cálculos en la BD sin traer todos los datos a Python
from django.db.models import Count, Avg
posts = Post.objects.annotate(num_comentarios=Count("comments"))
for post in posts:
    print(f"{post.title}: {post.num_comentarios} comentarios")
'''


# ===========================================================================
# Script verificador y visualizador
# ===========================================================================

def verificar_django() -> bool:
    """
    Verifica si Django está instalado en el entorno actual.

    Returns:
        True si Django está disponible, False si no.
    """
    try:
        import django
        return True
    except ImportError:
        return False


def mostrar_arbol(estructura: str) -> None:
    """
    Imprime la estructura de carpetas del proyecto tipo.

    Args:
        estructura: String multilínea con el árbol de carpetas.
    """
    print("=" * 60)
    print("  ESTRUCTURA DE PROYECTO DJANGO PROFESIONAL")
    print("=" * 60)
    print(estructura)


def mostrar_seccion(titulo: str, contenido: str) -> None:
    """
    Imprime una sección de código con su título.

    Args:
        titulo  : Nombre de la sección.
        contenido: Código de ejemplo como string.
    """
    print(f"\n{'─' * 60}")
    print(f"  {titulo}")
    print('─' * 60)
    print(contenido)


def main() -> None:
    """
    Muestra la guía completa de Django y verifica si está instalado.
    """
    django_disponible = verificar_django()

    estado = "✓ instalado" if django_disponible else "✗ no instalado (pip install django)"
    print(f"\n  Django: {estado}\n")

    mostrar_arbol(ESTRUCTURA_PROYECTO)
    mostrar_seccion("SETTINGS POR ENTORNO — base.py", SETTINGS_BASE)
    mostrar_seccion("SETTINGS DE DESARROLLO — dev.py", SETTINGS_DEV)
    mostrar_seccion("SETTINGS DE PRODUCCIÓN — prod.py", SETTINGS_PROD)
    mostrar_seccion("DJANGO SIGNALS", SIGNALS_EJEMPLO)
    mostrar_seccion("CUSTOM MANAGEMENT COMMAND", MANAGEMENT_COMMAND)
    mostrar_seccion("OPTIMIZACIÓN DE QUERIES", OPTIMIZACION_QUERIES)

    print("\n" + "=" * 60)
    print("  COMANDOS CLAVE DE DJANGO")
    print("=" * 60)
    comandos = [
        ("Crear proyecto",       "django-admin startproject config ."),
        ("Crear app",            "python manage.py startapp users"),
        ("Migraciones",          "python manage.py makemigrations && python manage.py migrate"),
        ("Superusuario",         "python manage.py createsuperuser"),
        ("Servidor dev",         "python manage.py runserver"),
        ("Shell interactivo",    "python manage.py shell"),
        ("Archivos estáticos",   "python manage.py collectstatic"),
        ("Correr tests",         "python manage.py test"),
        ("Comando personalizado","python manage.py seed_users --count 50"),
    ]
    for nombre, cmd in comandos:
        print(f"  {nombre:<25} → {cmd}")


if __name__ == "__main__":
    main()
