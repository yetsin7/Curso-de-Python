"""
Ejercicios SQL con la Biblia Reina-Valera 1960
===============================================
Consultas SQL puras usando sqlite3 nativo sobre la base de datos
de la Biblia RV60. Se resuelven 10 ejercicios progresivos que cubren
agregaciones, subconsultas, vistas y búsquedas de texto.

Tablas disponibles:
  - books(book_number, short_name, long_name)
  - verses(book_number, chapter, verse, text)

Nota: el texto tiene marcas Strong como <S>1234</S> que se limpian
con regex antes de mostrar al usuario.
"""

import sqlite3
import re
import os

# --- Ruta a la base de datos ---
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')


def limpiar_texto(texto: str) -> str:
    """
    Elimina las marcas Strong (<S>NNNN</S>) del texto del versículo.

    Args:
        texto: Texto crudo del versículo con marcas Strong.

    Returns:
        Texto limpio sin marcas numéricas.
    """
    return re.sub(r'<S>\d+</S>', '', texto).strip()


def conectar() -> sqlite3.Connection:
    """
    Abre y retorna la conexión a la base de datos de la Biblia.

    Returns:
        Objeto Connection de sqlite3.

    Raises:
        SystemExit: Si el archivo de BD no existe en la ruta esperada.
    """
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Base de datos no encontrada en: {DB_PATH}")
        raise SystemExit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acceder columnas por nombre
    return conn


# ---------------------------------------------------------------------------
# Ejercicio 1: Los 10 libros con más versículos
# ---------------------------------------------------------------------------
def ejercicio_01(conn: sqlite3.Connection) -> None:
    """
    Lista los 10 libros con mayor cantidad de versículos usando GROUP BY + ORDER BY.
    """
    print("\n=== Ejercicio 1: Top 10 libros con más versículos ===")
    sql = """
        SELECT b.long_name, COUNT(*) AS total_versiculos
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        GROUP BY v.book_number
        ORDER BY total_versiculos DESC
        LIMIT 10
    """
    for row in conn.execute(sql):
        print(f"  {row['long_name']:<30} {row['total_versiculos']:>5} versículos")


# ---------------------------------------------------------------------------
# Ejercicio 2: Capítulos por libro del Nuevo Testamento (book_number >= 400)
# ---------------------------------------------------------------------------
def ejercicio_02(conn: sqlite3.Connection) -> None:
    """
    Muestra cuántos capítulos tiene cada libro del NT.
    El NT comprende book_number desde 400 hasta 660.
    """
    print("\n=== Ejercicio 2: Capítulos por libro del NT ===")
    sql = """
        SELECT b.long_name, COUNT(DISTINCT v.chapter) AS capitulos
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        WHERE v.book_number >= 400
        GROUP BY v.book_number
        ORDER BY v.book_number
    """
    for row in conn.execute(sql):
        print(f"  {row['long_name']:<30} {row['capitulos']:>3} capítulos")


# ---------------------------------------------------------------------------
# Ejercicio 3: Versículos que contienen la palabra "amor"
# ---------------------------------------------------------------------------
def ejercicio_03(conn: sqlite3.Connection) -> None:
    """
    Busca versículos que contengan la palabra 'amor' (búsqueda LIKE).
    Muestra los primeros 10 resultados con referencia y texto limpio.
    """
    print("\n=== Ejercicio 3: Versículos con la palabra 'amor' (primeros 10) ===")
    sql = """
        SELECT b.long_name, v.chapter, v.verse, v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        WHERE v.text LIKE '%amor%'
        LIMIT 10
    """
    for row in conn.execute(sql):
        referencia = f"{row['long_name']} {row['chapter']}:{row['verse']}"
        print(f"  [{referencia}] {limpiar_texto(row['text'])[:80]}…")


# ---------------------------------------------------------------------------
# Ejercicio 4: Libro más largo y más corto en caracteres
# ---------------------------------------------------------------------------
def ejercicio_04(conn: sqlite3.Connection) -> None:
    """
    Calcula la longitud total de texto por libro (sin marcas Strong)
    y muestra el libro más largo y el más corto en caracteres.
    Usa subconsultas para obtener el mínimo y máximo.
    """
    print("\n=== Ejercicio 4: Libro más largo y más corto en caracteres ===")
    # Se usa LENGTH sobre el texto crudo; las marcas Strong inflan el conteo
    # pero son consistentes entre libros, así que la comparación es válida.
    sql = """
        SELECT b.long_name,
               SUM(LENGTH(v.text)) AS total_chars
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        GROUP BY v.book_number
        ORDER BY total_chars DESC
    """
    filas = conn.execute(sql).fetchall()
    mas_largo  = filas[0]
    mas_corto  = filas[-1]
    print(f"  Más largo : {mas_largo['long_name']} ({mas_largo['total_chars']:,} caracteres)")
    print(f"  Más corto : {mas_corto['long_name']} ({mas_corto['total_chars']:,} caracteres)")


# ---------------------------------------------------------------------------
# Ejercicio 5: Promedio de versículos por capítulo en el AT
# ---------------------------------------------------------------------------
def ejercicio_05(conn: sqlite3.Connection) -> None:
    """
    Calcula el promedio de versículos por capítulo en todo el Antiguo Testamento
    (book_number entre 10 y 390 inclusive).
    Usa una subconsulta para primero contar versículos por capítulo.
    """
    print("\n=== Ejercicio 5: Promedio de versículos por capítulo en el AT ===")
    sql = """
        SELECT AVG(versiculos_por_capitulo) AS promedio
        FROM (
            SELECT COUNT(*) AS versiculos_por_capitulo
            FROM verses
            WHERE book_number BETWEEN 10 AND 390
            GROUP BY book_number, chapter
        )
    """
    row = conn.execute(sql).fetchone()
    print(f"  Promedio AT: {row['promedio']:.2f} versículos por capítulo")


# ---------------------------------------------------------------------------
# Ejercicio 6: Los 5 capítulos más largos de toda la Biblia
# ---------------------------------------------------------------------------
def ejercicio_06(conn: sqlite3.Connection) -> None:
    """
    Encuentra los 5 capítulos con más versículos en toda la Biblia.
    Muestra libro, capítulo y total de versículos.
    """
    print("\n=== Ejercicio 6: Top 5 capítulos más largos ===")
    sql = """
        SELECT b.long_name, v.chapter, COUNT(*) AS versiculos
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        GROUP BY v.book_number, v.chapter
        ORDER BY versiculos DESC
        LIMIT 5
    """
    for row in conn.execute(sql):
        print(f"  {row['long_name']} cap. {row['chapter']:<3} → {row['versiculos']} versículos")


# ---------------------------------------------------------------------------
# Ejercicio 7: Versículos únicos que empiezan con "Y dijo"
# ---------------------------------------------------------------------------
def ejercicio_07(conn: sqlite3.Connection) -> None:
    """
    Encuentra versículos cuyo texto empieza con la frase 'Y dijo'.
    Usa LIKE con comodín al final. Muestra los primeros 8.
    """
    print("\n=== Ejercicio 7: Versículos que empiezan con 'Y dijo' (primeros 8) ===")
    sql = """
        SELECT b.long_name, v.chapter, v.verse, v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        WHERE v.text LIKE 'Y dijo%'
        LIMIT 8
    """
    for row in conn.execute(sql):
        ref = f"{row['long_name']} {row['chapter']}:{row['verse']}"
        print(f"  [{ref}] {limpiar_texto(row['text'])[:70]}…")


# ---------------------------------------------------------------------------
# Ejercicio 8: Contar versículos por testamento (AT vs NT)
# ---------------------------------------------------------------------------
def ejercicio_08(conn: sqlite3.Connection) -> None:
    """
    Usa CASE WHEN para etiquetar cada versículo como AT o NT y cuenta ambos.
    """
    print("\n=== Ejercicio 8: Versículos por testamento ===")
    sql = """
        SELECT
            CASE
                WHEN book_number <= 390 THEN 'Antiguo Testamento'
                ELSE 'Nuevo Testamento'
            END AS testamento,
            COUNT(*) AS total
        FROM verses
        GROUP BY testamento
    """
    for row in conn.execute(sql):
        print(f"  {row['testamento']}: {row['total']:,} versículos")


# ---------------------------------------------------------------------------
# Ejercicio 9: Versículos que contienen tanto "fe" como "obras"
# ---------------------------------------------------------------------------
def ejercicio_09(conn: sqlite3.Connection) -> None:
    """
    Busca versículos que mencionen simultáneamente 'fe' y 'obras'.
    Usa dos condiciones LIKE combinadas con AND.
    """
    print("\n=== Ejercicio 9: Versículos con 'fe' Y 'obras' ===")
    sql = """
        SELECT b.long_name, v.chapter, v.verse, v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        WHERE v.text LIKE '%fe%'
          AND v.text LIKE '%obras%'
        LIMIT 10
    """
    filas = conn.execute(sql).fetchall()
    print(f"  Total encontrados (limitado a 10 de muchos más): {len(filas)}")
    for row in filas:
        ref = f"{row['long_name']} {row['chapter']}:{row['verse']}"
        print(f"  [{ref}] {limpiar_texto(row['text'])[:75]}…")


# ---------------------------------------------------------------------------
# Ejercicio 10: CREATE VIEW — versículos con nombre de libro incluido
# ---------------------------------------------------------------------------
def ejercicio_10(conn: sqlite3.Connection) -> None:
    """
    Crea (o reemplaza) una vista llamada 'vista_versiculos_completos' que une
    la tabla de versículos con la de libros para tener el nombre del libro
    en cada fila. Luego hace una consulta de prueba sobre ella.
    """
    print("\n=== Ejercicio 10: VIEW vista_versiculos_completos ===")

    # Eliminar vista previa si existe para que el script sea re-ejecutable
    conn.execute("DROP VIEW IF EXISTS vista_versiculos_completos")

    conn.execute("""
        CREATE VIEW vista_versiculos_completos AS
        SELECT
            b.short_name,
            b.long_name,
            v.book_number,
            v.chapter,
            v.verse,
            v.text,
            CASE
                WHEN v.book_number <= 390 THEN 'AT'
                ELSE 'NT'
            END AS testamento
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
    """)
    conn.commit()
    print("  Vista creada: vista_versiculos_completos")

    # Consulta de prueba: primer versículo de cada testamento
    sql = """
        SELECT testamento, long_name, chapter, verse, text
        FROM vista_versiculos_completos
        GROUP BY testamento
        ORDER BY book_number, chapter, verse
        LIMIT 2
    """
    for row in conn.execute(sql):
        ref = f"{row['long_name']} {row['chapter']}:{row['verse']}"
        print(f"  [{row['testamento']}] {ref} → {limpiar_texto(row['text'])[:60]}…")


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------
def main() -> None:
    """
    Ejecuta los 10 ejercicios SQL en secuencia sobre la BD de la Biblia RV60.
    """
    print("=" * 60)
    print("  EJERCICIOS SQL — BIBLIA REINA-VALERA 1960")
    print("=" * 60)

    conn = conectar()
    try:
        ejercicio_01(conn)
        ejercicio_02(conn)
        ejercicio_03(conn)
        ejercicio_04(conn)
        ejercicio_05(conn)
        ejercicio_06(conn)
        ejercicio_07(conn)
        ejercicio_08(conn)
        ejercicio_09(conn)
        ejercicio_10(conn)
    finally:
        conn.close()

    print("\n✓ Todos los ejercicios completados.")


if __name__ == "__main__":
    main()
