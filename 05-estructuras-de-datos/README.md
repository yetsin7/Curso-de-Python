# Capítulo 05 — Estructuras de Datos

Las estructuras de datos son formas de organizar y almacenar múltiples valores.
Hasta ahora guardabas un valor por variable. Ahora aprenderás a guardar
colecciones enteras de valores.

---

## Las cuatro estructuras básicas de Python

| Estructura | Sintaxis | Ordenada | Modificable | Duplicados |
|---|---|---|---|---|
| **Lista** | `[1, 2, 3]` | ✅ Sí | ✅ Sí | ✅ Sí |
| **Tupla** | `(1, 2, 3)` | ✅ Sí | ❌ No | ✅ Sí |
| **Diccionario** | `{"a": 1}` | ✅ Sí* | ✅ Sí | ❌ (claves únicas) |
| **Conjunto** | `{1, 2, 3}` | ❌ No | ✅ Sí | ❌ No |

*Desde Python 3.7, los diccionarios mantienen el orden de inserción.

---

## ¿Cuándo usar cada una?

- **Lista** → cuando necesitas una secuencia ordenada que puede cambiar (la más común)
- **Tupla** → cuando los datos no deben cambiar (coordenadas, colores RGB, configuración)
- **Diccionario** → cuando necesitas buscar por nombre/clave (base de datos simple, config)
- **Conjunto** → cuando no quieres duplicados (tags, permisos, elementos únicos)

---

## Archivos de este capítulo

| Archivo | Qué aprenderás |
|---|---|
| `01_listas.py` | Crear, modificar, recorrer y operar listas |
| `02_tuplas.py` | Tuplas inmutables y cuándo usarlas |
| `03_diccionarios.py` | Clave-valor: el más poderoso para modelar datos |
| `04_conjuntos.py` | Sets: eliminar duplicados y operaciones de conjuntos |

---

> ✅ Cuando termines, pasa a `06-strings/`
