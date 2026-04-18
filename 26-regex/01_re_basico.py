# =============================================================================
# CAPÍTULO 26 — Expresiones Regulares (Regex)
# Archivo 1: Módulo re — Funciones básicas y esenciales
# =============================================================================
# Este archivo cubre todas las funciones principales del módulo re:
# search, match, fullmatch, findall, finditer, sub, split
# Flags: IGNORECASE, MULTILINE, DOTALL
# Grupos de captura con paréntesis ()
# =============================================================================

import re

# =============================================================================
# SECCIÓN 1: re.search — Busca el patrón en cualquier parte del string
# =============================================================================

print("=" * 60)
print("1. re.search()")
print("=" * 60)

texto = "Mi número de teléfono es 555-1234 y mi código es ABC-99"

# Buscar un número de teléfono simple
resultado = re.search(r"\d{3}-\d{4}", texto)

if resultado:
    # .group() retorna el texto que hizo match
    print(f"Encontrado: {resultado.group()}")
    # .start() y .end() retornan posiciones
    print(f"Posición inicio: {resultado.start()}, fin: {resultado.end()}")
    # .span() retorna la tupla (inicio, fin)
    print(f"Span: {resultado.span()}")
else:
    print("No se encontró el patrón")

# search retorna None si no hay coincidencia — siempre verificar antes de usar
sin_match = re.search(r"\d{10}", texto)
print(f"Sin match: {sin_match}")  # None


# =============================================================================
# SECCIÓN 2: re.match — Solo busca al INICIO del string
# =============================================================================

print("\n" + "=" * 60)
print("2. re.match() — Solo busca al inicio")
print("=" * 60)

texto_a = "Hola mundo 123"
texto_b = "123 Hola mundo"

# match solo encuentra si el patrón está AL INICIO
m1 = re.match(r"\d+", texto_a)  # No encuentra — el string empieza con "Hola"
m2 = re.match(r"\d+", texto_b)  # Sí encuentra — empieza con "123"

print(f"match en '{texto_a}': {m1}")        # None
print(f"match en '{texto_b}': {m2.group()}")  # 123

# Diferencia clave con search:
s1 = re.search(r"\d+", texto_a)  # Sí encuentra aunque no está al inicio
print(f"search en '{texto_a}': {s1.group()}")  # 123


# =============================================================================
# SECCIÓN 3: re.fullmatch — El patrón debe cubrir TODO el string
# =============================================================================

print("\n" + "=" * 60)
print("3. re.fullmatch() — El patrón debe cubrir todo el string")
print("=" * 60)

# Útil para validación: el string completo debe cumplir el patrón
cadenas = ["12345", "123abc", "  123  ", "99999"]

patron_solo_digitos = r"\d+"

for c in cadenas:
    fm = re.fullmatch(patron_solo_digitos, c)
    estado = "VÁLIDO" if fm else "INVÁLIDO"
    print(f"'{c}' → {estado}")


# =============================================================================
# SECCIÓN 4: re.findall — Retorna lista de TODAS las coincidencias
# =============================================================================

print("\n" + "=" * 60)
print("4. re.findall() — Todas las coincidencias como lista")
print("=" * 60)

texto = "Precios: $10.50, $200.00, $3.99 y también €15 y £8.75"

# Encontrar todos los números con decimales
precios = re.findall(r"\d+\.\d+", texto)
print(f"Precios encontrados: {precios}")

# Cuando el patrón tiene grupos de captura, findall retorna los grupos
texto_html = "<b>negrita</b> y <i>cursiva</i> y <strong>fuerte</strong>"
etiquetas = re.findall(r"<(\w+)>", texto_html)
print(f"Etiquetas HTML: {etiquetas}")

# Con múltiples grupos de captura, retorna lista de tuplas
pares = re.findall(r"(\w+)=(\w+)", "color=rojo tamaño=grande tipo=texto")
print(f"Pares clave=valor: {pares}")


# =============================================================================
# SECCIÓN 5: re.finditer — Iterador de Match objects (más eficiente)
# =============================================================================

print("\n" + "=" * 60)
print("5. re.finditer() — Iterador de Match objects")
print("=" * 60)

texto = "Error en línea 10, Warning en línea 25, Error en línea 47"

# finditer es preferible cuando necesitas posiciones o trabajas con textos grandes
for match in re.finditer(r"(Error|Warning) en línea (\d+)", texto):
    tipo = match.group(1)
    linea = match.group(2)
    inicio = match.start()
    print(f"  Tipo: {tipo}, Línea: {linea}, Posición en texto: {inicio}")


# =============================================================================
# SECCIÓN 6: re.sub — Reemplazar coincidencias
# =============================================================================

print("\n" + "=" * 60)
print("6. re.sub() — Reemplazar coincidencias")
print("=" * 60)

# Reemplazo simple
texto = "Hola   mundo,   cómo   estás"
limpio = re.sub(r"\s+", " ", texto)  # Múltiples espacios → un espacio
print(f"Original:  '{texto}'")
print(f"Limpio:    '{limpio}'")

# Reemplazo con referencias a grupos de captura (\1, \2, etc.)
fecha_us = "La reunión es el 12/25/2024 y el evento el 01/01/2025"
# Convierte MM/DD/YYYY → YYYY-MM-DD usando referencias de grupos
fecha_iso = re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\3-\1-\2", fecha_us)
print(f"Fecha US:  '{fecha_us}'")
print(f"Fecha ISO: '{fecha_iso}'")

# Reemplazo con función lambda
texto_con_nums = "valor1=10, valor2=20, valor3=30"
# Duplicar todos los números
resultado = re.sub(r"\d+", lambda m: str(int(m.group()) * 2), texto_con_nums)
print(f"Original:   '{texto_con_nums}'")
print(f"Duplicado:  '{resultado}'")

# Limitar número de reemplazos con el parámetro count
texto_rep = "gato gato gato gato"
uno = re.sub(r"gato", "perro", texto_rep, count=2)
print(f"Solo 2 reemplazos: '{uno}'")


# =============================================================================
# SECCIÓN 7: re.split — Dividir string por un patrón
# =============================================================================

print("\n" + "=" * 60)
print("7. re.split() — Dividir por patrón")
print("=" * 60)

# Dividir por múltiples delimitadores a la vez
csv_sucio = "nombre,apellido;edad|ciudad  país"
partes = re.split(r"[,;|\s]+", csv_sucio)
print(f"Partes: {partes}")

# Incluir el delimitador en el resultado usando grupos de captura
texto = "uno1dos2tres3cuatro"
partes_con_sep = re.split(r"(\d)", texto)
print(f"Con separadores: {partes_con_sep}")


# =============================================================================
# SECCIÓN 8: FLAGS — Modificadores del comportamiento
# =============================================================================

print("\n" + "=" * 60)
print("8. Flags — Modificadores de comportamiento")
print("=" * 60)

# --- re.IGNORECASE (re.I) ---
print("\n8a. IGNORECASE:")
texto = "Python es GENIAL y python es divertido"
coincidencias = re.findall(r"python", texto, re.IGNORECASE)
print(f"  Todas las menciones de 'python' (sin importar mayúsculas): {coincidencias}")

# --- re.MULTILINE (re.M) ---
print("\n8b. MULTILINE:")
log = """ERROR: archivo no encontrado
INFO: proceso iniciado
ERROR: conexión rechazada
WARNING: memoria alta"""

# Sin MULTILINE, ^ solo hace match al inicio del string completo
errores_sin = re.findall(r"^ERROR.*", log)
print(f"  Sin MULTILINE: {errores_sin}")

# Con MULTILINE, ^ hace match al inicio de CADA línea
errores_con = re.findall(r"^ERROR.*", log, re.MULTILINE)
print(f"  Con MULTILINE: {errores_con}")

# --- re.DOTALL (re.S) ---
print("\n8c. DOTALL:")
html_bloque = "<div>\n  Contenido\n  en múltiples\n  líneas\n</div>"

# Sin DOTALL, el punto (.) no hace match con \n
sin_dotall = re.search(r"<div>(.*)</div>", html_bloque)
print(f"  Sin DOTALL: {sin_dotall}")  # None, porque hay saltos de línea

# Con DOTALL, el punto hace match con cualquier carácter incluyendo \n
con_dotall = re.search(r"<div>(.*)</div>", html_bloque, re.DOTALL)
if con_dotall:
    print(f"  Con DOTALL: encontrado ({len(con_dotall.group(1))} caracteres)")

# Combinar múltiples flags con el operador |
resultado = re.findall(r"^error.*", log, re.IGNORECASE | re.MULTILINE)
print(f"\nFlags combinados (IGNORECASE + MULTILINE): {resultado}")


# =============================================================================
# SECCIÓN 9: GRUPOS DE CAPTURA ()
# =============================================================================

print("\n" + "=" * 60)
print("9. Grupos de captura ()")
print("=" * 60)

# Grupos básicos — acceder con .group(n)
fecha = "Fecha de nacimiento: 15-03-1990"
m = re.search(r"(\d{2})-(\d{2})-(\d{4})", fecha)

if m:
    print(f"Match completo:  {m.group(0)}")  # group(0) = todo el match
    print(f"Día:    {m.group(1)}")
    print(f"Mes:    {m.group(2)}")
    print(f"Año:    {m.group(3)}")
    print(f"Todos los grupos: {m.groups()}")  # Tupla con todos los grupos

# Grupos anidados
texto = "abc123def456"
m = re.search(r"(([a-z]+)(\d+))", texto)
if m:
    print(f"\nGrupo 0 (todo): {m.group(0)}")
    print(f"Grupo 1 (externo): {m.group(1)}")
    print(f"Grupo 2 (letras): {m.group(2)}")
    print(f"Grupo 3 (números): {m.group(3)}")


# =============================================================================
# SECCIÓN 10: re.compile — Compilar patrones para reutilización eficiente
# =============================================================================

print("\n" + "=" * 60)
print("10. re.compile() — Patrones precompilados")
print("=" * 60)

# Cuando usas el mismo patrón muchas veces, compílalo primero
# Esto mejora el rendimiento porque el patrón se convierte a bytecode una sola vez
patron_numero = re.compile(r"\d+")

textos = ["abc123", "xyz456", "hello789world", "no hay números aquí"]

for t in textos:
    m = patron_numero.search(t)
    if m:
        print(f"  '{t}' → primer número: {m.group()}")
    else:
        print(f"  '{t}' → sin números")

# El objeto compilado tiene los mismos métodos: search, match, findall, etc.
patron_email = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+", re.IGNORECASE)
emails_texto = "Contáctame en juan@example.com o info@empresa.org para más info"
print(f"\nEmails encontrados: {patron_email.findall(emails_texto)}")


print("\n" + "=" * 60)
print("FIN: 01_re_basico.py completado")
print("=" * 60)
