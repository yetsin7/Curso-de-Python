"""
Lector básico de la Biblia RV60.
Aprende a consultar versículos, capítulos y libros desde SQLite con funciones limpias.
Ejecutar: python 01_lector_basico.py
"""

import sqlite3
import os
import re

# --- Ruta relativa a la BD ---
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')

LINEA = '-' * 60


def conectar():
    """
    Abre y devuelve una conexión SQLite a la BD de la Biblia.
    Lanza FileNotFoundError si el archivo no existe.
    """
    ruta = os.path.abspath(DB_PATH)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f'No se encontró la BD en: {ruta}')
    return sqlite3.connect(ruta)


def limpiar_texto(texto):
    """
    Elimina las marcas de números Strong del texto bíblico.
    Entrada : 'En el principio<S>7225</S> creó<S>1254</S> Dios<S>430</S>'
    Salida  : 'En el principio creó Dios'
    """
    limpio = re.sub(r'<S>\d+</S>', '', texto)
    # Elimina espacios múltiples que quedan tras quitar las marcas
    limpio = re.sub(r' {2,}', ' ', limpio)
    return limpio.strip()


def obtener_versiculo(conn, libro_num, capitulo, versiculo):
    """
    Devuelve un diccionario con los datos de un versículo específico.
    Retorna None si la referencia no existe en la BD.

    Parámetros:
        conn      -- conexión SQLite activa
        libro_num -- book_number del libro (ej: 430 para Juan)
        capitulo  -- número de capítulo
        versiculo -- número de versículo
    """
    cur = conn.cursor()
    fila = cur.execute('''
        SELECT b.long_name, b.short_name, v.chapter, v.verse, v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        WHERE v.book_number = ? AND v.chapter = ? AND v.verse = ?
    ''', (libro_num, capitulo, versiculo)).fetchone()

    if not fila:
        return None

    return {
        'libro':     fila[0],
        'abrev':     fila[1],
        'capitulo':  fila[2],
        'versiculo': fila[3],
        'texto':     limpiar_texto(fila[4]),
        'referencia': f'{fila[1]} {fila[2]}:{fila[3]}'
    }


def obtener_capitulo(conn, libro_num, capitulo):
    """
    Devuelve una lista de versículos limpios de un capítulo completo.
    Cada elemento es un dict con: versiculo, texto, referencia.

    Parámetros:
        conn      -- conexión SQLite activa
        libro_num -- book_number del libro
        capitulo  -- número de capítulo
    """
    cur = conn.cursor()
    filas = cur.execute('''
        SELECT b.long_name, b.short_name, v.verse, v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        WHERE v.book_number = ? AND v.chapter = ?
        ORDER BY v.verse
    ''', (libro_num, capitulo)).fetchall()

    resultado = []
    for nombre, abrev, ver, texto in filas:
        resultado.append({
            'libro':     nombre,
            'abrev':     abrev,
            'capitulo':  capitulo,
            'versiculo': ver,
            'texto':     limpiar_texto(texto),
            'referencia': f'{abrev} {capitulo}:{ver}'
        })
    return resultado


def obtener_libro_info(conn, identificador):
    """
    Busca un libro por su book_number (int) o por su nombre/abreviatura (str).
    Devuelve un dict con: book_number, short_name, long_name, book_color.
    Retorna None si no se encuentra.

    Parámetros:
        conn          -- conexión SQLite activa
        identificador -- int (book_number) o str (nombre completo o abreviatura)
    """
    cur = conn.cursor()

    if isinstance(identificador, int):
        fila = cur.execute(
            'SELECT book_number, short_name, long_name, book_color FROM books WHERE book_number = ?',
            (identificador,)
        ).fetchone()
    else:
        # Búsqueda insensible a mayúsculas por nombre o abreviatura
        termino = identificador.strip()
        fila = cur.execute(
            '''SELECT book_number, short_name, long_name, book_color
               FROM books
               WHERE LOWER(short_name) = LOWER(?)
                  OR LOWER(long_name)  = LOWER(?)''',
            (termino, termino)
        ).fetchone()

    if not fila:
        return None
    return {
        'book_number': fila[0],
        'short_name':  fila[1],
        'long_name':   fila[2],
        'book_color':  fila[3]
    }


def imprimir_versiculo(v):
    """
    Imprime un versículo con formato legible en consola.
    Recibe el dict devuelto por obtener_versiculo().
    """
    if v:
        print(f'\n  {v["referencia"]}')
        print(f'  {v["texto"]}')
    else:
        print('  [No encontrado]')


def imprimir_capitulo(versiculos):
    """
    Imprime un capítulo completo con todos sus versículos numerados.
    Recibe la lista devuelta por obtener_capitulo().
    """
    if not versiculos:
        print('  [Capítulo no encontrado]')
        return
    info = versiculos[0]
    print(f'\n  {info["libro"]} — Capítulo {info["capitulo"]}')
    print(f'  {LINEA}')
    for v in versiculos:
        print(f'  {v["versiculo"]:>3}. {v["texto"]}')


def demo_ejemplos(conn):
    """
    Muestra ejemplos predefinidos: Juan 3:16, Salmos 23 y Génesis 1:1-10.
    """
    print(f'\n{"=" * 60}')
    print('  EJEMPLOS DE USO')
    print('=' * 60)

    # Juan 3:16
    print('\n>>> Juan 3:16')
    libro = obtener_libro_info(conn, 'Jn')
    if libro:
        v = obtener_versiculo(conn, libro['book_number'], 3, 16)
        imprimir_versiculo(v)

    # Salmos 23 completo
    print('\n>>> Salmos 23 (completo)')
    libro = obtener_libro_info(conn, 'Sal')
    if libro:
        cap = obtener_capitulo(conn, libro['book_number'], 23)
        imprimir_capitulo(cap)

    # Génesis 1:1-10
    print('\n>>> Génesis 1:1-10')
    libro = obtener_libro_info(conn, 'Génesis')
    if libro:
        for num_ver in range(1, 11):
            v = obtener_versiculo(conn, libro['book_number'], 1, num_ver)
            if v:
                print(f'  {v["versiculo"]:>3}. {v["texto"]}')


def menu_interactivo(conn):
    """
    Menú de consola que permite al usuario leer versículos y capítulos
    ingresando el nombre del libro, capítulo y versículo.
    """
    print(f'\n{"=" * 60}')
    print('  LECTOR BÍBLICO INTERACTIVO')
    print('  Escribe "salir" en cualquier momento para terminar.')
    print('=' * 60)

    while True:
        print('\n  Opciones:')
        print('  1. Leer un versículo')
        print('  2. Leer un capítulo completo')
        print('  3. Ver ejemplos')
        print('  0. Salir')

        opcion = input('\n  Elige una opción: ').strip()

        if opcion == '0' or opcion.lower() == 'salir':
            print('\n  ¡Hasta luego!\n')
            break

        elif opcion == '1':
            nombre = input('  Nombre del libro (ej: Juan, Gn, Salmos): ').strip()
            if nombre.lower() == 'salir':
                break
            libro = obtener_libro_info(conn, nombre)
            if not libro:
                print(f'  [!] Libro "{nombre}" no encontrado.')
                continue
            try:
                cap = int(input(f'  Capítulo de {libro["long_name"]}: '))
                ver = int(input(f'  Versículo: '))
            except ValueError:
                print('  [!] Ingresa un número válido.')
                continue
            v = obtener_versiculo(conn, libro['book_number'], cap, ver)
            imprimir_versiculo(v)

        elif opcion == '2':
            nombre = input('  Nombre del libro (ej: Juan, Sal, Génesis): ').strip()
            if nombre.lower() == 'salir':
                break
            libro = obtener_libro_info(conn, nombre)
            if not libro:
                print(f'  [!] Libro "{nombre}" no encontrado.')
                continue
            try:
                cap = int(input(f'  Capítulo de {libro["long_name"]}: '))
            except ValueError:
                print('  [!] Ingresa un número válido.')
                continue
            versiculos = obtener_capitulo(conn, libro['book_number'], cap)
            imprimir_capitulo(versiculos)

        elif opcion == '3':
            demo_ejemplos(conn)

        else:
            print('  [!] Opción no válida.')


def main():
    """
    Punto de entrada: muestra ejemplos y luego abre el menú interactivo.
    """
    try:
        conn = conectar()
        demo_ejemplos(conn)
        menu_interactivo(conn)
        conn.close()
    except FileNotFoundError as e:
        print(f'\n[ERROR] {e}')
    except sqlite3.Error as e:
        print(f'\n[ERROR SQLite] {e}')


if __name__ == '__main__':
    main()
