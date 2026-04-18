"""
Capítulo 13 — Entorno Virtual y pip
Archivo: 03_requirements.py

requirements.txt y pyproject.toml — gestión de dependencias.

Este script:
1. Explica el formato de requirements.txt con ejemplos detallados
2. Genera un archivo requirements.txt de ejemplo con comentarios
3. Explica pyproject.toml como el estándar moderno
4. Genera un pyproject.toml de ejemplo

No instala nada ni modifica el entorno Python.

Ejecución:
    python 03_requirements.py
"""

import os       # Para crear directorios y gestionar rutas
import sys      # Para obtener info del entorno actual


# ==============================================================
# CONSTANTES: rutas de salida de los archivos generados
# ==============================================================

# Directorio donde se generarán los archivos de ejemplo
# Usamos el directorio del script para no escribir en lugares inesperados
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Nombre de los archivos que generaremos
OUTPUT_REQUIREMENTS = os.path.join(SCRIPT_DIR, "ejemplo_requirements.txt")
OUTPUT_PYPROJECT = os.path.join(SCRIPT_DIR, "ejemplo_pyproject.toml")


# ==============================================================
# SECCIÓN 1: Explicar el formato de requirements.txt
# ==============================================================

def explain_requirements_format():
    """
    Imprime una explicación detallada del formato de requirements.txt,
    incluyendo todos los operadores de versión disponibles y cuándo
    usar cada uno.
    """
    print("=" * 60)
    print("  ¿QUÉ ES requirements.txt?")
    print("=" * 60)

    explicacion = """
  requirements.txt es un archivo de texto plano que lista
  los paquetes Python que tu proyecto necesita para funcionar.

  Es el mecanismo estándar para compartir dependencias entre
  desarrolladores y para despliegues en producción.

  ┌──────────────────────────────────────────────────────┐
  │  OPERADORES DE VERSIÓN                               │
  │                                                      │
  │  requests          → última versión disponible       │
  │  requests==2.31.0  → versión EXACTA (recomendado)    │
  │  requests>=2.28.0  → versión mínima                  │
  │  requests<=2.31.0  → versión máxima                  │
  │  requests~=2.28.0  → compatible con 2.28.x           │
  │  requests!=2.29.0  → excluye esta versión específica │
  │  requests>=2.28,<3 → rango de versiones              │
  └──────────────────────────────────────────────────────┘

  OPERADOR ~= (compatible release):
    ~=2.28.0  equivale a  >=2.28.0, ==2.28.*
    ~=2.28    equivale a  >=2.28,   ==2.*

    Es útil cuando quieres aceptar parches pero no versiones
    mayores que puedan romper la API.

  CUÁNDO USAR VERSIONES EXACTAS vs RANGOS:
    - requirements.txt para DESPLIEGUE → versiones exactas (==)
      Reproducibilidad total. El mismo código siempre.
    - pyproject.toml para LIBRERÍA → rangos (>=, ~=)
      Flexibilidad para que otros proyectos usen tu librería.
    """
    print(explicacion)


# ==============================================================
# SECCIÓN 2: Generar un requirements.txt de ejemplo
# ==============================================================

def generate_requirements_file():
    """
    Genera un archivo requirements.txt de ejemplo bien comentado
    que ilustra las buenas prácticas de gestión de dependencias.

    El archivo generado es funcional — pip podría instalarlo,
    aunque los paquetes son de ejemplo genérico.
    """
    print("=" * 60)
    print("  GENERANDO: ejemplo_requirements.txt")
    print("=" * 60)

    # Contenido del requirements.txt con comentarios explicativos
    # Los comentarios en requirements.txt se escriben con #
    contenido = """\
# ==============================================================
# requirements.txt — Dependencias del proyecto MiAplicacion
# ==============================================================
#
# Cómo usar este archivo:
#   pip install -r requirements.txt
#
# Cómo regenerarlo desde el entorno activo:
#   pip freeze > requirements.txt
#
# IMPORTANTE: Este archivo debe subirse al repositorio.
# La carpeta venv/ NO debe subirse (agrégala al .gitignore).
# ==============================================================

# --- Dependencias principales ---

# Cliente HTTP para hacer requests a APIs externas
# Versión exacta para garantizar comportamiento reproducible
requests==2.31.0

# Manipulación de datos en formato tabular (tablas, CSVs, etc.)
# Usamos rango para aceptar parches de seguridad automáticamente
numpy>=1.26.0,<2.0.0

# Framework web ligero para la API REST
Flask==3.0.0

# ORM para base de datos - interacción con PostgreSQL/SQLite
SQLAlchemy==2.0.23

# Validación de datos y configuración (settings con tipos)
pydantic==2.5.0

# --- Dependencias de desarrollo (solo para el equipo) ---
# Convención: separar dev deps con comentario claro
# Para instalar solo las de producción, usa un archivo separado:
#   requirements-prod.txt  → solo las de arriba
#   requirements-dev.txt   → incluye requirements-prod.txt + las de abajo

# Formateador de código - garantiza estilo consistente en el equipo
black==23.11.0

# Linter - detecta errores y malas prácticas en el código
flake8==6.1.0

# Verificador de tipos estáticos
mypy==1.7.1

# Framework de testing
pytest==7.4.3
pytest-cov==4.1.0  # Cobertura de código con pytest

# --- Paquetes con URLs directas (cuando no están en PyPI) ---
# Instalar desde un repositorio git (rama específica):
# git+https://github.com/usuario/repo.git@main#egg=nombre_paquete

# Instalar desde una ruta local (útil en monorepos):
# -e ../mi-libreria-local

# --- Incluir otro requirements.txt ---
# Útil para dividir dependencias por ambiente:
# -r requirements-base.txt
"""

    try:
        with open(OUTPUT_REQUIREMENTS, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"\n  Archivo generado: {OUTPUT_REQUIREMENTS}")
        print("  Ábrelo para ver el formato completo con comentarios.\n")
    except IOError as e:
        print(f"\n  [ERROR] No se pudo escribir el archivo: {e}\n")


# ==============================================================
# SECCIÓN 3: Explicar el flujo de trabajo con requirements.txt
# ==============================================================

def explain_workflow():
    """
    Explica el flujo de trabajo estándar con requirements.txt
    que se usa en proyectos Python profesionales.
    """
    print("=" * 60)
    print("  FLUJO DE TRABAJO CON requirements.txt")
    print("=" * 60)

    flujo = """
  DESARROLLADOR A (crea el proyecto):
  ──────────────────────────────────
    1. python -m venv venv
    2. source venv/bin/activate  (o venv\\Scripts\\activate)
    3. pip install requests flask pandas
    4. pip freeze > requirements.txt
    5. git add requirements.txt
    6. git commit -m "Add project dependencies"

  DESARROLLADOR B (clona el proyecto):
  ────────────────────────────────────
    1. git clone https://github.com/repo
    2. python -m venv venv
    3. source venv/bin/activate
    4. pip install -r requirements.txt   ← ¡Todo listo!

  SERVIDOR DE PRODUCCIÓN / CI-CD:
  ─────────────────────────────────
    1. python -m venv venv
    2. source venv/bin/activate
    3. pip install -r requirements.txt --no-cache-dir
       (--no-cache-dir para instalación limpia sin caché)

  .gitignore OBLIGATORIO:
  ───────────────────────
    venv/
    .venv/
    __pycache__/
    *.pyc
    *.pyo
    .env          ← variables de entorno (nunca al repo)
    """
    print(flujo)


# ==============================================================
# SECCIÓN 4: pyproject.toml — el estándar moderno
# ==============================================================

def explain_pyproject():
    """
    Explica pyproject.toml, el estándar moderno de Python para
    gestionar la configuración del proyecto, dependencias y
    herramientas de desarrollo en un solo archivo.

    PEP 518 (2016) introdujo pyproject.toml para reemplazar
    la fragmentación de setup.py + setup.cfg + requirements.txt.
    """
    print("=" * 60)
    print("  pyproject.toml — EL ESTÁNDAR MODERNO (PEP 517/518/621)")
    print("=" * 60)

    explicacion = """
  PROBLEMA que resuelve:
    Antes de pyproject.toml, la configuración estaba fragmentada:
      setup.py       → metadatos del paquete
      setup.cfg      → configuración adicional
      requirements.txt → dependencias
      tox.ini        → configuración de tests
      .flake8        → configuración del linter
      mypy.ini       → configuración de mypy

    pyproject.toml unifica todo en UN SOLO ARCHIVO.

  SECCIONES PRINCIPALES:
  ─────────────────────
    [build-system]     → qué herramienta construye el paquete
    [project]          → metadatos (nombre, versión, autor...)
    [project.dependencies]    → dependencias de producción
    [project.optional-dependencies] → dependencias opcionales (dev, test)
    [tool.pytest]      → configuración de pytest
    [tool.mypy]        → configuración de mypy
    [tool.black]       → configuración del formateador
    [tool.ruff]        → configuración del linter ruff

  HERRAMIENTAS QUE LO USAN:
  ─────────────────────────
    pip     → puede leer pyproject.toml para instalar
    poetry  → gestor completo con lock file
    hatch   → herramienta de build y versionado
    pdm     → gestor moderno similar a npm
    uv      → gestor ultrarrápido (escrito en Rust)
    """
    print(explicacion)


# ==============================================================
# SECCIÓN 5: Generar un pyproject.toml de ejemplo
# ==============================================================

def generate_pyproject_file():
    """
    Genera un archivo pyproject.toml de ejemplo bien comentado.
    Incluye configuración para las herramientas más comunes
    del ecosistema Python moderno.
    """
    print("=" * 60)
    print("  GENERANDO: ejemplo_pyproject.toml")
    print("=" * 60)

    # Contenido del pyproject.toml con secciones comentadas
    contenido = """\
# ==============================================================
# pyproject.toml — Configuración unificada del proyecto
# Estándar: PEP 517 (build), PEP 518 (build-system), PEP 621 (metadata)
# ==============================================================

# SECCIÓN BUILD-SYSTEM: qué herramienta construye el paquete
# setuptools es el default tradicional; poetry, hatch y pdm
# tienen sus propios build backends
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends.legacy:build"


# SECCIÓN PROJECT: metadatos del proyecto (PEP 621)
[project]
name = "mi-aplicacion"
version = "1.0.0"
description = "Una aplicación de ejemplo con pyproject.toml"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11"

# Información del autor
authors = [
    { name = "Tu Nombre", email = "tu@email.com" }
]

# Palabras clave para PyPI
keywords = ["python", "ejemplo", "tutorial"]

# Clasificadores: https://pypi.org/classifiers/
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

# Dependencias de PRODUCCIÓN
# Usa rangos para librerías; versiones exactas para apps
dependencies = [
    "requests>=2.28.0,<3.0.0",
    "Flask>=3.0.0",
    "SQLAlchemy>=2.0.0",
    "pydantic>=2.0.0",
]


# Dependencias OPCIONALES agrupadas por propósito
[project.optional-dependencies]

# Instalar con: pip install -e ".[dev]"
dev = [
    "black>=23.0",
    "flake8>=6.0",
    "mypy>=1.0",
    "pre-commit>=3.0",
]

# Instalar con: pip install -e ".[test]"
test = [
    "pytest>=7.4",
    "pytest-cov>=4.0",
    "httpx>=0.25",          # Para testear clientes HTTP
    "factory-boy>=3.3",     # Para generar datos de prueba
]

# Instalar con: pip install -e ".[all]"
# Instala TODAS las dependencias opcionales
all = ["mi-aplicacion[dev,test]"]


# Scripts de línea de comandos que se instalan con el paquete
[project.scripts]
mi-app = "mi_aplicacion.main:main"


# URLs del proyecto en PyPI
[project.urls]
Homepage = "https://github.com/usuario/mi-aplicacion"
Repository = "https://github.com/usuario/mi-aplicacion"
Documentation = "https://mi-aplicacion.readthedocs.io"
"Bug Tracker" = "https://github.com/usuario/mi-aplicacion/issues"


# ==============================================================
# CONFIGURACIÓN DE HERRAMIENTAS
# ==============================================================

# Configuración de pytest
[tool.pytest.ini_options]
testpaths = ["tests"]               # Dónde buscar los tests
python_files = ["test_*.py"]        # Patrón de archivos de test
python_functions = ["test_*"]       # Patrón de funciones de test
addopts = [
    "-v",                           # Verbose: muestra cada test
    "--tb=short",                   # Traceback corto en errores
    "--cov=src",                    # Cobertura del código en src/
    "--cov-report=term-missing",    # Muestra líneas sin cobertura
]

# Configuración de mypy (verificador de tipos)
[tool.mypy]
python_version = "3.11"
strict = true                       # Activa todas las verificaciones
ignore_missing_imports = true       # Ignora paquetes sin stubs de tipos

# Configuración de black (formateador de código)
[tool.black]
line-length = 88                    # Longitud de línea estándar de black
target-version = ["py311", "py312"]
include = '\\.pyi?$'

# Configuración de ruff (linter moderno, reemplaza a flake8+isort)
[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "W", "I"]      # Error, Flake8, Warning, isort
ignore = ["E501"]                   # Ignora líneas largas (lo maneja black)
"""

    try:
        with open(OUTPUT_PYPROJECT, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"\n  Archivo generado: {OUTPUT_PYPROJECT}")
        print("  Ábrelo para ver la configuración completa.\n")
    except IOError as e:
        print(f"\n  [ERROR] No se pudo escribir el archivo: {e}\n")


# ==============================================================
# SECCIÓN 6: Comparación requirements.txt vs pyproject.toml
# ==============================================================

def compare_approaches():
    """
    Tabla comparativa entre requirements.txt y pyproject.toml
    para ayudar a elegir el enfoque correcto según el caso de uso.
    """
    print("=" * 60)
    print("  requirements.txt vs pyproject.toml — COMPARACIÓN")
    print("=" * 60)

    print("""
  ┌─────────────────────┬──────────────────┬──────────────────┐
  │ Aspecto             │ requirements.txt │ pyproject.toml   │
  ├─────────────────────┼──────────────────┼──────────────────┤
  │ Estándar actual     │ Legado (funciona)│ Moderno (PEP 621)│
  │ Simplicidad         │ Muy simple       │ Más estructura   │
  │ Configuración unif. │ No               │ Sí               │
  │ Soporte de herram.  │ Básico           │ Amplio           │
  │ Lock file           │ Con pip freeze   │ Poetry/PDM/uv    │
  │ Uso recomendado     │ Scripts simples  │ Proyectos reales │
  │ Aprendizaje         │ Inmediato        │ Curva suave      │
  └─────────────────────┴──────────────────┴──────────────────┘

  RECOMENDACIÓN:
    - Script personal o tutorial  → requirements.txt es suficiente
    - Proyecto en equipo          → pyproject.toml + lock file
    - Librería para publicar      → pyproject.toml (obligatorio)
    - Microservicio en producción → pyproject.toml + pip
    """)


# ==============================================================
# PUNTO DE ENTRADA
# ==============================================================

if __name__ == "__main__":
    explain_requirements_format()
    generate_requirements_file()
    explain_workflow()
    explain_pyproject()
    generate_pyproject_file()
    compare_approaches()

    print("=" * 60)
    print("  ARCHIVOS GENERADOS:")
    print(f"  - {OUTPUT_REQUIREMENTS}")
    print(f"  - {OUTPUT_PYPROJECT}")
    print()
    print("  Ábrelos y estúdialos — son plantillas reutilizables.")
    print("=" * 60)
