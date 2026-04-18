# Capítulo 10 — Manejo de Archivos

La mayoría de las aplicaciones del mundo real necesitan guardar y leer
información de forma permanente. Python hace que trabajar con archivos
sea muy simple.

---

## ¿Por qué archivos?

Los datos en variables solo viven mientras el programa corre.
Al cerrarlo, desaparecen. Los archivos permiten **persistir** datos
entre ejecuciones del programa.

---

## Modos de apertura de archivos

| Modo | Descripción |
|---|---|
| `"r"` | Leer (read). El archivo debe existir. Modo por defecto. |
| `"w"` | Escribir (write). Crea el archivo o lo **sobreescribe** si existe. |
| `"a"` | Agregar (append). Escribe al final sin borrar el contenido existente. |
| `"x"` | Crear. Falla si el archivo ya existe. |
| `"r+"` | Leer y escribir. El archivo debe existir. |

---

## La forma correcta: `with`

Siempre abre archivos con `with open(...) as f:`.
Esto cierra el archivo automáticamente al terminar el bloque,
incluso si ocurre un error.

```python
with open("archivo.txt", "r", encoding="utf-8") as f:
    contenido = f.read()
```

---

## Archivos de este capítulo

| Archivo | Qué aprenderás |
|---|---|
| `01_leer_escribir.py` | Crear, leer y modificar archivos de texto |
| `02_csv_json.py` | Trabajar con archivos CSV y JSON |

---

> ✅ Cuando termines, pasa a `11-nivel-intermedio/`
