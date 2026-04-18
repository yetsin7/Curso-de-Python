# =============================================================================
# CAPÍTULO 04 - FUNCIONES
# Archivo: 05_funciones_utiles.py
# Descripción: Librería de funciones de utilidad reutilizables.
#              Cada función resuelve un problema práctico real y
#              puede ser importada en otros proyectos.
# =============================================================================

import re
from datetime import date, datetime
from collections import Counter


# =============================================================================
# FUNCIÓN 1: Validar email con regex
# Verifica si una cadena tiene el formato básico de un email válido.
# =============================================================================
def validar_email(email: str) -> bool:
    """
    Verifica si el string 'email' tiene un formato válido de correo.
    Usa una expresión regular básica que cubre la mayoría de los casos.

    Args:
        email: El string a validar.

    Returns:
        True si tiene formato de email, False en caso contrario.

    Ejemplo:
        validar_email("user@example.com") → True
        validar_email("sin_arroba.com")   → False
    """
    # Patrón: algo@algo.algo (al menos un punto en el dominio)
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# =============================================================================
# FUNCIÓN 2: Formatear un número como moneda
# Convierte un número a su representación como monto monetario.
# =============================================================================
def formatear_moneda(monto: float, simbolo: str = '$', decimales: int = 2) -> str:
    """
    Formatea un número flotante como cadena de moneda legible.

    Args:
        monto:     El valor numérico a formatear.
        simbolo:   Símbolo de moneda (por defecto '$').
        decimales: Cantidad de decimales a mostrar (por defecto 2).

    Returns:
        String con el monto formateado, ej: "$1,234.56"

    Ejemplo:
        formatear_moneda(1234567.8)       → "$1,234,567.80"
        formatear_moneda(99.5, "€", 2)    → "€99.50"
    """
    # Formatear con separador de miles y los decimales solicitados
    formatted = f"{monto:,.{decimales}f}"
    return f"{simbolo}{formatted}"


# =============================================================================
# FUNCIÓN 3: Truncar texto con sufijo
# Acorta un texto al número máximo de caracteres especificado.
# =============================================================================
def truncar_texto(texto: str, max_chars: int, sufijo: str = '...') -> str:
    """
    Trunca un texto si supera la longitud máxima, añadiendo un sufijo.

    Args:
        texto:     El texto a truncar.
        max_chars: Longitud máxima permitida (incluyendo el sufijo).
        sufijo:    Texto a agregar al final si se trunca (por defecto '...').

    Returns:
        El texto original si cabe, o el texto truncado con sufijo.

    Ejemplo:
        truncar_texto("Hola Mundo", 7)     → "Hola..."
        truncar_texto("Hola", 10)          → "Hola"
    """
    if len(texto) <= max_chars:
        return texto
    # Calcular espacio disponible para el texto antes del sufijo
    limite = max_chars - len(sufijo)
    if limite <= 0:
        return sufijo[:max_chars]
    return texto[:limite] + sufijo


# =============================================================================
# FUNCIÓN 4: Calcular edad desde fecha de nacimiento
# Recibe una fecha en formato 'YYYY-MM-DD' y retorna la edad en años.
# =============================================================================
def calcular_edad(fecha_nacimiento_str: str) -> int:
    """
    Calcula la edad actual en años a partir de una fecha de nacimiento.

    Args:
        fecha_nacimiento_str: Fecha en formato 'YYYY-MM-DD', ej: '1990-05-15'.

    Returns:
        Edad en años completos (entero).

    Raises:
        ValueError: Si el formato de fecha no es 'YYYY-MM-DD'.

    Ejemplo:
        calcular_edad("1990-05-15") → 34  (dependiendo de la fecha actual)
    """
    birth_date = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
    today = date.today()
    # Restar 1 si todavía no ha llegado el cumpleaños este año
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


# =============================================================================
# FUNCIÓN 5: Generar slug desde texto
# Convierte un título legible a un slug válido para URLs.
# =============================================================================
def generar_slug(texto: str) -> str:
    """
    Convierte un texto con espacios, mayúsculas y caracteres especiales
    en un slug válido para URLs (solo minúsculas, números y guiones).

    Args:
        texto: El texto a convertir, ej: "Hola Mundo! (2024)"

    Returns:
        Slug limpio, ej: "hola-mundo-2024"

    Ejemplo:
        generar_slug("Python es Genial!")   → "python-es-genial"
        generar_slug("  múltiples  espacios  ") → "multiples-espacios"
    """
    # Reemplazar caracteres acentuados comunes
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
        'ñ': 'n', 'Ñ': 'n', 'ü': 'u', 'Ü': 'u',
    }
    for char, replacement in replacements.items():
        texto = texto.replace(char, replacement)

    texto = texto.lower()
    # Dejar solo letras, números y espacios
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    # Reemplazar múltiples espacios por un guión
    texto = re.sub(r'\s+', '-', texto.strip())
    return texto


# =============================================================================
# FUNCIÓN 6: Contar palabras con frecuencia
# Retorna el total de palabras únicas y la frecuencia de cada una.
# =============================================================================
def contar_palabras(texto: str) -> dict:
    """
    Cuenta las palabras en un texto, ignorando mayúsculas y puntuación.
    Retorna un diccionario con estadísticas de frecuencia.

    Args:
        texto: El texto a analizar.

    Returns:
        Diccionario con:
        - 'total':    Total de palabras (con repeticiones)
        - 'unicas':   Cantidad de palabras distintas
        - 'frecuencia': Counter con frecuencia de cada palabra (más común primero)

    Ejemplo:
        contar_palabras("hola mundo hola")
        → {'total': 3, 'unicas': 2, 'frecuencia': Counter({'hola': 2, 'mundo': 1})}
    """
    # Extraer solo palabras (ignorar puntuación)
    words = re.findall(r'\b[a-záéíóúüñ]+\b', texto.lower())
    frequency = Counter(words)

    return {
        "total": len(words),
        "unicas": len(frequency),
        "frecuencia": frequency
    }


# =============================================================================
# FUNCIÓN 7: Verificar palíndromo ignorando espacios y capitalización
# =============================================================================
def es_palindromo(texto: str) -> bool:
    """
    Verifica si un texto es palíndromo, ignorando espacios,
    signos de puntuación y diferencias de capitalización.

    Args:
        texto: La cadena a verificar.

    Returns:
        True si es palíndromo, False en caso contrario.

    Ejemplo:
        es_palindromo("Anita lava la tina") → True
        es_palindromo("reconocer")          → True
        es_palindromo("hola")               → False
    """
    # Limpiar: solo letras y dígitos en minúsculas
    cleaned = re.sub(r'[^a-z0-9]', '', texto.lower())
    return cleaned == cleaned[::-1]


# =============================================================================
# FUNCIÓN 8: Convertir número arábigo a romano
# Soporta números del 1 al 3999.
# =============================================================================
def convertir_a_romano(numero: int) -> str:
    """
    Convierte un número entero arábigo a su representación en números romanos.
    Soporta el rango de 1 a 3999.

    Args:
        numero: Entero entre 1 y 3999.

    Returns:
        String con la representación romana, ej: "XIV", "MMXXIV"

    Raises:
        ValueError: Si el número está fuera del rango soportado.

    Ejemplo:
        convertir_a_romano(2024) → "MMXXIV"
        convertir_a_romano(14)   → "XIV"
    """
    if not (1 <= numero <= 3999):
        raise ValueError(f"El número debe estar entre 1 y 3999, recibido: {numero}")

    # Tabla de valores en orden descendente (incluye substractivos como IV, IX)
    values = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
    ]

    result = ""
    for value, symbol in values:
        while numero >= value:
            result += symbol
            numero -= value
    return result


# =============================================================================
# FUNCIÓN 9: Distancia de Levenshtein
# Calcula cuántas ediciones (inserción, eliminación, sustitución)
# se necesitan para convertir s1 en s2.
# =============================================================================
def distancia_levenshtein(s1: str, s2: str) -> int:
    """
    Calcula la distancia de edición (Levenshtein) entre dos strings.
    La distancia es el número mínimo de operaciones de un solo carácter
    (inserción, eliminación o sustitución) para transformar s1 en s2.

    Args:
        s1: Primer string.
        s2: Segundo string.

    Returns:
        Entero con la distancia de edición (0 = idénticos).

    Ejemplo:
        distancia_levenshtein("kitten", "sitting") → 3
        distancia_levenshtein("python", "python")  → 0
        distancia_levenshtein("gato", "pato")      → 1
    """
    len1, len2 = len(s1), len(s2)

    # Crear la matriz de distancias (programación dinámica)
    # dp[i][j] = distancia entre s1[:i] y s2[:j]
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    # Casos base: transformar a/desde string vacío
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    # Rellenar la matriz
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # Mismos caracteres: sin costo
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],     # Eliminación
                    dp[i][j - 1],     # Inserción
                    dp[i - 1][j - 1]  # Sustitución
                )

    return dp[len1][len2]


# =============================================================================
# DEMO: Mostrar todas las funciones en acción
# =============================================================================
def demo():
    """
    Ejecuta una demostración de todas las funciones de utilidad
    con ejemplos representativos de cada una.
    """
    print("=" * 55)
    print("   LIBRERÍA DE FUNCIONES ÚTILES - CAPÍTULO 04")
    print("=" * 55)

    # 1. Validar email
    print("\n1. validar_email()")
    emails = ["user@example.com", "invalido@", "otro@dominio.org", "sin_arroba.com"]
    for e in emails:
        print(f"   {e:<30} → {validar_email(e)}")

    # 2. Formatear moneda
    print("\n2. formatear_moneda()")
    print(f"   1234567.8         → {formatear_moneda(1234567.8)}")
    print(f"   99.5, '€'         → {formatear_moneda(99.5, '€')}")
    print(f"   0.5, 'Bs.', 0     → {formatear_moneda(0.5, 'Bs.', 0)}")

    # 3. Truncar texto
    print("\n3. truncar_texto()")
    largo = "Python es un lenguaje increíble y muy poderoso"
    print(f"   Original: '{largo}'")
    print(f"   Truncado a 25: '{truncar_texto(largo, 25)}'")
    print(f"   Truncado a 10: '{truncar_texto(largo, 10)}'")

    # 4. Calcular edad
    print("\n4. calcular_edad()")
    print(f"   '1990-05-15' → {calcular_edad('1990-05-15')} años")
    print(f"   '2000-01-01' → {calcular_edad('2000-01-01')} años")

    # 5. Generar slug
    print("\n5. generar_slug()")
    slugs = ["Hola Mundo!", "Python es Genial 2024", "Café & Té", "  múltiples  espacios  "]
    for s in slugs:
        print(f"   '{s}' → '{generar_slug(s)}'")

    # 6. Contar palabras
    print("\n6. contar_palabras()")
    texto = "el gato come el ratón y el ratón huye del gato"
    resultado = contar_palabras(texto)
    print(f"   Texto: '{texto}'")
    print(f"   Total palabras: {resultado['total']}")
    print(f"   Palabras únicas: {resultado['unicas']}")
    print(f"   Más comunes: {resultado['frecuencia'].most_common(3)}")

    # 7. Es palíndromo
    print("\n7. es_palindromo()")
    textos = ["Anita lava la tina", "reconocer", "Yo soy", "hola mundo"]
    for t in textos:
        print(f"   '{t}' → {es_palindromo(t)}")

    # 8. Convertir a romano
    print("\n8. convertir_a_romano()")
    numeros = [1, 4, 9, 14, 40, 90, 400, 900, 1994, 2024, 3999]
    for n in numeros:
        print(f"   {n:5d} → {convertir_a_romano(n)}")

    # 9. Distancia Levenshtein
    print("\n9. distancia_levenshtein()")
    pares = [("kitten", "sitting"), ("python", "python"), ("gato", "pato"), ("casa", "cama")]
    for s1, s2 in pares:
        dist = distancia_levenshtein(s1, s2)
        print(f"   '{s1}' ↔ '{s2}' → distancia: {dist}")


if __name__ == "__main__":
    demo()
