"""
Análisis estadístico completo de la Biblia RV60.
Aprende a usar collections.Counter, GROUP BY en SQL y comparativas AT/NT.
Ejecutar: python 03_estadisticas.py
"""

import sqlite3
import os
import re
from collections import Counter

# --- Ruta relativa a la BD ---
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')

LINEA = '=' * 60

# Palabras muy comunes en español que se excluyen del conteo de frecuencia
STOPWORDS = {
    'de', 'la', 'el', 'en', 'y', 'a', 'los', 'las', 'un', 'una',
    'que', 'del', 'se', 'no', 'su', 'le', 'al', 'lo', 'con', 'por',
    'es', 'me', 'si', 'mas', 'mi', 'te', 'tu', 'yo', 'él', 'mi',
    'nos', 'les', 'sus', 'ha', 'he', 'ni', 'o', 'sea', 'fue', 'era',
    'para', 'pero', 'como', 'más', 'todo', 'ya', 'también', 'sobre',
    'cuando', 'porque', 'será', 'son', 'ante', 'todos', 'todas',
}


def conectar():
    """
    Abre y devuelve la conexión SQLite a la Biblia RV60.
    """
    ruta = os.path.abspath(DB_PATH)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f'No se encontró la BD en: {ruta}')
    return sqlite3.connect(ruta)


def limpiar_texto(texto):
    """
    Elimina marcas Strong y normaliza espacios en el texto del versículo.
    """
    limpio = re.sub(r'<S>\d+</S>', '', texto)
    return re.sub(r' {2,}', ' ', limpio).strip()


def conteos_globales(cur):
    """
    Calcula y muestra los totales generales de la Biblia:
    libros, capítulos, versículos y palabras (aproximado).
    """
    print(f'\n{LINEA}')
    print('  CONTEOS GLOBALES')
    print(LINEA)

    libros    = cur.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    versiculos = cur.execute('SELECT COUNT(*) FROM verses').fetchone()[0]
    capitulos  = cur.execute(
        'SELECT COUNT(DISTINCT book_number || "-" || chapter) FROM verses'
    ).fetchone()[0]

    # Conteo aproximado de palabras: suma el conteo de espacios+1 por versículo
    filas_texto = cur.execute('SELECT text FROM verses').fetchall()
    total_palabras = 0
    for (texto,) in filas_texto:
        limpio = limpiar_texto(texto)
        total_palabras += len(limpio.split())

    print(f'  Libros     : {libros}')
    print(f'  Capítulos  : {capitulos:,}')
    print(f'  Versículos : {versiculos:,}')
    print(f'  Palabras   : ~{total_palabras:,} (aprox.)')


def palabras_mas_frecuentes(cur, top=25):
    """
    Cuenta las palabras más frecuentes en toda la Biblia,
    excluyendo artículos, preposiciones y conjunciones comunes.
    Usa collections.Counter para el conteo eficiente.

    Parámetros:
        cur -- cursor SQLite activo
        top -- cuántas palabras mostrar
    """
    print(f'\n{LINEA}')
    print(f'  TOP {top} PALABRAS MÁS FRECUENTES (excl. stopwords)')
    print(LINEA)

    filas = cur.execute('SELECT text FROM verses').fetchall()
    contador = Counter()

    for (texto,) in filas:
        limpio = limpiar_texto(texto).lower()
        # Elimina puntuación básica antes de contar
        limpio = re.sub(r'[.,;:!?¿¡()\"\'\-—]', '', limpio)
        for palabra in limpio.split():
            if palabra not in STOPWORDS and len(palabra) > 2:
                contador[palabra] += 1

    print(f'  {"Palabra":<20} {"Apariciones":>12}')
    print('  ' + '-' * 34)
    for palabra, count in contador.most_common(top):
        barra = '█' * (count // 500)  # barra visual proporcional
        print(f'  {palabra:<20} {count:>12,}  {barra}')


def distribucion_por_libro(cur):
    """
    Muestra una tabla ordenada de versículos por libro,
    de mayor a menor, con barra visual proporcional.
    """
    print(f'\n{LINEA}')
    print('  DISTRIBUCIÓN DE VERSÍCULOS POR LIBRO')
    print(LINEA)

    datos = cur.execute('''
        SELECT b.long_name, b.book_number, COUNT(*) AS total
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        GROUP BY v.book_number
        ORDER BY total DESC
    ''').fetchall()

    max_vers = datos[0][2] if datos else 1
    print(f'  {"Libro":<22} {"Vers":>6}  Distribución relativa')
    print('  ' + '-' * 55)

    for nombre, bnum, total in datos:
        barra_len = int((total / max_vers) * 30)
        barra = '█' * barra_len
        testamento = 'AT' if bnum <= 390 else 'NT'
        print(f'  [{testamento}] {nombre:<18} {total:>6}  {barra}')


def extremos_por_libro(cur):
    """
    Muestra los 5 libros con más versículos y los 5 con menos.
    """
    print(f'\n{LINEA}')
    print('  LIBROS CON MÁS Y MENOS VERSÍCULOS')
    print(LINEA)

    datos = cur.execute('''
        SELECT b.long_name, COUNT(*) AS total
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        GROUP BY v.book_number
        ORDER BY total DESC
    ''').fetchall()

    print('\n  --- 5 LIBROS CON MÁS VERSÍCULOS ---')
    for nombre, total in datos[:5]:
        print(f'  {nombre:<22} {total:>6} versículos')

    print('\n  --- 5 LIBROS CON MENOS VERSÍCULOS ---')
    for nombre, total in datos[-5:]:
        print(f'  {nombre:<22} {total:>6} versículos')


def comparativa_at_nt(cur):
    """
    Compara el Antiguo Testamento (libros 10-390) con el Nuevo Testamento (400-660):
    libros, capítulos, versículos, palabras y promedio de longitud.
    """
    print(f'\n{LINEA}')
    print('  COMPARATIVA AT vs NT')
    print(LINEA)

    def stats_testamento(max_book):
        """Calcula estadísticas para AT (book<=390) o NT (book>=400)."""
        op = '<=' if max_book == 390 else '>='
        val = 390 if max_book == 390 else 400

        libros = cur.execute(
            f'SELECT COUNT(*) FROM books WHERE book_number {op} {val}'
        ).fetchone()[0]
        vers = cur.execute(
            f'SELECT COUNT(*) FROM verses WHERE book_number {op} {val}'
        ).fetchone()[0]
        caps = cur.execute(
            f'SELECT COUNT(DISTINCT book_number || "-" || chapter) FROM verses WHERE book_number {op} {val}'
        ).fetchone()[0]
        textos = cur.execute(
            f'SELECT text FROM verses WHERE book_number {op} {val}'
        ).fetchall()
        palabras = sum(len(limpiar_texto(t[0]).split()) for t in textos)
        return libros, caps, vers, palabras

    at = stats_testamento(390)
    nt = stats_testamento(400)

    print(f'  {"Métrica":<22} {"AT":>10} {"NT":>10}')
    print('  ' + '-' * 44)
    etiquetas = ['Libros', 'Capítulos', 'Versículos', 'Palabras (~)']
    for label, av, nv in zip(etiquetas, at, nt):
        print(f'  {label:<22} {av:>10,} {nv:>10,}')

    porc_at = at[2] / (at[2] + nt[2]) * 100
    porc_nt = 100 - porc_at
    print(f'\n  Proporción versículos: AT {porc_at:.1f}% | NT {porc_nt:.1f}%')


def longitud_versiculos(cur):
    """
    Analiza la longitud de los versículos: el más largo, el más corto
    y el promedio de caracteres por versículo en toda la Biblia.
    """
    print(f'\n{LINEA}')
    print('  LONGITUD DE VERSÍCULOS')
    print(LINEA)

    filas = cur.execute('''
        SELECT b.short_name, v.chapter, v.verse, v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
    ''').fetchall()

    medidos = []
    for abrev, cap, ver, texto in filas:
        limpio = limpiar_texto(texto)
        medidos.append((len(limpio), abrev, cap, ver, limpio))

    medidos.sort(key=lambda x: x[0])

    total_chars = sum(m[0] for m in medidos)
    promedio    = total_chars / len(medidos)

    print(f'  Versículo más corto  : {medidos[0][1]} {medidos[0][2]}:{medidos[0][3]}')
    print(f'    Texto: {medidos[0][4]}')
    print(f'    Longitud: {medidos[0][0]} caracteres')

    print(f'\n  Versículo más largo  : {medidos[-1][1]} {medidos[-1][2]}:{medidos[-1][3]}')
    preview = medidos[-1][4][:80] + '...'
    print(f'    Texto: {preview}')
    print(f'    Longitud: {medidos[-1][0]} caracteres')

    print(f'\n  Promedio por versículo: {promedio:.1f} caracteres')


def main():
    """
    Punto de entrada: ejecuta todos los análisis estadísticos en secuencia.
    """
    print(f'\n{"#" * 60}')
    print('  ESTADÍSTICAS DE LA BIBLIA REINA-VALERA 1960')
    print(f'{"#" * 60}')

    try:
        conn = conectar()
        cur  = conn.cursor()

        conteos_globales(cur)
        comparativa_at_nt(cur)
        extremos_por_libro(cur)
        distribucion_por_libro(cur)
        longitud_versiculos(cur)
        palabras_mas_frecuentes(cur, top=25)

        conn.close()
        print(f'\n{LINEA}')
        print('  Análisis completado.')
        print(LINEA)

    except FileNotFoundError as e:
        print(f'\n[ERROR] {e}')
    except sqlite3.Error as e:
        print(f'\n[ERROR SQLite] {e}')


if __name__ == '__main__':
    main()
