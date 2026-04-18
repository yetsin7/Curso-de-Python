# =============================================================================
# CAPÍTULO 25 — Scripts, Herramientas y CLI
# Archivo: 03_rich.py
# Tema: Rich — Salida visual rica en la terminal
# =============================================================================
#
# Rich transforma la terminal en una interfaz visual profesional.
# Permite mostrar tablas, árboles, paneles, barras de progreso, markdown,
# syntax highlighting y mucho más — todo en la terminal estándar.
#
# Sin Rich: print("Error: archivo no encontrado")
# Con Rich: [bold red]Error:[/bold red] archivo no encontrado
#
# Instalación: pip install rich
# =============================================================================

import os
import sys
import time
import random
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import (
        Progress, SpinnerColumn, BarColumn,
        TextColumn, TimeRemainingColumn, TimeElapsedColumn
    )
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.text import Text
    from rich.columns import Columns
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich import box
    from rich.logging import RichHandler
    import logging
except ImportError:
    print("Rich no está instalado.")
    print("Instala con: pip install rich")
    sys.exit(1)

# Console es el objeto principal de Rich
# Todos los print() del script usan este objeto para tener control total
console = Console()

# =============================================================================
# SECCIÓN 1: Texto con markup — Colores y estilos
# =============================================================================

def demo_texto():
    """Muestra las capacidades de texto y markup de Rich."""
    console.rule("[bold blue]1. Texto con Markup y Estilos")

    # Markup básico (similar a BBCode)
    console.print("[bold green]¡Hola desde Rich![/bold green]")
    console.print("[red]Error:[/red] Archivo no encontrado")
    console.print("[yellow]Advertencia:[/yellow] El disco está al 90%")
    console.print("[blue]Info:[/blue] Proceso completado correctamente")

    # Estilos combinados
    console.print("\n[bold][underline]Estilos disponibles:[/underline][/bold]")
    console.print("  [bold]Negrita[/bold]")
    console.print("  [italic]Cursiva[/italic]")
    console.print("  [underline]Subrayado[/underline]")
    console.print("  [strike]Tachado[/strike]")
    console.print("  [blink]Parpadeante[/blink] (puede no funcionar en todas las terminales)")

    # Colores de 256 bits
    console.print("\n[bold]Colores de la paleta:[/bold]")
    colores = ["red", "orange3", "yellow", "green", "cyan", "blue", "purple", "magenta"]
    for color in colores:
        console.print(f"  [{color}]████[/{color}] {color}")

    # Objeto Text para manipulación programática
    texto = Text()
    texto.append("Texto ", style="bold")
    texto.append("multi", style="red bold")
    texto.append("color", style="blue bold")
    texto.append(" con Rich", style="green")
    console.print(f"\n{texto}")


# =============================================================================
# SECCIÓN 2: Tablas — Datos tabulares con estilo
# =============================================================================

def demo_tablas():
    """Muestra cómo crear tablas profesionales con Rich."""
    console.rule("[bold blue]2. Tablas Profesionales")

    # Tabla básica
    tabla = Table(
        title="Ranking de Lenguajes de Programación",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold blue"
    )

    # Definir columnas
    tabla.add_column("Posición", style="cyan", justify="right", width=10)
    tabla.add_column("Lenguaje", style="bold")
    tabla.add_column("Popularidad", justify="center")
    tabla.add_column("Uso Principal", style="dim")

    # Datos
    datos = [
        ("🥇 1", "Python", "████████░░ 85%", "Data Science, Web, IA"),
        ("🥈 2", "JavaScript", "███████░░░ 72%", "Web Frontend/Backend"),
        ("🥉 3", "Java", "██████░░░░ 60%", "Empresarial, Android"),
        ("4", "TypeScript", "█████░░░░░ 55%", "Web con tipado fuerte"),
        ("5", "Rust", "███░░░░░░░ 32%", "Sistemas, Performance"),
        ("6", "Go", "███░░░░░░░ 30%", "Microservicios, Cloud"),
    ]

    # Alternar colores en las filas para legibilidad
    for i, (pos, lang, pop, uso) in enumerate(datos):
        estilo_fila = "on grey11" if i % 2 == 0 else ""
        tabla.add_row(pos, lang, pop, uso, style=estilo_fila)

    console.print(tabla)

    # Tabla de métricas de sistema
    console.print()
    tabla_metricas = Table(box=box.SIMPLE_HEAD, title="Métricas del Sistema (simuladas)")
    tabla_metricas.add_column("Métrica", style="bold")
    tabla_metricas.add_column("Valor", justify="right")
    tabla_metricas.add_column("Estado", justify="center")

    metricas = [
        ("CPU Usage", "45%", "[green]OK[/green]"),
        ("RAM Usage", "78%", "[yellow]ALTO[/yellow]"),
        ("Disco /", "92%", "[red]CRÍTICO[/red]"),
        ("Red (MB/s)", "12.4", "[green]OK[/green]"),
        ("Temp. CPU", "65°C", "[green]OK[/green]"),
    ]
    for metrica, valor, estado in metricas:
        tabla_metricas.add_row(metrica, valor, estado)

    console.print(tabla_metricas)


# =============================================================================
# SECCIÓN 3: Paneles y layouts
# =============================================================================

def demo_paneles():
    """Muestra paneles y layouts para organizar información."""
    console.rule("[bold blue]3. Paneles y Layouts")

    # Panel simple
    console.print(Panel(
        "[bold green]✓ Despliegue exitoso[/bold green]\n"
        "Versión: [cyan]2.4.1[/cyan]\n"
        "Entorno: [yellow]Producción[/yellow]\n"
        "Tiempo: [blue]0.842s[/blue]",
        title="Estado del Deploy",
        subtitle="hace 2 minutos",
        border_style="green"
    ))

    # Panel de error
    console.print(Panel(
        "[bold]TypeError:[/bold] 'NoneType' object is not subscriptable\n"
        "  File [cyan]app.py[/cyan], line [yellow]142[/yellow], in [green]process_data[/green]\n"
        "    result = data['value']\n"
        "[dim]Verifica que 'data' no sea None antes de acceder a sus claves.[/dim]",
        title="[red]Error Encontrado[/red]",
        border_style="red"
    ))

    # Múltiples paneles en columnas
    cards = [
        Panel(f"[bold cyan]7,842[/bold cyan]\n[dim]Visitantes hoy[/dim]", border_style="cyan"),
        Panel(f"[bold green]€24,500[/bold green]\n[dim]Ventas del día[/dim]", border_style="green"),
        Panel(f"[bold yellow]156[/bold yellow]\n[dim]Pedidos activos[/dim]", border_style="yellow"),
        Panel(f"[bold red]3[/bold red]\n[dim]Errores críticos[/dim]", border_style="red"),
    ]
    console.print(Columns(cards))


# =============================================================================
# SECCIÓN 4: Syntax Highlighting — Código con color
# =============================================================================

def demo_syntax():
    """Muestra syntax highlighting para código."""
    console.rule("[bold blue]4. Syntax Highlighting")

    codigo_python = '''
def calcular_factorial(n: int) -> int:
    """Calcula el factorial de n de forma recursiva."""
    if n < 0:
        raise ValueError(f"n debe ser >= 0, recibido: {n}")
    if n == 0:
        return 1
    return n * calcular_factorial(n - 1)

# Ejemplo de uso
resultado = calcular_factorial(10)
print(f"10! = {resultado:,}")
'''

    syntax = Syntax(
        codigo_python,
        "python",
        theme="monokai",     # Tema de color (similar a VS Code Dark+)
        line_numbers=True,   # Mostrar números de línea
        word_wrap=True
    )

    console.print(Panel(syntax, title="[bold]Ejemplo de Código Python[/bold]",
                        border_style="blue"))


# =============================================================================
# SECCIÓN 5: Progress bars — Feedback visual para tareas largas
# =============================================================================

def demo_progress():
    """Muestra barras de progreso y spinners."""
    console.rule("[bold blue]5. Barras de Progreso")

    # Barra de progreso simple
    console.print("\n[bold]Simulando descarga de archivos:[/bold]")

    archivos = [
        ("modelo_ml.pkl", 45_000_000),
        ("dataset.csv", 12_000_000),
        ("config.json", 8_000),
        ("requirements.txt", 2_000),
    ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        tarea_total = progress.add_task("[cyan]Total", total=sum(t for _, t in archivos))

        for nombre, tamaño in archivos:
            tarea = progress.add_task(f"[green]{nombre}", total=tamaño)

            # Simular descarga por bloques
            descargado = 0
            bloque = tamaño // 15
            while descargado < tamaño:
                avance = min(bloque, tamaño - descargado)
                time.sleep(0.03)  # Simular tiempo de red
                progress.advance(tarea, avance)
                progress.advance(tarea_total, avance)
                descargado += avance

    console.print("[bold green]✓ Todos los archivos descargados[/bold green]")


# =============================================================================
# SECCIÓN 6: Logging con Rich — Reemplazar el logging estándar
# =============================================================================

def demo_logging():
    """Muestra cómo usar Rich como handler de logging."""
    console.rule("[bold blue]6. Logging con Rich")

    # Configurar logging con RichHandler
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )

    log = logging.getLogger("mi_aplicacion")

    log.debug("Iniciando módulo de procesamiento")
    log.info("Conexión a base de datos establecida")
    log.warning("El caché está al 80% de capacidad")
    log.error("No se pudo escribir en el directorio /tmp")

    console.print("\n[dim]Los logs incluyen nivel, hora y nombre del módulo automáticamente.[/dim]")


# =============================================================================
# REPORTE FINAL: Combinar todo en un reporte visual
# =============================================================================

def generar_reporte():
    """Genera un reporte visual completo combinando todas las capacidades."""
    console.rule("[bold blue]REPORTE VISUAL DE SISTEMA")

    # Header del reporte
    console.print(Panel(
        "[bold white]Reporte de Estado del Sistema[/bold white]\n"
        f"[dim]Generado por Rich Python — {time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="blue"
    ))

    # Tabla de resumen
    tabla_resumen = Table(box=box.DOUBLE_EDGE, show_header=True)
    tabla_resumen.add_column("Módulo", style="bold")
    tabla_resumen.add_column("Estado", justify="center")
    tabla_resumen.add_column("Última ejecución")
    tabla_resumen.add_column("Siguiente ejecución")

    servicios = [
        ("Backup", "[green]✓ OK[/green]", "hace 2h", "en 22h"),
        ("Monitor de logs", "[green]✓ OK[/green]", "hace 5m", "en 5m"),
        ("Limpieza de caché", "[yellow]⚠ LENTO[/yellow]", "hace 1d", "en 23h"),
        ("Sync BD réplica", "[red]✗ ERROR[/red]", "hace 4h", "Reintentando..."),
    ]

    for servicio, estado, ultima, siguiente in servicios:
        tabla_resumen.add_row(servicio, estado, ultima, siguiente)

    console.print(tabla_resumen)

    # Árbol de archivos
    arbol = Tree("[bold blue]Proyecto")
    src = arbol.add("[bold green]src/")
    src.add("main.py")
    src.add("utils.py")
    tests = arbol.add("[bold yellow]tests/")
    tests.add("test_main.py")
    arbol.add("[dim].gitignore")
    arbol.add("[dim]requirements.txt")
    arbol.add("[dim]README.md")

    console.print("\n[bold]Estructura del proyecto:[/bold]")
    console.print(arbol)

    console.print(Panel(
        "[bold green]Reporte completado.[/bold green]\n"
        "Guarda este output con: [cyan]python 03_rich.py > reporte.txt[/cyan]",
        border_style="green"
    ))


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    console.print(Panel(
        "[bold]Rich — Terminal Profesional con Python[/bold]\n"
        "[dim]pip install rich[/dim]",
        border_style="bright_blue"
    ))

    demo_texto()
    console.print()
    demo_tablas()
    console.print()
    demo_paneles()
    console.print()
    demo_syntax()
    console.print()
    demo_progress()
    console.print()
    demo_logging()
    console.print()
    generar_reporte()

    console.print(f"\n[bold]Fin de la demostración de Rich[/bold]")
    console.print("[dim]Continúa con 04_scripts_utiles.py[/dim]")
