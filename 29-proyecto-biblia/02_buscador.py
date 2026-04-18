"""
Buscador de texto en la Biblia RV60.
Aprende a usar LIKE en SQL, búsqueda case-insensitive y estadísticas de resultados.
Ejecutar: python 02_buscador.py
"""

import sqlite3
import os
import re

# --- Ruta relativa a la BD ---
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')

LINEA = '-' * 60
MAX_DEFAULT = 20


def conectar():
    """
    Abre y devuelve la conexión SQLite a la Biblia RV60.
    """
    ruta = os.path.abspath(DB_PATH)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f'No se encontró la BD en: {ruta}')
    conn = sqlite3.connect(ruta)
    # Activa el modo de comparación case-insensitive para caracteres ASCII
    conn.execute("PRAGMA case_sensitive_like = OFF")
    return conn


def limpiar_texto(texto):
    """
    Elimina marcas Strong (<S>NNNN</S>) y espacios dobles del texto.
    """
    limpio = re.sub(r'<S>\d+</S>', '', texto)
    return re.sub(r' {2,}', ' ', limpio).strip()


def buscar_texto(conn, query, limite=MAX_DEFAULT):
    """
    Busca versículos cuyo texto contenga la cadena 'query' usando LIKE.
    La búsqueda es insensible a mayúsculas (funciona bien para ASCII/español básico).

    Devuelve una lista de dicts: libro, abrev, capitulo, versiculo, texto, referencia.

    Parámetros:
        conn   -- conexión SQLite activa
        query  -- texto a buscar
        limite -- máximo de resultados a devolver
    """
    patron = f'%{query}%'
    cur = conn.cursor()
    filas = cur.execute('''
        SELECT b.long_name, b.short_name, v.book_number, v.chapter, v.verse, v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        WHERE v.text LIKE ?
        ORDER BY v.book_number, v.chapter, v.verse
        LIMIT ?
    ''', (patron, limite)).fetchall()

    resultados = []
    for nombre, abrev, bnum, cap, ver, texto in filas:
        resultados.append({
            'libro':      nombre,
            'abrev':      abrev,
            'book_number': bnum,
            'capitulo':   cap,
            'versiculo':  ver,
            'texto':      limpiar_texto(texto),
            'referencia': f'{abrev} {cap}:{ver}'
        })
    return resultados


def buscar_por_palabra(conn, palabra, limite=MAX_DEFAULT):
    """
    Busca una palabra completa en el texto bíblico.
    Usa espacios y puntuación como delimitadores para mayor precisión.

    Retorna lista de dicts igual que buscar_texto().
    """
    # SQLite no tiene word boundary en LIKE, entonces buscamos variantes comunes
    variantes = [
        f' {palabra} ', f' {palabra},', f' {palabra}.', f' {palabra};',
        f' {palabra}:', f' {palabra}!', f' {palabra}?',
        f'{palabra} ',  # inicio de texto
    ]
    cur = conn.cursor()
    resultados = []
    vistos = set()

    for variante in variantes:
        patron = f'%{variante}%'
        filas = cur.execute('''
            SELECT b.long_name, b.short_name, v.book_number, v.chapter, v.verse, v.text
            FROM verses v
            JOIN books b ON v.book_number = b.book_number
            WHERE v.text LIKE ?
            ORDER BY v.book_number, v.chapter, v.verse
        ''', (patron,)).fetchall()

        for nombre, abrev, bnum, cap, ver, texto in filas:
            clave = (bnum, cap, ver)
            if clave not in vistos:
                vistos.add(clave)
                resultados.append({
                    'libro':      nombre,
                    'abrev':      abrev,
                    'book_number': bnum,
                    'capitulo':   cap,
                    'versiculo':  ver,
                    'texto':      limpiar_texto(texto),
                    'referencia': f'{abrev} {cap}:{ver}'
                })

    # Ordena por posición bíblica
    resultados.sort(key=lambda x: (x['book_number'], x['capitulo'], x['versiculo']))
    return resultados[:limite]


def referencias_cruzadas(conn, texto_query, limite=MAX_DEFAULT):
    """
    Busca versículos que contengan TODAS las palabras del texto_query.
    Útil para búsquedas más precisas con múltiples términos.

    Parámetros:
        conn        -- conexión SQLite activa
        texto_query -- cadena con varias palabras, ej: "amor eterno"
        limite      -- máximo de resultados
    """
    palabras = [p.strip() for p in texto_query.split() if len(p.strip()) > 2]
    if not palabras:
        return []

    # Construye una cláusula WHERE con AND LIKE para cada palabra
    condiciones = ' AND '.join(['v.text LIKE ?' for _ in palabras])
    patrones = [f'%{p}%' for p in palabras]

    cur = conn.cursor()
    filas = cur.execute(f'''
        SELECT b.long_name, b.short_name, v.book_number, v.chapter, v.verse, v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        WHERE {condiciones}
        ORDER BY v.book_number, v.chapter, v.verse
        LIMIT ?
    ''', patrones + [limite]).fetchall()

    resultados = []
    for nombre, abrev, bnum, cap, ver, texto in filas:
        resultados.append({
            'libro':      nombre,
            'abrev':      abrev,
            'book_number': bnum,
            'capitulo':   cap,
            'versiculo':  ver,
            'texto':      limpiar_texto(texto),
            'referencia': f'{abrev} {cap}:{ver}'
        })
    return resultados


def estadisticas_busqueda(resultados, query):
    """
    Imprime un resumen estadístico de los resultados de una búsqueda:
    total encontrado, libros involucrados, capítulos involucrados.

    Parámetros:
        resultados -- lista de dicts devuelta por las funciones de búsqueda
        query      -- texto original buscado (para mostrar en el encabezado)
    """
    libros = set(r['libro'] for r in resultados)
    caps   = set((r['book_number'], r['capitulo']) for r in resultados)

    print(f'\n  Búsqueda: "{query}"')
    print(f'  Resultados encontrados : {len(resultados)}')
    print(f'  Libros involucrados    : {len(libros)}')
    print(f'  Capítulos involucrados : {len(caps)}')
    if libros:
        print(f'  Libros: {", ".join(sorted(libros))}')


def imprimir_resultados(resultados, max_mostrar=20):
    """
    Imprime los versículos encontrados con el formato:
    Libro Capítulo:Versículo → texto

    Parámetros:
        resultados  -- lista de dicts de búsqueda
        max_mostrar -- cuántos resultados imprimir (evita inundar la consola)
    """
    if not resultados:
        print('\n  [Sin resultados]')
        return

    print()
    for r in resultados[:max_mostrar]:
        # Referencia alineada para mayor legibilidad
        ref = r['referencia'].ljust(14)
        print(f'  {ref} → {r["texto"]}')

    if len(resultados) > max_mostrar:
        print(f'\n  ... y {len(resultados) - max_mostrar} más (usa limite= para ver todos)')


def menu_busqueda(conn):
    """
    Menú interactivo de búsqueda con tres modos:
    1. Búsqueda por frase (LIKE simple)
    2. Búsqueda por palabra exacta
    3. Referencias cruzadas (todas las palabras presentes)
    """
    print(f'\n{"=" * 60}')
    print('  BUSCADOR BÍBLICO INTERACTIVO')
    print('  Escribe "salir" para terminar.')
    print('=' * 60)

    while True:
        print('\n  Tipo de búsqueda:')
        print('  1. Por frase o fragmento')
        print('  2. Por palabra (más precisa)')
        print('  3. Referencias cruzadas (varias palabras)')
        print('  0. Salir')

        opcion = input('\n  Elige: ').strip()

        if opcion == '0' or opcion.lower() == 'salir':
            break

        elif opcion == '1':
            query = input('  Frase a buscar: ').strip()
            if not query:
                continue
            resultados = buscar_texto(conn, query, limite=50)
            estadisticas_busqueda(resultados, query)
            imprimir_resultados(resultados)

        elif opcion == '2':
            palabra = input('  Palabra a buscar: ').strip()
            if not palabra:
                continue
            resultados = buscar_por_palabra(conn, palabra, limite=50)
            estadisticas_busqueda(resultados, palabra)
            imprimir_resultados(resultados)

        elif opcion == '3':
            query = input('  Palabras (separadas por espacio): ').strip()
            if not query:
                continue
            resultados = referencias_cruzadas(conn, query, limite=50)
            estadisticas_busqueda(resultados, query)
            imprimir_resultados(resultados)

        else:
            print('  [!] Opción no válida.')


def demo_busquedas(conn):
    """
    Ejecuta búsquedas de ejemplo para demostrar las tres funciones.
    """
    print(f'\n{"=" * 60}')
    print('  DEMOSTRACIONES DE BÚSQUEDA')
    print('=' * 60)

    print('\n--- Frase: "Dios es amor" ---')
    r = buscar_texto(conn, 'Dios es amor', limite=10)
    estadisticas_busqueda(r, 'Dios es amor')
    imprimir_resultados(r, max_mostrar=5)

    print('\n--- Palabra: "misericordia" ---')
    r = buscar_por_palabra(conn, 'misericordia', limite=10)
    estadisticas_busqueda(r, 'misericordia')
    imprimir_resultados(r, max_mostrar=5)

    print('\n--- Referencias cruzadas: "luz mundo" ---')
    r = referencias_cruzadas(conn, 'luz mundo', limite=10)
    estadisticas_busqueda(r, 'luz mundo')
    imprimir_resultados(r, max_mostrar=5)


def main():
    """
    Punto de entrada: ejecuta demos y abre el menú interactivo.
    """
    try:
        conn = conectar()
        demo_busquedas(conn)
        menu_busqueda(conn)
        conn.close()
    except FileNotFoundError as e:
        print(f'\n[ERROR] {e}')
    except sqlite3.Error as e:
        print(f'\n[ERROR SQLite] {e}')


if __name__ == '__main__':
    main()
