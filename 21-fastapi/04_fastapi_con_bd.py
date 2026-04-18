# =============================================================================
# CAPÍTULO 21 — FastAPI
# Archivo 04: FastAPI + SQLAlchemy + SQLite — base de datos real
# =============================================================================
# En producción necesitamos una DB real. Este ejemplo usa:
# - SQLAlchemy: ORM para Python (el más popular)
# - SQLite: DB en archivo — perfecta para aprendizaje
# - Depends(): sistema de inyección de dependencias de FastAPI
# - Lifespan events: inicialización/limpieza al arrancar/apagar
#
# Instalación:
#   pip install "fastapi[standard]" sqlalchemy
#
# Para PostgreSQL en producción:
#   pip install psycopg2-binary
# =============================================================================

try:
    from fastapi import FastAPI, HTTPException, Depends, status
    from pydantic import BaseModel, Field, EmailStr
    FASTAPI_DISPONIBLE = True
except ImportError:
    FASTAPI_DISPONIBLE = False
    print('FastAPI no instalado. Instala: pip install "fastapi[standard]"')

try:
    from sqlalchemy import (
        create_engine, Column, Integer, String, Boolean,
        DateTime, ForeignKey, Text,
    )
    from sqlalchemy.orm import (
        DeclarativeBase, Session, sessionmaker, relationship,
    )
    from sqlalchemy.sql import func
    SQLALCHEMY_DISPONIBLE = True
except ImportError:
    SQLALCHEMY_DISPONIBLE = False
    print("SQLAlchemy no instalado. Instala: pip install sqlalchemy")

from typing import Optional, Generator
from datetime import datetime
from contextlib import asynccontextmanager


# =============================================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# =============================================================================

# URL de conexión a SQLite — crea el archivo db.sqlite3 en el directorio actual
# Para PostgreSQL sería: "postgresql://usuario:password@host:5432/nombre_db"
DATABASE_URL = "sqlite:///./libro_python_fastapi.db"

# create_engine crea el pool de conexiones
# check_same_thread=False es necesario para SQLite con FastAPI (múltiples hilos)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    # echo=True imprime el SQL generado — útil para debug
    echo=False,
)

# sessionmaker genera nuevas sesiones de DB — una por petición HTTP
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# =============================================================================
# MODELOS SQLALCHEMY (tablas de la base de datos)
# =============================================================================

class Base(DeclarativeBase):
    """
    Clase base de la que heredan todos los modelos SQLAlchemy.
    DeclarativeBase de SQLAlchemy 2.0 — versión moderna.
    """
    pass


class UsuarioDB(Base):
    """
    Modelo SQLAlchemy para la tabla 'usuarios'.

    Por qué separar el modelo DB del schema Pydantic:
    SQLAlchemy gestiona la tabla y las relaciones con la DB.
    Pydantic gestiona la validación y serialización HTTP.
    Son responsabilidades distintas — no deben mezclarse.
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    activo = Column(Boolean, default=True)
    # server_default=func.now() usa la función de fecha del servidor SQL
    creado_en = Column(DateTime, server_default=func.now())
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relación inversa: acceder a los posts del usuario con usuario.posts
    posts = relationship("PostDB", back_populates="autor", cascade="all, delete-orphan")


class PostDB(Base):
    """Modelo SQLAlchemy para la tabla 'posts'."""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    contenido = Column(Text, nullable=False)
    publicado = Column(Boolean, default=False)
    creado_en = Column(DateTime, server_default=func.now())

    # ForeignKey: columna que referencia la tabla usuarios
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Relación: acceder al objeto autor con post.autor
    autor = relationship("UsuarioDB", back_populates="posts")


# =============================================================================
# SCHEMAS PYDANTIC (validación HTTP)
# =============================================================================

class UsuarioCreate(BaseModel):
    """Schema para crear un usuario (POST body)."""
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 chars)")


class UsuarioResponse(BaseModel):
    """Schema de respuesta del usuario — SIN password."""
    id: int
    nombre: str
    apellido: str
    email: str
    activo: bool
    creado_en: Optional[datetime]

    model_config = {"from_attributes": True}


class PostCreate(BaseModel):
    """Schema para crear un post."""
    titulo: str = Field(..., min_length=5, max_length=200)
    contenido: str = Field(..., min_length=10)
    publicado: bool = False


class PostResponse(BaseModel):
    """Schema de respuesta de post — incluye datos del autor."""
    id: int
    titulo: str
    contenido: str
    publicado: bool
    creado_en: Optional[datetime]
    autor_id: int

    model_config = {"from_attributes": True}


# =============================================================================
# DEPENDENCIA: get_db — sesión de base de datos por petición
# =============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Genera una sesión de base de datos para cada petición HTTP.

    Por qué Depends(get_db): FastAPI inyecta la sesión en cada endpoint.
    El bloque try/finally garantiza que la sesión se cierre siempre,
    incluso si ocurre un error durante la petición.

    Patrón: una sesión por petición (request-scoped session).
    No reutilizamos sesiones entre peticiones — evita problemas de estado.

    Yields:
        Session de SQLAlchemy activa para usar en el endpoint.
    """
    db = SessionLocal()
    try:
        yield db  # El endpoint usa la sesión aquí
    finally:
        db.close()  # Se cierra siempre al terminar la petición


# =============================================================================
# APLICACIÓN FASTAPI CON LIFESPAN
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: código que se ejecuta al arrancar y apagar la app.

    Por qué lifespan vs @app.on_event: lifespan es la forma moderna
    (FastAPI 0.95+). Los eventos on_event están deprecados.

    El código ANTES del yield se ejecuta al arrancar.
    El código DESPUÉS del yield se ejecuta al apagar.
    """
    # Arranque: crear tablas si no existen
    print("Iniciando aplicación — creando tablas en la DB...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas.")

    yield  # Aquí la app está corriendo y atendiendo peticiones

    # Apagado: cleanup
    print("Apagando aplicación — liberando recursos...")


app = FastAPI(
    title="FastAPI + SQLAlchemy",
    description="CRUD de usuarios y posts con base de datos SQLite real",
    version="1.0.0",
    lifespan=lifespan,
)


# =============================================================================
# ENDPOINTS DE USUARIOS
# =============================================================================

@app.post(
    "/usuarios",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuarios"],
)
def crear_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),  # FastAPI inyecta la sesión automáticamente
):
    """
    Crea un nuevo usuario.

    Depends(get_db): FastAPI llama a get_db(), obtiene la sesión,
    la pasa a este parámetro, y la cierra al terminar la petición.
    """
    # Verificar si el email ya existe
    existente = db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El email '{usuario.email}' ya está registrado.",
        )

    # En producción usaríamos passlib para hashear — ver archivo 05
    # Aquí usamos un prefijo simple para no mezclar conceptos
    password_hasheada = f"hash_{usuario.password}"

    nuevo_usuario = UsuarioDB(
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        email=usuario.email,
        hashed_password=password_hasheada,
    )

    db.add(nuevo_usuario)      # Añadir a la sesión (pendiente de commit)
    db.commit()                 # Persistir en la DB
    db.refresh(nuevo_usuario)  # Recarga el objeto con los datos de la DB (ej: ID generado)

    return nuevo_usuario


@app.get(
    "/usuarios",
    response_model=list[UsuarioResponse],
    tags=["Usuarios"],
)
def listar_usuarios(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Retorna todos los usuarios activos."""
    return db.query(UsuarioDB).filter(UsuarioDB.activo == True).offset(skip).limit(limit).all()


@app.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResponse,
    tags=["Usuarios"],
)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    """Obtiene un usuario por ID."""
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {usuario_id} no encontrado.",
        )
    return usuario


@app.delete(
    "/usuarios/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Usuarios"],
)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    """
    Elimina un usuario y todos sus posts (cascade delete por la relación).
    """
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    db.delete(usuario)
    db.commit()


# =============================================================================
# ENDPOINTS DE POSTS
# =============================================================================

@app.post(
    "/usuarios/{usuario_id}/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Posts"],
)
def crear_post(
    usuario_id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
):
    """Crea un post asociado a un usuario específico."""
    # Verificar que el usuario existe
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    nuevo_post = PostDB(
        titulo=post.titulo,
        contenido=post.contenido,
        publicado=post.publicado,
        autor_id=usuario_id,
    )

    db.add(nuevo_post)
    db.commit()
    db.refresh(nuevo_post)
    return nuevo_post


@app.get(
    "/usuarios/{usuario_id}/posts",
    response_model=list[PostResponse],
    tags=["Posts"],
)
def listar_posts_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    """Lista todos los posts de un usuario."""
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return usuario.posts


@app.get(
    "/posts",
    response_model=list[PostResponse],
    tags=["Posts"],
)
def listar_posts_publicados(
    db: Session = Depends(get_db),
):
    """Lista todos los posts publicados."""
    return db.query(PostDB).filter(PostDB.publicado == True).all()


# =============================================================================
# EJECUTAR
# =============================================================================

if __name__ == "__main__":
    if not FASTAPI_DISPONIBLE or not SQLALCHEMY_DISPONIBLE:
        print("Instala dependencias:")
        print('  pip install "fastapi[standard]" sqlalchemy')
    else:
        import uvicorn
        print("Iniciando FastAPI + SQLAlchemy...")
        print("DB: libro_python_fastapi.db (SQLite)")
        print("Docs: http://127.0.0.1:8000/docs")
        uvicorn.run("04_fastapi_con_bd:app", host="127.0.0.1", port=8000, reload=True)
