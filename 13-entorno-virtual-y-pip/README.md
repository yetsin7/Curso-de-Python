# Capítulo 13 — Entorno Virtual y pip

## ¿Por qué este capítulo importa?

Cuando empiezas a trabajar en proyectos Python reales, tarde o temprano instalarás paquetes de terceros. Sin un entorno virtual, todos esos paquetes se instalan de forma **global** en tu sistema. Esto parece conveniente al principio, pero muy rápido genera un problema serio: **conflictos de versiones**.

---

## El problema de la instalación global

Imagina que tienes dos proyectos:

- **Proyecto A** requiere `requests==2.20.0`
- **Proyecto B** requiere `requests==2.31.0`

Si instalas todo globalmente, solo puede existir **una versión** de `requests` a la vez. Cuando instales la versión nueva para el Proyecto B, el Proyecto A podría dejar de funcionar.

Esto se llama **dependency hell** (infierno de dependencias), y es uno de los problemas más frustrantes en el desarrollo de software.

---

## ¿Qué es un entorno virtual?

Un **entorno virtual** (virtual environment o `venv`) es una **carpeta aislada** que contiene:

- Su propia copia del intérprete de Python
- Su propio directorio `site-packages` donde se instalan los paquetes
- Sus propios scripts (`pip`, `python`)

Cada proyecto tiene su propio entorno virtual. Los paquetes instalados en un entorno **no afectan** a otro entorno ni al sistema global.

```
mi-proyecto/
├── venv/              ← El entorno virtual (esta carpeta NO se sube a git)
│   ├── Scripts/       ← En Windows
│   ├── bin/           ← En Mac/Linux
│   └── Lib/
│       └── site-packages/  ← Aquí se instalan los paquetes
├── src/
│   └── main.py
└── requirements.txt
```

---

## Instalación global vs Entorno virtual

| Aspecto | Global | Entorno Virtual |
|---|---|---|
| Compartido entre proyectos | Sí | No |
| Conflictos de versiones | Posible | Imposible |
| Reproducibilidad | Baja | Alta |
| Limpieza al terminar | Difícil | Borra la carpeta |
| Uso recomendado | Herramientas del sistema | Todo proyecto Python |

---

## Cómo crear, activar y desactivar un venv

### Crear el entorno virtual

```bash
# Desde la carpeta de tu proyecto:
python -m venv venv

# También puedes nombrarlo .venv (convención común)
python -m venv .venv
```

El argumento final (`venv` o `.venv`) es el nombre de la carpeta que se creará.

### Activar el entorno virtual

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

Cuando está activado, tu prompt cambia y muestra el nombre del entorno:
```
(venv) C:\mi-proyecto>
```

### Verificar que está activo

```bash
which python      # Mac/Linux
where python      # Windows
# Debe apuntar a la carpeta venv, no al Python del sistema
```

### Desactivar el entorno virtual

```bash
deactivate
```

---

## requirements.txt — El contrato de dependencias

`requirements.txt` es un archivo de texto que lista todos los paquetes que tu proyecto necesita, con sus versiones exactas. Es la forma estándar de **compartir y reproducir** un entorno de trabajo.

### Formato básico

```
requests==2.31.0
numpy==1.26.4
pandas>=2.0.0,<3.0.0
flask
```

- `==` fija la versión exacta (más reproducible)
- `>=` indica versión mínima
- Sin versión, instala la última disponible

### Generar requirements.txt automáticamente

```bash
# Genera un archivo con TODOS los paquetes instalados en el entorno activo
pip freeze > requirements.txt
```

### Instalar desde requirements.txt

```bash
# En un entorno nuevo, instala todo lo que el proyecto necesita
pip install -r requirements.txt
```

Este flujo es la base del trabajo en equipo y del despliegue:

1. Desarrollador A crea el entorno, instala paquetes, ejecuta `pip freeze > requirements.txt`
2. Sube `requirements.txt` al repositorio (¡NO sube la carpeta `venv`!)
3. Desarrollador B clona el repo, crea su propio `venv`, ejecuta `pip install -r requirements.txt`
4. Ambos tienen exactamente el mismo entorno

### Agregar venv al .gitignore

```gitignore
# .gitignore
venv/
.venv/
__pycache__/
*.pyc
```

---

## pyproject.toml — El estándar moderno

`requirements.txt` es simple y funciona, pero el ecosistema moderno de Python usa `pyproject.toml` (PEP 518, PEP 621). Es más poderoso y es el estándar actual para:

- **Poetry** — gestor de paquetes moderno
- **Hatch** — herramienta de empaquetado
- **PDM** — otro gestor moderno
- **pip** — también puede leerlo

```toml
[project]
name = "mi-proyecto"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
    "numpy>=1.26.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "mypy>=1.0",
]
```

---

## Comandos pip más usados

```bash
# Instalar un paquete
pip install requests

# Instalar versión específica
pip install requests==2.31.0

# Actualizar un paquete
pip install --upgrade requests

# Desinstalar
pip uninstall requests

# Listar paquetes instalados
pip list

# Ver info de un paquete (versión, autor, dependencias)
pip show requests

# Buscar paquetes (requiere conexión)
pip search requests       # NOTA: deshabilitado en versiones recientes
# Mejor buscar en https://pypi.org

# Exportar dependencias
pip freeze > requirements.txt

# Instalar desde requirements.txt
pip install -r requirements.txt

# Ver paquetes desactualizados
pip list --outdated
```

---

## Archivos de este capítulo

| Archivo | Qué aprenderás |
|---|---|
| `01_que_es_venv.py` | Inspeccionar el entorno Python actual con código |
| `02_pip_comandos.py` | Usar pip desde Python con subprocess |
| `03_requirements.py` | Generar y entender requirements.txt y pyproject.toml |

---

## Flujo de trabajo recomendado para cada proyecto

```bash
# 1. Crear proyecto
mkdir mi-proyecto
cd mi-proyecto

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# 4. Instalar dependencias
pip install requests pandas

# 5. Guardar dependencias
pip freeze > requirements.txt

# 6. Trabajar en el proyecto...

# 7. Al terminar, desactivar
deactivate
```
