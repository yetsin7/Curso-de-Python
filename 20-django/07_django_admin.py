# =============================================================================
# CAPÍTULO 20 — Django
# Archivo 07: Personalización del panel de administración de Django
# =============================================================================
# El admin de Django es una de sus características más potentes.
# Con solo registrar un modelo tienes un CRUD completo y seguro.
# Personalizándolo con ModelAdmin, el admin se convierte en una
# herramienta de gestión profesional sin escribir casi HTML.
# =============================================================================

try:
    import django
    DJANGO_DISPONIBLE = True
except ImportError:
    DJANGO_DISPONIBLE = False
    print("Django no instalado. Instala: pip install django\n")


# =============================================================================
# SECCIÓN 1: Registro básico vs ModelAdmin personalizado
# =============================================================================

CODIGO_ADMIN_BASICO = '''
# ============================================================
# blog/admin.py — Registro básico (sin personalización)
# ============================================================
# Solo con estas líneas ya tienes CRUD completo en /admin/
# Suficiente para proyectos pequeños o durante desarrollo.
# ============================================================

from django.contrib import admin
from .models import Post, Category, Tag, Comment

# Registro simple — Django genera interfaz mínima automáticamente
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Comment)
'''

CODIGO_ADMIN_COMPLETO = '''
# ============================================================
# blog/admin.py — Admin completamente personalizado
# ============================================================

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count
from .models import Post, Category, Tag, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin para categorías.

    @admin.register(Category) es equivalente a admin.site.register(Category, CategoryAdmin)
    pero más limpio y moderno.
    """

    # list_display: columnas visibles en la lista de objetos
    list_display = ["name", "slug", "post_count", "description_short"]

    # list_filter: filtros en el panel derecho de la lista
    list_filter = ["name"]

    # search_fields: activa el buscador — busca en estos campos
    search_fields = ["name", "description"]

    # prepopulated_fields: genera el slug automáticamente desde el nombre
    # en el frontend con JavaScript mientras el admin escribe el nombre
    prepopulated_fields = {"slug": ("name",)}

    # ordering: orden por defecto en la lista
    ordering = ["name"]

    def post_count(self, obj) -> int:
        """Columna calculada: cuántos posts tiene la categoría."""
        return obj.posts.count()

    # short_description es la etiqueta de la columna en la lista
    post_count.short_description = "Posts"

    def description_short(self, obj) -> str:
        """Versión truncada de la descripción para la lista."""
        return (obj.description[:50] + "...") if len(obj.description) > 50 else obj.description

    description_short.short_description = "Descripción"

    def get_queryset(self, request):
        """
        Sobreescribimos para añadir anotación de conteo de posts.
        Evita N queries — mejor que llamar obj.posts.count() por fila.
        """
        return super().get_queryset(request).annotate(
            _post_count=Count("posts")
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin de tags — sencillo."""
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


class CommentInline(admin.TabularInline):
    """
    Inline: muestra y permite editar comentarios dentro del admin de Post.

    TabularInline: comentarios en tabla horizontal (compacto).
    StackedInline: cada comentario expandido verticalmente (más detalle).
    """
    model = Comment
    # Cuántos formularios vacíos añadir al final para nuevos comentarios
    extra = 0
    # Campos a mostrar en el inline
    fields = ["author_name", "author_email", "body", "is_approved"]
    # Solo permitimos editar estos campos — el resto es de solo lectura
    readonly_fields = ["author_name", "author_email", "created_at"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin altamente personalizado para posts.
    Muestra la potencia completa del sistema de admin de Django.
    """

    # ---- Configuración de la lista ----

    list_display = [
        "title",
        "author",
        "category",
        "status_badge",   # Campo calculado con HTML
        "views_count",
        "published_at",
        "created_at",
    ]

    # Campos que son links al formulario de edición
    list_display_links = ["title"]

    # Campos editables directamente desde la lista (sin entrar al detalle)
    list_editable = ["status"]  # No funciona si está en list_display_links

    list_filter = ["status", "category", "author", "created_at"]

    search_fields = ["title", "body", "excerpt", "author__username"]

    # date_hierarchy añade navegación por fecha en la parte superior
    date_hierarchy = "created_at"

    ordering = ["-created_at"]

    # Cuántos objetos por página en la lista
    list_per_page = 25

    # Permite seleccionar todos los objetos entre páginas
    show_full_result_count = True

    # ---- Configuración del formulario de edición ----

    # fieldsets organiza los campos en secciones con título
    fieldsets = [
        (
            "Contenido",  # Título de la sección (None para sin título)
            {
                "fields": ["title", "slug", "excerpt", "body", "cover_image"],
            },
        ),
        (
            "Clasificación",
            {
                "fields": ["category", "tags"],
            },
        ),
        (
            "Publicación",
            {
                "fields": ["author", "status", "published_at"],
                # "classes": ["collapse"] haría la sección colapsable
            },
        ),
        (
            "Metadatos",
            {
                "fields": ["views_count", "created_at", "updated_at"],
                "classes": ["collapse"],  # Sección colapsada por defecto
            },
        ),
    ]

    # Campos que se generan automáticamente — solo lectura en el form
    readonly_fields = ["slug", "views_count", "created_at", "updated_at"]

    # filter_horizontal: widget más cómodo para ManyToManyField
    # (dos cuadros: disponibles y seleccionados, con búsqueda)
    filter_horizontal = ["tags"]

    # Mostramos los comentarios dentro del post (Inline)
    inlines = [CommentInline]

    # ---- Métodos de columnas personalizadas ----

    def status_badge(self, obj) -> str:
        """
        Columna con badge de color según el estado del post.
        format_html protege contra XSS — SIEMPRE úsalo cuando generes HTML.
        """
        colores = {
            "published": "#28a745",  # Verde
            "draft": "#6c757d",       # Gris
        }
        color = colores.get(obj.status, "#6c757d")
        etiqueta = obj.get_status_display()  # Devuelve el verbose del choice

        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color,
            etiqueta,
        )

    status_badge.short_description = "Estado"
    # allow_tags ya no es necesario en Django 4+ (format_html es suficiente)

    # ---- Acciones personalizadas ----

    # actions: lista de funciones de acción disponibles en el admin
    actions = ["publicar_posts", "guardar_como_borrador"]

    @admin.action(description="Publicar posts seleccionados")
    def publicar_posts(self, request, queryset):
        """
        Acción para publicar múltiples posts de una vez desde la lista.

        queryset contiene los posts seleccionados por el usuario.
        """
        actualizados = queryset.filter(status="draft").update(
            status="published",
            published_at=timezone.now(),
        )
        # self.message_user envía un mensaje flash al admin
        self.message_user(
            request,
            f"{actualizados} post(s) publicados correctamente.",
            level="success",
        )

    @admin.action(description="Guardar como borrador")
    def guardar_como_borrador(self, request, queryset):
        """Acción inversa: pasar posts publicados a borrador."""
        actualizados = queryset.update(status="draft")
        self.message_user(
            request,
            f"{actualizados} post(s) guardados como borrador.",
        )

    # ---- Sobreescribir comportamiento ----

    def save_model(self, request, obj, form, change):
        """
        Sobreescribimos save_model para asignar author automáticamente.
        'change' es True si es edición, False si es creación nueva.
        """
        if not change:  # Solo al crear, no al editar
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """
        Los autores normales solo ven sus propios posts.
        El staff y superusuarios ven todos.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs
        return qs.filter(author=request.user)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin de comentarios con acción de aprobación masiva."""

    list_display = ["__str__", "post", "is_approved", "created_at"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["body", "author_name", "author_email", "post__title"]
    list_editable = ["is_approved"]
    actions = ["aprobar_comentarios"]
    readonly_fields = ["created_at"]

    @admin.action(description="Aprobar comentarios seleccionados")
    def aprobar_comentarios(self, request, queryset):
        cantidad = queryset.update(is_approved=True)
        self.message_user(request, f"{cantidad} comentario(s) aprobados.")
'''


# =============================================================================
# SECCIÓN 2: Personalización global del Admin Site
# =============================================================================

CODIGO_ADMIN_SITE = '''
# ============================================================
# blog/apps.py o mi_blog/admin.py — Personalización global del admin
# ============================================================

from django.contrib import admin

# Cambia el título del navegador y la cabecera del panel admin
admin.site.site_header = "Administración del Blog"
admin.site.site_title = "Blog Admin"
admin.site.index_title = "Panel de Control"

# ============================================================
# Crear un Admin Site personalizado (avanzado)
# ============================================================
# Si necesitas múltiples paneles admin (uno para clientes, otro para staff):

from django.contrib.admin import AdminSite


class StaffAdminSite(AdminSite):
    """Admin site solo para el equipo interno."""
    site_header = "Administración Interna"
    site_title = "Staff Admin"

    def has_permission(self, request):
        """Solo staff puede acceder a este panel."""
        return request.user.is_active and request.user.is_staff


# Instancia del admin personalizado
staff_admin = StaffAdminSite(name="staff_admin")

# Registramos modelos en el admin personalizado
# staff_admin.register(Post, PostAdmin)

# En urls.py:
# path("staff/", staff_admin.urls),
'''


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 65)
    print("DJANGO ADMIN — PERSONALIZACIÓN COMPLETA")
    print("=" * 65)

    print("\n[1] Registro básico del admin:")
    print(CODIGO_ADMIN_BASICO)

    print("\n[2] Admin completamente personalizado:")
    print(CODIGO_ADMIN_COMPLETO)

    print("\n[3] Personalización global del admin site:")
    print(CODIGO_ADMIN_SITE)

    print("\n" + "=" * 65)
    print("RESUMEN — Características del Admin de Django:")
    print("  list_display      → Columnas en la lista de objetos")
    print("  list_filter       → Filtros laterales")
    print("  search_fields     → Buscador por texto")
    print("  list_editable     → Edición inline en la lista")
    print("  fieldsets         → Organización del formulario en secciones")
    print("  readonly_fields   → Campos no editables")
    print("  filter_horizontal → Widget cómodo para M2M")
    print("  inlines           → Editar relaciones dentro del objeto padre")
    print("  actions           → Acciones masivas desde la lista")
    print("  prepopulated_fields → Autorellenar campos (ej: slug desde title)")
    print("  date_hierarchy    → Navegación por fecha")
    print()
    print("  Accede al admin en: http://127.0.0.1:8000/admin/")
    print("  Crea superusuario: python manage.py createsuperuser")
    print("=" * 65)
