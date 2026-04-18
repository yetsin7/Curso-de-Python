# =============================================================================
# CAPÍTULO 25 — Scripts, Herramientas y CLI
# Archivo: 02_click.py
# Tema: Click — CLI con decoradores, más elegante que argparse
# =============================================================================
#
# Click es la librería más popular para crear CLIs en Python.
# Ventajas sobre argparse:
# - Sintaxis declarativa con decoradores — mucho más limpia
# - Grupos de comandos con anidamiento
# - Colores y estilos en la terminal
# - Confirmaciones, contraseñas, prompts interactivos
# - Progreso, spinners y feedback visual
# - Testing más sencillo (CliRunner)
#
# Instalación: pip install click
# =============================================================================

import os
import sys
import string
import secrets
import hashlib
from pathlib import Path

try:
    import click
except ImportError:
    print("Click no está instalado.")
    print("Instala con: pip install click")
    sys.exit(1)

# =============================================================================
# GRUPO PRINCIPAL DE COMANDOS
# =============================================================================

@click.group()
@click.version_option(version="2.0.0", prog_name="toolkit")
@click.option("--debug", is_flag=True, default=False,
              help="Activar modo debug con información extra.")
@click.pass_context
def cli(ctx, debug):
    """
    Toolkit — Herramienta de utilidades CLI con Click.

    Una colección de utilidades para el día a día del desarrollador.
    Usa 'toolkit COMANDO --help' para ver la ayuda de cada comando.
    """
    # ctx.ensure_object(dict) inicializa el contexto compartido entre comandos
    # Esto permite pasar información entre el grupo y sus subcomandos
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    if debug:
        click.echo(click.style("Modo debug activado", fg="yellow", bold=True))


# =============================================================================
# COMANDO 1: texto — Transformaciones de texto
# =============================================================================

@cli.command()
@click.argument("contenido")
@click.option("--mayusculas", "-M", is_flag=True, help="Convertir a MAYÚSCULAS")
@click.option("--minusculas", "-m", is_flag=True, help="Convertir a minúsculas")
@click.option("--titulo", "-t", is_flag=True, help="Convertir a Formato Título")
@click.option("--invertir", "-i", is_flag=True, help="Invertir el texto")
@click.option("--contar", "-c", is_flag=True, help="Mostrar estadísticas del texto")
@click.option("--repetir", "-r", default=1, metavar="N",
              help="Repetir el texto N veces (default: 1)")
@click.pass_context
def texto(ctx, contenido, mayusculas, minusculas, titulo, invertir, contar, repetir):
    """
    Transforma y analiza texto.

    CONTENIDO es el texto a procesar.
    """
    resultado = contenido

    if mayusculas:
        resultado = resultado.upper()
    elif minusculas:
        resultado = resultado.lower()
    elif titulo:
        resultado = resultado.title()

    if invertir:
        resultado = resultado[::-1]

    # Mostrar resultado (en verde si hay transformación)
    color = "green" if resultado != contenido else None
    if repetir > 1:
        salida = (" " * repetir).join([resultado] * repetir)
    else:
        salida = resultado

    click.echo(click.style(salida, fg=color))

    # Estadísticas opcionales
    if contar:
        click.echo("")
        click.echo(click.style("─" * 40, fg="blue"))
        click.echo(f"Caracteres totales: {len(resultado)}")
        click.echo(f"Caracteres sin espacios: {len(resultado.replace(' ', ''))}")
        click.echo(f"Palabras: {len(resultado.split())}")
        click.echo(f"Líneas: {resultado.count(chr(10)) + 1}")

    if ctx.obj.get("debug"):
        click.echo(click.style(f"[DEBUG] Original: {contenido!r}", fg="yellow"))


# =============================================================================
# COMANDO 2: archivos — Gestión de archivos
# =============================================================================

@cli.group()
def archivos():
    """Comandos para gestión de archivos."""
    pass


@archivos.command("listar")
@click.argument("directorio", default=".", type=click.Path(exists=True))
@click.option("--extension", "-e", default=None, help="Filtrar por extensión (.py, .txt, ...)")
@click.option("--limite", "-n", default=20, show_default=True, help="Máximo de resultados")
@click.option("--ordenar", type=click.Choice(["nombre", "tamaño", "tipo"]),
              default="nombre", show_default=True, help="Criterio de ordenación")
def archivos_listar(directorio, extension, limite, ordenar):
    """
    Lista archivos de un directorio.

    DIRECTORIO es la ruta a explorar (default: directorio actual).
    """
    ruta = Path(directorio)
    archivos_encontrados = []

    for entrada in ruta.iterdir():
        if not entrada.is_file():
            continue
        if extension and not entrada.suffix.lower() == extension.lower():
            continue
        archivos_encontrados.append(entrada)

    # Ordenar
    if ordenar == "tamaño":
        archivos_encontrados.sort(key=lambda p: p.stat().st_size, reverse=True)
    elif ordenar == "tipo":
        archivos_encontrados.sort(key=lambda p: (p.suffix, p.name))
    else:
        archivos_encontrados.sort(key=lambda p: p.name)

    archivos_encontrados = archivos_encontrados[:limite]

    if not archivos_encontrados:
        click.echo(click.style("No se encontraron archivos.", fg="yellow"))
        return

    # Cabecera con color
    click.echo(click.style(f"\n{'Nombre':<38} {'Extensión':<10} {'Tamaño':>10}", bold=True))
    click.echo(click.style("─" * 62, fg="blue"))

    for archivo in archivos_encontrados:
        tamaño = archivo.stat().st_size
        if tamaño > 1_000_000:
            tamaño_str = f"{tamaño/1_000_000:.1f} MB"
        elif tamaño > 1_000:
            tamaño_str = f"{tamaño/1_000:.1f} KB"
        else:
            tamaño_str = f"{tamaño} B"

        # Colorear por tipo de archivo
        ext = archivo.suffix.lower()
        if ext == ".py":
            color = "cyan"
        elif ext in (".txt", ".md", ".rst"):
            color = "green"
        elif ext in (".jpg", ".png", ".gif"):
            color = "magenta"
        else:
            color = None

        linea = f"{archivo.name:<38} {ext:<10} {tamaño_str:>10}"
        click.echo(click.style(linea, fg=color))

    click.echo(f"\nTotal: {len(archivos_encontrados)} archivos")


@archivos.command("hash")
@click.argument("archivo", type=click.Path(exists=True))
@click.option("--algoritmo", "-a",
              type=click.Choice(["md5", "sha1", "sha256", "sha512"]),
              default="sha256", show_default=True,
              help="Algoritmo de hash a usar")
def archivos_hash(archivo, algoritmo):
    """
    Calcula el hash de un archivo.

    ARCHIVO es el fichero a hashear.
    """
    ruta = Path(archivo)
    hasher = hashlib.new(algoritmo)

    tamaño = ruta.stat().st_size
    with click.progressbar(length=tamaño, label=f"Leyendo {ruta.name}") as bar:
        with open(ruta, "rb") as f:
            while True:
                bloque = f.read(65536)  # Leer en bloques de 64KB
                if not bloque:
                    break
                hasher.update(bloque)
                bar.update(len(bloque))

    resultado_hash = hasher.hexdigest()
    click.echo(f"\n{click.style(algoritmo.upper(), fg='blue', bold=True)}: {resultado_hash}")
    click.echo(f"Archivo: {ruta.name}")
    click.echo(f"Tamaño: {tamaño:,} bytes")


# =============================================================================
# COMANDO 3: password — Generador de contraseñas seguras
# =============================================================================

@cli.command()
@click.option("--longitud", "-l", default=16, show_default=True,
              metavar="N", help="Longitud de la contraseña")
@click.option("--cantidad", "-n", default=1, show_default=True,
              metavar="N", help="Cuántas contraseñas generar")
@click.option("--sin-simbolos", is_flag=True,
              help="Excluir símbolos especiales (!@#$...)")
@click.option("--sin-numeros", is_flag=True,
              help="Excluir números")
@click.option("--solo-letras", is_flag=True,
              help="Solo letras (mayúsculas y minúsculas)")
@click.option("--confirmar", is_flag=True,
              help="Pedir confirmación antes de mostrar")
def password(longitud, cantidad, sin_simbolos, sin_numeros, solo_letras, confirmar):
    """
    Genera contraseñas criptográficamente seguras.

    Usa el módulo `secrets` que es apropiado para criptografía
    (a diferencia de `random` que NO debe usarse para contraseñas).
    """
    # Construir el conjunto de caracteres
    caracteres = string.ascii_letters  # a-z + A-Z

    if not solo_letras:
        if not sin_numeros:
            caracteres += string.digits

        if not sin_simbolos:
            caracteres += string.punctuation

    if len(caracteres) < 10:
        click.echo(click.style("Error: muy pocos caracteres permitidos.", fg="red"))
        return

    if confirmar:
        if not click.confirm(f"¿Generar {cantidad} contraseña(s) de {longitud} caracteres?"):
            click.echo("Operación cancelada.")
            return

    click.echo(click.style(f"\nContraseñas generadas ({longitud} caracteres, {len(caracteres)} posibles):", bold=True))
    click.echo(click.style("─" * 50, fg="blue"))

    for i in range(cantidad):
        pw = "".join(secrets.choice(caracteres) for _ in range(longitud))
        # Mostrar en verde y negrita para destacar
        click.echo(f"  {i+1:2d}. {click.style(pw, fg='green', bold=True)}")

    click.echo(click.style("\nUSO: Copia y pega en tu gestor de contraseñas.", fg="yellow"))


# =============================================================================
# COMANDO 4: buscar — Búsqueda de texto en archivos
# =============================================================================

@cli.command()
@click.argument("patron")
@click.argument("directorio", default=".", type=click.Path(exists=True))
@click.option("--extension", "-e", default=".py", show_default=True,
              help="Extensión de archivos a buscar")
@click.option("--ignorar-caso", "-i", is_flag=True,
              help="Búsqueda sin distinguir mayúsculas/minúsculas")
@click.option("--contar", "-c", is_flag=True,
              help="Solo mostrar el conteo de coincidencias")
def buscar(patron, directorio, extension, ignorar_caso, contar):
    """
    Busca un patrón de texto en archivos.

    PATRON es el texto a buscar.
    DIRECTORIO es la carpeta donde buscar (default: directorio actual).
    """
    ruta_base = Path(directorio)
    archivos_con_match = 0
    total_matches = 0

    # Usar rglob para búsqueda recursiva
    for archivo in sorted(ruta_base.rglob(f"*{extension}")):
        try:
            contenido = archivo.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Comparar con o sin distinción de mayúsculas
        busqueda_en = contenido.lower() if ignorar_caso else contenido
        busqueda_patron = patron.lower() if ignorar_caso else patron

        if busqueda_patron not in busqueda_en:
            continue

        archivos_con_match += 1
        lineas = contenido.splitlines()
        matches_en_archivo = 0

        if not contar:
            click.echo(click.style(f"\n{archivo}", fg="blue", bold=True))

        for num, linea in enumerate(lineas, 1):
            linea_comp = linea.lower() if ignorar_caso else linea
            if busqueda_patron in linea_comp:
                matches_en_archivo += 1
                total_matches += 1
                if not contar:
                    # Resaltar el patrón encontrado
                    click.echo(f"  {click.style(str(num), fg='yellow')}:  {linea.strip()}")

        if contar:
            click.echo(f"{archivo}: {click.style(str(matches_en_archivo), fg='green')} coincidencias")

    click.echo(click.style(f"\nTotal: {total_matches} coincidencias en {archivos_con_match} archivos", bold=True))


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    cli(obj={})
