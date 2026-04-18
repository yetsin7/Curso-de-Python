# =============================================================================
# 03_sqlalchemy_intro.py — SQLAlchemy Core y ORM básico
# =============================================================================
# SQLAlchemy es el ORM más popular de Python.
# Permite interactuar con bases de datos usando objetos Python en vez de SQL.
#
# Instalación:
#   pip install sqlalchemy
#
# SQLAlchemy tiene dos capas:
#   - Core: nivel bajo, construcción de SQL mediante objetos Python
#   - ORM: nivel alto, mapea tablas a clases Python (lo más usado)
#
# Este archivo cubre:
#   - Instalación y verificación de SQLAlchemy
#   - Definición de modelos ORM (clases que representan tablas)
#   - Sesión: el objeto central para interactuar con la DB en ORM
#   - CRUD completo usando la API de ORM
#   - Consultas con filter, order_by, limit
# =============================================================================

# Intento de importación con manejo de error claro
try:
    from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, text
    from sqlalchemy.orm import DeclarativeBase, Session
    from sqlalchemy import select, update, delete
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

import os


# =============================================================================
# VERIFICACIÓN DE DISPONIBILIDAD
# =============================================================================

def check_sqlalchemy():
    """
    Verifica que SQLAlchemy esté instalado y muestra instrucciones si no.

    Retorna:
        bool: True si está disponible, False si no está instalado
    """
    if not SQLALCHEMY_AVAILABLE:
        print("=" * 60)
        print("  SQLAlchemy NO está instalado.")
        print("=" * 60)
        print("\nPara instalarlo, ejecuta en tu terminal:")
        print("\n    pip install sqlalchemy")
        print("\nO si usas un entorno virtual (recomendado):")
        print("    source venv/bin/activate  # Linux/Mac")
        print("    venv\\Scripts\\activate     # Windows")
        print("    pip install sqlalchemy")
        print("\nLuego vuelve a ejecutar este archivo.")
        return False
    return True


# =============================================================================
# MODELO ORM — Definición de la clase que mapea a la tabla
# =============================================================================

if SQLALCHEMY_AVAILABLE:

    class Base(DeclarativeBase):
        """
        Clase base de la que deben heredar todos los modelos ORM.

        DeclarativeBase es la forma moderna de definir modelos en SQLAlchemy 2.x.
        Mantiene un registro interno de todas las tablas para poder crearlas
        automáticamente con Base.metadata.create_all().
        """
        pass

    class User(Base):
        """
        Modelo ORM que representa la tabla 'users' en la base de datos.

        Cada atributo de clase con Column() se convierte en una columna.
        Los tipos (Integer, String, Float) corresponden a tipos SQL estándar.

        El ORM hace el mapeo bidireccional:
        - Python → SQL: cuando guardas un objeto User, genera INSERT
        - SQL → Python: cuando consultas, devuelve objetos User
        """

        # __tablename__ define el nombre de la tabla en la base de datos
        __tablename__ = "users"

        # Columnas — cada Column() define una columna de la tabla
        id       = Column(Integer, primary_key=True, autoincrement=True)
        name     = Column(String(100), nullable=False)
        email    = Column(String(150), unique=True, nullable=False)
        age      = Column(Integer)
        salary   = Column(Float, default=0.0)
        is_admin = Column(Boolean, default=False)

        def __repr__(self):
            """
            Representación legible del objeto para debugging.
            Se muestra cuando imprimes el objeto directamente.
            """
            return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

        def to_dict(self):
            """
            Convierte el modelo a diccionario Python.
            Útil para serializar a JSON o para comparaciones.
            """
            return {
                "id":       self.id,
                "name":     self.name,
                "email":    self.email,
                "age":      self.age,
                "salary":   self.salary,
                "is_admin": self.is_admin,
            }

    class Product(Base):
        """
        Modelo de producto para demostrar múltiples modelos en el mismo archivo.
        """
        __tablename__ = "products"

        id       = Column(Integer, primary_key=True, autoincrement=True)
        name     = Column(String(200), nullable=False)
        price    = Column(Float, nullable=False)
        category = Column(String(100))
        in_stock = Column(Boolean, default=True)

        def __repr__(self):
            return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"


# =============================================================================
# CONFIGURACIÓN DEL ENGINE Y SESIÓN
# =============================================================================

def create_db_engine(db_path="sqlalchemy_demo.db"):
    """
    Crea el engine de SQLAlchemy y crea todas las tablas.

    El Engine es el punto de entrada a la base de datos.
    Gestiona el pool de conexiones y traduce entre Python y SQL.

    Parámetros:
        db_path (str): ruta al archivo SQLite

    Retorna:
        Engine: objeto engine listo para usar

    La URL de conexión tiene el formato:
        sqlite:///nombre_archivo.db   (ruta relativa)
        sqlite:////ruta/absoluta.db   (ruta absoluta, 4 barras)
        sqlite:///:memory:            (base de datos en RAM, solo para pruebas)
    """
    # echo=True imprime el SQL generado en consola — muy útil para aprender
    # En producción pon echo=False para no llenar los logs
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    # create_all() crea todas las tablas registradas en Base.metadata
    # Si la tabla ya existe, no la sobreescribe (equivale a CREATE TABLE IF NOT EXISTS)
    Base.metadata.create_all(engine)

    print(f"Engine creado. Base de datos: {db_path}")
    return engine


# =============================================================================
# CRUD CON ORM
# =============================================================================

def demo_create(session):
    """
    Demuestra cómo crear registros con el ORM.

    session.add() marca el objeto para ser insertado.
    session.commit() ejecuta el INSERT y confirma la transacción.
    session.flush() envía el SQL sin hacer commit (útil para obtener el ID).
    """
    print("\n--- CREATE: Insertar usuarios ---")

    # Crear objetos Python — el ORM los convertirá en INSERT
    user1 = User(name="Ana García", email="ana@example.com", age=30, salary=45000.0)
    user2 = User(name="Carlos López", email="carlos@example.com", age=25, salary=38000.0)
    user3 = User(name="María Torres", email="maria@example.com", age=35, salary=62000.0, is_admin=True)

    # add_all() agrega múltiples objetos de una vez
    session.add_all([user1, user2, user3])
    session.commit()

    # Después del commit, los objetos tienen su ID asignado por la DB
    print(f"  Usuario creado: {user1}")
    print(f"  Usuario creado: {user2}")
    print(f"  Usuario creado: {user3}")

    # Crear productos
    products = [
        Product(name="Laptop Pro", price=1299.99, category="Tecnología"),
        Product(name="Mouse Inalámbrico", price=29.99, category="Periféricos"),
        Product(name="Teclado Mecánico", price=89.99, category="Periféricos"),
    ]
    session.add_all(products)
    session.commit()
    print(f"  {len(products)} productos creados.")


def demo_read(session):
    """
    Demuestra las diferentes formas de consultar con ORM.

    SQLAlchemy 2.x usa session.execute(select(Model)) como forma moderna.
    También soporta session.get() para buscar por clave primaria.
    """
    print("\n--- READ: Consultar registros ---")

    # Forma 1: Obtener todos los registros
    # select(User) genera: SELECT * FROM users
    stmt = select(User).order_by(User.name)
    users = session.execute(stmt).scalars().all()
    print(f"  Total de usuarios: {len(users)}")

    for user in users:
        print(f"    {user.id}. {user.name} | {user.email} | Edad: {user.age}")

    # Forma 2: Buscar por clave primaria (el método más eficiente)
    user = session.get(User, 1)
    print(f"\n  Usuario con ID 1: {user}")

    # Forma 3: Filtrar con condiciones
    # where() es el equivalente ORM de WHERE en SQL
    stmt_admin = select(User).where(User.is_admin == True)
    admins = session.execute(stmt_admin).scalars().all()
    print(f"\n  Administradores: {[u.name for u in admins]}")

    # Forma 4: Filtros múltiples y rango
    stmt_range = select(User).where(
        User.age >= 25,
        User.age <= 32
    ).order_by(User.age)
    young_users = session.execute(stmt_range).scalars().all()
    print(f"\n  Usuarios entre 25-32 años: {[u.name for u in young_users]}")

    # Forma 5: limit y offset para paginación
    stmt_page = select(User).order_by(User.id).limit(2).offset(0)
    page_users = session.execute(stmt_page).scalars().all()
    print(f"\n  Primera página (2 por página): {[u.name for u in page_users]}")


def demo_update(session):
    """
    Demuestra cómo actualizar registros con ORM.

    Dos métodos:
    1. Modificar el objeto directamente y hacer commit (para pocos registros)
    2. Usar stmt UPDATE para actualizar múltiples registros de una vez
    """
    print("\n--- UPDATE: Modificar registros ---")

    # Método 1: Modificar objeto Python directamente
    user = session.get(User, 1)
    if user:
        old_salary = user.salary
        user.salary = 50000.0  # SQLAlchemy detecta el cambio automáticamente
        session.commit()
        print(f"  Salario de '{user.name}' actualizado: ${old_salary} → ${user.salary}")

    # Método 2: UPDATE masivo con sentencia SQL
    # Útil para actualizar muchos registros con la misma condición
    stmt = (
        update(User)
        .where(User.age < 30)
        .values(salary=User.salary * 1.10)  # +10% de aumento
    )
    result = session.execute(stmt)
    session.commit()
    print(f"  Aumento de 10% aplicado a {result.rowcount} usuarios menores de 30 años.")


def demo_delete(session):
    """
    Demuestra cómo eliminar registros con ORM.

    Igual que con UPDATE, hay dos métodos según la cantidad de registros.
    """
    print("\n--- DELETE: Eliminar registros ---")

    # Método 1: Eliminar un objeto específico
    user = session.get(User, 2)
    if user:
        name = user.name
        session.delete(user)
        session.commit()
        print(f"  Usuario '{name}' eliminado.")

    # Verificación: el usuario ya no existe
    deleted = session.get(User, 2)
    print(f"  Verificación: usuario ID 2 = {deleted}")  # Debe ser None


def demo_raw_sql(engine):
    """
    Demuestra cómo ejecutar SQL crudo cuando el ORM no es suficiente.

    A veces necesitas SQL muy específico que el ORM no puede expresar fácilmente.
    SQLAlchemy permite mezclar ORM y SQL crudo de forma segura.

    Parámetros:
        engine: objeto Engine de SQLAlchemy
    """
    print("\n--- SQL CRUDO con SQLAlchemy ---")

    # text() envuelve SQL crudo de forma segura
    with engine.connect() as conn:
        # Consulta de estadísticas que sería compleja con ORM
        result = conn.execute(text("""
            SELECT
                COUNT(*) as total,
                AVG(age)    as avg_age,
                AVG(salary) as avg_salary,
                MIN(salary) as min_salary,
                MAX(salary) as max_salary
            FROM users
        """))

        row = result.fetchone()
        if row:
            print(f"  Total usuarios: {row[0]}")
            print(f"  Edad promedio:  {row[1]:.1f} años")
            print(f"  Salario promedio: ${row[2]:,.2f}")
            print(f"  Salario mínimo:   ${row[3]:,.2f}")
            print(f"  Salario máximo:   ${row[4]:,.2f}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal que demuestra SQLAlchemy ORM completo."""

    # Verificar que SQLAlchemy esté instalado antes de continuar
    if not check_sqlalchemy():
        return

    print("=" * 60)
    print("  DEMO: SQLAlchemy ORM — CRUD Completo")
    print("=" * 60)

    db_path = "sqlalchemy_demo.db"

    # Crear engine y tablas
    engine = create_db_engine(db_path)

    # La Session es el objeto central del ORM.
    # Actúa como una "unidad de trabajo": rastrea todos los objetos
    # modificados y los sincroniza con la DB en el commit.
    # Usar 'with Session(engine)' garantiza que se cierre correctamente.
    with Session(engine) as session:

        demo_create(session)
        demo_read(session)
        demo_update(session)
        demo_delete(session)

    # SQL crudo con el engine directamente
    demo_raw_sql(engine)

    # Disposar el engine libera todas las conexiones del pool
    engine.dispose()

    print(f"\nBase de datos: {db_path}")

    # Limpieza del archivo de demo
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Archivo '{db_path}' eliminado (limpieza de demo).")


if __name__ == "__main__":
    main()
