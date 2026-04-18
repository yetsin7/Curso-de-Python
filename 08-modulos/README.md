# Capítulo 08 — Módulos y la Biblioteca Estándar

Un módulo es un archivo Python que contiene funciones, clases y variables que
puedes reutilizar en otros programas. En lugar de reescribir todo desde cero,
importas lo que ya está hecho.

---

## ¿Por qué existen los módulos?

Imagina que necesitas saber la raíz cuadrada de un número.
Podrías programarla desde cero, o simplemente escribir:

```python
import math
print(math.sqrt(16))   # 4.0
```

Python incluye cientos de módulos ya listos. Eso se llama la **Biblioteca Estándar**.
Y además existe **pip**, que te permite instalar módulos creados por la comunidad.

---

## Tipos de módulos

| Tipo | Descripción | Ejemplo |
|---|---|---|
| **Estándar** | Vienen con Python, ya instalados | `math`, `random`, `os`, `datetime` |
| **Propios** | Los que tú creas | Tu archivo `utilidades.py` |
| **Externos** | Instalados con pip | `requests`, `pandas`, `flask` |

---

## Archivos de este capítulo

| Archivo | Qué aprenderás |
|---|---|
| `01_importar.py` | import, from...import, alias |
| `02_modulos_estandar.py` | math, random, os, datetime — los más útiles |
| `03_modulo_propio.py` y `mis_utilidades.py` | Crear y usar tus propios módulos |

---

> ✅ Cuando termines, pasa a `09-poo/`
