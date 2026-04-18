# =============================================================================
# CAPÍTULO 20 — Django
# Archivo 03: Vistas y URLs — FBV, CBV y configuración de rutas
# =============================================================================
# Las vistas son el "controlador" en MTV. Reciben un HttpRequest,
# ejecutan lógica (consultan el ORM, procesan datos), y devuelven
# un HttpResponse (HTML, JSON, redirect, etc.).
#
# Django ofrece dos estilos: Function-Based Views (FBV) y
# Class-Based Views (CBV). Ambos son válidos — cada uno tiene ventajas.
# =============================================================================

try:
    import django
    DJANGO_DISPONIBLE = True
except ImportError:
    DJANGO_DISPONIBLE = False
    print("Django no instalado. Archivo educativo — instala: pip install django\n")


# =============================================================================
# SECCIÓN 1: Function-Based Views (FBV)
# =============================================================================

CODIGO_FBV = '''
# ============================================================
# FUNCTION-BASED VIEWS (FBV) — blog/views.py
# ============================================================
# Por qué FBV: son simples, explícitas y fáciles de entender.
# Ideales para vistas con lógica personalizada o pocas variantes.
# ============================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm


def post_list(request: HttpRequest) -> HttpResponse:
    """
    Lista todos los posts publicados con paginación.

    Por qué get_queryset aquí: separar la consulta de la vista
    permite reutilizarla y facilita los tests.
    """
    # Solo mostramos posts publicados a visitantes
    posts = Post.objects.filter(
        status="published"
    ).select_related("author", "category").prefetch_related("tags")

    # Filtro por categoría desde query param: /posts/?categoria=python
    categoria_slug = request.GET.get("categoria")
    if categoria_slug:
        posts = posts.filter(category__slug=categoria_slug)

    # Paginación: 10 posts por página
    paginator = Paginator(posts, 10)
    numero_pagina = request.GET.get("pagina", 1)
    pagina = paginator.get_page(numero_pagina)

    categorias = Category.objects.all()

    # render() busca el template y le pasa el contexto (dict)
    return render(request, "blog/post_list.html", {
        "pagina": pagina,
        "categorias": categorias,
        "categoria_activa": categoria_slug,
    })


def post_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Detalle de un post con sus comentarios y formulario para comentar.

    get_object_or_404: si el post no existe, devuelve 404 automáticamente.
    Evita el try/except Post.DoesNotExist repetido en cada vista.
    """
    # get_object_or_404 lanza Http404 si no encuentra el objeto
    post = get_object_or_404(Post, slug=slug, status="published")

    # Incrementamos vistas de forma thread-safe con F()
    post.incrementar_vistas()

    # Solo comentarios aprobados, con datos del autor precargados
    comentarios = post.comments.filter(
        is_approved=True
    ).select_related("author")

    # Procesamos el formulario de comentario si es POST
    form = CommentForm()
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)  # No guardar aún
            comentario.post = post                # Asignamos el post
            if request.user.is_authenticated:
                comentario.author = request.user  # Usuario logueado
            comentario.save()
            # messages.success añade un mensaje flash al contexto
            messages.success(request, "Comentario enviado. Pendiente de aprobación.")
            # redirect evita que recargar la página reenvíe el POST
            return redirect("blog:post_detail", slug=slug)

    return render(request, "blog/post_detail.html", {
        "post": post,
        "comentarios": comentarios,
        "form": form,
    })


@login_required  # Redirige a login si el usuario no está autenticado
def post_create(request: HttpRequest) -> HttpResponse:
    """
    Formulario para crear un nuevo post.

    @login_required: decorador que verifica autenticación.
    Si no está logueado, redirige a settings.LOGIN_URL.
    """
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)  # FILES para imágenes
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # El autor es el usuario actual
            post.save()
            # save_m2m() es necesario cuando usamos commit=False con M2M
            form.save_m2m()
            messages.success(request, f"Post '{post.title}' creado exitosamente.")
            return redirect("blog:post_detail", slug=post.slug)
    else:
        # GET: mostramos el formulario vacío
        form = PostForm()

    return render(request, "blog/post_form.html", {
        "form": form,
        "titulo": "Crear nuevo post",
    })


@login_required
def post_delete(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Elimina un post. Solo acepta POST para evitar eliminaciones accidentales
    con una petición GET (como un link malicioso en otro sitio).
    """
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == "POST":
        titulo = post.title
        post.delete()
        messages.success(request, f"Post '{titulo}' eliminado.")
        return redirect("blog:post_list")

    # Si es GET, mostramos pantalla de confirmación
    return render(request, "blog/post_confirm_delete.html", {"post": post})


def api_posts_json(request: HttpRequest) -> JsonResponse:
    """
    Vista que devuelve posts en formato JSON (mini-API sin DRF).

    JsonResponse serializa automáticamente el dict a JSON y establece
    el header Content-Type: application/json.
    """
    posts = Post.objects.filter(status="published").values(
        "id", "title", "slug", "author__username", "created_at"
    )[:20]

    # values() retorna QuerySet de dicts — lo convertimos a lista
    datos = list(posts)

    # JsonResponse acepta dict o lista con safe=False
    return JsonResponse({"posts": datos, "total": len(datos)})
'''


# =============================================================================
# SECCIÓN 2: Class-Based Views (CBV)
# =============================================================================

CODIGO_CBV = '''
# ============================================================
# CLASS-BASED VIEWS (CBV) — blog/views_cbv.py
# ============================================================
# Por qué CBV: encapsulan patrones comunes (listar, crear, editar)
# en clases reutilizables. Menos código repetido para CRUD estándar.
# Desventaja: más "magia" — menos obvia que FBV para principiantes.
# ============================================================

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Post, Category


class PostListView(ListView):
    """
    Lista de posts usando CBV ListView.

    ListView gestiona automáticamente:
    - Consultar todos los objetos del model
    - Paginación
    - Pasar el contexto al template con nombre estándar "object_list"
    """
    model = Post
    # Template: blog/post_list.html (convención: modelo_list.html)
    template_name = "blog/post_list.html"
    # Nombre de la variable en el template
    context_object_name = "posts"
    # Posts por página
    paginate_by = 10

    def get_queryset(self):
        """
        Sobreescribimos para personalizar la consulta.
        Solo mostramos posts publicados, con datos relacionados precargados.
        """
        return (
            Post.objects.filter(status="published")
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        """
        Añadimos datos adicionales al contexto del template.
        Llamamos a super() para mantener el contexto base de ListView.
        """
        contexto = super().get_context_data(**kwargs)
        contexto["categorias"] = Category.objects.all()
        return contexto


class PostDetailView(DetailView):
    """
    Detalle de un post. DetailView maneja get_object() automáticamente
    buscando por pk o slug según la URL.
    """
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    # Indica que el lookup se hace por el campo 'slug' en lugar de pk
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Solo posts publicados son accesibles."""
        return Post.objects.filter(status="published")


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Formulario de creación de post.

    LoginRequiredMixin: equivale a @login_required pero para CBV.
    Si no está autenticado, redirige a login_url.
    """
    model = Post
    # Campos del formulario a mostrar (o usa form_class=MiFormulario)
    fields = ["title", "category", "tags", "excerpt", "body", "status"]
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        """
        Se llama cuando el formulario es válido, antes de guardar.
        Aprovechamos para asignar el autor automáticamente.
        """
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """URL a la que redirigir tras crear exitosamente."""
        return self.object.get_absolute_url()


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Formulario de edición. UserPassesTestMixin verifica permisos
    personalizados — aquí que el usuario sea el autor del post.
    """
    model = Post
    fields = ["title", "category", "tags", "excerpt", "body", "status"]
    template_name = "blog/post_form.html"

    def test_func(self):
        """
        test_func de UserPassesTestMixin: retorna True si el usuario
        tiene permiso. Si retorna False, devuelve 403 Forbidden.
        """
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Confirmación y eliminación de post.
    success_url a donde redirigir tras eliminar.
    """
    model = Post
    template_name = "blog/post_confirm_delete.html"
    # reverse_lazy porque success_url se evalúa antes de que las URLs estén listas
    success_url = reverse_lazy("blog:post_list")

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
'''


# =============================================================================
# SECCIÓN 3: Configuración de URLs
# =============================================================================

CODIGO_URLS = '''
# ============================================================
# blog/urls.py — URLs de la app blog
# ============================================================

from django.urls import path
from . import views

# app_name activa los namespaces para reverse() en templates:
# {% url "blog:post_list" %} en lugar de {% url "post_list" %}
# Evita colisiones de nombres entre distintas apps.
app_name = "blog"

urlpatterns = [
    # path(ruta, vista, name=nombre_para_reverse)
    # La ruta no incluye el prefijo — ese lo define el proyecto

    # Lista de posts: /blog/
    path("", views.post_list, name="post_list"),

    # Detalle de post por slug: /blog/mi-primer-post/
    # <slug:slug> captura el parámetro y lo pasa como kwarg a la vista
    path("<slug:slug>/", views.post_detail, name="post_detail"),

    # Crear post: /blog/crear/
    path("crear/", views.post_create, name="post_create"),

    # Editar post: /blog/mi-post/editar/
    path("<slug:slug>/editar/", views.PostUpdateView.as_view(), name="post_update"),

    # Eliminar post: /blog/mi-post/eliminar/
    path("<slug:slug>/eliminar/", views.post_delete, name="post_delete"),

    # Mini-API JSON: /blog/api/posts/
    path("api/posts/", views.api_posts_json, name="api_posts"),
]

# ============================================================
# mi_blog/urls.py — URLs raíz del proyecto
# ============================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración de Django
    path("admin/", admin.site.urls),

    # Incluimos las URLs de la app blog con prefijo "blog/"
    # include() con namespace requiere que la app tenga app_name
    path("blog/", include("blog.urls", namespace="blog")),

    # Autenticación built-in de Django (login, logout, password reset)
    path("accounts/", include("django.contrib.auth.urls")),
]

# En desarrollo, servimos archivos media directamente
# En producción esto lo maneja nginx/apache/CDN
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# ============================================================
# Tipos de capturadores en path():
# ============================================================
# <int:pk>         → Entero positivo: /posts/42/
# <slug:slug>      → Slug (letras, números, guiones): /posts/mi-post/
# <str:nombre>     → Cualquier string sin "/": /users/ana/
# <uuid:id>        → UUID: /items/550e8400-e29b-41d4-a716/
# <path:ruta>      → String que puede incluir "/": /archivos/img/foto.jpg

# re_path() para patrones más complejos con regex:
# from django.urls import re_path
# re_path(r"^legacy/(?P<anio>[0-9]{4})/$", views.legacy_view),
'''


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def mostrar_comparacion_fbv_cbv() -> None:
    """Muestra la comparación entre FBV y CBV con sus pros y contras."""
    print("""
  FUNCTION-BASED VIEWS (FBV)          CLASS-BASED VIEWS (CBV)
  ─────────────────────────────────   ────────────────────────────────
  + Simples y explícitas              + Menos código para CRUD estándar
  + Fáciles de leer                   + Reutilizables mediante herencia
  + Control total del flujo           + Mixins para funcionalidad común
  + Mejor para lógica personalizada   + Mejor para vistas estándar
  - Código repetido en CRUD           - Más difíciles de seguir el flujo
  - No reutilizables fácilmente       - Curva de aprendizaje mayor

  Recomendación: FBV para aprender y vistas complejas.
  CBV para CRUD estándar (List, Detail, Create, Update, Delete).
""")


if __name__ == "__main__":
    print("=" * 65)
    print("DJANGO — VISTAS Y URLs")
    print("=" * 65)

    print("\n[1] Comparación FBV vs CBV:")
    mostrar_comparacion_fbv_cbv()

    print("\n[2] Function-Based Views — código:")
    print(CODIGO_FBV)

    print("\n[3] Class-Based Views — código:")
    print(CODIGO_CBV)

    print("\n[4] Configuración de URLs:")
    print(CODIGO_URLS)

    print("\n" + "=" * 65)
    print("Fin — siguiente: 04_templates_y_forms.py")
    print("=" * 65)
