"""
Proyecto FastAPI de Nivel Producción: API de Libros
=====================================================
App completa con:
  - CRUD de libros con SQLite (via sqlite3 nativo para evitar dependencias extra)
  - Pydantic schemas: BookCreate, BookUpdate, BookResponse
  - Dependencias reutilizables (get_db, paginación)
  - Pagination correcta con offset/limit
  - Error handling centralizado con HTTPException
  - OpenAPI documentation personalizada
  - Environment variables con pydantic-settings (opcional)
  - Tests con TestClient incluidos en el mismo archivo

Dependencias requeridas:
    pip install fastapi uvicorn

Dependencias opcionales:
    pip install pydantic-settings   ← para env vars tipadas

Ejecutar la app:
    uvicorn 07_fastapi_proyecto_completo:app --reload

Ejecutar los tests:
    python 07_fastapi_proyecto_completo.py --test
"""

import argparse
import sqlite3
import sys
from contextlib import contextmanager
from typing import Generator, Optional

# --- FastAPI y Pydantic ---
try:
    from fastapi import Depends, FastAPI, HTTPException, Query, status
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field, field_validator
    FASTAPI_OK = True
except ImportError:
    FASTAPI_OK = False
    print("[AVISO] Instala las dependencias: pip install fastapi uvicorn")

# --- pydantic-settings (opcional) ---
try:
    from pydantic_settings import BaseSettings
    SETTINGS_OK = True
except ImportError:
    SETTINGS_OK = False


# ===========================================================================
# Configuración con pydantic-settings
# ===========================================================================

if SETTINGS_OK:
    class Settings(BaseSettings):
        """
        Variables de entorno de la aplicación.
        Se leen automáticamente desde el entorno o un archivo .env
        """
        app_name: str = "API de Libros"
        app_version: str = "1.0.0"
        database_url: str = ":memory:"
        debug: bool = False

        class Config:
            env_file = ".env"

    settings = Settings()
else:
    # Fallback sin pydantic-settings
    class _Settings:
        app_name    = "API de Libros"
        app_version = "1.0.0"
        database_url = ":memory:"
        debug        = False

    settings = _Settings()


# ===========================================================================
# Base de datos SQLite (en memoria para demo y tests)
# ===========================================================================

def crear_tablas(conn: sqlite3.Connection) -> None:
    """
    Crea la tabla `books` si no existe.
    Se llama una vez al inicio de la aplicación.

    Args:
        conn: Conexión activa a SQLite.
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            author      TEXT    NOT NULL,
            year        INTEGER,
            genre       TEXT,
            description TEXT,
            available   INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.commit()


# Conexión global para la app (en producción usarías un pool o SQLAlchemy)
_DB_CONN: sqlite3.Connection = None


def get_connection() -> sqlite3.Connection:
    """
    Retorna la conexión global a SQLite.
    Se inicializa una sola vez al arrancar la app.

    Returns:
        Conexión sqlite3 configurada.
    """
    global _DB_CONN
    if _DB_CONN is None:
        _DB_CONN = sqlite3.connect(":memory:", check_same_thread=False)
        _DB_CONN.row_factory = sqlite3.Row
        crear_tablas(_DB_CONN)
        _sembrar_datos_iniciales(_DB_CONN)
    return _DB_CONN


def get_db() -> Generator:
    """
    Dependencia inyectable de FastAPI que provee la conexión a la BD.
    Uso: def mi_ruta(db = Depends(get_db))
    """
    yield get_connection()


def _sembrar_datos_iniciales(conn: sqlite3.Connection) -> None:
    """Inserta libros de ejemplo para poder probar la API desde el inicio."""
    libros = [
        ("Cien años de soledad", "Gabriel García Márquez", 1967, "Novela", "Obra maestra del realismo mágico"),
        ("Don Quijote",          "Miguel de Cervantes",    1605, "Novela", "Primera novela moderna"),
        ("El Principito",        "Antoine de Saint-Exupéry", 1943, "Fábula", "Clásico de la literatura infantil"),
    ]
    conn.executemany(
        "INSERT INTO books (title, author, year, genre, description) VALUES (?,?,?,?,?)",
        libros
    )
    conn.commit()


# ===========================================================================
# Pydantic Schemas
# ===========================================================================

if FASTAPI_OK:
    class BookCreate(BaseModel):
        """Schema para crear un nuevo libro. Todos los campos requeridos."""
        title       : str = Field(..., min_length=1, max_length=200, description="Título del libro")
        author      : str = Field(..., min_length=1, max_length=100, description="Nombre del autor")
        year        : Optional[int] = Field(None, ge=1000, le=2100, description="Año de publicación")
        genre       : Optional[str] = Field(None, max_length=50, description="Género literario")
        description : Optional[str] = Field(None, max_length=1000, description="Descripción del libro")

        @field_validator("title", "author")
        @classmethod
        def no_solo_espacios(cls, v: str) -> str:
            """Valida que el campo no sea solo espacios en blanco."""
            if not v.strip():
                raise ValueError("No puede ser solo espacios en blanco")
            return v.strip()

    class BookUpdate(BaseModel):
        """Schema para actualizar un libro. Todos los campos son opcionales."""
        title       : Optional[str] = Field(None, min_length=1, max_length=200)
        author      : Optional[str] = Field(None, min_length=1, max_length=100)
        year        : Optional[int] = Field(None, ge=1000, le=2100)
        genre       : Optional[str] = Field(None, max_length=50)
        description : Optional[str] = Field(None, max_length=1000)
        available   : Optional[bool] = None

    class BookResponse(BaseModel):
        """Schema de respuesta con todos los campos del libro."""
        id          : int
        title       : str
        author      : str
        year        : Optional[int]
        genre       : Optional[str]
        description : Optional[str]
        available   : bool

        model_config = {"from_attributes": True}

    class PaginatedResponse(BaseModel):
        """Respuesta paginada con metadata."""
        items : list[BookResponse]
        total : int
        offset: int
        limit : int


# ===========================================================================
# Aplicación FastAPI
# ===========================================================================

if FASTAPI_OK:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
API REST de gestión de libros.

## Características
- CRUD completo de libros
- Paginación con offset/limit
- Validación con Pydantic
- Error handling centralizado
        """,
        contact={"name": "Libro de Python", "url": "https://github.com/ejemplo"},
        license_info={"name": "MIT"},
    )

    # ---------------------------------------------------------------------------
    # Manejador global de excepciones
    # ---------------------------------------------------------------------------
    @app.exception_handler(Exception)
    async def manejador_generico(request, exc):
        """
        Captura cualquier excepción no manejada y retorna un JSON limpio
        en vez de exponer el traceback al cliente.
        """
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno del servidor", "type": type(exc).__name__}
        )

    # ---------------------------------------------------------------------------
    # Dependencia de paginación reutilizable
    # ---------------------------------------------------------------------------
    def paginacion(
        offset: int = Query(default=0, ge=0, description="Número de registros a saltar"),
        limit : int = Query(default=10, ge=1, le=100, description="Registros por página")
    ) -> dict:
        """
        Dependencia reutilizable que valida y retorna los parámetros de paginación.
        Uso: def ruta(pag = Depends(paginacion))
        """
        return {"offset": offset, "limit": limit}

    # ---------------------------------------------------------------------------
    # Endpoints CRUD
    # ---------------------------------------------------------------------------

    @app.get("/", tags=["Info"])
    def raiz():
        """Endpoint de bienvenida con información de la API."""
        return {"app": settings.app_name, "version": settings.app_version, "docs": "/docs"}

    @app.get("/books", response_model=PaginatedResponse, tags=["Libros"])
    def listar_libros(
        pag: dict = Depends(paginacion),
        db: sqlite3.Connection = Depends(get_db),
        buscar: Optional[str] = Query(None, description="Filtrar por título o autor")
    ):
        """
        Lista todos los libros con paginación.
        Opcionalmente filtra por texto en título o autor.
        """
        if buscar:
            patron = f"%{buscar}%"
            filas  = db.execute(
                "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? LIMIT ? OFFSET ?",
                (patron, patron, pag["limit"], pag["offset"])
            ).fetchall()
            total = db.execute(
                "SELECT COUNT(*) FROM books WHERE title LIKE ? OR author LIKE ?",
                (patron, patron)
            ).fetchone()[0]
        else:
            filas = db.execute(
                "SELECT * FROM books LIMIT ? OFFSET ?",
                (pag["limit"], pag["offset"])
            ).fetchall()
            total = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]

        items = [BookResponse(**dict(row)) for row in filas]
        return PaginatedResponse(items=items, total=total, **pag)

    @app.get("/books/{book_id}", response_model=BookResponse, tags=["Libros"])
    def obtener_libro(book_id: int, db: sqlite3.Connection = Depends(get_db)):
        """Obtiene un libro por su ID. Retorna 404 si no existe."""
        fila = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
        if not fila:
            raise HTTPException(status_code=404, detail=f"Libro con ID={book_id} no encontrado")
        return BookResponse(**dict(fila))

    @app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["Libros"])
    def crear_libro(libro: BookCreate, db: sqlite3.Connection = Depends(get_db)):
        """Crea un nuevo libro y retorna el registro creado con su ID."""
        cursor = db.execute(
            "INSERT INTO books (title, author, year, genre, description) VALUES (?,?,?,?,?)",
            (libro.title, libro.author, libro.year, libro.genre, libro.description)
        )
        db.commit()
        fila = db.execute("SELECT * FROM books WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return BookResponse(**dict(fila))

    @app.patch("/books/{book_id}", response_model=BookResponse, tags=["Libros"])
    def actualizar_libro(
        book_id: int,
        datos: BookUpdate,
        db: sqlite3.Connection = Depends(get_db)
    ):
        """
        Actualización parcial (PATCH) de un libro.
        Solo actualiza los campos enviados en el body.
        """
        fila = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
        if not fila:
            raise HTTPException(status_code=404, detail=f"Libro con ID={book_id} no encontrado")

        # Construir SET dinámico solo con los campos enviados
        campos = datos.model_dump(exclude_unset=True)
        if not campos:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

        set_clause = ", ".join(f"{col} = ?" for col in campos)
        valores    = list(campos.values()) + [book_id]
        db.execute(f"UPDATE books SET {set_clause} WHERE id = ?", valores)
        db.commit()

        fila = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
        return BookResponse(**dict(fila))

    @app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Libros"])
    def eliminar_libro(book_id: int, db: sqlite3.Connection = Depends(get_db)):
        """Elimina un libro por su ID. Retorna 404 si no existe."""
        fila = db.execute("SELECT id FROM books WHERE id = ?", (book_id,)).fetchone()
        if not fila:
            raise HTTPException(status_code=404, detail=f"Libro con ID={book_id} no encontrado")
        db.execute("DELETE FROM books WHERE id = ?", (book_id,))
        db.commit()


# ===========================================================================
# Tests con TestClient
# ===========================================================================

def ejecutar_tests() -> None:
    """
    Ejecuta los tests de la API usando TestClient de FastAPI.
    Verifica los endpoints principales: list, get, create, update, delete.
    """
    if not FASTAPI_OK:
        print("[SKIP] FastAPI no está instalado.")
        return

    try:
        from fastapi.testclient import TestClient
    except ImportError:
        print("[SKIP] httpx no disponible: pip install httpx")
        return

    client = TestClient(app)
    errores = 0

    def verificar(descripcion: str, condicion: bool) -> None:
        """Imprime el resultado de un test individual."""
        nonlocal errores
        icono = "✓" if condicion else "✗"
        print(f"  {icono} {descripcion}")
        if not condicion:
            errores += 1

    print("\n=== TESTS DE LA API ===\n")

    # GET /
    r = client.get("/")
    verificar("GET / → 200", r.status_code == 200)

    # GET /books (paginación)
    r = client.get("/books?limit=2&offset=0")
    verificar("GET /books → 200 con paginación", r.status_code == 200)
    data = r.json()
    verificar("GET /books contiene campo 'items'", "items" in data)
    verificar("GET /books tiene 'total' correcto", data.get("total", 0) >= 3)

    # GET /books/:id (existe)
    r = client.get("/books/1")
    verificar("GET /books/1 → 200", r.status_code == 200)

    # GET /books/:id (no existe)
    r = client.get("/books/9999")
    verificar("GET /books/9999 → 404", r.status_code == 404)

    # POST /books (crear)
    nuevo = {"title": "Prueba Test", "author": "Autor Test", "year": 2024}
    r = client.post("/books", json=nuevo)
    verificar("POST /books → 201", r.status_code == 201)
    libro_id = r.json().get("id")

    # PATCH /books/:id (actualizar)
    r = client.patch(f"/books/{libro_id}", json={"genre": "Test"})
    verificar("PATCH /books/:id → 200", r.status_code == 200)
    verificar("PATCH aplicó cambio", r.json().get("genre") == "Test")

    # DELETE /books/:id
    r = client.delete(f"/books/{libro_id}")
    verificar("DELETE /books/:id → 204", r.status_code == 204)

    # Confirmar eliminación
    r = client.get(f"/books/{libro_id}")
    verificar("GET libro eliminado → 404", r.status_code == 404)

    # Buscar por texto
    r = client.get("/books?buscar=Quijote")
    verificar("GET /books?buscar=Quijote devuelve resultados", r.json().get("total", 0) >= 1)

    print(f"\n  Resultado: {'TODOS OK' if errores == 0 else f'{errores} FALLARON'}")


# ===========================================================================
# Nota sobre Alembic
# ===========================================================================

NOTA_ALEMBIC = """
NOTA: Alembic para migraciones con SQLAlchemy
================================================
En un proyecto real reemplazarías sqlite3 directo por SQLAlchemy + Alembic:

    pip install sqlalchemy alembic

    # Configurar Alembic
    alembic init migrations
    # Editar alembic.ini para apuntar a tu DATABASE_URL

    # Generar migración automática desde modelos
    alembic revision --autogenerate -m "crear tabla books"

    # Aplicar migraciones
    alembic upgrade head

    # Revertir una migración
    alembic downgrade -1
"""


# ===========================================================================
# Punto de entrada
# ===========================================================================

def main() -> None:
    """
    Punto de entrada: ejecuta tests si se pasa --test,
    muestra instrucciones de inicio si no.
    """
    parser = argparse.ArgumentParser(description="API de Libros - FastAPI")
    parser.add_argument("--test", action="store_true", help="Ejecutar los tests de la API")
    args = parser.parse_args()

    if args.test:
        ejecutar_tests()
    else:
        if not FASTAPI_OK:
            print("Instala: pip install fastapi uvicorn")
            return
        print("Inicia la API con:\n  uvicorn 07_fastapi_proyecto_completo:app --reload")
        print("Documentación en: http://127.0.0.1:8000/docs")
        print(NOTA_ALEMBIC)


if __name__ == "__main__":
    main()
