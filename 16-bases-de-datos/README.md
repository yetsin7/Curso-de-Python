# Capítulo 16 — Bases de Datos con Python

## ¿Qué es una base de datos?

Una base de datos es un sistema organizado para **almacenar, gestionar y recuperar información** de forma persistente. Sin bases de datos, los datos de una aplicación se perderían al cerrarla.

---

## Bases de datos relacionales vs. NoSQL

### Relacionales (SQL)
Organizan los datos en **tablas** con filas y columnas, igual que una hoja de cálculo, pero con relaciones entre tablas.

- Los datos siguen un **esquema fijo** (estructura definida previamente).
- Usan **SQL** (Structured Query Language) para consultar y manipular datos.
- Son ideales cuando los datos tienen relaciones claras: usuarios → pedidos → productos.
- Ejemplos: **SQLite**, PostgreSQL, MySQL, SQL Server.

### NoSQL
Almacenan datos en formatos alternativos: documentos JSON, clave-valor, grafos, etc.

- **Esquema flexible**: los documentos no necesitan tener la misma estructura.
- Escalan mejor horizontalmente para grandes volúmenes de datos.
- Ejemplos: MongoDB (documentos), Redis (clave-valor), Neo4j (grafos).

### ¿Cuándo usar cada uno?
| Situación | Recomendación |
|-----------|---------------|
| Datos estructurados con relaciones | SQL (PostgreSQL, SQLite) |
| Datos variables / documentos JSON | NoSQL (MongoDB) |
| Caché y sesiones rápidas | Redis |
| Aprender bases de datos | SQLite |
| Producción en apps web | PostgreSQL |

---

## SQLite — La base de datos perfecta para aprender

SQLite es una base de datos **relacional que se almacena en un único archivo .db**. No requiere servidor, no requiere instalación adicional, y viene incluida con Python en el módulo `sqlite3`.

```python
import sqlite3  # ¡Ya incluido con Python!
```

### ¿Por qué SQLite para aprender?
1. **Sin configuración**: crea el archivo `.db` automáticamente.
2. **Portátil**: el archivo de la base de datos se puede copiar como cualquier archivo.
3. **Estándar SQL**: lo que aprendes aquí aplica a PostgreSQL y MySQL.
4. **Ideal para apps pequeñas y medianas**: muchas apps móviles y de escritorio lo usan en producción.

---

## SQL Básico — Los 4 comandos fundamentales

### CREATE TABLE — Crear una tabla
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    age INTEGER
);
```

### INSERT — Agregar datos
```sql
INSERT INTO users (name, email, age) VALUES ('Ana', 'ana@example.com', 30);
```

### SELECT — Consultar datos
```sql
SELECT * FROM users;                          -- todos los registros
SELECT name, email FROM users WHERE age > 25; -- con filtro
SELECT * FROM users ORDER BY name ASC;        -- ordenado
```

### UPDATE — Modificar datos
```sql
UPDATE users SET age = 31 WHERE email = 'ana@example.com';
```

### DELETE — Eliminar datos
```sql
DELETE FROM users WHERE id = 1;
```

### JOIN — Unir tablas
```sql
SELECT orders.id, users.name, products.title
FROM orders
JOIN users ON orders.user_id = users.id
JOIN products ON orders.product_id = products.id;
```

---

## ORM — ¿Qué es y por qué SQLAlchemy?

**ORM** (Object-Relational Mapping) es una técnica que permite interactuar con la base de datos usando **objetos Python** en lugar de escribir SQL directamente.

```python
# Sin ORM (SQL directo)
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Ana", "ana@example.com"))

# Con ORM (SQLAlchemy)
user = User(name="Ana", email="ana@example.com")
session.add(user)
session.commit()
```

### Ventajas del ORM
- Código más **Pythónico** y legible.
- **Portabilidad**: cambiar de SQLite a PostgreSQL sin reescribir queries.
- **Seguridad**: previene SQL injection automáticamente.
- **Productividad**: menos código repetitivo.

### ¿Por qué SQLAlchemy?
SQLAlchemy es el ORM más popular de Python. Ofrece dos modos:
- **Core**: nivel bajo, más cercano a SQL pero sin escribir SQL crudo.
- **ORM**: nivel alto, mapea tablas a clases Python.

```bash
pip install sqlalchemy
```

---

## ¿Cuándo usar cada opción?

| Herramienta | Cuándo usarla |
|-------------|---------------|
| `sqlite3` nativo | Scripts simples, aprender SQL, apps pequeñas |
| SQLAlchemy Core | Control total sobre SQL con ayuda de Python |
| SQLAlchemy ORM | Apps medianas/grandes, código mantenible |
| PostgreSQL + psycopg2 | Producción, múltiples usuarios concurrentes |

---

## Archivos del capítulo

| Archivo | Contenido |
|---------|-----------|
| `01_sqlite_basico.py` | CRUD completo con sqlite3 nativo y context managers |
| `02_sqlite_avanzado.py` | Joins, transacciones, índices, SQL injection prevention |
| `03_sqlalchemy_intro.py` | SQLAlchemy Core y ORM, instalación y CRUD básico |
| `04_sqlalchemy_relaciones.py` | Relaciones one-to-many y many-to-many con ORM |

---

## Conceptos clave del capítulo

- **Transacción**: conjunto de operaciones que se ejecutan todas o ninguna (ACID).
- **Índice**: estructura que acelera las búsquedas (como el índice de un libro).
- **Clave primaria (PK)**: identificador único de cada fila.
- **Clave foránea (FK)**: referencia a la PK de otra tabla (crea la relación).
- **SQL Injection**: ataque que inyecta SQL malicioso — se previene con parámetros `?`.
- **Context manager**: bloque `with` que garantiza cierre correcto de conexiones.
