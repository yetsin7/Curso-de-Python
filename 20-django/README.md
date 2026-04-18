# Capítulo 20 — Django

## ¿Qué es Django?

**Django** es un framework web de alto nivel para Python que promueve el desarrollo rápido y el diseño limpio y pragmático. Fue creado en 2003 para desarrollar sitios de noticias y se convirtió en uno de los frameworks web más populares del mundo.

Su filosofía central: **"batteries included"** (baterías incluidas). Django trae todo lo que necesitas:
- ORM para base de datos
- Panel de administración automático
- Sistema de autenticación
- Formularios con validación
- Sistema de templates
- Seguridad contra CSRF, XSS, SQL Injection por defecto

---

## ¿Cuándo usar Django vs Flask vs FastAPI?

| Criterio | Django | Flask | FastAPI |
|---------|--------|-------|---------|
| **Tamaño del proyecto** | Grande, enterprise | Pequeño, flexible | Mediano a grande |
| **API REST pura** | Con DRF | Sí | Sí (nativo) |
| **Admin panel** | Incluido gratis | Extensión | No incluido |
| **ORM** | Incluido y potente | SQLAlchemy externo | SQLAlchemy/Tortoise |
| **Autenticación** | Incluida | Extensión | Implementar |
| **Curva de aprendizaje** | Media-alta | Baja | Media |
| **Rendimiento** | Bueno (sync) | Bueno (sync) | Excelente (async) |
| **Mejor para** | Apps web completas, CMS, e-commerce | Microservicios, prototipado | APIs modernas, alto rendimiento |

**Elige Django cuando** necesitas un sitio web completo con admin, auth, ORM, templates — todo en un solo framework bien integrado.

---

## Arquitectura MTV (Model-Template-View)

Django usa el patrón **MTV**, similar al MVC tradicional:

```
Navegador → URL Dispatcher → View → Model (DB) → Template → HTML → Navegador
```

| Componente | Descripción | Equivale en MVC |
|-----------|-------------|-----------------|
| **Model** | Define la estructura de datos y la lógica de negocio. Mapea a tablas de DB. | Model |
| **Template** | El HTML con variables dinámicas. Separado de la lógica. | View |
| **View** | Recibe la petición HTTP, consulta el Model, pasa datos al Template. | Controller |

---

## El ecosistema Django

### ORM (Object-Relational Mapper)
Permite trabajar con la base de datos usando Python puro sin escribir SQL:
```python
# En lugar de: SELECT * FROM posts WHERE activo = 1
posts = Post.objects.filter(activo=True)
```

### Admin automático
Con solo registrar tus modelos, Django genera un panel de administración completo, funcional y seguro. Ideal para gestión interna.

### Migrations
Sistema de control de versiones para el esquema de la base de datos. Cada cambio en los models se convierte en una migración:
```bash
python manage.py makemigrations   # Detecta cambios en models
python manage.py migrate          # Aplica cambios a la DB
```

### Forms
Sistema de formularios con validación automática, protección CSRF y widgets HTML configurables.

### Auth
Sistema completo: User model, login/logout, registro, permisos, grupos, decoradores como `@login_required`.

### Django REST Framework (DRF)
El paquete más popular para construir APIs REST con Django. Añade Serializers, ViewSets, autenticación por token/JWT, paginación, permisos granulares.

---

## Comandos esenciales de manage.py

```bash
# Crear nuevo proyecto Django
django-admin startproject nombre_proyecto

# Crear una nueva app dentro del proyecto
python manage.py startapp nombre_app

# Iniciar servidor de desarrollo en http://127.0.0.1:8000
python manage.py runserver

# Detectar cambios en los models y crear archivos de migración
python manage.py makemigrations

# Aplicar migraciones pendientes a la base de datos
python manage.py migrate

# Crear superusuario para el admin
python manage.py createsuperuser

# Abrir shell interactivo con el contexto de Django cargado
python manage.py shell

# Ver SQL que generará una migración (sin ejecutarla)
python manage.py sqlmigrate app 0001

# Recopilar archivos estáticos para producción
python manage.py collectstatic
```

---

## Instalación y primer proyecto

```bash
# 1. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Instalar Django
pip install django

# 3. Crear proyecto
django-admin startproject mi_blog

# 4. Entrar al proyecto y crear una app
cd mi_blog
python manage.py startapp blog

# 5. Ejecutar el servidor
python manage.py runserver
# Visita: http://127.0.0.1:8000
```

---

## Estructura de un proyecto Django

```
mi_blog/                     ← Raíz del proyecto
│
├── mi_blog/                 ← Paquete de configuración del proyecto
│   ├── settings.py          ← Toda la configuración (DB, apps, templates...)
│   ├── urls.py              ← URLs raíz del proyecto
│   ├── wsgi.py              ← Punto de entrada WSGI (producción sync)
│   └── asgi.py              ← Punto de entrada ASGI (producción async)
│
├── blog/                    ← Una app dentro del proyecto
│   ├── migrations/          ← Historial de cambios al schema de DB
│   ├── templates/           ← Archivos HTML de la app
│   ├── admin.py             ← Registro de modelos en el admin
│   ├── apps.py              ← Configuración de la app
│   ├── models.py            ← Definición de los modelos (tablas)
│   ├── forms.py             ← Formularios de la app
│   ├── urls.py              ← URLs específicas de esta app
│   └── views.py             ← Lógica de las vistas
│
└── manage.py                ← Herramienta de administración del proyecto
```

---

## Archivos del capítulo

> **Nota importante**: Los archivos de este capítulo son **snippets educativos comentados**. No forman un proyecto Django ejecutable directamente — Django requiere una estructura específica de proyecto. Estos archivos muestran el código de cada parte de Django con explicaciones detalladas.

| Archivo | Tema |
|---------|------|
| `01_setup_y_estructura.py` | Instalación, estructura del proyecto, comandos esenciales |
| `02_modelos.py` | ORM models, fields, relaciones, migraciones |
| `03_vistas_y_urls.py` | FBV, CBV, URL patterns, namespaces |
| `04_templates_y_forms.py` | Template syntax, ModelForm, validación, widgets |
| `05_django_auth.py` | Autenticación, permisos, grupos, AbstractUser |
| `06_django_rest_framework.py` | DRF: Serializers, ViewSets, autenticación de API |
| `07_django_admin.py` | Personalización del admin: ModelAdmin, inlines, actions |
