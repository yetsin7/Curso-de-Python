# Capítulo 26 — Expresiones Regulares (Regex)

## ¿Qué son las expresiones regulares?

Una **expresión regular** (regex o regexp) es un patrón de búsqueda que describe un conjunto de cadenas de texto. Son un lenguaje dentro del lenguaje, un mini-programa que te permite describir, buscar, extraer y transformar texto de forma extremadamente precisa.

Si alguna vez necesitaste validar si un email tiene el formato correcto, extraer todos los números de un documento, o reemplazar patrones complejos en miles de archivos simultáneamente — las regex son la herramienta correcta.

> **"Knowing regex is a superpower. You can do in one line what would take 50 lines of manual parsing."**

---

## ¿Cuándo usarlas?

| Caso de uso | Ejemplo |
|---|---|
| **Validación** | ¿Este string es un email válido? ¿Es un número de teléfono? |
| **Extracción** | Dame todos los precios de este documento HTML |
| **Transformación** | Reemplaza todas las fechas DD/MM/YYYY por YYYY-MM-DD |
| **Búsqueda avanzada** | Encuentra todas las líneas de un log que contengan errores HTTP 5xx |
| **Parsing** | Analiza logs de servidor, CSVs no estándar, archivos de configuración |
| **Limpieza de datos** | Elimina caracteres especiales, normaliza espacios, etc. |

### Cuándo NO usarlas

- Para parsear HTML/XML complejo → usa `BeautifulSoup` o `lxml`
- Para parsear JSON → usa el módulo `json`
- Cuando una comparación simple (`==`, `in`, `.startswith()`) es suficiente
- Cuando el patrón es tan complejo que nadie lo entenderá en 6 meses

---

## El módulo `re` de Python

Python incluye el módulo `re` en su librería estándar. No necesitas instalar nada.

```python
import re
```

### Funciones principales

| Función | Descripción |
|---|---|
| `re.search(pattern, string)` | Busca el patrón en cualquier parte del string |
| `re.match(pattern, string)` | Busca el patrón solo al inicio del string |
| `re.fullmatch(pattern, string)` | El patrón debe cubrir todo el string |
| `re.findall(pattern, string)` | Retorna lista de todas las coincidencias |
| `re.finditer(pattern, string)` | Retorna iterador de Match objects |
| `re.sub(pattern, repl, string)` | Reemplaza coincidencias |
| `re.split(pattern, string)` | Divide el string por el patrón |
| `re.compile(pattern)` | Compila el patrón para reutilización eficiente |

---

## Referencia rápida de metacaracteres

### Caracteres especiales

| Símbolo | Significado | Ejemplo |
|---|---|---|
| `.` | Cualquier carácter (excepto newline) | `a.c` → "abc", "a1c" |
| `^` | Inicio del string (o línea con MULTILINE) | `^Hola` |
| `$` | Fin del string (o línea con MULTILINE) | `mundo$` |
| `*` | 0 o más repeticiones | `ab*c` → "ac", "abc", "abbc" |
| `+` | 1 o más repeticiones | `ab+c` → "abc", "abbc" |
| `?` | 0 o 1 repetición (opcional) | `colou?r` → "color", "colour" |
| `{n}` | Exactamente n repeticiones | `\d{4}` → "2024" |
| `{n,m}` | Entre n y m repeticiones | `\d{2,4}` → "12", "123", "1234" |
| `[]` | Clase de caracteres | `[aeiou]`, `[a-z]`, `[0-9]` |
| `[^]` | Negación de clase | `[^0-9]` = no dígito |
| `\|` | Alternativa (OR) | `cat\|dog` |
| `()` | Grupo de captura | `(ab)+` |
| `\` | Escape de metacarácter | `\.` = punto literal |

### Secuencias de escape especiales

| Símbolo | Significado |
|---|---|
| `\d` | Dígito `[0-9]` |
| `\D` | No dígito `[^0-9]` |
| `\w` | Carácter de palabra `[a-zA-Z0-9_]` |
| `\W` | No carácter de palabra |
| `\s` | Espacio en blanco (espacio, tab, newline) |
| `\S` | No espacio en blanco |
| `\b` | Límite de palabra (word boundary) |
| `\B` | No límite de palabra |
| `\n` | Newline |
| `\t` | Tab |

### Cuantificadores greedy vs lazy

Por defecto los cuantificadores son **greedy** (capturan lo máximo posible):
- `.*` → greedy: captura todo lo posible
- `.*?` → lazy: captura lo mínimo posible

### Grupos especiales

| Sintaxis | Tipo |
|---|---|
| `(abc)` | Grupo de captura |
| `(?:abc)` | Grupo no-capturante |
| `(?P<nombre>abc)` | Grupo nombrado |
| `(?=abc)` | Lookahead positivo |
| `(?!abc)` | Lookahead negativo |
| `(?<=abc)` | Lookbehind positivo |
| `(?<!abc)` | Lookbehind negativo |

### Flags

| Flag | Abreviatura | Efecto |
|---|---|---|
| `re.IGNORECASE` | `re.I` | Ignora mayúsculas/minúsculas |
| `re.MULTILINE` | `re.M` | `^` y `$` aplican a cada línea |
| `re.DOTALL` | `re.S` | `.` también hace match con newline |
| `re.VERBOSE` | `re.X` | Permite espacios y comentarios en el patrón |
| `re.ASCII` | `re.A` | `\w`, `\d`, etc. solo ASCII |

---

## Archivos de este capítulo

1. **`01_re_basico.py`** — Módulo `re`: todas las funciones principales con ejemplos detallados
2. **`02_patrones_comunes.py`** — Validadores del mundo real: emails, URLs, teléfonos, fechas, etc.
3. **`03_regex_avanzado.py`** — Técnicas avanzadas: grupos nombrados, lookaheads, parser de logs

---

## Recursos adicionales

- [Documentación oficial de `re`](https://docs.python.org/3/library/re.html)
- [regex101.com](https://regex101.com) — Tester interactivo con explicación de cada parte
- [regexr.com](https://regexr.com) — Alternativa visual muy clara
- [regexcrossword.com](https://regexcrossword.com) — Aprende regex con crucigramas
