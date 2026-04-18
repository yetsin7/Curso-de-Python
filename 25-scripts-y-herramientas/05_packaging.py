# =============================================================================
# CAPÍTULO 25 — Scripts, Herramientas y CLI
# Archivo: 05_packaging.py
# Tema: Empaquetar y publicar herramientas Python en PyPI
# =============================================================================
#
# Una vez que tienes una herramienta útil, puedes compartirla con el mundo
# publicándola en PyPI (Python Package Index) para que cualquiera pueda
# instalarla con: pip install tu-herramienta
#
# Este archivo explica:
# 1. La estructura de un paquete Python profesional
# 2. pyproject.toml — el estándar moderno de empaquetado
# 3. Entry points — cómo convertir tu módulo en un comando CLI
# 4. Versionado semántico
# 5. Cómo publicar en PyPI paso a paso
# =============================================================================

print("=" * 65)
print("PACKAGING — Empaquetar y Publicar en PyPI")
print("=" * 65)

# =============================================================================
# SECCIÓN 1: Estructura de un paquete Python
# =============================================================================
print("""
--- 1. Estructura de un Paquete Profesional ---

mi-herramienta/                    ← Raíz del proyecto (nombre con guiones)
│
├── src/                           ← Código fuente (estructura moderna recomendada)
│   └── mi_herramienta/            ← El paquete Python (nombre con guiones bajos)
│       ├── __init__.py            ← Hace de la carpeta un paquete Python
│       ├── cli.py                 ← Código del comando CLI (entry point)
│       ├── core.py                ← Lógica de negocio
│       └── utils.py               ← Utilidades internas
│
├── tests/                         ← Tests (pytest)
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_core.py
│
├── pyproject.toml                 ← Configuración del paquete (estándar moderno)
├── README.md                      ← Descripción del proyecto (se muestra en PyPI)
├── LICENSE                        ← Licencia (MIT, Apache, GPL...)
├── .gitignore                     ← Archivos que Git debe ignorar
└── CHANGELOG.md                   ← Historial de cambios por versión

NOTA: La estructura src/ es la recomendada porque:
- Evita confusión entre el paquete instalado y el código local
- Fuerza instalar el paquete para usarlo (tests más reales)
- Más limpia en proyectos grandes
""")

# =============================================================================
# SECCIÓN 2: __init__.py — El archivo de inicialización del paquete
# =============================================================================
print("""
--- 2. __init__.py ---

El __init__.py hace que una carpeta sea un "paquete Python".
Puede estar vacío o definir qué se exporta públicamente.

# src/mi_herramienta/__init__.py

# Versión del paquete — importable como: import mi_herramienta; mi_herramienta.__version__
__version__ = "1.0.0"
__author__ = "Tu Nombre"
__email__ = "tu@email.com"

# Importar lo que quieres que sea accesible directamente
# Esto permite: from mi_herramienta import mi_funcion_principal
from .core import mi_funcion_principal, MiClasePrincipal

# __all__ define qué se exporta con "from mi_herramienta import *"
__all__ = ["mi_funcion_principal", "MiClasePrincipal"]
""")

# =============================================================================
# SECCIÓN 3: pyproject.toml — La configuración moderna
# =============================================================================
print("""
--- 3. pyproject.toml (estándar moderno) ---

pyproject.toml reemplaza a setup.py y setup.cfg.
Es el formato estándar desde PEP 517/518.

Ejemplo completo:

[build-system]
requires = ["hatchling"]          # Herramienta de build (alternativas: setuptools, flit)
build-backend = "hatchling.build"

[project]
name = "mi-herramienta"          # Nombre en PyPI (guiones, no guiones bajos)
version = "1.0.0"
description = "Una herramienta útil para desarrolladores Python"
readme = "README.md"
license = { text = "MIT" }
authors = [
    { name = "Tu Nombre", email = "tu@email.com" }
]
keywords = ["cli", "herramientas", "python"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

# Versión mínima de Python requerida
requires-python = ">=3.9"

# Dependencias del paquete — se instalan automáticamente con pip install
dependencies = [
    "click>=8.0",
    "rich>=13.0",
    "requests>=2.28",
]

# Dependencias opcionales (grupos de extras)
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "black",
    "mypy",
]

# ENTRY POINTS — Aquí se definen los comandos CLI
# Cuando el usuario instala el paquete, estos comandos quedan disponibles
# en la terminal como si fueran programas del sistema.
[project.scripts]
mi-tool = "mi_herramienta.cli:main"
# ^ Esto crea el comando "mi-tool" que llama a main() en cli.py

# Si tienes múltiples comandos:
# organizar = "mi_herramienta.cli:comando_organizar"
# hashear = "mi_herramienta.cli:comando_hash"

[project.urls]
Homepage = "https://github.com/tu-usuario/mi-herramienta"
Documentation = "https://mi-herramienta.readthedocs.io"
"Bug Tracker" = "https://github.com/tu-usuario/mi-herramienta/issues"
Changelog = "https://github.com/tu-usuario/mi-herramienta/blob/main/CHANGELOG.md"

# Configuración de herramientas de desarrollo
[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.black]
line-length = 88
target-version = ["py39", "py310", "py311"]
""")

# =============================================================================
# SECCIÓN 4: Entry Points — CLI tools instalables
# =============================================================================
print("""
--- 4. Entry Points — Convertir en Comando del Sistema ---

Con entry_points en pyproject.toml, tu script se convierte en un
comando disponible en cualquier lugar del sistema (dentro del virtualenv
o globalmente si se instala con pip install -g).

# src/mi_herramienta/cli.py

import click
from . import __version__
from .core import procesar_archivo

@click.group()
@click.version_option(version=__version__)
def main():
    \"\"\"Mi Herramienta — Descripción de la CLI.\"\"\"
    pass

@main.command()
@click.argument("archivo", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True)
def procesar(archivo, verbose):
    \"\"\"Procesa un archivo.\"\"\"
    resultado = procesar_archivo(archivo, verbose=verbose)
    click.echo(resultado)

# main() es el entry point — pyproject.toml apunta aquí
if __name__ == "__main__":
    main()

Una vez instalado con pip:
    mi-tool --help
    mi-tool procesar mi_archivo.txt --verbose
""")

# =============================================================================
# SECCIÓN 5: Versionado Semántico
# =============================================================================
print("""
--- 5. Versionado Semántico (SemVer) ---

El formato es: MAJOR.MINOR.PATCH   →   1.4.2

PATCH (1.4.2 → 1.4.3):
  - Corrección de bugs que no rompen la API
  - Pequeñas mejoras de rendimiento
  - "Este cambio es seguro para actualizar"

MINOR (1.4.2 → 1.5.0):
  - Nueva funcionalidad compatible con versiones anteriores
  - Nuevas funciones o comandos
  - "Hay cosas nuevas pero nada se rompe"

MAJOR (1.4.2 → 2.0.0):
  - Cambios que ROMPEN la compatibilidad
  - Se eliminaron o renombraron funciones/comandos
  - "Revisa el CHANGELOG antes de actualizar"

Versiones especiales:
  1.0.0-alpha.1   → En desarrollo activo, puede cambiar mucho
  1.0.0-beta.2    → Feature-complete, pero puede tener bugs
  1.0.0-rc.1      → Release Candidate, casi listo para producción
  1.0.0           → Estable para producción
""")

# =============================================================================
# SECCIÓN 6: Publicar en PyPI — Paso a paso
# =============================================================================
print("""
--- 6. Publicar en PyPI — Paso a Paso ---

PRERREQUISITOS:
  1. Cuenta en https://pypi.org (y https://test.pypi.org para pruebas)
  2. Token de API de PyPI (más seguro que usuario/contraseña)
  3. Instalar herramientas: pip install build twine

PASO 1: Preparar el proyecto
  - Asegurarse que pyproject.toml está correcto
  - README.md claro y con ejemplos
  - Versión actualizada

PASO 2: Construir los archivos de distribución
  # Crea los archivos en dist/
  python -m build

  # Esto genera:
  # dist/mi_herramienta-1.0.0-py3-none-any.whl   ← Wheel (instalación rápida)
  # dist/mi_herramienta-1.0.0.tar.gz              ← Source distribution

PASO 3: Verificar antes de subir
  # Revisar que el paquete se ve bien
  twine check dist/*

PASO 4: Subir a TestPyPI (prueba)
  twine upload --repository testpypi dist/*
  # Verificar en: https://test.pypi.org/project/mi-herramienta/
  # Probar instalación: pip install -i https://test.pypi.org/simple/ mi-herramienta

PASO 5: Subir a PyPI oficial
  twine upload dist/*
  # El paquete ya está disponible en https://pypi.org/project/mi-herramienta/
  # Cualquiera puede instalarlo con: pip install mi-herramienta

PASO 6: Nuevas versiones
  1. Actualizar __version__ en __init__.py (y pyproject.toml si no es dinámico)
  2. Actualizar CHANGELOG.md
  3. Crear tag en Git: git tag v1.0.1 && git push --tags
  4. Repetir pasos 2-5

AUTOMATIZACIÓN CON CI/CD (GitHub Actions):
  Se puede configurar para que cada "git tag v*" publique automáticamente en PyPI.
  Ver: https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
""")

# =============================================================================
# SECCIÓN 7: Herramientas del ecosistema de packaging
# =============================================================================
print("""
--- 7. Herramientas del Ecosistema ---

PARA CONSTRUIR Y PUBLICAR:
  build     → Construye el paquete (python -m build)
  twine     → Sube a PyPI (twine upload dist/*)
  hatch     → Todo en uno: build, test, publish (alternativa moderna)
  flit      → Para paquetes simples, mínima configuración

PARA DESARROLLO:
  pip-tools → Gestión determinista de dependencias (pip-compile)
  poetry    → Todo en uno: dependencies, build, publish
  uv        → Gestor de entornos y dependencias ultrarrápido (nueva generación)

PARA DOCUMENTACIÓN:
  sphinx    → Documentación desde docstrings
  mkdocs    → Documentación en Markdown (más simple)

PARA CALIDAD:
  black     → Formateo automático de código
  ruff      → Linter ultra-rápido
  mypy      → Type checking estático
  pytest    → Tests

INSTALAR TODOS DE UNA:
  pip install build twine black ruff mypy pytest pytest-cov
""")

print("\n" + "=" * 65)
print("Fin del Capítulo 25 — ¡Has completado el Libro de Python!")
print("=" * 65)
print("""
RESUMEN DE LO APRENDIDO EN LOS CAPÍTULOS 22-25:

Capítulo 22 - Data Science:
  NumPy, Pandas, Matplotlib, Seaborn, EDA

Capítulo 23 - Machine Learning:
  Scikit-learn, Regresión, Clasificación, Clustering, Pipelines

Capítulo 24 - Inteligencia Artificial:
  Redes Neuronales, Keras, NLP, APIs de IA (OpenAI/Claude), LangChain

Capítulo 25 - Scripts y Herramientas:
  argparse, Click, Rich, Scripts del mundo real, Packaging/PyPI

El siguiente paso es construir proyectos reales que combinen
múltiples áreas: un chatbot que analiza datos, una CLI que
usa ML para clasificar, una API que sirve predicciones...
¡El mundo es tu oyster!
""")
