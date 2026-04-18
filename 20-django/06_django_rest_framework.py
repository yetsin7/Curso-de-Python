# =============================================================================
# CAPÍTULO 20 — Django
# Archivo 06: Django REST Framework (DRF)
# =============================================================================
# DRF es el paquete más popular para construir APIs REST con Django.
# Proporciona Serializers, ViewSets, Routers, autenticación y más.
#
# Instalación:
#   pip install djangorestframework
#   pip install markdown        (para el navegador de API)
#   pip install django-filter   (para filtros avanzados)
#
# Agregar en settings.py:
#   INSTALLED_APPS = [..., "rest_framework"]
# =============================================================================

try:
    import django
    import rest_framework
    DRF_DISPONIBLE = True
    print(f"DRF instalado: versión {rest_framework.VERSION}")
except ImportError as e:
    DRF_DISPONIBLE = False
    print(f"DRF no instalado: {e}")
    print("Instala con: pip install djangorestframework\n")


# =============================================================================
# SECCIÓN 1: Serializers — el corazón de DRF
# =============================================================================

CODIGO_SERIALIZERS = '''
# ============================================================
# blog/serializers.py — Serializers del blog
# ============================================================
# Por qué Serializers: hacen lo que Django Forms hacen para HTML,
# pero para JSON. Convierten objetos Python ↔ JSON y validan datos.
# ============================================================

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Category, Tag, Comment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer básico de usuario — solo expone campos seguros.

    Por qué no incluir password: nunca exponemos el hash de contraseña.
    Solo retornamos campos públicos del perfil.
    """

    class Meta:
        model = User
        # Especificamos campos explícitamente por seguridad
        fields = ["id", "username", "first_name", "last_name", "email"]
        # read_only_fields: campos que no se pueden modificar via API
        read_only_fields = ["id"]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer de categorías con conteo de posts."""

    # SerializerMethodField para campos calculados que no son del modelo
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "posts_count"]
        read_only_fields = ["id", "slug"]

    def get_posts_count(self, obj) -> int:
        """
        Método para el SerializerMethodField.
        Nombre: get_<nombre_del_campo>.
        """
        return obj.posts.filter(status="published").count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]


class PostListSerializer(serializers.ModelSerializer):
    """
    Serializer para la LISTA de posts — campos resumidos.

    Por qué dos serializers para Post: en la lista no necesitamos
    el body completo (ahorra ancho de banda). En el detalle sí.
    """

    # Nested serializer — incluye el objeto autor completo
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    # StringRelatedField muestra __str__() en lugar del id
    tags = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "title", "slug", "author", "category", "tags",
            "excerpt", "status", "published_at", "views_count",
        ]
        read_only_fields = ["id", "slug", "views_count"]


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para el DETALLE de un post — campos completos.
    Incluye el body y los comentarios.
    """

    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "title", "slug", "author", "category", "tags",
            "excerpt", "body", "cover_image", "status",
            "created_at", "updated_at", "published_at", "views_count",
            "comments",
        ]
        read_only_fields = ["id", "slug", "views_count", "created_at", "updated_at"]

    def get_comments(self, obj) -> list:
        """Retorna los comentarios aprobados del post."""
        comentarios = obj.comments.filter(is_approved=True)
        return CommentSerializer(comentarios, many=True).data


class PostWriteSerializer(serializers.ModelSerializer):
    """
    Serializer separado para ESCRIBIR (crear/editar) posts.

    Por qué separado: cuando el cliente envía datos, usa IDs de categoría
    y tags, no objetos anidados completos. Separamos lectura y escritura.
    """

    # PrimaryKeyRelatedField acepta el ID del objeto relacionado
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Post
        fields = ["title", "category", "tags", "excerpt", "body", "status"]

    def validate_title(self, valor):
        """Validación del campo title — mismo patrón que Django Forms."""
        if len(valor.strip()) < 5:
            raise serializers.ValidationError(
                "El título debe tener al menos 5 caracteres."
            )
        return valor.strip()

    def create(self, validated_data):
        """
        Sobreescribimos create para manejar el author y los tags (M2M).
        validated_data viene del serializer después de la validación.
        """
        # Extraemos tags antes de crear el post (M2M requiere que el objeto exista)
        tags = validated_data.pop("tags", [])

        # El author viene del contexto de la request (seteado en la vista)
        validated_data["author"] = self.context["request"].user

        post = Post.objects.create(**validated_data)
        post.tags.set(tags)  # Asignamos los tags
        return post

    def update(self, instance, validated_data):
        """Sobreescribimos update para manejar tags M2M."""
        tags = validated_data.pop("tags", None)
        # Actualizamos los campos del post
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author_name", "author_email", "body", "created_at"]
        read_only_fields = ["id", "created_at"]
'''


# =============================================================================
# SECCIÓN 2: ViewSets y Routers
# =============================================================================

CODIGO_VIEWSETS = '''
# ============================================================
# blog/api_views.py — ViewSets de DRF
# ============================================================
# ViewSet agrupa todas las acciones de un recurso en una clase:
# list, create, retrieve, update, partial_update, destroy
# ============================================================

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Category, Tag
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostWriteSerializer,
    CategorySerializer, TagSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para posts — CRUD automático.

    ModelViewSet implementa automáticamente:
      GET    /posts/         → list()
      POST   /posts/         → create()
      GET    /posts/{id}/    → retrieve()
      PUT    /posts/{id}/    → update()
      PATCH  /posts/{id}/    → partial_update()
      DELETE /posts/{id}/    → destroy()
    """

    # Permisos: IsAuthenticatedOrReadOnly permite lectura a todos,
    # escritura solo a usuarios autenticados
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Filtrado, búsqueda y ordenamiento automáticos
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "category__slug", "author__username"]
    search_fields = ["title", "body", "excerpt"]     # ?search=python
    ordering_fields = ["published_at", "views_count"]  # ?ordering=-views_count

    def get_queryset(self):
        """
        Retorna posts según el usuario: todos para staff, solo publicados para otros.
        """
        if self.request.user.is_staff:
            return Post.objects.all().select_related("author", "category")
        return Post.objects.filter(
            status="published"
        ).select_related("author", "category")

    def get_serializer_class(self):
        """
        Elige el serializer según la acción.
        Por qué: usamos serializers distintos para lista, detalle y escritura.
        """
        if self.action == "list":
            return PostListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return PostWriteSerializer
        return PostDetailSerializer

    def get_permissions(self):
        """
        Permisos más granulares: solo el autor puede editar/eliminar su post.
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        return super().get_permissions()

    # @action define endpoints adicionales fuera del CRUD estándar
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        """
        Endpoint personalizado: POST /posts/{id}/publish/
        Publica un post borrador.
        """
        post = self.get_object()

        if post.author != request.user and not request.user.is_staff:
            return Response(
                {"error": "No tienes permiso para publicar este post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if post.status == "published":
            return Response({"message": "El post ya está publicado."})

        post.status = "published"
        post.save()
        return Response({"message": f"Post '{post.title}' publicado."})

    @action(detail=False, methods=["get"])
    def populares(self, request):
        """
        Endpoint personalizado: GET /posts/populares/
        Los 10 posts más vistos.
        """
        posts = self.get_queryset().order_by("-views_count")[:10]
        serializer = PostListSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para categorías.
    ReadOnlyModelViewSet solo implementa list() y retrieve().
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # Buscamos por slug o nombre: GET /categories/python-avanzado/
    lookup_field = "slug"


# ============================================================
# Permiso personalizado: solo el autor puede modificar
# ============================================================

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    Permiso personalizado: lectura para todos, escritura solo para el autor.

    SAFE_METHODS = ("GET", "HEAD", "OPTIONS") — métodos de solo lectura.
    """

    def has_object_permission(self, request, view, obj):
        # Peticiones de solo lectura: siempre permitidas
        if request.method in SAFE_METHODS:
            return True
        # Escritura: solo el autor o staff
        return obj.author == request.user or request.user.is_staff
'''


# =============================================================================
# SECCIÓN 3: Router y configuración de URLs
# =============================================================================

CODIGO_ROUTER = '''
# ============================================================
# blog/api_urls.py — Rutas automáticas con Router
# ============================================================
# Router genera automáticamente todas las URLs del ViewSet:
# sin tener que definir cada path() manualmente.
# ============================================================

from rest_framework.routers import DefaultRouter
from . import api_views

# DefaultRouter genera URLs estándar y también una URL raíz
# que lista todos los endpoints disponibles
router = DefaultRouter()

# router.register(prefijo, ViewSet, basename)
router.register(r"posts", api_views.PostViewSet, basename="post")
router.register(r"categories", api_views.CategoryViewSet, basename="category")

# URLs generadas automáticamente:
#   GET    /api/posts/              → PostViewSet.list()
#   POST   /api/posts/              → PostViewSet.create()
#   GET    /api/posts/{id}/         → PostViewSet.retrieve()
#   PUT    /api/posts/{id}/         → PostViewSet.update()
#   PATCH  /api/posts/{id}/         → PostViewSet.partial_update()
#   DELETE /api/posts/{id}/         → PostViewSet.destroy()
#   POST   /api/posts/{id}/publish/ → PostViewSet.publish()
#   GET    /api/posts/populares/    → PostViewSet.populares()

urlpatterns = router.urls


# ============================================================
# mi_blog/urls.py — Incluir API en el proyecto
# ============================================================

from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("blog.urls")),
    # Todas las rutas de la API bajo /api/
    path("api/", include("blog.api_urls")),
    # Navegador de API de DRF (para explorar la API en el browser)
    path("api-auth/", include("rest_framework.urls")),
]
'''


# =============================================================================
# SECCIÓN 4: Configuración de DRF en settings.py
# =============================================================================

CODIGO_DRF_SETTINGS = '''
# ============================================================
# settings.py — Configuración de Django REST Framework
# ============================================================

REST_FRAMEWORK = {
    # Autenticación por defecto (qué esquemas se intentan)
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",   # Cookies de sesión
        "rest_framework.authentication.BasicAuthentication",     # HTTP Basic
        # Para JWT: "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],

    # Permiso por defecto si la vista no especifica uno
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],

    # Paginación automática para todas las vistas list()
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,

    # Renderers: qué formatos puede devolver la API
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        # BrowsableAPIRenderer activa la UI navegable en el browser
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],

    # Backends de filtrado globales
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],

    # Throttling: limitar peticiones por usuario/IP
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",    # Anónimos: 100 por hora
        "user": "1000/hour",   # Autenticados: 1000 por hora
    },
}
'''


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 65)
    print("DJANGO REST FRAMEWORK (DRF)")
    print("=" * 65)

    if not DRF_DISPONIBLE:
        print("\nInstala DRF para usar este módulo:")
        print("  pip install djangorestframework django-filter")

    print("\n[1] Serializers:")
    print(CODIGO_SERIALIZERS)

    print("\n[2] ViewSets:")
    print(CODIGO_VIEWSETS)

    print("\n[3] Router y URLs:")
    print(CODIGO_ROUTER)

    print("\n[4] Configuración en settings.py:")
    print(CODIGO_DRF_SETTINGS)

    print("\n" + "=" * 65)
    print("Fin — siguiente: 07_django_admin.py")
    print("=" * 65)
