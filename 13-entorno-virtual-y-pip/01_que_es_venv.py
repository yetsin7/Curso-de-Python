"""
Capítulo 13 — Entorno Virtual y pip
Archivo: 01_que_es_venv.py

¿Qué es un entorno virtual y por qué existe?

Este script NO instala nada. Su propósito es mostrar información
real del entorno Python en el que se está ejecutando, para que
puedas entender visualmente la diferencia entre un entorno global
y un entorno virtual activo.

Ejecución:
    python 01_que_es_venv.py
"""

import sys          # Información del intérprete Python
import os           # Variables de entorno del sistema operativo
import sysconfig    # Rutas de configuración de la instalación de Python
import site         # Rutas de site-packages


# ==============================================================
# SECCIÓN 1: Información básica del intérprete Python activo
# ==============================================================

def show_python_info():
    """
    Muestra información sobre el intérprete Python que está
    ejecutando este script. Esto permite ver si estamos dentro
    de un venv o usando Python global del sistema.
    """
    print("=" * 60)
    print("  INFORMACIÓN DEL INTÉRPRETE PYTHON ACTIVO")
    print("=" * 60)

    # sys.executable: ruta absoluta al ejecutable python
    # Si estás en un venv, apuntará a la carpeta del venv.
    # Si estás en global, apuntará a la instalación del sistema.
    print(f"\n  Ejecutable Python : {sys.executable}")

    # sys.version: versión completa del intérprete
    print(f"  Versión           : {sys.version}")

    # sys.version_info: versión en forma de tupla (más fácil de comparar)
    v = sys.version_info
    print(f"  Versión (tupla)   : {v.major}.{v.minor}.{v.micro}")

    # sys.platform: plataforma del sistema operativo
    print(f"  Plataforma        : {sys.platform}")


# ==============================================================
# SECCIÓN 2: Detectar si estamos dentro de un entorno virtual
# ==============================================================

def detect_virtual_environment():
    """
    Detecta si el script se está ejecutando dentro de un entorno
    virtual o en la instalación global de Python.

    Hay dos mecanismos para detectarlo:
    1. sys.prefix vs sys.base_prefix: en un venv, son distintos.
       sys.prefix apunta al venv, sys.base_prefix al Python original.
    2. La variable de entorno VIRTUAL_ENV, que el activador del
       venv establece automáticamente al hacer 'source activate'.
    """
    print("\n" + "=" * 60)
    print("  DETECCIÓN DE ENTORNO VIRTUAL")
    print("=" * 60)

    # sys.prefix: directorio base del entorno activo
    # En venv: apunta a la carpeta del venv (ej: C:\mi-proyecto\venv)
    # En global: apunta a la instalación de Python (ej: C:\Python311)
    print(f"\n  sys.prefix      : {sys.prefix}")

    # sys.base_prefix: directorio base del Python ORIGINAL (sin venv)
    # En venv: sigue apuntando al Python del sistema
    # En global: igual que sys.prefix
    print(f"  sys.base_prefix : {sys.base_prefix}")

    # Si prefix != base_prefix, estamos en un venv
    in_venv = sys.prefix != sys.base_prefix

    if in_venv:
        print("\n  >>> RESULTADO: Estás dentro de un ENTORNO VIRTUAL ✓")
        print(f"  >>> Carpeta del venv: {sys.prefix}")
    else:
        print("\n  >>> RESULTADO: Estás usando Python GLOBAL (sin venv)")
        print("  >>> Recomendación: crea un venv para este proyecto")

    # La variable VIRTUAL_ENV también indica si el venv está activado
    # (la establece el script activate.bat / activate.ps1)
    virtual_env_var = os.environ.get("VIRTUAL_ENV")
    if virtual_env_var:
        print(f"\n  Variable VIRTUAL_ENV : {virtual_env_var}")
    else:
        print("\n  Variable VIRTUAL_ENV : no está definida")

    return in_venv


# ==============================================================
# SECCIÓN 3: Mostrar dónde se instalan los paquetes
# ==============================================================

def show_packages_location():
    """
    Muestra las rutas donde Python busca e instala los paquetes.
    Esta es la razón fundamental de los entornos virtuales:
    cada entorno tiene su propio directorio de paquetes aislado.
    """
    print("\n" + "=" * 60)
    print("  RUTAS DE INSTALACIÓN DE PAQUETES (site-packages)")
    print("=" * 60)

    # site.getsitepackages(): lista de carpetas donde se instalan
    # los paquetes de terceros (lo que haces con 'pip install X')
    try:
        site_packages = site.getsitepackages()
        print("\n  Directorios site-packages:")
        for path in site_packages:
            print(f"    - {path}")
    except AttributeError:
        # En algunos entornos virtuales, getsitepackages puede no estar
        print("  (getsitepackages no disponible en este entorno)")

    # site.getusersitepackages(): carpeta de paquetes del usuario actual
    # (cuando instalas con 'pip install --user X')
    try:
        user_site = site.getusersitepackages()
        print(f"\n  Paquetes del usuario: {user_site}")
    except AttributeError:
        print("  (getusersitepackages no disponible en este entorno)")


# ==============================================================
# SECCIÓN 4: Mostrar sys.path — cómo Python encuentra módulos
# ==============================================================

def show_sys_path():
    """
    sys.path es la lista de directorios donde Python busca módulos
    cuando haces 'import algo'. El orden importa: Python busca
    de izquierda a derecha y usa el primero que encuentre.

    En un entorno virtual, la carpeta site-packages del venv
    aparece antes que la del sistema, garantizando el aislamiento.
    """
    print("\n" + "=" * 60)
    print("  sys.path — DÓNDE BUSCA PYTHON LOS MÓDULOS")
    print("=" * 60)
    print()

    for i, path in enumerate(sys.path):
        # Mostramos cada ruta con su índice para ver la prioridad
        label = ""
        if path == "":
            label = "  ← directorio actual del script"
        elif "site-packages" in path:
            label = "  ← aquí se instalan los paquetes"
        print(f"  [{i}] {path}{label}")


# ==============================================================
# SECCIÓN 5: Explicación conceptual del problema sin venv
# ==============================================================

def explain_the_problem():
    """
    Explica con un ejemplo concreto por qué los entornos virtuales
    son imprescindibles. No ejecuta nada real, solo imprime
    el razonamiento para que quede claro.
    """
    print("\n" + "=" * 60)
    print("  EL PROBLEMA QUE RESUELVEN LOS ENTORNOS VIRTUALES")
    print("=" * 60)

    explicacion = """
  Escenario sin entorno virtual:
  ┌─────────────────────────────────────────────────┐
  │ Sistema Python Global                           │
  │   site-packages/                                │
  │     requests-2.20.0/   ← instalado para         │
  │                           proyecto_viejo        │
  └─────────────────────────────────────────────────┘

  Ahora instalas requests para tu proyecto nuevo:
    pip install requests==2.31.0

  ┌─────────────────────────────────────────────────┐
  │ Sistema Python Global                           │
  │   site-packages/                                │
  │     requests-2.31.0/   ← ¡la versión anterior  │
  │                           fue REEMPLAZADA!      │
  └─────────────────────────────────────────────────┘

  proyecto_viejo puede dejar de funcionar.
  Esto es "dependency hell".

  ─────────────────────────────────────────────────

  Escenario CON entornos virtuales:
  ┌────────────────────────┐  ┌────────────────────────┐
  │ venv de proyecto_viejo │  │ venv de proyecto_nuevo │
  │   site-packages/       │  │   site-packages/       │
  │     requests-2.20.0/   │  │     requests-2.31.0/   │
  └────────────────────────┘  └────────────────────────┘

  Cada proyecto tiene sus propias versiones.
  No interfieren entre sí. Siempre funciona.
    """
    print(explicacion)


# ==============================================================
# SECCIÓN 6: Cómo crear un venv (instrucciones impresas)
# ==============================================================

def show_venv_commands():
    """
    Imprime los comandos necesarios para crear y usar un entorno
    virtual. Útil como referencia rápida.
    """
    print("=" * 60)
    print("  COMANDOS PARA GESTIONAR ENTORNOS VIRTUALES")
    print("=" * 60)

    comandos = {
        "Crear venv": "python -m venv venv",
        "Activar (Windows CMD)": r"venv\Scripts\activate.bat",
        "Activar (Windows PS)": r"venv\Scripts\Activate.ps1",
        "Activar (Mac/Linux)": "source venv/bin/activate",
        "Verificar activación": "where python  (Windows) / which python (Mac/Linux)",
        "Desactivar": "deactivate",
        "Borrar venv": "Simplemente borra la carpeta venv/",
    }

    print()
    for accion, comando in comandos.items():
        print(f"  {accion:<30} {comando}")

    print()


# ==============================================================
# PUNTO DE ENTRADA
# ==============================================================

if __name__ == "__main__":
    # Ejecutamos todas las funciones en orden lógico
    show_python_info()
    in_venv = detect_virtual_environment()
    show_packages_location()
    show_sys_path()
    explain_the_problem()
    show_venv_commands()

    # Consejo final según el estado detectado
    print("=" * 60)
    if in_venv:
        print("  CONSEJO: Tienes un entorno virtual activo. ¡Perfecto!")
        print("  Puedes instalar paquetes con: pip install <nombre>")
    else:
        print("  CONSEJO: Considera crear un entorno virtual antes de")
        print("  instalar paquetes para este proyecto.")
        print("  Comando: python -m venv venv")
    print("=" * 60)
