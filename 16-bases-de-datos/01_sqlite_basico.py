# =============================================================================
# 01_sqlite_basico.py — CRUD completo con SQLite nativo
# =============================================================================
# SQLite es una base de datos relacional que se almacena en un archivo .db
# El módulo sqlite3 ya viene incluido con Python, no requiere instalación.
#
# En este archivo aprenderemos:
#   - Cómo conectarse a una base de datos SQLite
#   - Cómo crear tablas con CREATE TABLE
#   - CRUD completo: Create, Read, Update, Delete
#   - Uso de context managers para manejar conexiones correctamente
#   - Parametrización para evitar SQL injection
# =============================================================================

import sqlite3
import os

# -----------------------------------------------------------------------------
# Constante con el nombre del archivo de la base de datos
# Usamos un archivo temporal para que el ejemplo sea fácil de limpiar
# -----------------------------------------------------------------------------
DB_FILE = "usuarios_demo.db"


# =============================================================================
# CREACIÓN DE LA BASE DE DATOS Y TABLA
# =============================================================================

def create_table(connection):
    """
    Crea la tabla 'users' si no existe todavía.

    Parámetros:
        connection: objeto de conexión sqlite3 activo

    Nota: IF NOT EXISTS evita error si la tabla ya existe.
    AUTOINCREMENT hace que el id se asigne automáticamente.
    NOT NULL garantiza que el campo siempre tenga valor.
    UNIQUE impide correos duplicados.
    """
    # El cursor es el objeto que ejecuta las sentencias SQL
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            email   TEXT    UNIQUE NOT NULL,
            age     INTEGER,
            active  INTEGER DEFAULT 1
        )
    """)

    # commit() guarda los cambios permanentemente en el archivo .db
    connection.commit()
    print("Tabla 'users' creada o ya existía.")


# =============================================================================
# CREATE — Insertar registros
# =============================================================================

def insert_user(connection, name, email, age):
    """
    Inserta un nuevo usuario en la tabla 'users'.

    Parámetros:
        connection: objeto de conexión sqlite3
        name (str): nombre del usuario
        email (str): correo electrónico (debe ser único)
        age (int): edad del usuario

    Retorna:
        int: ID del registro recién insertado

    IMPORTANTE: Usamos '?' como marcador de posición (placeholder).
    NUNCA uses f-strings o concatenación para construir SQL con datos del usuario,
    eso abre la puerta a SQL Injection (un ataque de seguridad muy común).
    """
    cursor = connection.cursor()

    # Los valores se pasan como tupla en el segundo argumento — esto es seguro
    cursor.execute(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        (name, email, age)
    )

    connection.commit()

    # lastrowid devuelve el ID asignado al registro recién insertado
    new_id = cursor.lastrowid
    print(f"  Usuario '{name}' insertado con ID {new_id}")
    return new_id


def insert_many_users(connection, users_list):
    """
    Inserta múltiples usuarios de forma eficiente usando executemany().

    Parámetros:
        connection: objeto de conexión sqlite3
        users_list (list): lista de tuplas (name, email, age)

    executemany() es más eficiente que llamar execute() en un bucle
    porque agrupa las operaciones en una sola transacción.
    """
    cursor = connection.cursor()

    cursor.executemany(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        users_list
    )

    connection.commit()
    print(f"  {cursor.rowcount} usuarios insertados en bloque.")


# =============================================================================
# READ — Consultar registros
# =============================================================================

def get_all_users(connection):
    """
    Obtiene todos los usuarios de la base de datos.

    Parámetros:
        connection: objeto de conexión sqlite3

    Retorna:
        list: lista de tuplas con los datos de cada usuario

    fetchall() recupera todos los resultados de la última consulta SELECT.
    Cada fila es una tupla: (id, name, email, age, active)
    """
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users ORDER BY name ASC")

    # fetchall() trae todos los registros a memoria
    rows = cursor.fetchall()
    return rows


def get_user_by_id(connection, user_id):
    """
    Busca un usuario específico por su ID.

    Parámetros:
        connection: objeto de conexión sqlite3
        user_id (int): ID del usuario a buscar

    Retorna:
        tuple | None: datos del usuario o None si no existe

    fetchone() recupera solo el primer resultado (o None si no hay).
    """
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

    # Nota: (user_id,) es una tupla de un elemento — la coma es necesaria
    return cursor.fetchone()


def search_users_by_age(connection, min_age, max_age):
    """
    Busca usuarios dentro de un rango de edad.

    Parámetros:
        connection: objeto de conexión sqlite3
        min_age (int): edad mínima (inclusive)
        max_age (int): edad máxima (inclusive)

    Retorna:
        list: lista de usuarios que cumplen el criterio
    """
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE age BETWEEN ? AND ? ORDER BY age",
        (min_age, max_age)
    )
    return cursor.fetchall()


# =============================================================================
# UPDATE — Modificar registros
# =============================================================================

def update_user_email(connection, user_id, new_email):
    """
    Actualiza el correo electrónico de un usuario.

    Parámetros:
        connection: objeto de conexión sqlite3
        user_id (int): ID del usuario a modificar
        new_email (str): nuevo correo electrónico

    Retorna:
        bool: True si se modificó algún registro, False si no se encontró
    """
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE users SET email = ? WHERE id = ?",
        (new_email, user_id)
    )
    connection.commit()

    # rowcount indica cuántas filas fueron afectadas por la operación
    modified = cursor.rowcount > 0
    if modified:
        print(f"  Email del usuario ID {user_id} actualizado a '{new_email}'")
    else:
        print(f"  No se encontró usuario con ID {user_id}")
    return modified


def deactivate_user(connection, user_id):
    """
    Desactiva un usuario (borrado lógico, no físico).

    Es mejor práctica marcar registros como inactivos en vez de borrarlos,
    así se preserva el historial y se pueden restaurar después.

    Parámetros:
        connection: objeto de conexión sqlite3
        user_id (int): ID del usuario a desactivar
    """
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE users SET active = 0 WHERE id = ?",
        (user_id,)
    )
    connection.commit()
    print(f"  Usuario ID {user_id} desactivado.")


# =============================================================================
# DELETE — Eliminar registros
# =============================================================================

def delete_user(connection, user_id):
    """
    Elimina físicamente un usuario de la base de datos.

    Parámetros:
        connection: objeto de conexión sqlite3
        user_id (int): ID del usuario a eliminar

    Advertencia: esta operación es irreversible.
    En producción, prefiere deactivate_user() para preservar historial.
    """
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    connection.commit()

    if cursor.rowcount > 0:
        print(f"  Usuario ID {user_id} eliminado permanentemente.")
    else:
        print(f"  No se encontró usuario con ID {user_id}.")


# =============================================================================
# UTILIDADES
# =============================================================================

def print_users(users, title="Usuarios"):
    """
    Imprime una lista de usuarios con formato legible.

    Parámetros:
        users (list): lista de tuplas devuelta por las funciones SELECT
        title (str): encabezado de la sección
    """
    print(f"\n--- {title} ---")
    if not users:
        print("  (sin resultados)")
        return

    # Encabezado de la tabla
    print(f"  {'ID':<5} {'Nombre':<15} {'Email':<25} {'Edad':<6} {'Activo'}")
    print("  " + "-" * 60)

    for row in users:
        user_id, name, email, age, active = row
        estado = "Sí" if active else "No"
        print(f"  {user_id:<5} {name:<15} {email:<25} {str(age):<6} {estado}")


# =============================================================================
# PROGRAMA PRINCIPAL — Demostración completa del CRUD
# =============================================================================

def main():
    """
    Función principal que demuestra todas las operaciones CRUD.

    Usa un context manager (with) para manejar la conexión.
    El bloque 'with' garantiza que la conexión se cierre aunque ocurra un error,
    evitando bloqueos o corrupción del archivo de base de datos.
    """
    print("=" * 60)
    print("  DEMO: SQLite CRUD Básico con Python")
    print("=" * 60)

    # El context manager abre la conexión y la cierra automáticamente al salir
    # Si el archivo DB_FILE no existe, sqlite3 lo crea automáticamente
    with sqlite3.connect(DB_FILE) as conn:

        # Paso 1: Crear la tabla
        print("\n[1] Creando tabla...")
        create_table(conn)

        # Paso 2: Insertar usuarios individuales
        print("\n[2] Insertando usuarios...")
        insert_user(conn, "Ana García", "ana@example.com", 30)
        insert_user(conn, "Carlos López", "carlos@example.com", 25)
        insert_user(conn, "María Rodríguez", "maria@example.com", 35)

        # Paso 3: Inserción masiva con executemany
        print("\n[3] Inserción masiva...")
        more_users = [
            ("Pedro Sánchez", "pedro@example.com", 28),
            ("Lucía Martínez", "lucia@example.com", 22),
            ("Roberto Torres", "roberto@example.com", 45),
        ]
        insert_many_users(conn, more_users)

        # Paso 4: Consultar todos los usuarios
        print("\n[4] Consultando todos los usuarios...")
        all_users = get_all_users(conn)
        print_users(all_users, "Todos los usuarios")

        # Paso 5: Buscar por ID
        print("\n[5] Buscando usuario con ID 1...")
        user = get_user_by_id(conn, 1)
        if user:
            print(f"  Encontrado: {user[1]} ({user[2]})")

        # Paso 6: Buscar por rango de edad
        print("\n[6] Usuarios entre 25 y 32 años...")
        young_users = search_users_by_age(conn, 25, 32)
        print_users(young_users, "Rango de edad 25-32")

        # Paso 7: Actualizar un registro
        print("\n[7] Actualizando email de usuario ID 1...")
        update_user_email(conn, 1, "ana.garcia@nuevoemail.com")

        # Paso 8: Borrado lógico
        print("\n[8] Desactivando usuario ID 2...")
        deactivate_user(conn, 2)

        # Paso 9: Borrado físico
        print("\n[9] Eliminando usuario ID 6...")
        delete_user(conn, 6)

        # Paso 10: Estado final
        print("\n[10] Estado final de la base de datos...")
        final_users = get_all_users(conn)
        print_users(final_users, "Estado final")

    print(f"\nBase de datos guardada en: {DB_FILE}")

    # Limpieza: eliminamos el archivo de demo
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Archivo '{DB_FILE}' eliminado (limpieza de demo).")


# -----------------------------------------------------------------------------
# Punto de entrada del script
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
