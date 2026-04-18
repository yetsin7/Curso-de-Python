# =============================================================================
# CAPÍTULO 20 — Django
# Archivo 05: Sistema de autenticación de Django
# =============================================================================
# Django incluye un sistema completo de autenticación:
# - Modelo User con manejo seguro de contraseñas
# - Login, logout, registro, cambio/reset de contraseña
# - Permisos granulares por objeto o por modelo
# - Grupos para asignar permisos a conjuntos de usuarios
# - AbstractUser para extender el User sin reemplazarlo
# =============================================================================

try:
    import django
    DJANGO_DISPONIBLE = True
except ImportError:
    DJANGO_DISPONIBLE = False
    print("Django no instalado. Instala: pip install django\n")


# =============================================================================
# SECCIÓN 1: El modelo User de Django
# =============================================================================

CODIGO_USER_MODEL = '''
# ============================================================
# EL MODELO USER DE DJANGO
# ============================================================
# Django incluye django.contrib.auth.models.User con estos campos:
#
#   username        → Identificador único de login (obligatorio)
#   email           → Email del usuario
#   password        → Hash de la contraseña (NUNCA en texto plano)
#   first_name      → Nombre
#   last_name       → Apellido
#   is_active       → Si puede iniciar sesión (True/False)
#   is_staff        → Acceso al panel /admin/ (True/False)
#   is_superuser    → Todos los permisos sin verificación (True/False)
#   date_joined     → Cuándo se registró
#   last_login      → Última vez que inició sesión
#   groups          → ManyToMany con Group
#   user_permissions → Permisos específicos del usuario
#
# MÉTODOS ÚTILES DEL USER:
from django.contrib.auth.models import User

user = User.objects.get(username="ana")

# Verificar contraseña sin exponer el hash
user.check_password("mi_contraseña")  # True/False

# Cambiar contraseña de forma segura (hashea automáticamente)
user.set_password("nueva_contraseña")
user.save()

# Verificar permisos
user.has_perm("blog.add_post")         # Permiso específico
user.has_module_perms("blog")          # Algún permiso del módulo
user.get_all_permissions()             # Todos sus permisos

# Crear usuario de forma segura
nuevo_user = User.objects.create_user(
    username="pedro",
    email="pedro@ejemplo.com",
    password="contraseña_segura",      # Se hashea automáticamente
)
'''


# =============================================================================
# SECCIÓN 2: AbstractUser — extender el modelo User
# =============================================================================

CODIGO_ABSTRACT_USER = '''
# ============================================================
# accounts/models.py — Extender User con AbstractUser
# ============================================================
# Por qué AbstractUser y no editar el User de Django directamente:
# - El User de Django no se puede modificar sin romper cosas
# - AbstractUser nos da todos los campos y métodos del User original
# - Podemos añadir nuestros campos y auth.User seguirá funcionando
#
# IMPORTANTE: Definir AUTH_USER_MODEL ANTES de la primera migración.
# Cambiarlo después es posible pero muy tedioso.
# ============================================================

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Usuario personalizado que extiende el User de Django.

    AbstractUser incluye todos los campos y métodos del User estándar.
    Solo añadimos los campos adicionales que necesitamos.

    Configuración requerida en settings.py:
        AUTH_USER_MODEL = "accounts.CustomUser"
    """

    # Bio opcional del usuario
    bio = models.TextField(blank=True, verbose_name="Biografía")

    # Avatar del perfil
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Avatar",
    )

    # URL del sitio web personal
    website = models.URLField(blank=True, verbose_name="Sitio web")

    # Fecha de nacimiento para perfiles
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de nacimiento",
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    @property
    def nombre_completo(self) -> str:
        """Nombre completo o username si no tiene nombre configurado."""
        return self.get_full_name() or self.username


# ============================================================
# settings.py — Configuración necesaria para CustomUser
# ============================================================

# Esta línea le dice a Django qué modelo usar como User
# DEBE estar en settings.py antes de la primera migración
AUTH_USER_MODEL = "accounts.CustomUser"

# Si usas DRF, configura esto también:
# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": [
#         "rest_framework.authentication.SessionAuthentication",
#     ]
# }
'''


# =============================================================================
# SECCIÓN 3: Vistas de autenticación
# =============================================================================

CODIGO_AUTH_VIEWS = '''
# ============================================================
# accounts/views.py — Login, logout y registro
# ============================================================

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm


def login_view(request):
    """
    Vista de login personalizada.

    Por qué no usar la vista built-in de Django:
    Podemos personalizarla para nuestra UI, agregar intentos fallidos,
    2FA, o lógica especial. Si no necesitamos personalización,
    las vistas de django.contrib.auth.views son perfectas.
    """
    if request.user.is_authenticated:
        return redirect("blog:post_list")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # login() establece la sesión del usuario
            login(request, user)
            messages.success(request, f"Bienvenido de vuelta, {user.username}!")

            # Redirigimos a la página que intentaba visitar, o a home
            siguiente = request.GET.get("next", "blog:post_list")
            return redirect(siguiente)
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """
    Solo acepta POST para evitar logout con links GET (CSRF protection).
    """
    if request.method == "POST":
        logout(request)  # Limpia la sesión
        messages.info(request, "Sesión cerrada correctamente.")
    return redirect("blog:post_list")


def register_view(request):
    """
    Registro de nuevos usuarios.
    """
    if request.user.is_authenticated:
        return redirect("blog:post_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # commit=False para añadir lógica antes de guardar
            user = form.save(commit=False)
            user.is_active = True  # Activo de inmediato (sin verificación email)
            user.save()

            # Logueamos al usuario automáticamente tras registrarse
            login(request, user)
            messages.success(request, f"Cuenta creada. ¡Bienvenido, {user.username}!")
            return redirect("blog:post_list")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    """
    @login_required: si no está autenticado, redirige a settings.LOGIN_URL.
    Por defecto LOGIN_URL = "/accounts/login/"
    """
    return render(request, "accounts/profile.html", {"user": request.user})


@permission_required("blog.add_post", raise_exception=True)
def create_post_staff(request):
    """
    @permission_required: requiere un permiso específico.
    raise_exception=True → devuelve 403 en lugar de redirigir al login.
    Sin raise_exception → redirige al login (confuso si ya está logueado).
    """
    pass
'''


# =============================================================================
# SECCIÓN 4: Formulario de registro personalizado
# =============================================================================

CODIGO_REGISTER_FORM = '''
# ============================================================
# accounts/forms.py — Formulario de registro
# ============================================================

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# get_user_model() retorna el modelo de usuario activo (nuestro CustomUser
# si definimos AUTH_USER_MODEL, o el User estándar si no)
User = get_user_model()


class RegisterForm(UserCreationForm):
    """
    Formulario de registro extendido.

    UserCreationForm incluye username, password1, password2 con validación.
    Añadimos email, nombre y apellido.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "tu@email.com"}),
    )
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label="Nombre",
        widget=forms.TextInput(attrs={"placeholder": "Tu nombre"}),
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        label="Apellido",
        widget=forms.TextInput(attrs={"placeholder": "Tu apellido"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def clean_email(self):
        """Validación: email único en el sistema."""
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese email.")
        return email
'''


# =============================================================================
# SECCIÓN 5: Permisos y grupos
# =============================================================================

CODIGO_PERMISOS = '''
# ============================================================
# PERMISOS EN DJANGO
# ============================================================
# Django crea automáticamente 4 permisos por cada modelo:
#   app.add_modelo     → Puede crear objetos
#   app.view_modelo    → Puede ver objetos
#   app.change_modelo  → Puede editar objetos
#   app.delete_modelo  → Puede eliminar objetos
#
# Ejemplo para Post: blog.add_post, blog.view_post, etc.
# ============================================================

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()

# --- Asignar permiso a un usuario ---
user = User.objects.get(username="ana")
permiso = Permission.objects.get(codename="add_post")
user.user_permissions.add(permiso)

# --- Verificar permisos en código Python ---
if user.has_perm("blog.add_post"):
    print("Ana puede crear posts")

# --- Verificar en templates ---
# {% if perms.blog.add_post %}
#     <a href="{% url 'blog:post_create' %}">Nuevo post</a>
# {% endif %}

# --- Grupos: asignar permisos a conjuntos de usuarios ---
# Creamos un grupo "Editores" con permisos de blog
grupo_editores, _ = Group.objects.get_or_create(name="Editores")

# Asignamos permisos al grupo
for codename in ["add_post", "change_post", "view_post"]:
    permiso = Permission.objects.get(codename=codename)
    grupo_editores.permissions.add(permiso)

# Añadimos usuarios al grupo
user.groups.add(grupo_editores)

# Todos los usuarios del grupo heredan sus permisos automáticamente

# --- Permiso personalizado en el modelo ---
class Post(models.Model):
    class Meta:
        permissions = [
            # (codename, descripción legible)
            ("publish_post", "Puede publicar posts"),
            ("feature_post", "Puede destacar posts"),
        ]

# Acceder al permiso personalizado:
# user.has_perm("blog.publish_post")
'''


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 65)
    print("DJANGO — SISTEMA DE AUTENTICACIÓN")
    print("=" * 65)

    print("\n[1] El modelo User de Django:")
    print(CODIGO_USER_MODEL)

    print("\n[2] Extender User con AbstractUser:")
    print(CODIGO_ABSTRACT_USER)

    print("\n[3] Vistas de Login, Logout y Registro:")
    print(CODIGO_AUTH_VIEWS)

    print("\n[4] Formulario de registro personalizado:")
    print(CODIGO_REGISTER_FORM)

    print("\n[5] Permisos y grupos:")
    print(CODIGO_PERMISOS)

    print("\n" + "=" * 65)
    print("URLs de auth incluidas con django.contrib.auth.urls:")
    print("  /accounts/login/               → Iniciar sesión")
    print("  /accounts/logout/              → Cerrar sesión")
    print("  /accounts/password_change/     → Cambiar contraseña")
    print("  /accounts/password_reset/      → Resetear contraseña")
    print("Fin — siguiente: 06_django_rest_framework.py")
    print("=" * 65)
