# =============================================================================
# 04_sqlalchemy_relaciones.py — Relaciones One-to-Many y Many-to-Many
# =============================================================================
# Este archivo demuestra cómo modelar relaciones entre tablas con SQLAlchemy ORM.
#
# Instalación:
#   pip install sqlalchemy
#
# Tipos de relaciones en bases de datos relacionales:
#   - One-to-Many (1:N): un usuario tiene muchos posts
#   - Many-to-Many (N:M): un post puede tener muchos tags, un tag muchos posts
#   - One-to-One (1:1): una persona tiene un pasaporte (no cubierto aquí)
#
# Ejemplo: Blog con Usuarios, Posts y Tags
# =============================================================================

try:
    from sqlalchemy import (
        create_engine, Column, Integer, String, Text,
        Boolean, DateTime, ForeignKey, Table
    )
    from sqlalchemy.orm import (
        DeclarativeBase, relationship, Session, joinedload, selectinload
    )
    from sqlalchemy import select
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

import os
from datetime import datetime


# =============================================================================
# VERIFICACIÓN DE INSTALACIÓN
# =============================================================================

if not SQLALCHEMY_AVAILABLE:
    print("SQLAlchemy no está instalado.")
    print("Ejecuta: pip install sqlalchemy")
    exit(1)


# =============================================================================
# BASE Y TABLA DE ASOCIACIÓN (para Many-to-Many)
# =============================================================================

class Base(DeclarativeBase):
    """Clase base para todos los modelos del blog."""
    pass


# Tabla de asociación para la relación Many-to-Many entre Post y Tag.
# Esta tabla NO es un modelo ORM completo porque no tiene datos propios,
# solo guarda los pares (post_id, tag_id) que representan la relación.
# Se llama "tabla puente" o "tabla de unión".
post_tags = Table(
    "post_tags",              # nombre de la tabla en la DB
    Base.metadata,            # registro de tablas de la Base
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id",  Integer, ForeignKey("tags.id"),  primary_key=True),
)


# =============================================================================
# MODELOS ORM — Clases que representan las tablas del blog
# =============================================================================

class User(Base):
    """
    Modelo de usuario del blog.

    Relación con Post: One-to-Many (un usuario escribe muchos posts).
    El lado 'Uno' de la relación define el relationship().
    """
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    username   = Column(String(50), unique=True, nullable=False)
    email      = Column(String(150), unique=True, nullable=False)
    full_name  = Column(String(200))
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationship() define cómo navegar entre objetos relacionados.
    # 'posts' es el atributo que usaremos: user.posts devuelve los posts del usuario.
    # back_populates conecta ambos lados: post.author devuelve el User.
    # lazy='select' carga los posts solo cuando se accede a user.posts (lazy loading).
    posts = relationship(
        "Post",
        back_populates="author",
        lazy="select",
        cascade="all, delete-orphan"  # Si borras el usuario, se borran sus posts
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Tag(Base):
    """
    Etiqueta para clasificar posts.

    Relación con Post: Many-to-Many (un tag puede estar en muchos posts,
    un post puede tener muchos tags).
    """
    __tablename__ = "tags"

    id   = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(60), unique=True, nullable=False)

    # secondary indica la tabla puente que gestiona la relación N:M
    posts = relationship(
        "Post",
        secondary=post_tags,
        back_populates="tags"
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class Post(Base):
    """
    Entrada del blog.

    Este modelo es el centro de las relaciones:
    - Many-to-One con User (muchos posts pertenecen a un usuario)
    - Many-to-Many con Tag (un post puede tener varios tags)
    """
    __tablename__ = "posts"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    title      = Column(String(300), nullable=False)
    content    = Column(Text)
    published  = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Clave foránea — referencia al ID del usuario autor
    # ForeignKey("users.id") = columna 'id' de la tabla 'users'
    author_id  = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Lado 'Muchos' de la relación User → Post
    # author_id es la FK; back_populates conecta con User.posts
    author = relationship(
        "User",
        back_populates="posts"
    )

    # Relación Many-to-Many con Tag usando la tabla puente post_tags
    tags = relationship(
        "Tag",
        secondary=post_tags,
        back_populates="posts"
    )

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title[:30]}...', published={self.published})>"


# =============================================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# =============================================================================

DB_PATH = "blog_demo.db"


def setup_engine():
    """
    Crea el engine y las tablas del blog.

    Retorna:
        Engine: objeto engine configurado
    """
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    Base.metadata.create_all(engine)
    print(f"Base de datos del blog: {DB_PATH}")
    return engine


# =============================================================================
# FUNCIONES DE DEMOSTRACIÓN
# =============================================================================

def seed_blog(session):
    """
    Puebla la base de datos con datos de ejemplo para el blog.

    Parámetros:
        session: sesión activa de SQLAlchemy
    """
    print("\n[1] Creando usuarios, tags y posts...")

    # Crear usuarios
    alice = User(username="alice", email="alice@blog.com", full_name="Alice Smith")
    bob   = User(username="bob",   email="bob@blog.com",   full_name="Bob Johnson")
    carol = User(username="carol", email="carol@blog.com", full_name="Carol White")

    session.add_all([alice, bob, carol])
    session.flush()  # flush envía el SQL sin commit — necesario para obtener los IDs

    # Crear tags
    tag_python = Tag(name="Python",      slug="python")
    tag_db     = Tag(name="Bases de Datos", slug="bases-de-datos")
    tag_web    = Tag(name="Web",         slug="web")
    tag_tips   = Tag(name="Tips",        slug="tips")

    session.add_all([tag_python, tag_db, tag_web, tag_tips])
    session.flush()

    # Crear posts — notar cómo se asigna el author directamente como objeto
    # SQLAlchemy extrae automáticamente el author_id del objeto User
    post1 = Post(
        title="Introducción a SQLAlchemy",
        content="SQLAlchemy es el ORM más completo de Python...",
        published=True,
        author=alice,              # relación directa con el objeto User
        tags=[tag_python, tag_db]  # relación Many-to-Many en una sola línea
    )

    post2 = Post(
        title="Tips de Python para principiantes",
        content="Aquí van los mejores consejos para aprender Python...",
        published=True,
        author=alice,
        tags=[tag_python, tag_tips]
    )

    post3 = Post(
        title="Construyendo una API REST con Flask",
        content="Flask es el microframework más popular de Python...",
        published=True,
        author=bob,
        tags=[tag_python, tag_web]
    )

    post4 = Post(
        title="Borrador: Guía de PostgreSQL",
        content="Contenido en progreso...",
        published=False,   # Borrador, no publicado
        author=carol,
        tags=[tag_db]
    )

    session.add_all([post1, post2, post3, post4])
    session.commit()

    print(f"  3 usuarios, 4 tags y 4 posts creados.")


def demo_one_to_many(session):
    """
    Demuestra la navegación por relaciones One-to-Many.

    Con relationship() puedes navegar entre objetos relacionados
    como si fueran atributos normales de Python.
    """
    print("\n[2] Relación One-to-Many — Usuario → Posts:")

    # Carga todos los usuarios con sus posts de forma eficiente
    # selectinload() hace una consulta separada para los posts (evita N+1 problem)
    stmt = select(User).options(selectinload(User.posts)).order_by(User.username)
    users = session.execute(stmt).scalars().all()

    for user in users:
        published_count = sum(1 for p in user.posts if p.published)
        print(f"\n  Autor: {user.full_name} (@{user.username})")
        print(f"  Posts: {len(user.posts)} total, {published_count} publicados")

        for post in user.posts:
            status = "PUBLICADO" if post.published else "BORRADOR"
            tags_str = ", ".join(t.name for t in post.tags)
            print(f"    - [{status}] {post.title}")
            print(f"      Tags: {tags_str}")


def demo_many_to_many(session):
    """
    Demuestra la navegación por relaciones Many-to-Many.

    Con la tabla post_tags y relationship(), podemos navegar
    en cualquier dirección: post.tags o tag.posts.
    """
    print("\n[3] Relación Many-to-Many — Tags → Posts:")

    # Carga todos los tags con sus posts asociados
    stmt = select(Tag).options(selectinload(Tag.posts)).order_by(Tag.name)
    tags = session.execute(stmt).scalars().all()

    for tag in tags:
        published_posts = [p for p in tag.posts if p.published]
        print(f"\n  Tag: #{tag.name} ({len(tag.posts)} posts)")

        for post in published_posts:
            print(f"    - {post.title} (por {post.author.username})")


def demo_queries(session):
    """
    Demuestra consultas avanzadas con relaciones en ORM.
    """
    print("\n[4] Consultas avanzadas con relaciones:")

    # Consulta 1: Posts publicados con autor y tags cargados juntos
    # joinedload() hace un JOIN SQL para cargar todo en una sola consulta
    stmt = (
        select(Post)
        .options(
            joinedload(Post.author),
            selectinload(Post.tags)
        )
        .where(Post.published == True)
        .order_by(Post.created_at.desc())
    )
    posts = session.execute(stmt).unique().scalars().all()
    print(f"\n  Posts publicados: {len(posts)}")

    for post in posts:
        tags_str = " ".join(f"#{t.slug}" for t in post.tags)
        print(f"    '{post.title}' por {post.author.username} | {tags_str}")

    # Consulta 2: Posts de un usuario específico por username
    stmt_user = (
        select(Post)
        .join(Post.author)             # JOIN con la tabla users
        .where(User.username == "alice")
        .where(Post.published == True)
    )
    alice_posts = session.execute(stmt_user).scalars().all()
    print(f"\n  Posts publicados de alice: {len(alice_posts)}")

    # Consulta 3: Posts que tienen el tag 'python'
    stmt_tag = (
        select(Post)
        .join(Post.tags)               # JOIN con tabla post_tags y tags
        .where(Tag.slug == "python")
        .where(Post.published == True)
        .options(joinedload(Post.author))
    )
    python_posts = session.execute(stmt_tag).unique().scalars().all()
    print(f"\n  Posts con tag #python: {len(python_posts)}")
    for post in python_posts:
        print(f"    - {post.title}")


def demo_modify_relations(session):
    """
    Demuestra cómo agregar y quitar elementos en relaciones Many-to-Many.

    SQLAlchemy gestiona automáticamente la tabla post_tags:
    - Al hacer post.tags.append(tag), inserta en post_tags
    - Al hacer post.tags.remove(tag), borra de post_tags
    """
    print("\n[5] Modificar relaciones Many-to-Many:")

    # Obtener el primer post de alice y el tag 'web'
    post = session.execute(
        select(Post)
        .join(Post.author)
        .where(User.username == "alice")
        .where(Post.published == True)
        .options(selectinload(Post.tags))
        .limit(1)
    ).scalars().first()

    tag_web = session.execute(
        select(Tag).where(Tag.slug == "web")
    ).scalars().first()

    if post and tag_web:
        print(f"\n  Post: '{post.title}'")
        print(f"  Tags antes: {[t.name for t in post.tags]}")

        # Agregar un tag nuevo — SQLAlchemy inserta en post_tags automáticamente
        if tag_web not in post.tags:
            post.tags.append(tag_web)
            session.commit()
            print(f"  Tag '#web' agregado.")

        print(f"  Tags después: {[t.name for t in post.tags]}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal del demo de relaciones SQLAlchemy."""
    print("=" * 60)
    print("  DEMO: SQLAlchemy — Relaciones One-to-Many y Many-to-Many")
    print("=" * 60)

    engine = setup_engine()

    with Session(engine) as session:
        seed_blog(session)
        demo_one_to_many(session)
        demo_many_to_many(session)
        demo_queries(session)
        demo_modify_relations(session)

    engine.dispose()
    print("\n" + "=" * 60)
    print("  Demo completado.")
    print("=" * 60)

    # Limpieza
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Archivo '{DB_PATH}' eliminado (limpieza de demo).")


if __name__ == "__main__":
    main()
