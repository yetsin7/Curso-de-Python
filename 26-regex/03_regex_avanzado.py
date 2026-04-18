# =============================================================================
# CAPÍTULO 26 — Expresiones Regulares (Regex)
# Archivo 3: Técnicas avanzadas de regex
# =============================================================================
# Temas: grupos nombrados (?P<name>), lookahead/lookbehind,
# grupos no-capturantes (?:), backreferences, re.compile,
# regex en pandas, parser completo de logs de servidor web
# =============================================================================

import re

# Intentar importar pandas (librería externa)
try:
    import pandas as pd
    PANDAS_DISPONIBLE = True
except ImportError:
    PANDAS_DISPONIBLE = False
    print("NOTA: pandas no instalado. Instala con: pip install pandas")
    print("      Las secciones de pandas serán omitidas.\n")


# =============================================================================
# SECCIÓN 1: Grupos nombrados — (?P<nombre>...)
# =============================================================================
# En lugar de acceder a grupos por índice (group(1), group(2)...),
# podemos asignarles nombres descriptivos con (?P<nombre>...)
# Esto hace el código mucho más legible y mantenible.
# =============================================================================

print("=" * 60)
print("1. Grupos nombrados (?P<nombre>...)")
print("=" * 60)

# Sin grupos nombrados — frágil, depende del orden
fecha_str = "Reunión programada para: 25/12/2024"
m = re.search(r"(\d{2})/(\d{2})/(\d{4})", fecha_str)
if m:
    print(f"Sin nombres: día={m.group(1)}, mes={m.group(2)}, año={m.group(3)}")

# Con grupos nombrados — robusto y autodocumentado
m = re.search(r"(?P<dia>\d{2})/(?P<mes>\d{2})/(?P<anio>\d{4})", fecha_str)
if m:
    # Acceder por nombre con .group("nombre") o m.groupdict()
    print(f"Con nombres: día={m.group('dia')}, mes={m.group('mes')}, año={m.group('anio')}")
    print(f"Como diccionario: {m.groupdict()}")

# Grupos nombrados en URLs
url = "https://api.empresa.com:8080/v2/usuarios/123?formato=json"
patron_url = re.compile(
    r"(?P<protocolo>https?)://"
    r"(?P<dominio>[\w.-]+)"
    r"(?::(?P<puerto>\d+))?"
    r"(?P<ruta>/[^?]*)?"
    r"(?:\?(?P<query>.*))?",
    re.IGNORECASE
)

m = patron_url.match(url)
if m:
    datos = m.groupdict()
    print(f"\nURL parseada:")
    for clave, valor in datos.items():
        print(f"  {clave:10} → {valor}")


# =============================================================================
# SECCIÓN 2: Grupos no-capturantes — (?:...)
# =============================================================================
# A veces necesitamos agrupar para aplicar cuantificadores,
# pero NO queremos que ese grupo aparezca en los resultados.
# (?:...) agrupa sin capturar.
# =============================================================================

print("\n" + "=" * 60)
print("2. Grupos no-capturantes (?:...)")
print("=" * 60)

texto = "Los archivos son: imagen.jpg, foto.PNG, doc.pdf, video.mp4"

# CON captura — los resultados incluyen el grupo
con_captura = re.findall(r"(\w+)\.(jpg|png|pdf)", texto, re.IGNORECASE)
print(f"Con captura:     {con_captura}")
# Resultado: [('imagen', 'jpg'), ('foto', 'PNG'), ('doc', 'pdf')]
# El grupo de la extensión aparece por separado

# SIN captura para la extensión — resultado más limpio
sin_captura = re.findall(r"\w+\.(?:jpg|png|pdf)", texto, re.IGNORECASE)
print(f"Sin captura:     {sin_captura}")
# Resultado: ['imagen.jpg', 'foto.PNG', 'doc.pdf']

# Ejemplo práctico: extraer solo el nombre del archivo sin la extensión
solo_nombre = re.findall(r"(\w+)\.(?:jpg|png|pdf)", texto, re.IGNORECASE)
print(f"Solo nombres:    {solo_nombre}")


# =============================================================================
# SECCIÓN 3: Lookahead y Lookbehind (aserciones de posición)
# =============================================================================
# Lookahead/lookbehind son "aserciones de posición":
# verifican que algo esté (o no esté) antes/después, pero NO lo consumen.
# Es decir, no forman parte del match devuelto.
#
#   (?=X)   → Lookahead positivo:  seguido de X
#   (?!X)   → Lookahead negativo:  NO seguido de X
#   (?<=X)  → Lookbehind positivo: precedido de X
#   (?<!X)  → Lookbehind negativo: NO precedido de X
# =============================================================================

print("\n" + "=" * 60)
print("3. Lookahead y Lookbehind")
print("=" * 60)

# Lookahead positivo (?=): extraer número solo si está seguido de " USD"
precios = "10 USD, 20 EUR, 30 USD, 15 GBP, 50 USD"
dolares = re.findall(r"\d+(?=\s*USD)", precios)
print(f"Solo precios en USD: {dolares}")

# Lookahead negativo (?!): extraer número solo si NO está seguido de " USD"
no_dolares = re.findall(r"\d+(?!\s*USD)\b", precios)
print(f"Precios que NO son USD: {no_dolares}")

# Lookbehind positivo (?<=): extraer texto precedido de un prefijo
log_line = "username=admin password=secret123 role=superuser"
# Extraer el valor de username (lo que viene después de "username=")
username = re.search(r"(?<=username=)\w+", log_line)
print(f"Username: {username.group() if username else 'No encontrado'}")

# Lookbehind negativo (?<!): precio en euros que NO está precedido por "descuento: "
catalogo = "precio: €50, descuento: €10, precio: €75"
precios_reales = re.findall(r"(?<!descuento: )€\d+", catalogo)
print(f"Precios reales (sin descuentos): {precios_reales}")

# Caso de uso real: validar contraseña con múltiples lookaheads
def es_password_segura(password):
    """
    Verifica si una contraseña cumple todas las reglas usando lookaheads.
    Cada lookahead verifica una condición independiente.
    """
    patron = re.compile(
        r"(?=.*[a-z])"          # Al menos una minúscula
        r"(?=.*[A-Z])"          # Al menos una mayúscula
        r"(?=.*\d)"             # Al menos un dígito
        r"(?=.*[!@#$%^&*()_+])" # Al menos un carácter especial
        r".{10,}"               # Mínimo 10 caracteres en total
    )
    return bool(patron.fullmatch(password))

passwords_prueba = ["Hola123!", "HolaMundo1!", "MuySegura@2024X"]
for pwd in passwords_prueba:
    resultado = "SEGURA" if es_password_segura(pwd) else "INSEGURA"
    print(f"  '{pwd}' → {resultado}")


# =============================================================================
# SECCIÓN 4: Backreferences — Referencias a grupos ya capturados
# =============================================================================
# \1, \2, etc. (o (?P=nombre) para grupos nombrados) permiten
# referenciar dentro del mismo patrón un grupo ya capturado.
# Útil para detectar repeticiones, XML/HTML balanceado, duplicados.
# =============================================================================

print("\n" + "=" * 60)
print("4. Backreferences (referencias a grupos)")
print("=" * 60)

# Detectar palabras duplicadas consecutivas (error común de escritura)
texto = "El el gato subió subió al al techo"
duplicados = re.findall(r"\b(\w+)\s+\1\b", texto, re.IGNORECASE)
print(f"Palabras duplicadas consecutivas: {duplicados}")

# Eliminar duplicados usando sub con backreference
texto_limpio = re.sub(r"\b(\w+)\s+\1\b", r"\1", texto, flags=re.IGNORECASE)
print(f"Texto corregido: {texto_limpio}")

# Detectar etiquetas HTML balanceadas (opening = closing tag)
html = "<b>texto</b> <i>cursiva</b> <strong>fuerte</strong>"
etiquetas_balanceadas = re.findall(r"<(\w+)>.*?</\1>", html)
print(f"Etiquetas balanceadas: {etiquetas_balanceadas}")

# Backreference a grupo nombrado con (?P=nombre)
texto_comillas = 'Dijo: "hola mundo" y también \'adiós mundo\''
# Encontrar texto entre comillas (dobles O simples, pero debe ser el mismo tipo)
patron = r"""(?P<q>['"])(?P<contenido>.*?)(?P=q)"""
matches = re.findall(patron, texto_comillas)
# findall con grupos retorna solo los grupos, no el match completo
print(f"Contenido entre comillas: {[m[1] for m in matches]}")


# =============================================================================
# SECCIÓN 5: PARSER DE LOGS DE SERVIDOR WEB (Apache/Nginx Combined Log Format)
# =============================================================================
# Ejemplo del mundo real: parsear el formato estándar de logs Apache/Nginx
# Formato: IP - - [fecha] "MÉTODO /ruta HTTP/versión" código bytes "referer" "agente"
# =============================================================================

print("\n" + "=" * 60)
print("5. Parser de logs de servidor web")
print("=" * 60)

# Entradas de log simuladas (formato Apache Combined Log)
LOGS_MUESTRA = """
192.168.1.10 - juan [25/Dec/2024:10:30:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "https://google.com" "Mozilla/5.0 Chrome/120"
10.0.0.5 - - [25/Dec/2024:10:31:15 +0000] "POST /api/login HTTP/2" 401 89 "-" "curl/7.88.0"
172.16.0.1 - admin [25/Dec/2024:10:32:00 +0000] "GET /admin/users HTTP/1.1" 403 512 "-" "Mozilla/5.0 Firefox/121"
192.168.1.20 - - [25/Dec/2024:10:33:45 +0000] "GET /images/logo.png HTTP/1.1" 304 0 "https://example.com" "Mozilla/5.0 Safari/17"
10.0.0.99 - - [25/Dec/2024:10:34:00 +0000] "GET /../../etc/passwd HTTP/1.1" 404 128 "-" "python-requests/2.31"
""".strip()

# Patrón completo con grupos nombrados para cada campo del log
PATRON_LOG = re.compile(
    r"(?P<ip>\S+)"                          # Dirección IP
    r" \S+ "                                # Identd (generalmente -)
    r"(?P<usuario>\S+)"                     # Usuario autenticado
    r" \[(?P<fecha>[^\]]+)\]"               # Fecha entre corchetes
    r' "(?P<metodo>\w+)'                    # Método HTTP
    r" (?P<ruta>\S+)"                       # Ruta solicitada
    r' HTTP/(?P<version>[\d.]+)"'           # Versión HTTP
    r" (?P<codigo>\d{3})"                   # Código de respuesta
    r" (?P<bytes>\d+|-)"                    # Bytes enviados
    r' "(?P<referer>[^"]*)"'                # Referer
    r' "(?P<agente>[^"]*)"'                 # User-Agent
)


def parsear_log(linea):
    """
    Parsea una línea de log en formato Apache Combined Log Format.
    Retorna un diccionario con todos los campos o None si la línea es inválida.
    """
    m = PATRON_LOG.match(linea.strip())
    if not m:
        return None

    datos = m.groupdict()
    # Convertir campos numéricos
    datos["codigo"] = int(datos["codigo"])
    datos["bytes"] = int(datos["bytes"]) if datos["bytes"] != "-" else 0
    return datos


def analizar_logs(texto_logs):
    """
    Analiza múltiples líneas de log y genera un reporte estadístico.
    Detecta errores, accesos sospechosos y estadísticas generales.
    """
    registros = []
    for linea in texto_logs.split("\n"):
        if linea.strip():
            dato = parsear_log(linea)
            if dato:
                registros.append(dato)

    print(f"  Total de entradas procesadas: {len(registros)}")

    # Contar códigos de estado
    from collections import Counter
    codigos = Counter(r["codigo"] for r in registros)
    print(f"\n  Códigos de respuesta:")
    for codigo, cantidad in sorted(codigos.items()):
        categoria = {2: "ÉXITO", 3: "REDIRECCIÓN", 4: "ERROR CLIENTE", 5: "ERROR SERVIDOR"}
        cat = categoria.get(codigo // 100, "DESCONOCIDO")
        print(f"    {codigo} ({cat}): {cantidad} petición(es)")

    # Detectar posibles ataques (path traversal)
    sospechosos = [r for r in registros if ".." in r["ruta"]]
    if sospechosos:
        print(f"\n  ALERTA - Posibles path traversal detectados:")
        for s in sospechosos:
            print(f"    IP: {s['ip']} → {s['ruta']}")

    # IPs únicas
    ips_unicas = set(r["ip"] for r in registros)
    print(f"\n  IPs únicas: {ips_unicas}")

    return registros


registros = analizar_logs(LOGS_MUESTRA)


# =============================================================================
# SECCIÓN 6: Regex en pandas — str.extract y str.findall
# =============================================================================

print("\n" + "=" * 60)
print("6. Regex en pandas")
print("=" * 60)

if PANDAS_DISPONIBLE:
    # Crear DataFrame de ejemplo con datos de texto
    datos_usuarios = {
        "registro": [
            "Juan García | juan.garcia@gmail.com | +52 555 100-2000",
            "María López | m.lopez@empresa.mx | 555-200-3000",
            "Carlos Ruiz | carlos@test.org | +1 800 555-4000",
            "Ana Torres | ana.torres@correo.com | 55 5500 6000",
        ]
    }
    df = pd.DataFrame(datos_usuarios)

    # str.extract — extrae grupos de captura del primer match como columnas
    # Extraer email con grupo nombrado
    df["email"] = df["registro"].str.extract(r"([\w.+-]+@[\w-]+\.[\w.-]+)")
    print("Emails extraídos con str.extract:")
    print(df[["email"]].to_string(index=False))

    # str.extract con múltiples grupos — crea múltiples columnas
    partes = df["registro"].str.extract(
        r"(?P<nombre>[A-Za-záéíóúñÁÉÍÓÚÑ ]+) \| (?P<email>[\w.+-]+@\S+) \| (?P<telefono>[\d\s+\-]+)"
    )
    print("\nExtracción de múltiples campos:")
    print(partes.to_string(index=False))

    # str.findall — retorna lista de TODOS los matches por fila
    texto_multiples = pd.Series([
        "Contactos: juan@a.com y pedro@b.com",
        "Solo uno: info@empresa.mx",
        "Ningún email aquí",
    ])
    todos_emails = texto_multiples.str.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+")
    print("\nTodos los emails por fila (str.findall):")
    for i, emails in enumerate(todos_emails):
        print(f"  Fila {i}: {emails}")

    # str.contains — filtrar filas que coinciden con un patrón
    df_logs = pd.DataFrame({"log": LOGS_MUESTRA.split("\n") if LOGS_MUESTRA else []})
    df_logs = df_logs[df_logs["log"].str.strip() != ""]
    errores = df_logs[df_logs["log"].str.contains(r'" [45]\d\d ', regex=True)]
    print(f"\nEntradas con errores 4xx/5xx (str.contains): {len(errores)}")

else:
    print("  Omitido — pandas no disponible.")
    print("  Instala con: pip install pandas")

print("\nFIN: 03_regex_avanzado.py completado")
