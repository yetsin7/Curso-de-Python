"""
CLI Tool Completo para la Biblia RV60
=======================================
Herramienta de línea de comandos para consultar la Biblia usando argparse.

Comandos disponibles:
    leer    — Muestra un versículo específico (ej. Juan 3:16)
    buscar  — Busca versículos por texto
    stats   — Estadísticas generales de la Biblia
    aleatorio — Versículo aleatorio
    exportar  — Exporta un libro completo a JSON o TXT

Uso:
    python 06_cli_biblia.py leer "Juan" 3 16
    python 06_cli_biblia.py buscar "amor de Dios"
    python 06_cli_biblia.py stats
    python 06_cli_biblia.py aleatorio
    python 06_cli_biblia.py exportar --libro Salmos --formato json

Solo usa librería estándar (sqlite3, argparse, json, re, os).
"""

import argparse
import json
import os
import random
import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')


# ===========================================================================
# Utilidades de BD
# ===========================================================================

def conectar() -> sqlite3.Connection:
    """
    Abre la conexión a la BD de la Biblia.
    Termina el programa con mensaje claro si no se encuentra el archivo.

    Returns:
        Conexión sqlite3 configurada con row_factory.
    """
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Base de datos no encontrada en:\n  {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def limpiar_texto(texto: str) -> str:
    """
    Elimina marcas Strong <S>NNNN</S> del texto del versículo.

    Args:
        texto: Texto crudo con marcas numéricas Strong.

    Returns:
        Texto limpio sin marcas.
    """
    return re.sub(r'<S>\d+</S>', '', texto).strip()


def buscar_libro(conn: sqlite3.Connection, nombre: str) -> sqlite3.Row | None:
    """
    Busca un libro por nombre parcial (case-insensitive).
    Retorna el primer resultado encontrado.

    Args:
        conn  : Conexión activa a la BD.
        nombre: Nombre o fragmento del nombre del libro.

    Returns:
        Fila del libro o None si no se encontró.
    """
    libro = conn.execute(
        "SELECT * FROM books WHERE long_name LIKE ? OR short_name LIKE ?",
        (f"%{nombre}%", f"%{nombre}%")
    ).fetchone()
    return libro


# ===========================================================================
# Comando: leer
# ===========================================================================

def cmd_leer(args: argparse.Namespace) -> None:
    """
    Muestra el texto de un versículo específico por libro, capítulo y versículo.

    Maneja errores: libro no encontrado, capítulo/versículo fuera de rango.

    Args:
        args: Argumentos con libro (str), capitulo (int) y versiculo (int).
    """
    conn = conectar()

    libro = buscar_libro(conn, args.libro)
    if not libro:
        print(f"[ERROR] No se encontró el libro: '{args.libro}'")
        print("  Sugerencia: usa el nombre en español, ej. 'Juan', 'Génesis', 'Salmos'")
        conn.close()
        sys.exit(1)

    fila = conn.execute(
        "SELECT * FROM verses WHERE book_number=? AND chapter=? AND verse=?",
        (libro["book_number"], args.capitulo, args.versiculo)
    ).fetchone()

    conn.close()

    if not fila:
        print(f"[ERROR] {libro['long_name']} {args.capitulo}:{args.versiculo} no existe.")
        sys.exit(1)

    print(f"\n  {libro['long_name']} {args.capitulo}:{args.versiculo}")
    print(f"  \"{limpiar_texto(fila['text'])}\"\n")


# ===========================================================================
# Comando: buscar
# ===========================================================================

def cmd_buscar(args: argparse.Namespace) -> None:
    """
    Busca versículos que contengan el texto dado.
    Muestra hasta 10 resultados con su referencia completa.

    Args:
        args: Argumentos con query (str) y limit (int, opcional).
    """
    conn  = conectar()
    query = args.query
    limit = getattr(args, "limit", 10)

    patron = f"%{query}%"
    filas  = conn.execute("""
        SELECT b.long_name, v.chapter, v.verse, v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        WHERE v.text LIKE ?
        LIMIT ?
    """, (patron, limit)).fetchall()

    # Contar total sin límite
    total = conn.execute(
        "SELECT COUNT(*) FROM verses WHERE text LIKE ?", (patron,)
    ).fetchone()[0]

    conn.close()

    if not filas:
        print(f"\n  No se encontraron resultados para: '{query}'\n")
        return

    print(f"\n  {total:,} resultado(s) para \"{query}\" (mostrando {len(filas)}):\n")
    for row in filas:
        ref   = f"{row['long_name']} {row['chapter']}:{row['verse']}"
        texto = limpiar_texto(row["text"])
        print(f"  [{ref}]")
        print(f"  {texto}\n")


# ===========================================================================
# Comando: stats
# ===========================================================================

def cmd_stats(_args: argparse.Namespace) -> None:
    """
    Muestra estadísticas generales de la Biblia:
    total de libros, versículos, capítulos, palabras estimadas.

    Args:
        _args: Argumentos de argparse (no utilizados en este comando).
    """
    conn = conectar()

    total_libros   = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    total_versiculos = conn.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    total_capitulos = conn.execute(
        "SELECT COUNT(DISTINCT book_number || '-' || chapter) FROM verses"
    ).fetchone()[0]

    at_versiculos = conn.execute(
        "SELECT COUNT(*) FROM verses WHERE book_number <= 390"
    ).fetchone()[0]
    nt_versiculos = total_versiculos - at_versiculos

    libro_mas_largo = conn.execute("""
        SELECT b.long_name, COUNT(*) as total
        FROM verses v JOIN books b ON v.book_number = b.book_number
        GROUP BY v.book_number ORDER BY total DESC LIMIT 1
    """).fetchone()

    libro_mas_corto = conn.execute("""
        SELECT b.long_name, COUNT(*) as total
        FROM verses v JOIN books b ON v.book_number = b.book_number
        GROUP BY v.book_number ORDER BY total ASC LIMIT 1
    """).fetchone()

    conn.close()

    print("\n  ╔══════════════════════════════════════════╗")
    print("  ║   ESTADÍSTICAS — BIBLIA REINA-VALERA 1960 ║")
    print("  ╠══════════════════════════════════════════╣")
    print(f"  ║  Libros       : {total_libros:<26}║")
    print(f"  ║  Capítulos    : {total_capitulos:<26}║")
    print(f"  ║  Versículos   : {total_versiculos:<26,}║")
    print(f"  ║  AT versíc.   : {at_versiculos:<26,}║")
    print(f"  ║  NT versíc.   : {nt_versiculos:<26,}║")
    print(f"  ║  Libro + largo: {libro_mas_largo['long_name']:<26}║")
    print(f"  ║  Libro + corto: {libro_mas_corto['long_name']:<26}║")
    print("  ╚══════════════════════════════════════════╝\n")


# ===========================================================================
# Comando: aleatorio
# ===========================================================================

def cmd_aleatorio(_args: argparse.Namespace) -> None:
    """
    Muestra un versículo elegido al azar de toda la Biblia.

    Args:
        _args: Argumentos de argparse (no utilizados).
    """
    conn = conectar()

    total = conn.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    offset = random.randint(0, total - 1)

    fila = conn.execute("""
        SELECT b.long_name, v.chapter, v.verse, v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        LIMIT 1 OFFSET ?
    """, (offset,)).fetchone()

    conn.close()

    if fila:
        ref   = f"{fila['long_name']} {fila['chapter']}:{fila['verse']}"
        texto = limpiar_texto(fila["text"])
        print(f"\n  ✦ Versículo aleatorio: {ref}")
        print(f"  \"{texto}\"\n")


# ===========================================================================
# Comando: exportar
# ===========================================================================

def cmd_exportar(args: argparse.Namespace) -> None:
    """
    Exporta todos los versículos de un libro al formato indicado (json o txt).
    El archivo se guarda en el directorio de trabajo actual.

    Args:
        args: Argumentos con libro (str) y formato ('json' o 'txt').
    """
    conn   = conectar()
    libro  = buscar_libro(conn, args.libro)

    if not libro:
        print(f"[ERROR] Libro no encontrado: '{args.libro}'")
        conn.close()
        sys.exit(1)

    filas = conn.execute(
        "SELECT chapter, verse, text FROM verses WHERE book_number=? ORDER BY chapter, verse",
        (libro["book_number"],)
    ).fetchall()
    conn.close()

    nombre_archivo = libro["long_name"].lower().replace(" ", "_")
    versiculos = [
        {
            "referencia": f"{libro['long_name']} {r['chapter']}:{r['verse']}",
            "texto": limpiar_texto(r["text"]),
        }
        for r in filas
    ]

    if args.formato == "json":
        ruta = f"{nombre_archivo}.json"
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(versiculos, f, ensure_ascii=False, indent=2)
        print(f"\n  Exportado: {ruta} ({len(versiculos):,} versículos)\n")

    elif args.formato == "txt":
        ruta = f"{nombre_archivo}.txt"
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(f"BIBLIA REINA-VALERA 1960 — {libro['long_name'].upper()}\n")
            f.write("=" * 60 + "\n\n")
            capitulo_actual = None
            for v in versiculos:
                cap = int(v["referencia"].split(" ")[-1].split(":")[0])
                if cap != capitulo_actual:
                    capitulo_actual = cap
                    f.write(f"\nCAPÍTULO {cap}\n\n")
                num_versiculo = v["referencia"].split(":")[-1]
                f.write(f"  {num_versiculo}. {v['texto']}\n")

        print(f"\n  Exportado: {ruta} ({len(versiculos):,} versículos)\n")


# ===========================================================================
# Construcción del parser principal
# ===========================================================================

def construir_parser() -> argparse.ArgumentParser:
    """
    Construye el parser de argparse con todos los subcomandos disponibles.

    Returns:
        ArgumentParser configurado y listo para parsear sys.argv.
    """
    parser = argparse.ArgumentParser(
        prog="biblia",
        description="CLI para consultar la Biblia Reina-Valera 1960",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python 06_cli_biblia.py leer Juan 3 16
  python 06_cli_biblia.py buscar "amor de Dios"
  python 06_cli_biblia.py buscar "fe" --limit 20
  python 06_cli_biblia.py stats
  python 06_cli_biblia.py aleatorio
  python 06_cli_biblia.py exportar --libro Salmos --formato json
  python 06_cli_biblia.py exportar --libro Genesis --formato txt
        """
    )

    subparsers = parser.add_subparsers(dest="comando", required=True)

    # --- Subcomando: leer ---
    p_leer = subparsers.add_parser("leer", help="Leer un versículo específico")
    p_leer.add_argument("libro",     type=str, help="Nombre del libro (ej. Juan, Génesis)")
    p_leer.add_argument("capitulo",  type=int, help="Número de capítulo")
    p_leer.add_argument("versiculo", type=int, help="Número de versículo")
    p_leer.set_defaults(func=cmd_leer)

    # --- Subcomando: buscar ---
    p_buscar = subparsers.add_parser("buscar", help="Buscar versículos por texto")
    p_buscar.add_argument("query", type=str, help="Texto a buscar")
    p_buscar.add_argument(
        "--limit", type=int, default=10,
        help="Número máximo de resultados (default: 10)"
    )
    p_buscar.set_defaults(func=cmd_buscar)

    # --- Subcomando: stats ---
    p_stats = subparsers.add_parser("stats", help="Estadísticas generales de la Biblia")
    p_stats.set_defaults(func=cmd_stats)

    # --- Subcomando: aleatorio ---
    p_aleat = subparsers.add_parser("aleatorio", help="Versículo aleatorio")
    p_aleat.set_defaults(func=cmd_aleatorio)

    # --- Subcomando: exportar ---
    p_exp = subparsers.add_parser("exportar", help="Exportar un libro completo")
    p_exp.add_argument("--libro",   required=True, help="Nombre del libro a exportar")
    p_exp.add_argument(
        "--formato", choices=["json", "txt"], default="json",
        help="Formato de exportación: json o txt (default: json)"
    )
    p_exp.set_defaults(func=cmd_exportar)

    return parser


# ===========================================================================
# Punto de entrada
# ===========================================================================

def main() -> None:
    """
    Punto de entrada principal del CLI.
    Parsea los argumentos y delega al subcomando correspondiente.
    """
    parser = construir_parser()
    args   = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
