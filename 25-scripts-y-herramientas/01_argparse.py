# =============================================================================
# CAPÍTULO 25 — Scripts, Herramientas y CLI
# Archivo: 01_argparse.py
# Tema: argparse — Crear herramientas CLI con la librería estándar
# =============================================================================
#
# argparse es el módulo estándar de Python para parsear argumentos de línea
# de comandos. Sin instalar nada extra, puedes crear herramientas CLI
# profesionales con:
# - Argumentos posicionales (requeridos)
# - Opciones (--flag, -f)
# - Tipos de datos automáticos
# - Ayuda automática (--help)
# - Subcomandos (como git commit, git push)
#
# CÓMO USAR ESTE SCRIPT:
#   python 01_argparse.py --help
#   python 01_argparse.py texto --help
#   python 01_argparse.py archivos --help
# =============================================================================

import argparse
import os
import sys

# =============================================================================
# SECCIÓN 1: Parser básico — explicación con código
# =============================================================================

def demo_argparse_basico():
    """
    Muestra los conceptos básicos de argparse con ejemplos ejecutables.
    Se llama cuando el script se ejecuta sin argumentos.
    """
    print("=" * 60)
    print("ARGPARSE — CLI con la librería estándar de Python")
    print("=" * 60)

    print("""
CONCEPTOS DE ARGPARSE:

1. ArgumentParser — El objeto principal
   parser = argparse.ArgumentParser(
       prog="mi_tool",
       description="Descripción de qué hace la herramienta",
       epilog="Texto al final del --help"
   )

2. Argumentos posicionales — REQUERIDOS, sin --
   parser.add_argument("archivo", help="Ruta del archivo a procesar")
   # Uso: python script.py mi_archivo.txt

3. Argumentos opcionales — Con -- o -
   parser.add_argument("--salida", "-s", default="output.txt",
                       help="Archivo de salida (default: output.txt)")
   # Uso: python script.py --salida resultado.txt

4. Flags booleanos — Presentes = True, ausentes = False
   parser.add_argument("--verbose", "-v", action="store_true",
                       help="Mostrar información detallada")
   # Uso: python script.py --verbose

5. Tipo de dato automático
   parser.add_argument("--numero", type=int, default=5,
                       help="Número entero (default: 5)")
   # argparse convierte el string "10" al entero 10

6. Choices — Limitar valores permitidos
   parser.add_argument("--formato", choices=["json", "csv", "xml"],
                       default="json", help="Formato de salida")

7. nargs — Múltiples valores
   parser.add_argument("archivos", nargs="+",  # 1 o más
                       help="Uno o más archivos")
   parser.add_argument("--tags", nargs="*",    # 0 o más
                       help="Tags opcionales")

8. Parsear los argumentos
   args = parser.parse_args()
   print(args.archivo)     # Acceder al valor
   print(args.verbose)     # True o False
""")

# =============================================================================
# HERRAMIENTA REAL: Renombrador masivo de archivos
# =============================================================================

def crear_parser_principal():
    """
    Crea el parser principal con subcomandos.
    Cada subcomando tiene su propio conjunto de argumentos.
    """
    # Parser raíz
    parser = argparse.ArgumentParser(
        prog="filetool",
        description="Herramienta de gestión de archivos en Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS:
  python 01_argparse.py texto "Hola Mundo" --mayusculas
  python 01_argparse.py texto "hello" --repetir 3
  python 01_argparse.py archivos --directorio . --extension .py
  python 01_argparse.py info --version
        """
    )

    # Opción global (disponible en todos los subcomandos)
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Mostrar información detallada del proceso")

    # Subparsers: permite tener subcomandos como "git commit", "git push"
    subparsers = parser.add_subparsers(
        dest="comando",  # El subcomando elegido se guarda en args.comando
        help="Subcomandos disponibles",
        metavar="COMANDO"
    )

    # -----------------------------------------------------------------------
    # Subcomando: texto — Transformaciones de texto
    # -----------------------------------------------------------------------
    parser_texto = subparsers.add_parser(
        "texto",
        help="Transformar texto",
        description="Aplica transformaciones a un texto dado"
    )
    # Argumento posicional requerido
    parser_texto.add_argument(
        "contenido",
        help="El texto a transformar"
    )
    # Flags de transformación
    parser_texto.add_argument(
        "--mayusculas", "-M", action="store_true",
        help="Convertir a mayúsculas"
    )
    parser_texto.add_argument(
        "--minusculas", "-m", action="store_true",
        help="Convertir a minúsculas"
    )
    parser_texto.add_argument(
        "--titulo", "-t", action="store_true",
        help="Convertir a formato título"
    )
    parser_texto.add_argument(
        "--repetir", "-r", type=int, default=1, metavar="N",
        help="Repetir el texto N veces (default: 1)"
    )
    parser_texto.add_argument(
        "--separador", "-s", default=" ",
        help='Separador entre repeticiones (default: espacio)'
    )

    # -----------------------------------------------------------------------
    # Subcomando: archivos — Listar y filtrar archivos
    # -----------------------------------------------------------------------
    parser_archivos = subparsers.add_parser(
        "archivos",
        help="Listar y filtrar archivos",
        description="Lista archivos de un directorio con filtros opcionales"
    )
    parser_archivos.add_argument(
        "--directorio", "-d", default=".",
        metavar="RUTA",
        help="Directorio a explorar (default: directorio actual)"
    )
    parser_archivos.add_argument(
        "--extension", "-e", default=None,
        metavar=".ext",
        help="Filtrar por extensión (ej: .py, .txt, .csv)"
    )
    parser_archivos.add_argument(
        "--minimo", type=int, default=0, metavar="BYTES",
        help="Tamaño mínimo en bytes (default: 0)"
    )
    parser_archivos.add_argument(
        "--maximo", type=int, default=None, metavar="BYTES",
        help="Tamaño máximo en bytes (default: sin límite)"
    )
    parser_archivos.add_argument(
        "--ordenar", choices=["nombre", "tamaño", "extension"],
        default="nombre",
        help="Criterio de ordenación (default: nombre)"
    )
    parser_archivos.add_argument(
        "--limite", "-n", type=int, default=50, metavar="N",
        help="Número máximo de resultados (default: 50)"
    )

    # -----------------------------------------------------------------------
    # Subcomando: info — Información del script
    # -----------------------------------------------------------------------
    parser_info = subparsers.add_parser(
        "info",
        help="Mostrar información y versión"
    )
    parser_info.add_argument(
        "--version", action="store_true",
        help="Mostrar versión del script"
    )

    return parser


def ejecutar_texto(args):
    """Procesa el subcomando 'texto'."""
    texto = args.contenido

    if args.mayusculas:
        texto = texto.upper()
    elif args.minusculas:
        texto = texto.lower()
    elif args.titulo:
        texto = texto.title()

    resultado = args.separador.join([texto] * args.repetir)

    if args.verbose:
        print(f"Texto original: {args.contenido}")
        print(f"Transformaciones aplicadas: "
              f"{'mayúsculas' if args.mayusculas else ''}"
              f"{'minúsculas' if args.minusculas else ''}"
              f"{'título' if args.titulo else ''}")
        print(f"Repeticiones: {args.repetir}")
        print(f"Resultado:")

    print(resultado)


def ejecutar_archivos(args):
    """Procesa el subcomando 'archivos'."""
    directorio = args.directorio

    if not os.path.isdir(directorio):
        print(f"Error: '{directorio}' no es un directorio válido", file=sys.stderr)
        sys.exit(1)

    # Recopilar archivos
    archivos_info = []
    try:
        for nombre in os.listdir(directorio):
            ruta_completa = os.path.join(directorio, nombre)
            if not os.path.isfile(ruta_completa):
                continue

            # Filtrar por extensión
            if args.extension and not nombre.endswith(args.extension):
                continue

            tamaño = os.path.getsize(ruta_completa)

            # Filtrar por tamaño mínimo
            if tamaño < args.minimo:
                continue

            # Filtrar por tamaño máximo
            if args.maximo is not None and tamaño > args.maximo:
                continue

            _, ext = os.path.splitext(nombre)
            archivos_info.append({
                "nombre": nombre,
                "tamaño": tamaño,
                "extension": ext.lower()
            })
    except PermissionError:
        print(f"Error: Sin permiso para acceder a '{directorio}'", file=sys.stderr)
        sys.exit(1)

    # Ordenar
    if args.ordenar == "tamaño":
        archivos_info.sort(key=lambda x: x["tamaño"], reverse=True)
    elif args.ordenar == "extension":
        archivos_info.sort(key=lambda x: (x["extension"], x["nombre"]))
    else:
        archivos_info.sort(key=lambda x: x["nombre"])

    # Limitar resultados
    archivos_info = archivos_info[:args.limite]

    if not archivos_info:
        print("No se encontraron archivos con los criterios especificados.")
        return

    if args.verbose:
        print(f"Directorio: {os.path.abspath(directorio)}")
        print(f"Filtros: extensión={args.extension}, "
              f"tamaño=[{args.minimo}, {args.maximo}]")
        print(f"Encontrados: {len(archivos_info)} archivos\n")

    # Mostrar resultados formateados
    print(f"{'Nombre':<40} {'Extensión':<12} {'Tamaño':>10}")
    print("-" * 65)
    for info in archivos_info:
        tamaño_str = f"{info['tamaño']:,} B"
        print(f"{info['nombre']:<40} {info['extension']:<12} {tamaño_str:>10}")

    print(f"\nTotal: {len(archivos_info)} archivos")


def ejecutar_info(args):
    """Procesa el subcomando 'info'."""
    print("filetool v1.0.0 — Herramienta de archivos en Python")
    print("Autor: Libro de Python — Capítulo 25")
    print("Python:", sys.version)


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    # Si no se pasan argumentos, mostrar demo
    if len(sys.argv) == 1:
        demo_argparse_basico()
        print("\nEjecutar con --help para ver los comandos disponibles:")
        print(f"  python {os.path.basename(__file__)} --help")
        print(f"  python {os.path.basename(__file__)} texto --help")
        sys.exit(0)

    parser = crear_parser_principal()
    args = parser.parse_args()

    if args.comando == "texto":
        ejecutar_texto(args)
    elif args.comando == "archivos":
        ejecutar_archivos(args)
    elif args.comando == "info":
        ejecutar_info(args)
    else:
        parser.print_help()
        sys.exit(1)
