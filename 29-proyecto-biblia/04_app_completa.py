"""
App de consola completa para leer, buscar y gestionar la Biblia RV60.
Integra los módulos anteriores: lectura, búsqueda y estadísticas.
Incluye favoritos en JSON, versículo aleatorio y plan de lectura.
Ejecutar: python 04_app_completa.py
"""

import sqlite3
import os
import re
import json
import random
import sys

# --- Ruta relativa a la BD ---
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')

# Archivo JSON donde se guardan los versículos favoritos del usuario
FAVORITOS_PATH = os.path.join(os.path.dirname(__file__), 'favoritos.json')

LINEA = '=' * 60


# ──────────────────────────────────────────────────────────────
#  UTILIDADES BASE
# ──────────────────────────────────────────────────────────────

def conectar():
    """
    Abre y devuelve la conexión SQLite.
    Lanza FileNotFoundError si la BD no existe.
    """
    ruta = os.path.abspath(DB_PATH)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f'No se encontró la BD en: {ruta}')
    conn = sqlite3.connect(ruta)
    conn.execute("PRAGMA case_sensitive_like = OFF")
    return conn


def limpiar_texto(texto):
    """
    Elimina marcas Strong y normaliza espacios en el texto bíblico.
    """
    limpio = re.sub(r'<S>\d+</S>', '', texto)
    return re.sub(r' {2,}', ' ', limpio).strip()


# ──────────────────────────────────────────────────────────────
#  LECTURA
# ──────────────────────────────────────────────────────────────

def buscar_libro(conn, nombre):
    """
    Busca un libro por nombre completo, abreviatura o book_number.
    Devuelve dict con book_number, short_name, long_name o None.
    """
    cur = conn.cursor()
    if isinstance(nombre, int) or (isinstance(nombre, str) and nombre.isdigit()):
        fila = cur.execute(
            'SELECT book_number, short_name, long_name FROM books WHERE book_number = ?',
            (int(nombre),)
        ).fetchone()
    else:
        fila = cur.execute(
            '''SELECT book_number, short_name, long_name FROM books
               WHERE LOWER(short_name) = LOWER(?) OR LOWER(long_name) = LOWER(?)''',
            (nombre, nombre)
        ).fetchone()
    if not fila:
        return None
    return {'book_number': fila[0], 'short_name': fila[1], 'long_name': fila[2]}


def obtener_versiculo(conn, book_number, cap, ver):
    """
    Devuelve un dict con los datos de un versículo específico, o None si no existe.
    """
    cur = conn.cursor()
    fila = cur.execute(
        '''SELECT b.long_name, b.short_name, v.chapter, v.verse, v.text
           FROM verses v JOIN books b ON v.book_number = b.book_number
           WHERE v.book_number=? AND v.chapter=? AND v.verse=?''',
        (book_number, cap, ver)
    ).fetchone()
    if not fila:
        return None
    return {
        'libro': fila[0], 'abrev': fila[1],
        'capitulo': fila[2], 'versiculo': fila[3],
        'texto': limpiar_texto(fila[4]),
        'referencia': f'{fila[1]} {fila[2]}:{fila[3]}'
    }


def obtener_capitulo(conn, book_number, cap):
    """
    Devuelve lista de versículos de un capítulo completo (texto limpio).
    """
    cur = conn.cursor()
    filas = cur.execute(
        '''SELECT b.long_name, b.short_name, v.verse, v.text
           FROM verses v JOIN books b ON v.book_number = b.book_number
           WHERE v.book_number=? AND v.chapter=? ORDER BY v.verse''',
        (book_number, cap)
    ).fetchall()
    return [
        {'libro': f[0], 'abrev': f[1], 'capitulo': cap,
         'versiculo': f[2], 'texto': limpiar_texto(f[3]),
         'referencia': f'{f[1]} {cap}:{f[2]}'}
        for f in filas
    ]


def parsear_referencia(conn, ref_texto):
    """
    Parsea una referencia como 'Juan 3:16' o 'Jn 3:16'.
    Devuelve (libro_dict, capitulo, versiculo) o None si no se puede parsear.

    Parámetros:
        ref_texto -- cadena como 'Juan 3:16' o 'Gn 1:1'
    """
    patron = r'^(.+?)\s+(\d+):(\d+)$'
    match  = re.match(patron, ref_texto.strip())
    if not match:
        return None
    nombre_libro = match.group(1)
    cap  = int(match.group(2))
    ver  = int(match.group(3))
    libro = buscar_libro(conn, nombre_libro)
    if not libro:
        return None
    return (libro, cap, ver)


# ──────────────────────────────────────────────────────────────
#  BÚSQUEDA
# ──────────────────────────────────────────────────────────────

def buscar_texto(conn, query, limite=20):
    """
    Busca versículos que contengan la frase 'query' usando LIKE.
    Devuelve lista de dicts con referencia y texto limpio.
    """
    cur = conn.cursor()
    filas = cur.execute(
        '''SELECT b.long_name, b.short_name, v.book_number, v.chapter, v.verse, v.text
           FROM verses v JOIN books b ON v.book_number = b.book_number
           WHERE v.text LIKE ?
           ORDER BY v.book_number, v.chapter, v.verse LIMIT ?''',
        (f'%{query}%', limite)
    ).fetchall()
    return [
        {'libro': f[0], 'abrev': f[1], 'book_number': f[2],
         'capitulo': f[3], 'versiculo': f[4],
         'texto': limpiar_texto(f[5]),
         'referencia': f'{f[1]} {f[3]}:{f[4]}'}
        for f in filas
    ]


# ──────────────────────────────────────────────────────────────
#  VERSÍCULO ALEATORIO
# ──────────────────────────────────────────────────────────────

def versiculo_aleatorio(conn):
    """
    Devuelve un versículo elegido al azar de toda la Biblia.
    Usa random.choice sobre la lista de IDs de la tabla verses.
    """
    cur = conn.cursor()
    ids = cur.execute(
        'SELECT book_number, chapter, verse FROM verses'
    ).fetchall()
    bnum, cap, ver = random.choice(ids)
    return obtener_versiculo(conn, bnum, cap, ver)


# ──────────────────────────────────────────────────────────────
#  LISTA DE LIBROS
# ──────────────────────────────────────────────────────────────

def listar_libros(conn):
    """
    Imprime todos los libros de la Biblia organizados por testamento.
    """
    cur = conn.cursor()
    libros = cur.execute(
        'SELECT book_number, short_name, long_name FROM books ORDER BY book_number'
    ).fetchall()

    print(f'\n{LINEA}')
    print('  ANTIGUO TESTAMENTO')
    print(LINEA)
    for num, abrev, nombre in libros:
        if num <= 390:
            print(f'  {num:>4}  {abrev:<5}  {nombre}')

    print(f'\n{LINEA}')
    print('  NUEVO TESTAMENTO')
    print(LINEA)
    for num, abrev, nombre in libros:
        if num >= 400:
            print(f'  {num:>4}  {abrev:<5}  {nombre}')


# ──────────────────────────────────────────────────────────────
#  FAVORITOS
# ──────────────────────────────────────────────────────────────

def cargar_favoritos():
    """
    Carga el archivo JSON de favoritos. Si no existe, devuelve lista vacía.
    """
    if not os.path.exists(FAVORITOS_PATH):
        return []
    try:
        with open(FAVORITOS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def guardar_favoritos(favoritos):
    """
    Guarda la lista de favoritos en el archivo JSON local.
    Parámetros:
        favoritos -- lista de dicts de versículos
    """
    with open(FAVORITOS_PATH, 'w', encoding='utf-8') as f:
        json.dump(favoritos, f, ensure_ascii=False, indent=2)


def agregar_favorito(conn, ref_texto):
    """
    Parsea una referencia bíblica y la agrega a los favoritos.
    Muestra un mensaje de confirmación o de error.
    """
    resultado = parsear_referencia(conn, ref_texto)
    if not resultado:
        print(f'  [!] No se pudo parsear la referencia: "{ref_texto}"')
        return
    libro, cap, ver = resultado
    v = obtener_versiculo(conn, libro['book_number'], cap, ver)
    if not v:
        print('  [!] Versículo no encontrado.')
        return
    favs = cargar_favoritos()
    if any(f['referencia'] == v['referencia'] for f in favs):
        print(f'  [!] "{v["referencia"]}" ya está en favoritos.')
        return
    favs.append(v)
    guardar_favoritos(favs)
    print(f'  Guardado: {v["referencia"]} — {v["texto"][:60]}...')


def ver_favoritos():
    """
    Lista todos los versículos guardados como favoritos.
    """
    favs = cargar_favoritos()
    if not favs:
        print('\n  No tienes favoritos guardados aún.')
        return
    print(f'\n{LINEA}')
    print(f'  MIS FAVORITOS ({len(favs)} versículos)')
    print(LINEA)
    for i, v in enumerate(favs, 1):
        print(f'  {i:>2}. {v["referencia"]:<14} {v["texto"][:70]}')


# ──────────────────────────────────────────────────────────────
#  PLAN DE LECTURA
# ──────────────────────────────────────────────────────────────

def plan_de_lectura(conn, dias):
    """
    Divide los 1,189 capítulos de la Biblia en porciones diarias para N días.
    Muestra las primeras 10 porciones y la última.

    Parámetros:
        conn -- conexión SQLite activa
        dias -- número de días del plan
    """
    if dias < 1:
        print('  [!] El plan debe ser de al menos 1 día.')
        return

    cur = conn.cursor()
    # Lista de todos los capítulos ordenados por posición bíblica
    capitulos = cur.execute(
        '''SELECT b.long_name, b.short_name, v.book_number, v.chapter,
                  COUNT(*) AS total_vers
           FROM verses v
           JOIN books b ON v.book_number = b.book_number
           GROUP BY v.book_number, v.chapter
           ORDER BY v.book_number, v.chapter'''
    ).fetchall()

    total_caps = len(capitulos)
    por_dia    = total_caps / dias
    print(f'\n{LINEA}')
    print(f'  PLAN DE LECTURA: {dias} DÍAS')
    print(f'  Total capítulos: {total_caps}  |  ~{por_dia:.1f} capítulos/día')
    print(LINEA)

    porciones = []
    for dia in range(dias):
        inicio = int(dia * por_dia)
        fin    = int((dia + 1) * por_dia)
        porcion = capitulos[inicio:fin]
        if porcion:
            primero = porcion[0]
            ultimo  = porcion[-1]
            vers_total = sum(p[4] for p in porcion)
            porciones.append({
                'dia':     dia + 1,
                'desde':   f'{primero[1]} {primero[3]}',
                'hasta':   f'{ultimo[1]} {ultimo[3]}',
                'caps':    len(porcion),
                'versiculos': vers_total
            })

    # Muestra las primeras 10 porciones
    mostrar = porciones[:10]
    for p in mostrar:
        print(f'  Día {p["dia"]:>4}: {p["desde"]:<12} → {p["hasta"]:<12}  '
              f'({p["caps"]} caps, {p["versiculos"]} vers)')

    if len(porciones) > 10:
        print(f'  ...')
        ultimo = porciones[-1]
        print(f'  Día {ultimo["dia"]:>4}: {ultimo["desde"]:<12} → {ultimo["hasta"]:<12}  '
              f'({ultimo["caps"]} caps, {ultimo["versiculos"]} vers)')


# ──────────────────────────────────────────────────────────────
#  MENÚ PRINCIPAL
# ──────────────────────────────────────────────────────────────

def menu_principal(conn):
    """
    Menú principal con todas las opciones de la app.
    Bucle que se repite hasta que el usuario elige salir.
    """
    while True:
        print(f'\n{"#" * 60}')
        print('  BIBLIA REINA-VALERA 1960 — Menú Principal')
        print('#' * 60)
        print('  1. Leer versículo por referencia (ej: Juan 3:16)')
        print('  2. Leer capítulo completo')
        print('  3. Buscar texto en la Biblia')
        print('  4. Versículo aleatorio')
        print('  5. Ver lista de libros')
        print('  6. Mis favoritos')
        print('  7. Agregar versículo a favoritos')
        print('  8. Plan de lectura')
        print('  0. Salir')

        opcion = input('\n  Elige una opción: ').strip()

        if opcion == '0':
            print('\n  ¡Hasta luego!\n')
            sys.exit(0)

        elif opcion == '1':
            ref = input('  Referencia (ej: Juan 3:16 o Gn 1:1): ').strip()
            resultado = parsear_referencia(conn, ref)
            if not resultado:
                print(f'  [!] No se reconoció la referencia "{ref}".')
                print('      Usa el formato: NombreLibro Capítulo:Versículo')
            else:
                libro, cap, ver = resultado
                v = obtener_versiculo(conn, libro['book_number'], cap, ver)
                if v:
                    print(f'\n  {v["referencia"]}')
                    print(f'  {v["texto"]}')
                else:
                    print('  [!] Versículo no encontrado.')

        elif opcion == '2':
            nombre = input('  Libro (ej: Juan, Sal, Génesis): ').strip()
            libro  = buscar_libro(conn, nombre)
            if not libro:
                print(f'  [!] Libro "{nombre}" no encontrado.')
                continue
            try:
                cap = int(input(f'  Capítulo de {libro["long_name"]}: '))
            except ValueError:
                print('  [!] Número no válido.')
                continue
            versiculos = obtener_capitulo(conn, libro['book_number'], cap)
            if not versiculos:
                print('  [!] Capítulo no encontrado.')
            else:
                print(f'\n  {versiculos[0]["libro"]} — Capítulo {cap}')
                print(f'  {LINEA}')
                for v in versiculos:
                    print(f'  {v["versiculo"]:>3}. {v["texto"]}')

        elif opcion == '3':
            query = input('  Texto a buscar: ').strip()
            if not query:
                continue
            resultados = buscar_texto(conn, query, limite=30)
            if not resultados:
                print('  [Sin resultados]')
            else:
                libros = set(r['libro'] for r in resultados)
                print(f'\n  {len(resultados)} resultados en {len(libros)} libros:\n')
                for r in resultados:
                    print(f'  {r["referencia"]:<14} → {r["texto"]}')

        elif opcion == '4':
            v = versiculo_aleatorio(conn)
            if v:
                print(f'\n  Versículo del día: {v["referencia"]}')
                print(f'  {v["texto"]}')

        elif opcion == '5':
            listar_libros(conn)

        elif opcion == '6':
            ver_favoritos()

        elif opcion == '7':
            ref = input('  Referencia a guardar (ej: Sal 23:1): ').strip()
            agregar_favorito(conn, ref)

        elif opcion == '8':
            try:
                dias = int(input('  ¿En cuántos días quieres leer la Biblia? '))
                plan_de_lectura(conn, dias)
            except ValueError:
                print('  [!] Ingresa un número válido.')

        else:
            print('  [!] Opción no válida.')


def main():
    """
    Punto de entrada de la aplicación completa.
    """
    print(f'\n{"#" * 60}')
    print('  Bienvenido a la App de Lectura Bíblica')
    print('  Biblia Reina-Valera 1960')
    print(f'{"#" * 60}')

    try:
        conn = conectar()
        menu_principal(conn)
        conn.close()
    except FileNotFoundError as e:
        print(f'\n[ERROR] {e}')
    except sqlite3.Error as e:
        print(f'\n[ERROR SQLite] {e}')
    except KeyboardInterrupt:
        print('\n\n  App cerrada por el usuario.\n')


if __name__ == '__main__':
    main()
