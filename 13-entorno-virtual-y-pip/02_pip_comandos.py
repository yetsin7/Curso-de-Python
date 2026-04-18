"""
Capítulo 13 — Entorno Virtual y pip
Archivo: 02_pip_comandos.py

Uso de pip desde Python con subprocess.

Este script demuestra cómo interactuar con pip programáticamente
usando el módulo subprocess. No instala ni desinstala nada —
solo ejecuta comandos de CONSULTA para que veas los resultados
reales de tu entorno actual.

Por qué usar subprocess en lugar de importar pip directamente:
    pip no tiene una API pública estable para usarse como librería.
    La recomendación oficial de los desarrolladores de pip es
    invocarlo como un subproceso: subprocess.run([sys.executable, "-m", "pip", ...])

Ejecución:
    python 02_pip_comandos.py
"""

import subprocess   # Para ejecutar comandos del sistema (pip) como subproceso
import sys          # Para obtener la ruta al ejecutable Python actual
import json         # Para parsear la salida JSON de algunos comandos pip


# ==============================================================
# FUNCIÓN AUXILIAR: ejecutar un comando pip y capturar su salida
# ==============================================================

def run_pip(*args):
    """
    Ejecuta pip como subproceso usando el mismo intérprete Python
    que está corriendo este script.

    Por qué usamos sys.executable en lugar de simplemente "python":
        En un entorno virtual, "python" puede apuntar a distintos
        ejecutables según el sistema operativo y la configuración del PATH.
        sys.executable SIEMPRE apunta al Python correcto, garantizando
        que pip use el entorno virtual activo.

    Args:
        *args: argumentos adicionales para pip (ej: "list", "--format=json")

    Returns:
        str: la salida estándar del comando, o un mensaje de error.
    """
    # Construimos el comando: python -m pip <arg1> <arg2> ...
    # "-m pip" es la forma recomendada de invocar pip para evitar
    # problemas con el PATH y entornos virtuales
    command = [sys.executable, "-m", "pip"] + list(args)

    try:
        resultado = subprocess.run(
            command,
            capture_output=True,    # Captura stdout y stderr (no imprime en pantalla)
            text=True,              # Decodifica la salida como texto (str, no bytes)
            check=False             # No lanza excepción si el comando falla (código != 0)
        )
        # Si hubo error, devolvemos stderr para que sea visible
        if resultado.returncode != 0 and resultado.stderr:
            return f"[ERROR] {resultado.stderr.strip()}"
        return resultado.stdout.strip()
    except FileNotFoundError:
        return "[ERROR] No se encontró el ejecutable Python/pip"
    except Exception as e:
        return f"[ERROR inesperado] {e}"


# ==============================================================
# SECCIÓN 1: Versión de pip instalada
# ==============================================================

def show_pip_version():
    """
    Muestra la versión de pip disponible en el entorno actual.
    Útil para saber si pip está actualizado.
    """
    print("=" * 60)
    print("  VERSIÓN DE pip")
    print("=" * 60)
    version = run_pip("--version")
    print(f"\n  {version}\n")


# ==============================================================
# SECCIÓN 2: Listar todos los paquetes instalados
# ==============================================================

def list_installed_packages():
    """
    Lista todos los paquetes instalados en el entorno actual.
    Usamos --format=json para obtener la salida estructurada
    y poder procesarla fácilmente desde Python.
    """
    print("=" * 60)
    print("  PAQUETES INSTALADOS EN ESTE ENTORNO")
    print("=" * 60)

    # --format=json devuelve una lista JSON: [{"name": "...", "version": "..."}, ...]
    raw_output = run_pip("list", "--format=json")

    if raw_output.startswith("[ERROR]"):
        print(f"\n  {raw_output}\n")
        return []

    try:
        packages = json.loads(raw_output)
        print(f"\n  Total de paquetes instalados: {len(packages)}\n")

        # Mostramos los primeros 20 para no saturar la pantalla
        limit = min(20, len(packages))
        print(f"  {'Paquete':<35} {'Versión':<15}")
        print(f"  {'-'*35} {'-'*15}")

        for pkg in packages[:limit]:
            print(f"  {pkg['name']:<35} {pkg['version']:<15}")

        if len(packages) > limit:
            print(f"\n  ... y {len(packages) - limit} paquetes más.")
            print("  Ejecuta: pip list   para verlos todos")

        return packages
    except json.JSONDecodeError:
        # Si por alguna razón no es JSON válido, mostramos el texto crudo
        print(f"\n{raw_output}\n")
        return []


# ==============================================================
# SECCIÓN 3: Ver paquetes desactualizados
# ==============================================================

def show_outdated_packages():
    """
    Muestra los paquetes que tienen una versión más nueva disponible
    en PyPI (el repositorio oficial de paquetes Python).

    Nota: este comando hace una consulta a internet.
    Si no tienes conexión, mostrará un error de red.
    """
    print("=" * 60)
    print("  PAQUETES CON ACTUALIZACIONES DISPONIBLES")
    print("=" * 60)
    print("\n  (Consultando PyPI, requiere conexión a internet...)\n")

    # --format=json para salida estructurada
    raw_output = run_pip("list", "--outdated", "--format=json")

    if raw_output.startswith("[ERROR]"):
        print(f"  {raw_output}\n")
        return

    if not raw_output or raw_output == "[]":
        print("  Todos los paquetes están actualizados.\n")
        return

    try:
        outdated = json.loads(raw_output)
        if not outdated:
            print("  Todos los paquetes están actualizados.\n")
            return

        print(f"  {'Paquete':<30} {'Instalada':<15} {'Disponible':<15}")
        print(f"  {'-'*30} {'-'*15} {'-'*15}")

        for pkg in outdated:
            print(f"  {pkg['name']:<30} {pkg['version']:<15} {pkg['latest_version']:<15}")

        print(f"\n  Para actualizar: pip install --upgrade <nombre_paquete>\n")
    except json.JSONDecodeError:
        print(f"\n{raw_output}\n")


# ==============================================================
# SECCIÓN 4: Ver información detallada de un paquete
# ==============================================================

def show_package_info(package_name: str):
    """
    Muestra información detallada de un paquete específico:
    versión, autor, descripción, dependencias, ubicación, etc.

    Args:
        package_name: nombre del paquete a inspeccionar.
    """
    print("=" * 60)
    print(f"  INFORMACIÓN DETALLADA: {package_name.upper()}")
    print("=" * 60)

    raw_output = run_pip("show", package_name)

    if raw_output.startswith("[ERROR]") or "WARNING: Package(s) not found" in raw_output:
        print(f"\n  El paquete '{package_name}' no está instalado en este entorno.")
        print(f"  Para instalarlo: pip install {package_name}\n")
        return

    # La salida de 'pip show' es texto plano con formato "Clave: Valor"
    print()
    for line in raw_output.split("\n"):
        print(f"  {line}")
    print()


# ==============================================================
# SECCIÓN 5: Verificar si pip puede ejecutarse correctamente
# ==============================================================

def check_pip_available():
    """
    Verifica que pip esté disponible y funcional en el entorno.
    Devuelve True si pip responde correctamente, False si no.
    """
    output = run_pip("--version")
    return not output.startswith("[ERROR]")


# ==============================================================
# SECCIÓN 6: Comandos pip más usados (referencia impresa)
# ==============================================================

def show_pip_reference():
    """
    Imprime una tabla de referencia rápida con los comandos
    pip más usados en el día a día del desarrollo Python.
    """
    print("=" * 60)
    print("  REFERENCIA RÁPIDA DE COMANDOS pip")
    print("=" * 60)

    comandos = [
        ("pip install requests", "Instala la versión más reciente"),
        ("pip install requests==2.31.0", "Instala versión específica"),
        ("pip install 'requests>=2.28'", "Instala versión mínima"),
        ("pip install -r requirements.txt", "Instala desde archivo"),
        ("pip install --upgrade requests", "Actualiza un paquete"),
        ("pip uninstall requests", "Desinstala un paquete"),
        ("pip list", "Lista paquetes instalados"),
        ("pip list --outdated", "Lista paquetes desactualizados"),
        ("pip show requests", "Info detallada de un paquete"),
        ("pip freeze", "Lista con versiones exactas"),
        ("pip freeze > requirements.txt", "Guarda las dependencias"),
        ("pip install --no-deps X", "Instala sin sus dependencias"),
        ("pip download requests", "Descarga sin instalar"),
        ("pip check", "Verifica compatibilidades"),
    ]

    print()
    for cmd, descripcion in comandos:
        print(f"  {cmd:<45} {descripcion}")
    print()


# ==============================================================
# PUNTO DE ENTRADA
# ==============================================================

if __name__ == "__main__":
    # Verificamos que pip esté disponible antes de continuar
    if not check_pip_available():
        print("[ERROR CRÍTICO] pip no está disponible en este entorno.")
        print("Instala pip o verifica tu instalación de Python.")
        sys.exit(1)

    show_pip_version()
    list_installed_packages()

    # Mostramos info de pip mismo (siempre está instalado)
    # Es un buen ejemplo de 'pip show' con salida garantizada
    show_package_info("pip")

    # setuptools también suele estar siempre disponible
    show_package_info("setuptools")

    # Mostramos paquetes desactualizados (requiere internet)
    show_outdated_packages()

    show_pip_reference()

    print("=" * 60)
    print("  TIP: Para ver info de cualquier paquete instalado,")
    print("  ejecuta: pip show <nombre_del_paquete>")
    print("=" * 60)
