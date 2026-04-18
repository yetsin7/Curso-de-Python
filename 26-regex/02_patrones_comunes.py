# =============================================================================
# CAPÍTULO 26 — Expresiones Regulares (Regex)
# Archivo 2: Patrones prácticos del mundo real
# =============================================================================
# Validadores para: email, URL, teléfono, fecha, código postal,
# contraseña segura, IPv4, número de tarjeta (enmascarado)
# Cada patrón incluye explicación detallada de su construcción
# =============================================================================

import re


def validar(nombre, patron, casos_validos, casos_invalidos, flags=0):
    """
    Función utilitaria para probar un patrón con casos de prueba.
    Muestra resultados visuales de qué pasa y qué falla.

    Args:
        nombre: Nombre descriptivo del validador
        patron: Patrón de regex compilado
        casos_validos: Lista de strings que DEBEN pasar
        casos_invalidos: Lista de strings que NO deben pasar
        flags: Flags de re (ej. re.IGNORECASE)
    """
    regex = re.compile(patron, flags)
    print(f"\n{'=' * 55}")
    print(f"  {nombre}")
    print(f"  Patrón: {patron}")
    print(f"{'=' * 55}")

    print("  Casos VÁLIDOS:")
    for caso in casos_validos:
        ok = bool(regex.fullmatch(caso))
        simbolo = "✓" if ok else "✗ ERROR"
        print(f"    {simbolo}  {caso}")

    print("  Casos INVÁLIDOS (deben fallar):")
    for caso in casos_invalidos:
        ok = bool(regex.fullmatch(caso))
        simbolo = "✓ (rechazado)" if not ok else "✗ FALSO POSITIVO"
        print(f"    {simbolo}  {caso}")


# =============================================================================
# 1. VALIDAR EMAIL
# =============================================================================
# Explicación del patrón:
#   [\w.+-]+       → parte local: letras, dígitos, puntos, +, -
#   @              → el símbolo @
#   [\w-]+         → dominio: letras, dígitos, guiones
#   \.             → punto literal (escapado)
#   [\w.-]+        → TLD y subdominios: letras, dígitos, puntos, guiones
#
# NOTA: La validación 100% correcta de emails según RFC 5321 es extremadamente
# compleja. Este patrón cubre el 99% de los casos del mundo real.
# =============================================================================

PATRON_EMAIL = r"[\w.+-]+@[\w-]+\.[\w.-]+"

validar(
    "VALIDADOR DE EMAIL",
    PATRON_EMAIL,
    casos_validos=[
        "usuario@example.com",
        "mi.nombre+filtro@empresa.org",
        "info@sub.dominio.co.uk",
        "user123@test-domain.net",
    ],
    casos_invalidos=[
        "sin-arroba.com",
        "@sinusuario.com",
        "usuario@",
        "doble@@ejemplo.com",
        "usuario@sin-punto",
    ],
    flags=re.IGNORECASE,
)


# =============================================================================
# 2. VALIDAR URL
# =============================================================================
# Explicación del patrón:
#   https?://          → http:// o https:// (la 's' es opcional)
#   (?:www\.)?         → www. opcional (grupo no-capturante)
#   [\w-]+             → nombre del dominio
#   (?:\.[\w-]+)+      → uno o más segmentos .xxx (TLD, subdominios)
#   (?:/[^\s]*)?        → path opcional (/ seguido de cualquier cosa sin espacios)
# =============================================================================

PATRON_URL = r"https?://(?:www\.)?[\w-]+(?:\.[\w-]+)+(?:/[^\s]*)?"

validar(
    "VALIDADOR DE URL",
    PATRON_URL,
    casos_validos=[
        "https://www.google.com",
        "http://example.com",
        "https://api.empresa.com/v1/usuarios",
        "https://sub.dominio.co.uk/path/to/page?param=value",
    ],
    casos_invalidos=[
        "ftp://no-es-http.com",
        "www.sin-protocolo.com",
        "solo-texto",
        "https://",
    ],
)


# =============================================================================
# 3. VALIDAR TELÉFONO (formato internacional y nacional)
# =============================================================================
# Patrón flexible que acepta varios formatos comunes:
#   (\+\d{1,3}[\s-])?    → código de país opcional: +1, +52, +34, etc.
#   \(?\d{3}\)?          → área de 3 dígitos, con o sin paréntesis
#   [\s.-]?              → separador opcional: espacio, punto o guión
#   \d{3}                → 3 dígitos
#   [\s.-]?              → separador opcional
#   \d{4}                → 4 dígitos finales
# =============================================================================

PATRON_TELEFONO = r"(\+\d{1,3}[\s-])?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"

validar(
    "VALIDADOR DE TELÉFONO",
    PATRON_TELEFONO,
    casos_validos=[
        "555-123-4567",
        "(555) 123-4567",
        "+1 555 123 4567",
        "+52-555-123-4567",
        "5551234567",
        "555.123.4567",
    ],
    casos_invalidos=[
        "12345",
        "555-12-34",
        "abcdefghij",
        "+1",
    ],
)


# =============================================================================
# 4. VALIDAR FECHA (DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY)
# =============================================================================
# Explicación:
#   (0[1-9]|[12]\d|3[01])   → día: 01-09, 10-19, 20-29, 30, 31
#   [/\-.]                   → separador: /, -, .
#   (0[1-9]|1[0-2])         → mes: 01-09, 10, 11, 12
#   \4                       → referencia al separador del grupo 4 (consistencia)
#   \d{4}                    → año de 4 dígitos
#
# NOTA: No valida fechas lógicas (ej. 31/02 sería inválido en el calendario)
# Para eso se necesita lógica adicional con datetime
# =============================================================================

PATRON_FECHA = r"(0[1-9]|[12]\d|3[01])([/\-.]) (0[1-9]|1[0-2])\2(\d{4})"
# Corregido sin espacio (el espacio fue error de formato):
PATRON_FECHA = r"(0[1-9]|[12]\d|3[01])([/\-.])(0[1-9]|1[0-2])\2(\d{4})"

validar(
    "VALIDADOR DE FECHA (DD/MM/YYYY)",
    PATRON_FECHA,
    casos_validos=[
        "25/12/2024",
        "01-01-2000",
        "31.10.1999",
        "15/06/2023",
    ],
    casos_invalidos=[
        "2024/12/25",     # Formato incorrecto (YYYY/MM/DD)
        "00/12/2024",     # Día 00 no existe
        "25/13/2024",     # Mes 13 no existe
        "25-12/2024",     # Separadores inconsistentes
        "5/6/2024",       # Día/mes sin cero inicial
    ],
)


# =============================================================================
# 5. VALIDAR CÓDIGO POSTAL
# =============================================================================
# Patrones para diferentes países:

# México: 5 dígitos
PATRON_CP_MX = r"\d{5}"

# Estados Unidos: 5 dígitos, opcionalmente +4 (ZIP+4)
PATRON_CP_US = r"\d{5}(?:-\d{4})?"

# España: 5 dígitos (01000-52999)
PATRON_CP_ES = r"(?:0[1-9]|[1-4]\d|5[0-2])\d{3}"

validar("CÓDIGO POSTAL MÉXICO (5 dígitos)", PATRON_CP_MX,
        casos_validos=["06600", "11000", "64000"],
        casos_invalidos=["1234", "123456", "ABCDE"])

validar("CÓDIGO POSTAL USA (ZIP / ZIP+4)", PATRON_CP_US,
        casos_validos=["90210", "10001-1234", "33101"],
        casos_invalidos=["9021", "1234-5678", "90210-12"])


# =============================================================================
# 6. VALIDAR CONTRASEÑA SEGURA
# =============================================================================
# Reglas:
#   (?=.*[a-z])     → lookahead: al menos una minúscula
#   (?=.*[A-Z])     → lookahead: al menos una mayúscula
#   (?=.*\d)        → lookahead: al menos un dígito
#   (?=.*[@$!%*?&]) → lookahead: al menos un carácter especial
#   [A-Za-z\d@$!%*?&]{8,}  → 8 o más caracteres del conjunto permitido
# =============================================================================

PATRON_PASSWORD = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}"

validar(
    "VALIDADOR DE CONTRASEÑA SEGURA",
    PATRON_PASSWORD,
    casos_validos=[
        "MiPass1!",
        "Segura@2024",
        "P@ssw0rd123",
        "AbCdEf1!2@",
    ],
    casos_invalidos=[
        "sinmayuscula1!",   # Sin mayúscula
        "SINMINUSCULA1!",   # Sin minúscula
        "SinNumero!",       # Sin número
        "SinEspecial1",     # Sin carácter especial
        "Corta1!",          # Menos de 8 caracteres
    ],
)


# =============================================================================
# 7. VALIDAR DIRECCIÓN IPv4
# =============================================================================
# Explicación:
#   (25[0-5]|2[0-4]\d|[01]?\d\d?)   → octeto válido: 0-255
#     25[0-5]   → 250-255
#     2[0-4]\d  → 200-249
#     [01]?\d\d? → 0-199 (con o sin cero inicial)
#   \.   → punto literal separador
#   {3}  → repetir el octeto+punto 3 veces
#   (misma expr)  → cuarto octeto (sin punto final)
# =============================================================================

_OCTETO = r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)"
PATRON_IPV4 = rf"{_OCTETO}\.{_OCTETO}\.{_OCTETO}\.{_OCTETO}"

validar(
    "VALIDADOR DE DIRECCIÓN IPv4",
    PATRON_IPV4,
    casos_validos=[
        "192.168.1.1",
        "10.0.0.1",
        "255.255.255.0",
        "0.0.0.0",
        "172.16.254.1",
    ],
    casos_invalidos=[
        "256.1.1.1",        # 256 > 255
        "192.168.1",        # Solo 3 octetos
        "192.168.1.1.1",    # 5 octetos
        "192.168.01.01",    # Puede generar ambigüedad octal (lo rechazamos)
        "abc.def.ghi.jkl",  # No son números
    ],
)


# =============================================================================
# 8. NÚMERO DE TARJETA DE CRÉDITO — Enmascarar (no validar)
# =============================================================================
# En producción NUNCA valides tarjetas solo con regex.
# Usa el algoritmo de Luhn + una librería de pagos.
# Aquí mostramos cómo DETECTAR y ENMASCARAR números de tarjeta en texto.
# =============================================================================

def enmascarar_tarjeta(texto):
    """
    Detecta números de tarjeta de crédito en el texto y los enmascara.
    Deja visibles solo los últimos 4 dígitos.

    Ejemplo: "4111 1111 1111 1234" → "**** **** **** 1234"
    """
    # Patrón: 4 grupos de 4 dígitos separados por espacios, guiones o sin separador
    patron = r"\b(\d{4}[\s-]?)(\d{4}[\s-]?)(\d{4}[\s-]?)(\d{4})\b"

    def reemplazar(m):
        # Conservar el formato del separador del original
        sep = " " if " " in m.group(0) else ("-" if "-" in m.group(0) else "")
        return f"****{sep}****{sep}****{sep}{m.group(4)}"

    return re.sub(patron, reemplazar, texto)


# Demostración de enmascarado
ejemplos_tarjetas = [
    "Tu tarjeta 4111 1111 1111 1234 fue procesada.",
    "Número: 5500-0000-0000-0004 aprobado.",
    "Tarjeta 378282246310005 registrada.",
]

print("\n" + "=" * 55)
print("  ENMASCARADO DE TARJETAS DE CRÉDITO")
print("=" * 55)

for ejemplo in ejemplos_tarjetas:
    enmascarado = enmascarar_tarjeta(ejemplo)
    print(f"  Original:   {ejemplo}")
    print(f"  Enmascarado: {enmascarado}")
    print()


# =============================================================================
# 9. EXTRACCIÓN — Extraer datos de texto no estructurado
# =============================================================================

print("=" * 55)
print("  EXTRACCIÓN DE MÚLTIPLES DATOS EN TEXTO")
print("=" * 55)

texto_factura = """
    Factura #2024-001
    Cliente: Juan García <juan.garcia@empresa.com>
    Teléfono: +52 555 123-4567
    Dirección IP servidor: 192.168.0.100
    Fecha: 15/03/2024
    Total: $1,250.99 USD
"""

# Extraer email
email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", texto_factura)
print(f"Email:    {email.group() if email else 'No encontrado'}")

# Extraer teléfono
tel = re.search(r"\+?\d[\d\s\-]{9,}", texto_factura)
print(f"Teléfono: {tel.group().strip() if tel else 'No encontrado'}")

# Extraer IP
ip = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", texto_factura)
print(f"IP:       {ip.group() if ip else 'No encontrada'}")

# Extraer fecha
fecha = re.search(r"\d{2}/\d{2}/\d{4}", texto_factura)
print(f"Fecha:    {fecha.group() if fecha else 'No encontrada'}")

# Extraer monto
monto = re.search(r"\$[\d,]+\.\d{2}", texto_factura)
print(f"Monto:    {monto.group() if monto else 'No encontrado'}")

print("\nFIN: 02_patrones_comunes.py completado")
