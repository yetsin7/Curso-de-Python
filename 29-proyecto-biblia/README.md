# Capítulo 29 — Proyecto: App de Lectura Bíblica

## Descripción del Proyecto

En este capítulo final construiremos una **aplicación de consola para leer, buscar y analizar la Biblia Reina-Valera 1960** usando Python y SQLite.

El proyecto parte de una base de datos real con los 31,103 versículos de la Biblia distribuidos en 66 libros, con sus marcas Strong originales. A lo largo de los archivos iremos construyendo desde una exploración básica hasta una API REST funcional.

---

## Por qué Este Dataset es Perfecto para Aprender Python

La Biblia RV60 como base de datos ofrece:

- **SQL real**: tablas relacionadas, JOINs, GROUP BY, ORDER BY, COUNT, LIKE
- **Texto con ruido**: los versículos traen marcas `<S>NNNN</S>` que hay que limpiar con regex
- **Volumen significativo**: 31,103 filas — suficiente para notar diferencias de rendimiento
- **Datos conocidos**: cualquier estudiante puede verificar si el resultado es correcto
- **Análisis natural**: frecuencia de palabras, distribuciones, comparativas AT vs NT

---

## Conceptos que Integra

| Concepto Python | Dónde se usa |
|---|---|
| `sqlite3` | Todos los archivos |
| Funciones y módulos | `01`, `04` importa funciones de los anteriores |
| Manejo de errores (`try/except`) | `01`, `04`, `06` |
| Strings y regex (`re`) | `01`, `02`, `03` |
| Programación orientada a objetos | `04`, `06` |
| `collections.Counter` | `03` |
| `json` para persistencia | `04` |
| `random` | `04` |
| `pandas` y `matplotlib` | `05` |
| `fastapi` / `http.server` | `06` |

---

## Cómo Encontrar la Base de Datos

Todos los scripts usan ruta **relativa** al propio archivo con `os.path`:

```python
import os

# Sube un nivel desde el script hasta la carpeta del libro, luego entra a datos/
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'datos', 'biblia_rv60.sqlite3')
```

Esto funciona sin importar desde qué directorio se ejecute el script.

---

## Archivos del Capítulo

| Archivo | Aprende |
|---|---|
| `00_explorar_bd.py` | Conectar a SQLite, explorar esquema, metadatos, estadísticas básicas |
| `01_lector_basico.py` | Limpiar texto con regex, funciones de consulta, menú interactivo |
| `02_buscador.py` | Búsqueda LIKE en SQL, resultados formateados, estadísticas de búsqueda |
| `03_estadisticas.py` | Análisis con `collections.Counter`, distribuciones, comparativas AT/NT |
| `04_app_completa.py` | App completa con menú, módulos importados, favoritos en JSON, plan de lectura |
| `05_biblia_con_pandas.py` | DataFrames, groupby, visualizaciones con matplotlib |
| `06_api_biblia_fastapi.py` | API REST con FastAPI, fallback con `http.server` |

---

## Cómo Ejecutar

```bash
# Desde la carpeta 29-proyecto-biblia/
python 00_explorar_bd.py
python 01_lector_basico.py
python 02_buscador.py
python 03_estadisticas.py
python 04_app_completa.py
python 05_biblia_con_pandas.py
python 06_api_biblia_fastapi.py
```

Para los últimos dos archivos necesitarás instalar dependencias opcionales:

```bash
pip install pandas matplotlib       # para 05
pip install fastapi uvicorn          # para 06
```

---

## Estructura de la Base de Datos

```
books   → 66 filas  (book_number, short_name, long_name, book_color)
verses  → 31,103 filas  (book_number, chapter, verse, text)
info    → 8 filas   (name, value) — metadatos del módulo
```

Los versículos tienen marcas Strong intercaladas: `En el principio<S>7225</S> creó<S>1254</S>...`  
Siempre se limpian con: `re.sub(r'<S>\d+</S>', '', texto).strip()`
