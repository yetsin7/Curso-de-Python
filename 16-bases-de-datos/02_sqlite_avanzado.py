# =============================================================================
# 02_sqlite_avanzado.py — SQLite avanzado: Joins, transacciones, índices
# =============================================================================
# Este archivo cubre técnicas avanzadas de SQLite:
#   - Múltiples tablas relacionadas con claves foráneas
#   - JOIN para combinar datos de varias tablas
#   - Transacciones explícitas (BEGIN / COMMIT / ROLLBACK)
#   - Índices para acelerar consultas
#   - Parametrización segura contra SQL Injection
#
# Ejemplo real: sistema de pedidos con clientes, productos y órdenes.
# =============================================================================

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_FILE = "pedidos_demo.db"


# =============================================================================
# CONFIGURACIÓN INICIAL — Activar claves foráneas
# =============================================================================

def configure_database(connection):
    """
    Configura opciones importantes de SQLite al abrir la conexión.

    SQLite no activa las claves foráneas (FOREIGN KEY) por defecto.
    Hay que habilitarlas explícitamente con PRAGMA.
    Los PRAGMA son comandos de configuración específicos de SQLite.
    """
    cursor = connection.cursor()

    # Habilita la verificación de claves foráneas
    # Sin esto, SQLite acepta IDs inválidos en campos FK sin dar error
    cursor.execute("PRAGMA foreign_keys = ON")

    # Modo journal WAL mejora el rendimiento en lecturas concurrentes
    cursor.execute("PRAGMA journal_mode = WAL")

    print("Base de datos configurada (FK activadas, WAL mode).")


# =============================================================================
# CREACIÓN DE TABLAS — Esquema relacional
# =============================================================================

def create_schema(connection):
    """
    Crea el esquema completo con tres tablas relacionadas:
        - clients: clientes del sistema
        - products: catálogo de productos
        - orders: pedidos que conectan clientes con productos

    Las FOREIGN KEY garantizan integridad referencial:
    no puedes crear un pedido con un cliente o producto inexistente.
    """
    cursor = connection.cursor()

    # Tabla de clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            email      TEXT    UNIQUE NOT NULL,
            city       TEXT,
            created_at TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Tabla de productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            price       REAL    NOT NULL CHECK(price > 0),
            stock       INTEGER NOT NULL DEFAULT 0,
            category    TEXT
        )
    """)

    # Tabla de pedidos — une clientes con productos
    # ON DELETE CASCADE: si se borra un cliente, sus pedidos también se borran
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id   INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            quantity    INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
            total_price REAL    NOT NULL,
            status      TEXT    DEFAULT 'pending',
            order_date  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (client_id)  REFERENCES clients(id)  ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
        )
    """)

    connection.commit()
    print("Esquema de tablas creado.")


# =============================================================================
# ÍNDICES — Acelerar consultas frecuentes
# =============================================================================

def create_indexes(connection):
    """
    Crea índices en columnas que se consultan frecuentemente.

    Un índice es como el índice de un libro: permite encontrar registros
    rápidamente sin leer toda la tabla. Mejora enormemente el rendimiento
    en tablas con miles o millones de registros.

    Desventaja: los índices ocupan espacio y ralentizan INSERT/UPDATE.
    Por eso solo se indexan columnas realmente usadas en búsquedas.
    """
    cursor = connection.cursor()

    # Índice en email de clientes (búsquedas frecuentes por email)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_clients_email
        ON clients(email)
    """)

    # Índice en categoría de productos (filtros frecuentes)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_category
        ON products(category)
    """)

    # Índice compuesto: pedidos por cliente y estado (consulta muy común)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_client_status
        ON orders(client_id, status)
    """)

    connection.commit()
    print("Índices creados para optimizar consultas.")


# =============================================================================
# INSERCIÓN DE DATOS DE PRUEBA
# =============================================================================

def seed_data(connection):
    """
    Inserta datos de prueba para demostrar los JOINs y consultas.
    'Seed' (semilla) es el término estándar para datos iniciales de demostración.
    """
    cursor = connection.cursor()

    # Insertar clientes
    clients = [
        ("Ana García", "ana@example.com", "Madrid"),
        ("Carlos López", "carlos@example.com", "Barcelona"),
        ("María Torres", "maria@example.com", "Valencia"),
        ("Pedro Ruiz", "pedro@example.com", "Sevilla"),
    ]
    cursor.executemany(
        "INSERT INTO clients (name, email, city) VALUES (?, ?, ?)",
        clients
    )

    # Insertar productos
    products = [
        ("Laptop Pro 15", 1299.99, 10, "Tecnología"),
        ("Mouse Inalámbrico", 29.99, 50, "Periféricos"),
        ("Teclado Mecánico", 89.99, 30, "Periféricos"),
        ("Monitor 27 pulgadas", 399.99, 15, "Tecnología"),
        ("Auriculares Bluetooth", 149.99, 25, "Audio"),
        ("Webcam HD", 79.99, 20, "Periféricos"),
    ]
    cursor.executemany(
        "INSERT INTO products (title, price, stock, category) VALUES (?, ?, ?, ?)",
        products
    )

    # Insertar pedidos
    orders = [
        (1, 1, 1, 1299.99, "completed"),
        (1, 2, 2, 59.98,   "completed"),
        (2, 3, 1, 89.99,   "pending"),
        (2, 4, 1, 399.99,  "shipped"),
        (3, 5, 2, 299.98,  "completed"),
        (4, 2, 3, 89.97,   "pending"),
        (1, 6, 1, 79.99,   "cancelled"),
        (3, 1, 1, 1299.99, "shipped"),
    ]
    cursor.executemany(
        """INSERT INTO orders (client_id, product_id, quantity, total_price, status)
           VALUES (?, ?, ?, ?, ?)""",
        orders
    )

    connection.commit()
    print("Datos de prueba insertados.")


# =============================================================================
# JOINS — Consultas con múltiples tablas
# =============================================================================

def get_orders_with_details(connection):
    """
    Obtiene todos los pedidos con nombre del cliente y producto.

    INNER JOIN: solo incluye registros que tienen coincidencia en AMBAS tablas.
    Se usa cuando queremos datos relacionados de varias tablas en una sola consulta.

    Retorna:
        list: lista de tuplas con los datos completos de cada pedido
    """
    cursor = connection.cursor()

    # JOIN une las tres tablas a través de sus claves foráneas
    cursor.execute("""
        SELECT
            o.id            AS order_id,
            c.name          AS client_name,
            c.city          AS client_city,
            p.title         AS product_title,
            o.quantity,
            o.total_price,
            o.status,
            o.order_date
        FROM orders o
        INNER JOIN clients  c ON o.client_id  = c.id
        INNER JOIN products p ON o.product_id = p.id
        ORDER BY o.order_date DESC
    """)

    return cursor.fetchall()


def get_client_summary(connection):
    """
    Obtiene un resumen por cliente: cuántos pedidos y total gastado.

    GROUP BY agrupa los resultados por cliente.
    Las funciones COUNT() y SUM() son funciones de agregación.
    HAVING filtra sobre los grupos (equivalente a WHERE pero para GROUP BY).
    """
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            c.name                      AS client_name,
            COUNT(o.id)                 AS total_orders,
            SUM(o.total_price)          AS total_spent,
            AVG(o.total_price)          AS avg_order_value,
            MAX(o.order_date)           AS last_order
        FROM clients c
        LEFT JOIN orders o ON c.id = o.client_id
        GROUP BY c.id, c.name
        HAVING total_orders > 0
        ORDER BY total_spent DESC
    """)

    return cursor.fetchall()


def get_products_by_category(connection, category):
    """
    Obtiene productos de una categoría con sus ventas totales.

    Parámetros:
        connection: objeto de conexión sqlite3
        category (str): nombre de la categoría a filtrar

    LEFT JOIN: incluye todos los productos aunque no tengan pedidos.
    COALESCE reemplaza NULL por 0 cuando no hay ventas.
    """
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            p.title,
            p.price,
            p.stock,
            COALESCE(SUM(o.quantity), 0)    AS units_sold,
            COALESCE(SUM(o.total_price), 0) AS revenue
        FROM products p
        LEFT JOIN orders o ON p.id = o.product_id AND o.status != 'cancelled'
        WHERE p.category = ?
        GROUP BY p.id, p.title
        ORDER BY revenue DESC
    """, (category,))

    return cursor.fetchall()


# =============================================================================
# TRANSACCIONES — Garantizar integridad de datos
# =============================================================================

def process_order(connection, client_id, product_id, quantity):
    """
    Procesa un pedido nuevo de forma atómica con transacción explícita.

    Una transacción garantiza que TODAS las operaciones se completan
    o NINGUNA se aplica. Esto es fundamental para mantener datos consistentes.

    Ejemplo: al crear un pedido, debemos:
    1. Verificar que hay stock suficiente
    2. Descontar el stock del producto
    3. Crear el registro del pedido

    Si el paso 3 falla después del paso 2, el stock quedaría descontado
    sin pedido. La transacción evita ese escenario.

    Parámetros:
        connection: objeto de conexión sqlite3
        client_id (int): ID del cliente
        product_id (int): ID del producto
        quantity (int): cantidad a pedir

    Retorna:
        int | None: ID del pedido creado, o None si falló
    """
    cursor = connection.cursor()

    try:
        # Iniciar transacción explícita
        cursor.execute("BEGIN")

        # Paso 1: Leer precio y stock actual (con bloqueo)
        cursor.execute(
            "SELECT price, stock FROM products WHERE id = ?",
            (product_id,)
        )
        product = cursor.fetchone()

        if not product:
            raise ValueError(f"Producto ID {product_id} no existe")

        price, stock = product

        if stock < quantity:
            raise ValueError(
                f"Stock insuficiente: se pidieron {quantity} pero hay {stock}"
            )

        # Paso 2: Descontar stock
        cursor.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity, product_id)
        )

        # Paso 3: Crear el pedido
        total = price * quantity
        cursor.execute(
            """INSERT INTO orders (client_id, product_id, quantity, total_price)
               VALUES (?, ?, ?, ?)""",
            (client_id, product_id, quantity, total)
        )

        order_id = cursor.lastrowid

        # Confirmar todas las operaciones juntas
        connection.commit()
        print(f"  Pedido #{order_id} creado: {quantity}x producto {product_id} = ${total:.2f}")
        return order_id

    except (ValueError, sqlite3.Error) as error:
        # Si algo falla, ROLLBACK deshace TODOS los cambios de la transacción
        connection.rollback()
        print(f"  Error al procesar pedido: {error}")
        return None


# =============================================================================
# SEGURIDAD — Demostración de SQL Injection
# =============================================================================

def demonstrate_sql_injection_prevention(connection):
    """
    Demuestra por qué NUNCA debes construir SQL con concatenación de strings.

    SQL Injection es uno de los ataques más comunes y peligrosos en aplicaciones
    con bases de datos. Un atacante inyecta SQL malicioso en los inputs.

    La solución es siempre usar parámetros (?) en lugar de formatear el SQL.
    """
    print("\n--- Demostración: Prevención de SQL Injection ---")

    # Simulamos un input malicioso de un atacante
    malicious_input = "'; DROP TABLE clients; --"

    # MAL: Construir SQL con f-string o format() — NUNCA hagas esto
    # Esta línea está comentada intencionalmente para no ejecutar el ataque
    # sql_malo = f"SELECT * FROM clients WHERE name = '{malicious_input}'"
    # El resultado sería: SELECT * FROM clients WHERE name = ''; DROP TABLE clients; --'
    # Esto ejecutaría DOS comandos: SELECT y DROP TABLE (¡borrando la tabla!)

    # BIEN: Usar parámetros — sqlite3 trata el input como dato, nunca como SQL
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM clients WHERE name = ?",
        (malicious_input,)
    )
    result = cursor.fetchall()

    print(f"  Input malicioso: {malicious_input!r}")
    print(f"  Con parámetros: la consulta es segura. Resultados: {result}")
    print("  El input malicioso fue tratado como texto, no como SQL.")


# =============================================================================
# UTILIDADES DE IMPRESIÓN
# =============================================================================

def print_orders(orders):
    """Imprime los pedidos con detalles de cliente y producto."""
    print(f"\n{'ID':<5} {'Cliente':<16} {'Ciudad':<12} {'Producto':<24} {'Cant':<5} {'Total':<10} {'Estado'}")
    print("-" * 90)
    for row in orders:
        order_id, client, city, product, qty, total, status, date = row
        print(f"{order_id:<5} {client:<16} {city:<12} {product:<24} {qty:<5} ${total:<9.2f} {status}")


def print_client_summary(summary):
    """Imprime el resumen de actividad por cliente."""
    print(f"\n{'Cliente':<18} {'Pedidos':<10} {'Total gastado':<16} {'Promedio':<12} {'Último pedido'}")
    print("-" * 75)
    for row in summary:
        name, count, total, avg, last = row
        print(f"{name:<18} {count:<10} ${total:<15.2f} ${avg:<11.2f} {last[:10]}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal que demuestra todas las técnicas avanzadas."""
    print("=" * 60)
    print("  DEMO: SQLite Avanzado — Joins, Transacciones, Índices")
    print("=" * 60)

    with sqlite3.connect(DB_FILE) as conn:

        print("\n[1] Configurando base de datos...")
        configure_database(conn)

        print("\n[2] Creando esquema relacional...")
        create_schema(conn)

        print("\n[3] Creando índices de optimización...")
        create_indexes(conn)

        print("\n[4] Insertando datos de prueba...")
        seed_data(conn)

        print("\n[5] Consulta con JOIN — pedidos completos:")
        orders = get_orders_with_details(conn)
        print_orders(orders)

        print("\n[6] Resumen por cliente (GROUP BY + agregaciones):")
        summary = get_client_summary(conn)
        print_client_summary(summary)

        print("\n[7] Productos de categoría 'Periféricos':")
        perifericos = get_products_by_category(conn, "Periféricos")
        for row in perifericos:
            title, price, stock, sold, revenue = row
            print(f"  {title}: ${price} | Stock: {stock} | Vendidos: {sold} | Ingresos: ${revenue:.2f}")

        print("\n[8] Procesando pedidos con transacciones:")
        process_order(conn, 2, 3, 2)   # pedido válido
        process_order(conn, 1, 1, 100)  # falla: stock insuficiente

        demonstrate_sql_injection_prevention(conn)

    print(f"\nBase de datos guardada en: {DB_FILE}")

    # Limpieza del archivo de demo
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Archivo '{DB_FILE}' eliminado (limpieza de demo).")


if __name__ == "__main__":
    main()
