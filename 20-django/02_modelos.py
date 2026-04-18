# =============================================================================
# CAPÍTULO 20 — Django
# Archivo 02: Modelos Django — ORM, fields, relaciones y migraciones
# =============================================================================
# Los modelos son la capa de datos de Django. Cada clase Model
# corresponde a una tabla en la base de datos. Django genera el SQL
# automáticamente y gestiona los cambios con el sistema de migraciones.
#
# NOTA: Este archivo es un snippet educativo. Para funcionar necesita
# estar dentro de un proyecto Django con settings configurados.
# =============================================================================

# Intentamos importar Django — si no está instalado, explicamos el error
try:
    import django
    from django.db import models
    from django.contrib.auth.models import User
    from django.utils import timezone
    from django.utils.text import slugify
    DJANGO_DISPONIBLE = True
except ImportError:
    DJANGO_DISPONIBLE = False
    print("Django no instalado. Este archivo muestra código educativo.")
    print("Instala con: pip install django\n")


# =============================================================================
# SECCIÓN 1: Tipos de fields más importantes en Django
# =============================================================================

def explicar_field_types() -> None:
    """
    Explica los tipos de campos más comunes del ORM de Django.

    Por qué importa elegir bien el tipo: cada field type se mapea a un
    tipo de columna en SQL. Elegir el incorrecto afecta rendimiento,
    almacenamiento y validación automática.
    """
    campos = {
        "CharField(max_length=200)": "Texto corto. max_length OBLIGATORIO. → VARCHAR(200)",
        "TextField()": "Texto largo sin límite. Para cuerpo de posts, descripciones. → TEXT",
        "IntegerField()": "Número entero. → INTEGER",
        "FloatField()": "Número decimal (precisión aproximada). → REAL",
        "DecimalField(max_digits=10, decimal_places=2)": "Decimal exacto. Para precios. → DECIMAL",
        "BooleanField()": "True/False. → BOOLEAN",
        "DateField()": "Solo fecha (año-mes-día). → DATE",
        "DateTimeField()": "Fecha y hora. → DATETIME/TIMESTAMP",
        "EmailField()": "Igual que CharField pero valida formato email.",
        "URLField()": "Igual que CharField pero valida formato URL.",
        "SlugField()": "Texto URL-friendly (letras, números, guiones). Para URLs.",
        "ImageField()": "Guarda ruta de imagen. Requiere pillow: pip install pillow.",
        "FileField()": "Guarda ruta de cualquier archivo subido.",
        "ForeignKey()": "Relación muchos-a-uno. Crea columna FK en la tabla.",
        "ManyToManyField()": "Relación muchos-a-muchos. Crea tabla intermedia.",
        "OneToOneField()": "Relación uno-a-uno. Para extender modelos.",
        "JSONField()": "Almacena JSON. Soportado en PostgreSQL, MySQL, SQLite 3.9+.",
        "UUIDField()": "Identificador UUID. Para IDs no predecibles.",
        "PositiveIntegerField()": "Entero positivo (>= 0). → INTEGER con CHECK",
    }

    print("\n--- Tipos de Fields en Django ---")
    print(f"  {'Field Type':<50} Descripción")
    print("  " + "-" * 80)
    for field, desc in campos.items():
        print(f"  {field:<50} {desc}")

    print("""
  Opciones comunes para casi todos los fields:
    null=True         → La columna puede ser NULL en la base de datos
    blank=True        → El campo puede estar vacío en formularios Django
    default=valor     → Valor por defecto si no se especifica
    unique=True       → La columna tendrá un índice UNIQUE
    db_index=True     → Crea un índice en esta columna (consultas más rápidas)
    verbose_name=""   → Nombre legible para el admin y formularios
    help_text=""      → Texto de ayuda que aparece en el admin

  Diferencia null vs blank:
    null=True   → Campo puede ser NULL en DB (afecta almacenamiento)
    blank=True  → Campo puede estar vacío en validación de formularios
    Para texto: usa blank=True, no null=True (Django usa "" en lugar de NULL)
    Para números/fechas: puedes usar null=True, blank=True juntos
""")


# =============================================================================
# SECCIÓN 2: Modelos del Blog — con todas las relaciones
# =============================================================================

# Solo definimos los modelos si Django está disponible
if DJANGO_DISPONIBLE:

    class Category(models.Model):
        """
        Categoría para organizar los posts del blog.

        Por qué una clase separada para categorías y no un CharField:
        - Permite gestionar categorías desde el admin fácilmente
        - Evita duplicados (no "Python" y "python" por error)
        - Permite añadir campos a categorías (descripción, imagen, etc.)
        """

        # El nombre de la categoría — único para evitar duplicados
        name = models.CharField(
            max_length=100,
            unique=True,
            verbose_name="Nombre",
        )

        # Slug para la URL: python-avanzado en lugar de "Python Avanzado"
        # unique garantiza que no haya URLs duplicadas
        slug = models.SlugField(
            max_length=100,
            unique=True,
            verbose_name="Slug URL",
        )

        # Descripción opcional de la categoría
        description = models.TextField(
            blank=True,  # Puede estar vacío en formularios
            verbose_name="Descripción",
        )

        class Meta:
            """
            Configuración de la tabla y comportamiento del model.
            verbose_name y ordering son los más usados.
            """
            verbose_name = "Categoría"
            verbose_name_plural = "Categorías"
            # Ordenamos por nombre — afecta QuerySets sin order_by explícito
            ordering = ["name"]

        def __str__(self) -> str:
            """
            Representación en texto del objeto.
            Django usa __str__ en el admin, formularios y depuración.
            """
            return self.name

        def save(self, *args, **kwargs):
            """
            Sobreescribimos save() para generar el slug automáticamente.

            Por qué aquí y no en el form: asegura que siempre haya slug,
            incluso cuando se crea desde el shell o desde la API.
            """
            if not self.slug:
                # slugify convierte "Python Avanzado" → "python-avanzado"
                self.slug = slugify(self.name)
            super().save(*args, **kwargs)


    class Tag(models.Model):
        """
        Etiqueta para clasificar posts con mayor granularidad que categorías.

        La diferencia con Category: un post tiene UNA categoría principal
        pero puede tener MUCHOS tags.
        """

        name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
        slug = models.SlugField(max_length=50, unique=True)

        class Meta:
            verbose_name = "Etiqueta"
            verbose_name_plural = "Etiquetas"
            ordering = ["name"]

        def __str__(self) -> str:
            return self.name


    class Post(models.Model):
        """
        El modelo principal del blog — representa un artículo.

        Relaciones demostradas:
        - ForeignKey → Category (muchos posts → una categoría)
        - ForeignKey → User (muchos posts → un autor)
        - ManyToManyField → Tag (muchos posts ↔ muchos tags)
        """

        # Opciones de estado del post — usamos constantes de clase
        BORRADOR = "draft"
        PUBLICADO = "published"
        STATUS_CHOICES = [
            (BORRADOR, "Borrador"),
            (PUBLICADO, "Publicado"),
        ]

        # El título del post
        title = models.CharField(max_length=200, verbose_name="Título")

        # Slug único para la URL del post
        slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug URL")

        # ForeignKey → User (el autor)
        # on_delete=CASCADE: si se elimina el usuario, se eliminan sus posts
        # on_delete=SET_NULL: si se elimina el usuario, author queda en NULL
        # related_name permite hacer user.posts.all() desde el User
        author = models.ForeignKey(
            User,
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name="posts",
            verbose_name="Autor",
        )

        # ForeignKey → Category
        # PROTECT evita borrar categorías que tienen posts
        category = models.ForeignKey(
            Category,
            on_delete=models.PROTECT,
            related_name="posts",
            verbose_name="Categoría",
        )

        # ManyToManyField → Tag
        # blank=True porque un post puede no tener tags
        # related_name permite hacer tag.posts.all() desde el Tag
        tags = models.ManyToManyField(
            Tag,
            blank=True,
            related_name="posts",
            verbose_name="Etiquetas",
        )

        # Resumen corto para listados y SEO
        excerpt = models.TextField(
            max_length=500,
            blank=True,
            verbose_name="Extracto",
        )

        # Cuerpo completo del post
        body = models.TextField(verbose_name="Contenido")

        # Imagen de portada — blank/null para posts sin imagen
        cover_image = models.ImageField(
            upload_to="posts/covers/",  # Se guarda en MEDIA_ROOT/posts/covers/
            blank=True,
            null=True,
            verbose_name="Imagen de portada",
        )

        # Estado del post
        status = models.CharField(
            max_length=10,
            choices=STATUS_CHOICES,
            default=BORRADOR,
            verbose_name="Estado",
        )

        # auto_now_add=True: se establece solo al crear (nunca cambia)
        created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

        # auto_now=True: se actualiza automáticamente en cada save()
        updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

        # Fecha de publicación — puede ser futura para programar posts
        published_at = models.DateTimeField(
            null=True,
            blank=True,
            verbose_name="Fecha de publicación",
        )

        # Contador de vistas — útil para mostrar popularidad
        views_count = models.PositiveIntegerField(default=0, verbose_name="Vistas")

        class Meta:
            verbose_name = "Post"
            verbose_name_plural = "Posts"
            # Más recientes primero — el "-" indica descendente
            ordering = ["-published_at", "-created_at"]
            # Índice compuesto para acelerar consultas frecuentes
            indexes = [
                models.Index(fields=["status", "-published_at"]),
                models.Index(fields=["author", "status"]),
            ]

        def __str__(self) -> str:
            return self.title

        def save(self, *args, **kwargs):
            """Genera slug desde el título y establece published_at al publicar."""
            if not self.slug:
                self.slug = slugify(self.title)

            # Si se está publicando ahora, registramos la fecha
            if self.status == self.PUBLICADO and not self.published_at:
                self.published_at = timezone.now()

            super().save(*args, **kwargs)

        @property
        def is_published(self) -> bool:
            """
            Property que indica si el post está publicado.

            Por qué property: permite usar post.is_published en templates
            sin llamar a un método: {{ post.is_published }}
            """
            return self.status == self.PUBLICADO

        def incrementar_vistas(self) -> None:
            """
            Incrementa el contador de vistas de forma eficiente.

            Por qué F(): en lugar de:
                self.views_count += 1; self.save()
            que lee el valor en Python y podría tener race conditions,
            F("views_count") + 1 hace el incremento directamente en SQL:
            UPDATE post SET views_count = views_count + 1 WHERE id = X
            """
            from django.db.models import F
            Post.objects.filter(pk=self.pk).update(views_count=F("views_count") + 1)


    class Comment(models.Model):
        """
        Comentario asociado a un post.

        Demuestra: ForeignKey con related_name para acceder comentarios
        desde el post (post.comments.all()).
        """

        post = models.ForeignKey(
            Post,
            on_delete=models.CASCADE,  # Si se borra el post, se borran sus comentarios
            related_name="comments",
            verbose_name="Post",
        )

        # El autor puede ser usuario registrado o anónimo
        author = models.ForeignKey(
            User,
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name="comments",
            verbose_name="Autor",
        )

        # Para comentarios de visitantes no registrados
        author_name = models.CharField(
            max_length=100,
            blank=True,
            verbose_name="Nombre del autor",
        )
        author_email = models.EmailField(
            blank=True,
            verbose_name="Email del autor",
        )

        body = models.TextField(verbose_name="Comentario")

        # Aprobación manual para evitar spam
        is_approved = models.BooleanField(
            default=False,
            verbose_name="Aprobado",
        )

        created_at = models.DateTimeField(auto_now_add=True)

        class Meta:
            verbose_name = "Comentario"
            verbose_name_plural = "Comentarios"
            ordering = ["created_at"]

        def __str__(self) -> str:
            nombre = self.author.username if self.author else self.author_name
            return f"Comentario de {nombre} en '{self.post.title[:30]}'"


# =============================================================================
# SECCIÓN 3: Ejemplos de QuerySets (consultas ORM)
# =============================================================================

def mostrar_ejemplos_queryset() -> None:
    """
    Muestra ejemplos de consultas ORM de Django como código comentado.

    Los QuerySets son lazy: no ejecutan SQL hasta que se iteran o
    se evalúan. Esto permite encadenar filtros sin múltiples queries.
    """
    codigo = '''
# ============================================================
# EJEMPLOS DE QUERYSETS — ejecutar en: python manage.py shell
# ============================================================

from blog.models import Post, Category, Tag, Comment
from django.contrib.auth.models import User

# --- Obtener todos los posts ---
todos = Post.objects.all()  # QuerySet lazy — no ejecuta SQL todavía

# --- Filtrar ---
publicados = Post.objects.filter(status="published")
de_autor = Post.objects.filter(author__username="ana")  # FK lookup con __
recientes = Post.objects.filter(created_at__year=2024)  # DateField lookup

# --- Encadenar filtros (AND implícito) ---
publicados_de_ana = Post.objects.filter(
    status="published",
    author__username="ana",
)

# --- Excluir ---
sin_borradores = Post.objects.exclude(status="draft")

# --- Ordenar ---
por_titulo = Post.objects.order_by("title")        # Ascendente
por_fecha  = Post.objects.order_by("-created_at")  # Descendente (-)

# --- Obtener un solo objeto ---
try:
    post = Post.objects.get(pk=1)         # Lanza DoesNotExist si no existe
    post = Post.objects.get(slug="mi-post")
except Post.DoesNotExist:
    print("Post no encontrado")

# --- get_or_create: obtiene o crea ---
categoria, creada = Category.objects.get_or_create(
    name="Python",
    defaults={"slug": "python", "description": "Todo sobre Python"},
)

# --- Limitar resultados ---
primeros_5 = Post.objects.all()[:5]           # LIMIT 5
del_3_al_8 = Post.objects.all()[3:8]          # OFFSET 3 LIMIT 5

# --- Contar sin cargar objetos ---
total = Post.objects.filter(status="published").count()

# --- Verificar existencia ---
existe = Post.objects.filter(slug="mi-post").exists()

# --- Seleccionar solo algunos campos (más eficiente) ---
solo_titulos = Post.objects.values("title", "slug")
solo_ids = Post.objects.values_list("id", flat=True)

# --- Prefetch para evitar el problema N+1 ---
# Sin optimización: hace 1 query por post para obtener el autor
posts = Post.objects.all()  # N+1 problem
for p in posts:
    print(p.author.username)  # Cada .author hace una nueva query SQL

# Con select_related: hace JOIN en una sola query (para ForeignKey)
posts = Post.objects.select_related("author", "category").filter(status="published")

# Con prefetch_related: para ManyToManyField y relaciones inversas
posts = Post.objects.prefetch_related("tags", "comments").all()

# --- Actualizar varios objetos a la vez ---
Post.objects.filter(status="draft").update(status="published")

# --- Eliminar ---
Post.objects.filter(author=None).delete()

# --- Agregar datos (sum, avg, count, max, min) ---
from django.db.models import Count, Avg, Sum
stats = Post.objects.aggregate(
    total=Count("id"),
    promedio_vistas=Avg("views_count"),
)
# stats = {"total": 150, "promedio_vistas": 234.5}

# --- Agrupar con annotate ---
categorias_con_conteo = Category.objects.annotate(
    num_posts=Count("posts"),
).order_by("-num_posts")
for cat in categorias_con_conteo:
    print(f"{cat.name}: {cat.num_posts} posts")
'''
    print("\n--- Ejemplos de QuerySets Django ---")
    print(codigo)


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 65)
    print("DJANGO — MODELOS, ORM, FIELDS Y RELACIONES")
    print("=" * 65)

    explicar_field_types()

    if DJANGO_DISPONIBLE:
        print("\n[2] Modelos definidos (requieren proyecto Django para funcionar):")
        print("  - Category: categorías del blog")
        print("  - Tag: etiquetas (ManyToMany con Post)")
        print("  - Post: artículo del blog (ForeignKey a User y Category)")
        print("  - Comment: comentarios (ForeignKey a Post)")
    else:
        print("\n[2] Instala Django para usar los modelos: pip install django")

    mostrar_ejemplos_queryset()

    print("\n" + "=" * 65)
    print("Fin — siguiente: 03_vistas_y_urls.py")
    print("=" * 65)
