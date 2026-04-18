"""
Migraciones de Base de Datos
=============================
Explica qué son las migraciones, por qué son esenciales en proyectos
reales y cómo implementar un sistema simple de migraciones manual
con sqlite3 nativo. Se compara con Alembic y Django migrations.

Conceptos cubiertos:
  - Qué es una migración y el problema que resuelve
  - Tabla `migrations` para llevar registro de versiones aplicadas
  - Aplicar migraciones hacia adelante (upgrade)
  - Revertir migraciones (downgrade)
  - Comparación con herramientas profesionales
"""

import sqlite3
import os
from datetime import datetime
from typing import Callable

# --- Base de datos de ejemplo (temporal, en memoria o archivo local) ---
DB_PATH = os.path.join(os.path.dirname(__file__), 'migraciones_demo.db')


# ===========================================================================
# CONCEPTO: ¿Qué es una migración?
# ===========================================================================
"""
Una MIGRACIÓN es un script versionado que describe un cambio en el esquema
de la base de datos (crear tabla, agregar columna, cambiar tipo, etc.).

Sin migraciones:
  - Se edita la BD a mano → los entornos se desincronizán
  - No hay historial de cambios → ¿quién borró esa columna?
  - Imposible reproducir la BD en otro servidor

Con migraciones:
  - Cada cambio queda registrado en un archivo de código
  - Se aplican en orden: v001 → v002 → v003
  - Se pueden revertir: v003 → v002
  - Se integran en CI/CD y control de versiones
"""


# ===========================================================================
# Sistema de migraciones manual con sqlite3
# ===========================================================================

def conectar(path: str = DB_PATH) -> sqlite3.Connection:
    """
    Abre la conexión a SQLite y activa las claves foráneas.

    Args:
        path: Ruta al archivo de base de datos.

    Returns:
        Conexión sqlite3 configurada.
    """
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_tabla_migraciones(conn: sqlite3.Connection) -> None:
    """
    Crea la tabla `migrations` si no existe.
    Esta tabla actúa como registro de todas las migraciones aplicadas.

    Columnas:
        id         - Número único de migración (ej. 1, 2, 3)
        name       - Nombre descriptivo de la migración
        applied_at - Timestamp de cuándo se aplicó
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            id         INTEGER PRIMARY KEY,
            name       TEXT    NOT NULL,
            applied_at TEXT    NOT NULL
        )
    """)
    conn.commit()


def obtener_migraciones_aplicadas(conn: sqlite3.Connection) -> set:
    """
    Retorna el conjunto de IDs de migraciones ya aplicadas en la BD.

    Args:
        conn: Conexión activa.

    Returns:
        Set de enteros con los IDs de migraciones registradas.
    """
    filas = conn.execute("SELECT id FROM migrations").fetchall()
    return {row[0] for row in filas}


def registrar_migracion(conn: sqlite3.Connection, id_: int, nombre: str) -> None:
    """
    Inserta un registro en la tabla `migrations` para marcar una migración
    como aplicada correctamente.

    Args:
        conn  : Conexión activa.
        id_   : Número de la migración.
        nombre: Nombre descriptivo.
    """
    ahora = datetime.now().isoformat(sep=' ', timespec='seconds')
    conn.execute(
        "INSERT INTO migrations (id, name, applied_at) VALUES (?, ?, ?)",
        (id_, nombre, ahora)
    )
    conn.commit()


def desregistrar_migracion(conn: sqlite3.Connection, id_: int) -> None:
    """
    Elimina el registro de una migración al hacer rollback/downgrade.

    Args:
        conn: Conexión activa.
        id_ : ID de la migración a eliminar del registro.
    """
    conn.execute("DELETE FROM migrations WHERE id = ?", (id_,))
    conn.commit()


# ===========================================================================
# Definición de migraciones (upgrade + downgrade)
# ===========================================================================

# Cada migración es una tupla: (id, nombre, upgrade_fn, downgrade_fn)
# upgrade   → aplica el cambio
# downgrade → revierte el cambio

def _m001_upgrade(conn: sqlite3.Connection) -> None:
    """Migración 001 — Crea la tabla inicial de usuarios."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            email    TEXT    NOT NULL
        )
    """)
    conn.commit()


def _m001_downgrade(conn: sqlite3.Connection) -> None:
    """Revierte migración 001 — Elimina la tabla de usuarios."""
    conn.execute("DROP TABLE IF EXISTS users")
    conn.commit()


def _m002_upgrade(conn: sqlite3.Connection) -> None:
    """Migración 002 — Agrega columna 'created_at' a users."""
    conn.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
    conn.commit()


def _m002_downgrade(conn: sqlite3.Connection) -> None:
    """
    Revierte migración 002.
    SQLite no soporta DROP COLUMN directamente en versiones antiguas,
    así que se recrea la tabla sin la columna eliminada.
    """
    conn.execute("""
        CREATE TABLE users_backup AS
        SELECT id, username, email FROM users
    """)
    conn.execute("DROP TABLE users")
    conn.execute("ALTER TABLE users_backup RENAME TO users")
    conn.commit()


def _m003_upgrade(conn: sqlite3.Connection) -> None:
    """Migración 003 — Crea tabla de publicaciones relacionada con users."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id),
            title      TEXT    NOT NULL,
            body       TEXT,
            created_at TEXT
        )
    """)
    conn.commit()


def _m003_downgrade(conn: sqlite3.Connection) -> None:
    """Revierte migración 003 — Elimina tabla de publicaciones."""
    conn.execute("DROP TABLE IF EXISTS posts")
    conn.commit()


# Registro central de migraciones (en orden)
MIGRACIONES: list[tuple[int, str, Callable, Callable]] = [
    (1, "crear_tabla_users",       _m001_upgrade, _m001_downgrade),
    (2, "agregar_created_at_users", _m002_upgrade, _m002_downgrade),
    (3, "crear_tabla_posts",        _m003_upgrade, _m003_downgrade),
]


# ===========================================================================
# Motor de migraciones
# ===========================================================================

def aplicar_migraciones(conn: sqlite3.Connection) -> None:
    """
    Aplica todas las migraciones pendientes en orden ascendente.
    Omite las que ya fueron aplicadas anteriormente.

    Args:
        conn: Conexión activa a la base de datos.
    """
    inicializar_tabla_migraciones(conn)
    aplicadas = obtener_migraciones_aplicadas(conn)

    pendientes = [m for m in MIGRACIONES if m[0] not in aplicadas]

    if not pendientes:
        print("  [INFO] La base de datos ya está al día. Sin migraciones pendientes.")
        return

    for id_, nombre, upgrade, _ in pendientes:
        print(f"  → Aplicando migración {id_:03d}: {nombre}…")
        try:
            upgrade(conn)
            registrar_migracion(conn, id_, nombre)
            print(f"     ✓ Completada")
        except Exception as e:
            print(f"     ✗ Error: {e}")
            raise


def revertir_ultima_migracion(conn: sqlite3.Connection) -> None:
    """
    Revierte la última migración aplicada (rollback de un paso).

    Args:
        conn: Conexión activa a la base de datos.
    """
    inicializar_tabla_migraciones(conn)
    aplicadas = obtener_migraciones_aplicadas(conn)

    if not aplicadas:
        print("  [INFO] No hay migraciones que revertir.")
        return

    # La migración más reciente es la de mayor ID
    ultimo_id = max(aplicadas)
    registro = next((m for m in MIGRACIONES if m[0] == ultimo_id), None)

    if registro is None:
        print(f"  [WARN] No se encontró definición para migración ID={ultimo_id}.")
        return

    id_, nombre, _, downgrade = registro
    print(f"  ← Revirtiendo migración {id_:03d}: {nombre}…")
    try:
        downgrade(conn)
        desregistrar_migracion(conn, id_)
        print(f"     ✓ Revertida")
    except Exception as e:
        print(f"     ✗ Error al revertir: {e}")
        raise


def mostrar_estado(conn: sqlite3.Connection) -> None:
    """
    Muestra el estado actual de todas las migraciones: aplicadas o pendientes.

    Args:
        conn: Conexión activa.
    """
    inicializar_tabla_migraciones(conn)
    aplicadas = obtener_migraciones_aplicadas(conn)

    print("\n  Estado de migraciones:")
    print(f"  {'ID':<5} {'Nombre':<35} {'Estado'}")
    print("  " + "-" * 55)
    for id_, nombre, _, _ in MIGRACIONES:
        estado = "✓ aplicada" if id_ in aplicadas else "○ pendiente"
        print(f"  {id_:<5} {nombre:<35} {estado}")


# ===========================================================================
# Comparación con herramientas profesionales
# ===========================================================================

def mostrar_comparacion() -> None:
    """
    Imprime una comparación conceptual entre el sistema manual,
    Alembic (SQLAlchemy) y Django migrations.
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          COMPARACIÓN DE SISTEMAS DE MIGRACIONES                 ║
╠══════════════════════════════════════════════════════════════════╣
║  SISTEMA MANUAL (este archivo)                                   ║
║  ─────────────────────────────                                   ║
║  • Sin dependencias externas (solo sqlite3)                      ║
║  • Total control sobre cada paso                                 ║
║  • Ideal para aprender y proyectos pequeños                      ║
║  • Hay que escribir upgrade Y downgrade manualmente              ║
║                                                                  ║
║  ALEMBIC (con SQLAlchemy)                                        ║
║  ─────────────────────────                                       ║
║  pip install alembic sqlalchemy                                  ║
║  alembic init migrations          ← crea carpeta de config       ║
║  alembic revision --autogenerate  ← genera migración automática  ║
║  alembic upgrade head             ← aplica todas                 ║
║  alembic downgrade -1             ← revierte 1 paso              ║
║  • Detecta cambios en modelos automáticamente                    ║
║  • Muy usado en proyectos Flask/FastAPI                          ║
║                                                                  ║
║  DJANGO MIGRATIONS                                               ║
║  ─────────────────                                               ║
║  python manage.py makemigrations  ← genera desde modelos         ║
║  python manage.py migrate         ← aplica                       ║
║  python manage.py migrate app 002 ← revierte a versión 002       ║
║  • 100% automático si usas modelos Django                        ║
║  • Detecta relaciones, índices y constraints                     ║
║  • La mejor opción dentro del ecosistema Django                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


# ===========================================================================
# Punto de entrada — demostración completa
# ===========================================================================

def main() -> None:
    """
    Demuestra el ciclo completo de migraciones:
    aplicar, ver estado, revertir, volver a ver estado.
    Al final elimina el archivo de BD de demo para no dejar residuos.
    """
    print("=" * 60)
    print("  SISTEMA DE MIGRACIONES — DEMO COMPLETA")
    print("=" * 60)

    conn = conectar()

    # 1. Aplicar todas las migraciones
    print("\n[1] Aplicando migraciones:")
    aplicar_migraciones(conn)

    # 2. Mostrar estado
    mostrar_estado(conn)

    # 3. Revertir la última migración
    print("\n[3] Revirtiendo la última migración:")
    revertir_ultima_migracion(conn)

    # 4. Estado tras revertir
    mostrar_estado(conn)

    # 5. Volver a aplicar
    print("\n[5] Reaplicando migraciones faltantes:")
    aplicar_migraciones(conn)

    conn.close()

    # Limpiar archivo de demo
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("\n  [INFO] Archivo de demo eliminado.")

    # 6. Comparación con herramientas profesionales
    mostrar_comparacion()


if __name__ == "__main__":
    main()
