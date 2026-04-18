"""
Exploración inicial de la base de datos de la Biblia RV60.
Aprende a conectar a SQLite, inspeccionar el esquema y obtener estadísticas.
Ejecutar: python 00_explorar_bd.py
"""

import sqlite3
import os
import re

# --- Ruta relativa a la BD desde este mismo archivo ---
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')

# Separador visual reutilizable
LINEA = '=' * 60


def conectar():
    """
    Abre y devuelve una conexión a la base de datos SQLite.
    Lanza FileNotFoundError si la BD no existe en la ruta esperada.
    """
    ruta = os.path.abspath(DB_PATH)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f'No se encontró la base de datos en:\n  {ruta}')
    return sqlite3.connect(ruta)


def limpiar_strong(texto):
    """
    Elimina las marcas Strong del texto del versículo.
    Ejemplo: 'principio<S>7225</S>' → 'principio'
    """
    return re.sub(r'<S>\d+</S>', '', texto).strip()


def mostrar_metadatos(cursor):
    """
    Muestra todos los registros de la tabla info (metadatos del módulo).
    """
    print(f'\n{LINEA}')
    print('  METADATOS DE LA BASE DE DATOS')
    print(LINEA)
    filas = cursor.execute('SELECT name, value FROM info').fetchall()
    for nombre, valor in filas:
        # Truncar valores muy largos para que quepan en consola
        valor_corto = valor[:80] + '...' if len(valor) > 80 else valor
        print(f'  {nombre:<25} {valor_corto}')


def mostrar_libros(cursor):
    """
    Lista los 66 libros con su número, abreviatura y nombre completo.
    """
    print(f'\n{LINEA}')
    print('  LIBROS DE LA BIBLIA (66 en total)')
    print(LINEA)
    # Las columnas son: book_color, book_number, short_name, long_name
    libros = cursor.execute(
        'SELECT book_number, short_name, long_name FROM books ORDER BY book_number'
    ).fetchall()
    for num, abrev, nombre in libros:
        testamento = 'AT' if num <= 390 else 'NT'
        print(f'  [{testamento}] {num:>4}  {abrev:<4}  {nombre}')


def mostrar_estadisticas_generales(cursor):
    """
    Muestra conteos globales: libros AT/NT, versículos totales,
    libro con más y menos versículos, capítulos totales.
    """
    print(f'\n{LINEA}')
    print('  ESTADÍSTICAS GENERALES')
    print(LINEA)

    # Conteos básicos
    total_libros = cursor.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    at_libros = cursor.execute(
        'SELECT COUNT(*) FROM books WHERE book_number <= 390'
    ).fetchone()[0]
    nt_libros = total_libros - at_libros

    total_versiculos = cursor.execute('SELECT COUNT(*) FROM verses').fetchone()[0]
    at_versiculos = cursor.execute(
        'SELECT COUNT(*) FROM verses WHERE book_number <= 390'
    ).fetchone()[0]
    nt_versiculos = total_versiculos - at_versiculos

    total_capitulos = cursor.execute(
        'SELECT COUNT(DISTINCT book_number || chapter) FROM verses'
    ).fetchone()[0]

    print(f'  Libros totales         : {total_libros}')
    print(f'  Antiguo Testamento     : {at_libros} libros  ({at_versiculos:,} versículos)')
    print(f'  Nuevo Testamento       : {nt_libros} libros  ({nt_versiculos:,} versículos)')
    print(f'  Versículos totales     : {total_versiculos:,}')
    print(f'  Capítulos totales      : {total_capitulos:,}')


def mostrar_versiculos_por_libro(cursor):
    """
    Muestra una tabla con capítulos y versículos por cada libro,
    ordenada de mayor a menor número de versículos.
    """
    print(f'\n{LINEA}')
    print('  VERSÍCULOS Y CAPÍTULOS POR LIBRO (top 15 y bottom 5)')
    print(LINEA)

    datos = cursor.execute('''
        SELECT b.long_name,
               COUNT(DISTINCT v.chapter)  AS capitulos,
               COUNT(v.verse)             AS versiculos
        FROM books b
        JOIN verses v ON b.book_number = v.book_number
        GROUP BY b.book_number
        ORDER BY versiculos DESC
    ''').fetchall()

    print(f'  {"Libro":<22} {"Caps":>5} {"Vers":>6}')
    print('  ' + '-' * 36)

    # Muestra top 15
    for nombre, caps, vers in datos[:15]:
        print(f'  {nombre:<22} {caps:>5} {vers:>6}')
    print('  ...')
    # Muestra los 5 libros más cortos
    for nombre, caps, vers in datos[-5:]:
        print(f'  {nombre:<22} {caps:>5} {vers:>6}')


def mostrar_versiculos_extremos(cursor):
    """
    Muestra los 5 versículos más largos y los 5 más cortos
    de toda la Biblia (por longitud de texto limpio).
    """
    print(f'\n{LINEA}')
    print('  VERSÍCULOS MÁS LARGOS Y MÁS CORTOS')
    print(LINEA)

    filas = cursor.execute('''
        SELECT b.short_name, v.chapter, v.verse, v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
    ''').fetchall()

    # Calcula longitud de texto limpio para cada versículo
    medidos = []
    for abrev, cap, ver, texto in filas:
        limpio = limpiar_strong(texto)
        medidos.append((len(limpio), abrev, cap, ver, limpio))

    medidos.sort(key=lambda x: x[0])

    print('\n  --- 5 MÁS CORTOS ---')
    for longitud, abrev, cap, ver, texto in medidos[:5]:
        print(f'  {abrev} {cap}:{ver} ({longitud} chars) → {texto}')

    print('\n  --- 5 MÁS LARGOS ---')
    for longitud, abrev, cap, ver, texto in medidos[-5:]:
        # Trunca para no desbordar la consola
        preview = texto[:100] + '...' if len(texto) > 100 else texto
        print(f'  {abrev} {cap}:{ver} ({longitud} chars) → {preview}')


def main():
    """
    Punto de entrada: conecta a la BD y ejecuta todas las exploraciones.
    """
    print(f'\n{"#" * 60}')
    print('  EXPLORACIÓN DE LA BIBLIA REINA-VALERA 1960')
    print(f'{"#" * 60}')
    print(f'  BD: {os.path.abspath(DB_PATH)}')

    try:
        conn = conectar()
        cur = conn.cursor()

        mostrar_metadatos(cur)
        mostrar_libros(cur)
        mostrar_estadisticas_generales(cur)
        mostrar_versiculos_por_libro(cur)
        mostrar_versiculos_extremos(cur)

        conn.close()
        print(f'\n{LINEA}')
        print('  Exploración completada.')
        print(LINEA)

    except FileNotFoundError as e:
        print(f'\n[ERROR] {e}')
    except sqlite3.Error as e:
        print(f'\n[ERROR SQLite] {e}')


if __name__ == '__main__':
    main()
