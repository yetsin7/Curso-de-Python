# Capítulo 21 — FastAPI

## ¿Qué es FastAPI?

**FastAPI** es un framework web moderno y de alto rendimiento para construir APIs con Python. Fue creado por Sebastián Ramírez en 2018 y en pocos años se convirtió en uno de los frameworks más populares de Python.

Sus características distintivas:
- **Muy rápido**: comparable a Node.js y Go, gracias a Starlette (ASGI) y Python async
- **Validación automática**: usa Pydantic para validar y serializar datos automáticamente
- **Documentación automática**: genera Swagger UI y ReDoc sin escribir una línea extra
- **Type hints**: aprovecha las anotaciones de tipos de Python para todo

---

## Comparación: Flask vs Django vs FastAPI

| Característica | Flask | Django | FastAPI |
|---------------|-------|--------|---------|
| **Tipo** | Micro-framework | Full-stack | API framework |
| **Arquitectura** | WSGI (sync) | WSGI (sync) | ASGI (async nativo) |
| **Validación** | Manual/Marshmallow | Django Forms | Pydantic (automática) |
| **Documentación API** | Flask-RESTX | DRF Browsable | Swagger/ReDoc automáticos |
| **ORM** | No incluido | Django ORM | No incluido (SQLAlchemy) |
| **Admin** | Flask-Admin | Incluido | No incluido |
| **Tipado** | Opcional | Opcional | Fundamental (requerido) |
| **Rendimiento** | Bueno | Bueno | Excelente |
| **Mejor para** | Flexibilidad | Web completa | APIs modernas, microservicios |

**Elige FastAPI cuando**: construyes una API REST/GraphQL moderna que necesita alto rendimiento, validación automática de datos, y documentación interactiva automática.

---

## ASGI vs WSGI — ¿Por qué FastAPI es async?

### WSGI (Web Server Gateway Interface)
- Estándar tradicional de Python web (Flask, Django clásico)
- **Síncrono**: cada petición ocupa un hilo hasta completarse
- Si una vista espera una respuesta de DB o API externa, el hilo queda bloqueado
- Para alta concurrencia necesitas muchos procesos/hilos (más RAM)

### ASGI (Asynchronous Server Gateway Interface)
- Estándar moderno para Python web asíncrono
- **Asíncrono**: mientras espera I/O (DB, red, archivos), puede atender otras peticiones
- Un solo proceso puede manejar miles de conexiones simultáneas
- FastAPI usa **Starlette** como base ASGI y **Uvicorn** como servidor

```
WSGI: 1 petición = 1 hilo ocupado hasta responder
ASGI: 1 proceso puede manejar miles de peticiones concurrentes con async/await
```

---

## Pydantic — Validación automática de datos

**Pydantic** es la librería de validación de datos que FastAPI usa internamente. Define la estructura esperada de los datos como clases Python con anotaciones de tipos.

```python
from pydantic import BaseModel

class Usuario(BaseModel):
    nombre: str
    edad: int
    email: str

# FastAPI valida automáticamente que el JSON recibido cumpla este schema
# Si falta un campo o el tipo es incorrecto → 422 Unprocessable Entity automático
```

Pydantic v2 (2023+) es mucho más rápido que v1 y es lo que FastAPI moderno usa.

---

## Documentación automática

FastAPI genera automáticamente dos interfaces de documentación interactiva:

| URL | Interfaz | Descripción |
|-----|---------|-------------|
| `/docs` | **Swagger UI** | Interfaz para explorar y probar endpoints |
| `/redoc` | **ReDoc** | Documentación más legible, estilo referencia |
| `/openapi.json` | **OpenAPI spec** | JSON con la especificación completa |

No necesitas configurar nada — FastAPI infiere tipos, validaciones y descripciones de tus type hints y docstrings.

---

## Instalación

```bash
# Instalación completa (incluye uvicorn y otras dependencias)
pip install "fastapi[standard]"

# O instalación mínima + uvicorn por separado
pip install fastapi uvicorn[standard]

# Dependencias adicionales para los ejemplos:
pip install sqlalchemy          # ORM para base de datos
pip install python-jose         # JWT tokens
pip install passlib[bcrypt]     # Hash de contraseñas
pip install python-multipart    # Para file uploads con forms
```

---

## Ejecutar una app FastAPI

```bash
# Forma estándar: uvicorn módulo:instancia
uvicorn 01_fastapi_basico:app --reload

# --reload: reinicia el servidor cuando detecta cambios (solo desarrollo)
# Visita: http://127.0.0.1:8000
# Docs: http://127.0.0.1:8000/docs
```

---

## Archivos del capítulo

| Archivo | Tema |
|---------|------|
| `01_fastapi_basico.py` | App mínima, rutas, path/query params, response models |
| `02_pydantic_modelos.py` | Pydantic v2: BaseModel, Field, validators, tipos complejos |
| `03_crud_completo.py` | CRUD en memoria: Tareas con todos los verbos HTTP |
| `04_fastapi_con_bd.py` | FastAPI + SQLAlchemy + SQLite: DB real con Depends() |
| `05_fastapi_auth.py` | JWT: OAuth2PasswordBearer, tokens, hash de contraseñas |
| `06_fastapi_avanzado.py` | Background tasks, middleware, CORS, uploads, WebSockets |
