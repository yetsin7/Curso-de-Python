# =============================================================================
# CAPÍTULO 20 — Django
# Archivo 04: Templates y Formularios
# =============================================================================
# Los templates generan el HTML dinámico. Los forms gestionan
# entrada de usuario con validación automática.
#
# Django Template Language (DTL) es el motor por defecto.
# Para formularios, Django genera HTML, valida datos y protege contra CSRF.
# =============================================================================

try:
    import django
    DJANGO_DISPONIBLE = True
except ImportError:
    DJANGO_DISPONIBLE = False
    print("Django no instalado. Instala: pip install django\n")


# =============================================================================
# SECCIÓN 1: Django Template Language (DTL) — sintaxis
# =============================================================================

TEMPLATE_BASE = '''
{# Esto es un comentario en DTL — no aparece en el HTML final #}

{# ============================================================ #}
{# base.html — Template padre con bloques que los hijos llenan #}
{# ============================================================ #}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {# block: espacio que los templates hijos pueden sobreescribir #}
    <title>{% block title %}Mi Blog{% endblock %}</title>

    {# {% load static %} carga el tag para archivos estáticos #}
    {% load static %}
    <link rel="stylesheet" href="{% static 'blog/style.css' %}">

    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav>
        {# request.user está disponible gracias al context processor auth #}
        {% if request.user.is_authenticated %}
            <span>Hola, {{ request.user.get_full_name|default:request.user.username }}</span>
            <a href="{% url 'blog:post_create' %}">Nuevo post</a>
            {# {% url 'nombre' %} genera la URL inversa — nunca hardcodees URLs #}
            <a href="{% url 'logout' %}">Salir</a>
        {% else %}
            <a href="{% url 'login' %}">Iniciar sesión</a>
        {% endif %}
    </nav>

    {# Mensajes flash del sistema de messages de Django #}
    {% if messages %}
        <div class="messages">
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">
                    {{ message }}
                </div>
            {% endfor %}
        </div>
    {% endif %}

    <main>
        {# Los hijos reemplazan este bloque con su contenido #}
        {% block content %}{% endblock %}
    </main>

    <footer>
        <p>© {% now "Y" %} Mi Blog</p>
        {# now "Y" devuelve el año actual #}
    </footer>

    {% block extra_js %}{% endblock %}
</body>
</html>
'''

TEMPLATE_POST_LIST = '''
{# ============================================================ #}
{# blog/post_list.html — Lista de posts #}
{# Hereda de base.html usando extends #}
{# ============================================================ #}

{% extends "base.html" %}

{% block title %}Blog — Artículos{% endblock %}

{% block content %}
<h1>Artículos del Blog</h1>

{# Filtro por categoría #}
<div class="categorias">
    <a href="{% url 'blog:post_list' %}">Todas</a>
    {% for categoria in categorias %}
        <a href="{% url 'blog:post_list' %}?categoria={{ categoria.slug }}"
           {% if categoria.slug == categoria_activa %}class="activa"{% endif %}>
            {{ categoria.name }}
        </a>
    {% endfor %}
</div>

{# Iteramos la página de posts #}
{% for post in pagina %}
    <article>
        {# Variables: {{ variable }} — se escapan automáticamente contra XSS #}
        <h2>
            <a href="{{ post.get_absolute_url }}">{{ post.title }}</a>
        </h2>

        <p>
            Por {{ post.author.get_full_name|default:post.author.username }}
            {# Filtros: | separa variable y filtro #}
            el {{ post.published_at|date:"d \d\e F \d\e Y" }}
        </p>

        {# truncatewords corta el texto a N palabras #}
        <p>{{ post.excerpt|truncatewords:30 }}</p>

        {# Mostrar tags #}
        {% if post.tags.all %}
            <div class="tags">
                {# with crea alias temporales para evitar queries repetidas #}
                {% with tags=post.tags.all %}
                    {% for tag in tags %}
                        <span class="tag">{{ tag.name }}</span>
                    {% endfor %}
                {% endwith %}
            </div>
        {% endif %}

        <a href="{{ post.get_absolute_url }}">Leer más →</a>
    </article>
{% empty %}
    {# empty se muestra cuando el for no tiene elementos #}
    <p>No hay posts publicados aún.</p>
{% endfor %}

{# Paginación #}
{% if pagina.has_other_pages %}
    <nav class="paginacion">
        {% if pagina.has_previous %}
            <a href="?pagina={{ pagina.previous_page_number }}">← Anterior</a>
        {% endif %}

        <span>Página {{ pagina.number }} de {{ pagina.paginator.num_pages }}</span>

        {% if pagina.has_next %}
            <a href="?pagina={{ pagina.next_page_number }}">Siguiente →</a>
        {% endif %}
    </nav>
{% endif %}

{% endblock %}
'''

TEMPLATE_FILTROS = '''
{# ============================================================ #}
{# FILTROS más útiles del Django Template Language #}
{# ============================================================ #}

{# Texto #}
{{ nombre|lower }}              {# "ANA" → "ana" #}
{{ nombre|upper }}              {# "ana" → "ANA" #}
{{ nombre|title }}              {# "hola mundo" → "Hola Mundo" #}
{{ texto|truncatewords:20 }}    {# Corta a 20 palabras #}
{{ texto|truncatechars:100 }}   {# Corta a 100 caracteres #}
{{ html|striptags }}            {# Elimina etiquetas HTML #}
{{ valor|default:"Sin valor" }} {# Valor por defecto si es falsy #}
{{ nombre|capfirst }}           {# Primera letra mayúscula #}
{{ lista|join:", " }}           {# Une lista con separador #}

{# Números #}
{{ precio|floatformat:2 }}      {# 19.9 → "19.90" #}
{{ numero|filesizeformat }}     {# 1048576 → "1.0 MB" #}

{# Fechas #}
{{ fecha|date:"d/m/Y" }}        {# "15/06/2024" #}
{{ fecha|date:"D, d M Y" }}     {# "Sat, 15 Jun 2024" #}
{{ fecha|timesince }}           {# "3 horas" (desde ahora) #}
{{ fecha|timeuntil }}           {# "2 días" (hasta esa fecha) #}

{# HTML seguro (desactiva el auto-escape — usar solo con contenido confiable) #}
{{ contenido_html|safe }}       {# No escapa el HTML #}
{% autoescape off %}{{ contenido }}{% endautoescape %}

{# URL encode #}
{{ busqueda|urlencode }}        {# "Python Avanzado" → "Python%20Avanzado" #}

{# Tags condicionales #}
{% if lista %}                  {# Verdadero si la lista no está vacía #}
{% if valor == "publicado" %}   {# Comparación de igualdad #}
{% if valor in lista %}         {# Pertenencia #}
{% if not oculto %}             {# Negación #}
{% if a and b %}                {# AND #}
{% if a or b %}                 {# OR #}
'''


# =============================================================================
# SECCIÓN 2: Django Forms — código Python
# =============================================================================

CODIGO_FORMS = '''
# ============================================================
# blog/forms.py — Formularios del blog
# ============================================================

from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Comment, Category


class PostForm(forms.ModelForm):
    """
    Formulario para crear y editar posts.

    ModelForm genera automáticamente los campos desde el modelo,
    incluye validación de tipos y longitudes, y puede generar
    el HTML de los inputs con {{ form.as_p }} en el template.
    """

    class Meta:
        """
        Meta clase configura qué modelo y campos usar.
        """
        model = Post
        # Especificamos los campos explícitamente (más seguro que '__all__')
        fields = ["title", "category", "tags", "excerpt", "body", "cover_image", "status"]

        # widgets sobreescribe el widget HTML por defecto de cada campo
        widgets = {
            # Textarea más grande para el cuerpo del post
            "body": forms.Textarea(attrs={
                "rows": 15,
                "class": "editor",
                "placeholder": "Escribe el contenido del post...",
            }),
            "excerpt": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Resumen corto del artículo...",
            }),
            "title": forms.TextInput(attrs={
                "placeholder": "Título del artículo",
                "class": "form-control",
            }),
            # Select múltiple para los tags (ManyToManyField)
            "tags": forms.CheckboxSelectMultiple(),
        }

        # labels sobreescribe el texto de la etiqueta del campo
        labels = {
            "title": "Título",
            "body": "Contenido",
            "cover_image": "Imagen de portada",
        }

        # help_texts agrega texto de ayuda debajo del campo
        help_texts = {
            "excerpt": "Texto corto que aparece en listados y buscadores.",
            "cover_image": "Formatos: JPG, PNG, WebP. Máximo 2MB.",
        }

    def clean_title(self):
        """
        Validación personalizada del campo title.

        Métodos clean_<campo>(): se ejecutan automáticamente por is_valid().
        Deben retornar el valor limpio o lanzar ValidationError.
        """
        titulo = self.cleaned_data.get("title", "").strip()

        if len(titulo) < 5:
            raise ValidationError("El título debe tener al menos 5 caracteres.")

        # Verificamos que el título no esté ya en uso (al crear, no al editar)
        existe = Post.objects.filter(title__iexact=titulo)
        if self.instance.pk:
            # Al editar, excluimos el post actual de la verificación
            existe = existe.exclude(pk=self.instance.pk)
        if existe.exists():
            raise ValidationError("Ya existe un post con ese título.")

        return titulo

    def clean(self):
        """
        Validación cross-field: se llama después de todos los clean_<campo>().
        Aquí podemos validar combinaciones de campos.
        """
        datos = super().clean()
        estado = datos.get("status")
        extracto = datos.get("excerpt", "").strip()

        # Si el post se va a publicar, el extracto es obligatorio
        if estado == "published" and not extracto:
            self.add_error(
                "excerpt",
                "El extracto es obligatorio para publicar un post."
            )

        return datos


class CommentForm(forms.ModelForm):
    """
    Formulario para añadir comentarios.
    Incluye campos para visitantes no registrados.
    """

    class Meta:
        model = Comment
        fields = ["author_name", "author_email", "body"]
        widgets = {
            "body": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Escribe tu comentario...",
            }),
            "author_name": forms.TextInput(attrs={
                "placeholder": "Tu nombre",
            }),
            "author_email": forms.EmailInput(attrs={
                "placeholder": "tu@email.com",
            }),
        }

    def clean_body(self):
        """Validación: el comentario no puede ser demasiado corto."""
        cuerpo = self.cleaned_data.get("body", "").strip()
        if len(cuerpo) < 10:
            raise ValidationError("El comentario debe tener al menos 10 caracteres.")
        return cuerpo


class ContactForm(forms.Form):
    """
    Formulario de contacto — no basado en un modelo (forms.Form).
    Útil para formularios que no guardan directamente en la DB.
    """

    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Tu nombre"}),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "tu@email.com"}),
    )

    asunto = forms.CharField(max_length=200)

    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6}),
        min_length=20,
    )

    # ChoiceField con opciones predefinidas
    tipo = forms.ChoiceField(
        choices=[
            ("consulta", "Consulta general"),
            ("error", "Reportar error"),
            ("colaboracion", "Propuesta de colaboración"),
        ],
        initial="consulta",
    )

    def clean_email(self):
        """Bloqueamos dominios desechables comunes."""
        email = self.cleaned_data.get("email", "")
        dominios_bloqueados = ["mailinator.com", "tempmail.org", "10minutemail.com"]
        dominio = email.split("@")[-1].lower()
        if dominio in dominios_bloqueados:
            raise ValidationError("Por favor usa una dirección de email real.")
        return email
'''

TEMPLATE_FORM = '''
{# ============================================================ #}
{# blog/post_form.html — Template para crear/editar post #}
{# ============================================================ #}

{% extends "base.html" %}

{% block title %}{{ titulo }}{% endblock %}

{% block content %}
<h1>{{ titulo }}</h1>

{# enctype="multipart/form-data" es OBLIGATORIO cuando el form tiene FileField/ImageField #}
<form method="POST" enctype="multipart/form-data">
    {# {% csrf_token %} es OBLIGATORIO en todo form POST — protege contra CSRF #}
    {% csrf_token %}

    {# Renderizar todo el form de golpe — rápido pero menos control visual #}
    {# {{ form.as_p }}     — cada campo en un <p> #}
    {# {{ form.as_table }} — tabla HTML #}
    {# {{ form.as_ul }}    — lista desordenada #}

    {# Renderizado campo por campo — más control visual #}
    {% for campo in form %}
        <div class="campo-form {% if campo.errors %}tiene-error{% endif %}">
            {{ campo.label_tag }}        {# <label for="id_campo">Título</label> #}
            {{ campo }}                  {# El widget del campo (input, textarea...) #}

            {% if campo.help_text %}
                <small class="ayuda">{{ campo.help_text }}</small>
            {% endif %}

            {# Errores de validación del campo #}
            {% if campo.errors %}
                <ul class="errores">
                    {% for error in campo.errors %}
                        <li>{{ error }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        </div>
    {% endfor %}

    {# Errores globales del form (del método clean()) #}
    {% if form.non_field_errors %}
        <div class="errores-generales">
            {{ form.non_field_errors }}
        </div>
    {% endif %}

    <div class="botones">
        <button type="submit">Guardar</button>
        <a href="{% url 'blog:post_list' %}">Cancelar</a>
    </div>
</form>
{% endblock %}
'''


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 65)
    print("DJANGO — TEMPLATES Y FORMULARIOS")
    print("=" * 65)

    print("\n[1] Template base.html:")
    print(TEMPLATE_BASE)

    print("\n[2] Template post_list.html:")
    print(TEMPLATE_POST_LIST)

    print("\n[3] Filtros más útiles del DTL:")
    print(TEMPLATE_FILTROS)

    print("\n[4] Formularios Django (forms.py):")
    print(CODIGO_FORMS)

    print("\n[5] Template del formulario:")
    print(TEMPLATE_FORM)

    print("\n" + "=" * 65)
    print("Fin — siguiente: 05_django_auth.py")
    print("=" * 65)
