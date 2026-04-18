# =============================================================================
# 05_automatizacion_web.py — Automatización de escritorio y sistema
# =============================================================================
# Python puede controlar el escritorio: mover el mouse, hacer clic,
# escribir texto, tomar capturas de pantalla y ejecutar programas.
#
# Instalación:
#   pip install pyautogui
#
# ADVERTENCIA DE SEGURIDAD CON PYAUTOGUI:
#   - pyautogui mueve el mouse y escribe en la ventana activa
#   - Para detenerlo de emergencia: mueve el mouse a la esquina
#     superior IZQUIERDA de la pantalla (activa FailSafe)
#   - NO ejecutes código pyautogui sin entender qué hace
#   - Cierra aplicaciones importantes antes de probar
#
# Módulos cubiertos:
#   pyautogui  — control de mouse, teclado y pantalla (pip install pyautogui)
#   webbrowser — abrir URLs en el navegador predeterminado (incluido)
#   subprocess — ejecutar comandos del sistema (incluido)
#   os         — variables de entorno, info del sistema (incluido)
# =============================================================================

import webbrowser
import subprocess
import os
import sys
import time
import platform
from pathlib import Path

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    # Configurar pausa entre acciones para seguridad
    # pyautogui.PAUSE pausa N segundos entre cada acción automáticamente
    pyautogui.PAUSE = 0.5
    # FAILSAFE: mover mouse a esquina superior izquierda cancela todo
    pyautogui.FAILSAFE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


# =============================================================================
# WEBBROWSER — Abrir URLs en el navegador
# =============================================================================

def demo_webbrowser():
    """
    Demuestra el módulo webbrowser para abrir URLs.

    webbrowser es la forma más simple de abrir URLs desde Python.
    Usa el navegador predeterminado del sistema.
    No requiere instalación, viene con Python.
    """
    print("\n--- webbrowser: Abrir URLs ---")

    # Mostrar el navegador que se usaría
    print(f"  Navegador registrado: {webbrowser.get().name}")

    print("""
  Funciones principales de webbrowser:

  # Abrir URL en el navegador predeterminado
  webbrowser.open("https://python.org")

  # Abrir en una nueva ventana
  webbrowser.open_new("https://python.org")

  # Abrir en una nueva pestaña
  webbrowser.open_new_tab("https://docs.python.org")

  # Abrir con un navegador específico
  chrome = webbrowser.get("chrome")
  chrome.open("https://python.org")

  Casos de uso reales:
  - Abrir documentación automáticamente después de instalar un paquete
  - Abrir el reporte generado en el navegador al terminar de crearlo
  - Abrir la URL de un resultado de API para inspección rápida
  - Launcher de aplicaciones web internas
    """)

    # Ejemplo: generar un reporte HTML y abrirlo
    # (no abrimos el navegador realmente para no interrumpir al usuario)
    print("  Ejemplo: generar HTML y abrirlo")
    print("    html_path = Path('reporte.html')")
    print("    html_path.write_text('<h1>Reporte</h1>')")
    print("    webbrowser.open(html_path.as_uri())")
    print("    # as_uri() convierte la ruta a URL de archivo: file:///...")


# =============================================================================
# SUBPROCESS — Ejecutar comandos del sistema
# =============================================================================

def demo_subprocess():
    """
    Demuestra subprocess para ejecutar comandos del sistema operativo.

    subprocess es la forma correcta de ejecutar programas externos desde Python.
    Reemplaza a os.system() con mucho más control sobre la ejecución.

    Conceptos:
    - subprocess.run()     → ejecutar y esperar a que termine
    - subprocess.Popen()   → ejecutar en background (no espera)
    - capture_output=True  → capturar stdout y stderr como strings
    - check=True           → lanzar excepción si el comando falla (código != 0)
    """
    print("\n--- subprocess: Ejecutar comandos del sistema ---")

    # Detectar el sistema operativo para usar comandos correctos
    is_windows = platform.system() == "Windows"
    is_mac     = platform.system() == "Darwin"
    is_linux   = platform.system() == "Linux"

    print(f"  Sistema operativo: {platform.system()} {platform.release()}")

    # -------------------------------------------------------------------------
    # Ejemplo 1: Ejecutar un comando y capturar su salida
    # -------------------------------------------------------------------------
    print("\n  [1] Capturar salida de un comando:")

    # Comando multiplataforma para listar directorio actual
    if is_windows:
        cmd = ["cmd", "/c", "echo", "Hola desde subprocess en Windows"]
    else:
        cmd = ["echo", "Hola desde subprocess en Linux/Mac"]

    result = subprocess.run(
        cmd,
        capture_output=True,  # captura stdout y stderr
        text=True,            # decodifica bytes a string automáticamente
        timeout=10            # timeout de seguridad
    )

    print(f"    Comando: {' '.join(cmd)}")
    print(f"    Salida: {result.stdout.strip()}")
    print(f"    Código de retorno: {result.returncode}  (0 = éxito)")

    # -------------------------------------------------------------------------
    # Ejemplo 2: Obtener información del sistema
    # -------------------------------------------------------------------------
    print("\n  [2] Información del sistema:")

    if is_windows:
        # En Windows: ver versión de Python instalada
        py_result = subprocess.run(
            ["python", "--version"],
            capture_output=True, text=True, timeout=10
        )
        print(f"    Python: {py_result.stdout.strip() or py_result.stderr.strip()}")

        # Espacio en disco
        disk_result = subprocess.run(
            ["fsutil", "volume", "diskfree", "C:"],
            capture_output=True, text=True, timeout=10
        )
        lines = disk_result.stdout.strip().split("\n")
        for line in lines[:2]:
            if line.strip():
                print(f"    Disco: {line.strip()}")
    else:
        # Linux/Mac: df para espacio en disco
        df_result = subprocess.run(
            ["df", "-h", "/"],
            capture_output=True, text=True, timeout=10
        )
        lines = df_result.stdout.strip().split("\n")
        for line in lines[:2]:
            print(f"    {line}")

    # -------------------------------------------------------------------------
    # Ejemplo 3: Manejo de errores en subprocess
    # -------------------------------------------------------------------------
    print("\n  [3] Manejo de errores:")

    try:
        # Intentar ejecutar un comando que no existe
        result = subprocess.run(
            ["comando_que_no_existe_xyz"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True   # lanza CalledProcessError si código != 0
        )
    except FileNotFoundError:
        print("    FileNotFoundError: el comando no existe en el PATH")
    except subprocess.CalledProcessError as e:
        print(f"    CalledProcessError: código {e.returncode}")
    except subprocess.TimeoutExpired:
        print("    TimeoutExpired: el comando tardó demasiado")

    # -------------------------------------------------------------------------
    # Ejemplo 4: Ejecutar script Python desde Python
    # -------------------------------------------------------------------------
    print("\n  [4] Ejecutar otro script Python:")
    print("    # Forma recomendada para llamar a otro script Python:")
    print("    result = subprocess.run(")
    print("        [sys.executable, 'otro_script.py', '--arg1', 'valor'],")
    print("        capture_output=True, text=True")
    print("    )")
    print(f"    # sys.executable = {sys.executable}")

    # -------------------------------------------------------------------------
    # Ejemplo 5: Proceso en background (no bloquea)
    # -------------------------------------------------------------------------
    print("\n  [5] Proceso en background con Popen:")
    print("    # Popen inicia el proceso pero NO espera a que termine")
    print("    proceso = subprocess.Popen(['python', 'mi_script.py'])")
    print("    print('El proceso corre en background')")
    print("    proceso.wait()   # esperar cuando lo necesites")
    print("    proceso.kill()   # o matar el proceso")


# =============================================================================
# PYAUTOGUI — Control de mouse y teclado
# =============================================================================

def demo_pyautogui_conceptual():
    """
    Explica los conceptos de PyAutoGUI de forma educativa.
    Se usa cuando PyAutoGUI no está instalado o como referencia.
    """
    print("""
--- PyAutoGUI: Control de mouse, teclado y pantalla ---

PyAutoGUI permite automatizar cualquier tarea de escritorio:
mover el mouse, hacer clic, escribir texto, tomar capturas.

SEGURIDAD:
  - FAILSAFE: mueve el mouse a la esquina superior izquierda para cancelar
  - PAUSE: pyautogui.PAUSE = 1.0 pausa 1 segundo entre cada acción
  - Siempre prueba con valores de posición correctos antes

MOUSE:
  pyautogui.moveTo(x, y)           → mover a posición absoluta
  pyautogui.moveTo(x, y, duration=1) → mover en 1 segundo (suave)
  pyautogui.moveRel(dx, dy)        → mover relativo a posición actual
  pyautogui.click(x, y)            → clic izquierdo
  pyautogui.rightClick(x, y)       → clic derecho
  pyautogui.doubleClick(x, y)      → doble clic
  pyautogui.dragTo(x, y)           → arrastrar a posición
  pyautogui.scroll(10)             → scroll hacia arriba
  pyautogui.position()             → posición actual del mouse

TECLADO:
  pyautogui.write("texto")         → escribir texto
  pyautogui.press("enter")         → presionar una tecla
  pyautogui.hotkey("ctrl", "c")    → atajo de teclado (copiar)
  pyautogui.hotkey("ctrl", "v")    → pegar
  pyautogui.hotkey("alt", "tab")   → cambiar ventana

PANTALLA:
  screenshot = pyautogui.screenshot()  → tomar captura
  screenshot.save("captura.png")
  x, y = pyautogui.locateCenterOnScreen("boton.png")  → buscar imagen
  pyautogui.click(x, y)

TECLAS ESPECIALES:
  "enter", "esc", "tab", "backspace", "delete"
  "up", "down", "left", "right"
  "f1"-"f12", "home", "end", "pageup", "pagedown"
  "ctrl", "alt", "shift", "win"

EJEMPLO: Abrir Bloc de notas en Windows y escribir texto
  pyautogui.hotkey("win", "r")          # Win + R (Ejecutar)
  time.sleep(1)
  pyautogui.write("notepad", interval=0.05)
  pyautogui.press("enter")
  time.sleep(2)
  pyautogui.write("Texto escrito automáticamente", interval=0.03)
  pyautogui.hotkey("ctrl", "s")         # Guardar
    """)


def demo_pyautogui_info():
    """
    Si PyAutoGUI está instalado, muestra información de la pantalla.
    No hace movimientos para no interrumpir al usuario.
    """
    if not PYAUTOGUI_AVAILABLE:
        print("  pyautogui no está instalado.")
        print("  Instala con: pip install pyautogui")
        return

    print("\n--- PyAutoGUI: Info de pantalla (sin mover el mouse) ---")

    # Tamaño de la pantalla
    width, height = pyautogui.size()
    print(f"  Resolución de pantalla: {width} x {height} px")

    # Posición actual del mouse
    x, y = pyautogui.position()
    print(f"  Posición actual del mouse: ({x}, {y})")

    # Tomar una captura de pantalla (sin guardarla para no crear archivos)
    screenshot = pyautogui.screenshot()
    print(f"  Captura tomada: {screenshot.width} x {screenshot.height} px")
    print(f"  Modo de color: {screenshot.mode}")

    print("\n  FAILSAFE activo: mueve el mouse a la esquina superior izquierda")
    print("  para cancelar cualquier automatización en progreso.")


def demo_pyautogui_safe_example():
    """
    Ejemplo seguro de PyAutoGUI: solo captura pantalla y muestra posición.
    No mueve el mouse ni hace clics para no interrumpir al usuario.
    """
    if not PYAUTOGUI_AVAILABLE:
        return

    print("\n--- Ejemplo seguro: captura de pantalla ---")
    print("  (No se mueve el mouse ni se hacen clics)")

    try:
        # Captura de pantalla segura
        import tempfile
        screenshot = pyautogui.screenshot()

        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(
            suffix=".png", delete=False, prefix="pyautogui_demo_"
        ) as tmp:
            tmp_path = tmp.name

        screenshot.save(tmp_path)
        size = Path(tmp_path).stat().st_size
        print(f"  Captura guardada temporalmente: {Path(tmp_path).name}")
        print(f"  Tamaño del archivo: {size:,} bytes")

        # Mostrar un pixel del centro de la pantalla
        w, h = pyautogui.size()
        center_x, center_y = w // 2, h // 2
        pixel_color = pyautogui.pixel(center_x, center_y)
        print(f"  Color del pixel central ({center_x}, {center_y}): RGB{pixel_color}")

        # Limpiar
        os.unlink(tmp_path)
        print(f"  Archivo temporal eliminado.")

    except Exception as e:
        print(f"  Error en demo de captura: {e}")


# =============================================================================
# CASO PRÁCTICO: AUTOMATIZACIÓN COMBINADA
# =============================================================================

def demo_automation_pipeline():
    """
    Demuestra un pipeline de automatización que combina varias herramientas.

    Caso de uso: generación y apertura de un reporte HTML.
    Usa solo herramientas incluidas con Python (no requiere instalación extra).
    """
    print("\n--- Pipeline práctico: Generar y abrir reporte HTML ---")

    import tempfile
    import json

    # Paso 1: Simular datos obtenidos (podrían venir de una DB, API, etc.)
    data = {
        "titulo":    "Reporte de Automatización",
        "fecha":     time.strftime("%d/%m/%Y %H:%M"),
        "sistema":   platform.system(),
        "python":    sys.version.split()[0],
        "metricas": [
            {"nombre": "Archivos procesados", "valor": 142},
            {"nombre": "Errores encontrados", "valor": 3},
            {"nombre": "Tiempo de ejecución", "valor": "2.4 segundos"},
            {"nombre": "Tasa de éxito",        "valor": "97.9%"},
        ]
    }

    # Paso 2: Generar HTML del reporte
    metricas_html = "".join(
        f"<tr><td>{m['nombre']}</td><td><strong>{m['valor']}</strong></td></tr>"
        for m in data["metricas"]
    )

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{data['titulo']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; }}
        h1 {{ color: #2E4057; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #2E4057; color: white; padding: 10px; }}
        td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
        .meta {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>{data['titulo']}</h1>
    <p class="meta">Generado: {data['fecha']} | Sistema: {data['sistema']} | Python {data['python']}</p>
    <table>
        <tr><th>Métrica</th><th>Valor</th></tr>
        {metricas_html}
    </table>
    <p><em>Generado automáticamente con Python.</em></p>
</body>
</html>"""

    # Paso 3: Guardar el reporte en archivo temporal
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False,
        prefix="reporte_", encoding="utf-8"
    ) as tmp:
        tmp.write(html_content)
        report_path = Path(tmp.name)

    print(f"  Reporte generado: {report_path.name}")
    print(f"  Tamaño: {report_path.stat().st_size} bytes")

    # Paso 4: Preguntar al usuario si quiere abrir el reporte
    print(f"\n  Para abrir el reporte en tu navegador ejecuta:")
    print(f"    import webbrowser")
    print(f"    webbrowser.open(r'{report_path}')")

    # Apertura automática comentada para no interrumpir la demo
    # webbrowser.open(report_path.as_uri())

    # Limpiar
    report_path.unlink()
    print(f"  Archivo temporal eliminado.")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal que demuestra todas las herramientas de automatización."""

    print("=" * 60)
    print("  DEMO: Automatización Web y de Escritorio")
    print("=" * 60)

    print(f"\nSistema: {platform.system()} {platform.release()}")
    print(f"Python:  {sys.version.split()[0]}")

    demo_webbrowser()
    demo_subprocess()

    print("\n" + "=" * 60)
    print("  PyAutoGUI — Automatización de GUI")
    print("=" * 60)

    if PYAUTOGUI_AVAILABLE:
        print(f"\n  pyautogui instalado. Versión: {pyautogui.__version__}")
        demo_pyautogui_info()
        demo_pyautogui_safe_example()
    else:
        print("\n  pyautogui NO está instalado.")
        print("  Instala con: pip install pyautogui")

    # Mostrar conceptos siempre, esté o no instalado
    demo_pyautogui_conceptual()

    demo_automation_pipeline()

    print("\n" + "=" * 60)
    print("  Demo completado.")
    print("=" * 60)


if __name__ == "__main__":
    main()
