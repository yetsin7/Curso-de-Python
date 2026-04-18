# =============================================================================
# CAPÍTULO 06 - STRINGS
# Archivo: 04_ejercicios.py
# Descripción: 9 ejercicios que cubren manipulación de strings, regex,
#              validación de texto y transformaciones de formato.
# =============================================================================

import re


# =============================================================================
# EJERCICIO 1: Invertir palabras de una oración (no las letras, las palabras)
# "Hola Mundo Python" → "Python Mundo Hola"
# =============================================================================
def invertir_palabras(sentence: str) -> str:
    """
    Invierte el orden de las palabras en una oración.
    Las letras dentro de cada palabra no se modifican.

    Args:
        sentence: La oración de entrada.

    Returns:
        La misma oración con las palabras en orden inverso.

    Ejemplo:
        invertir_palabras("Hola Mundo Python") → "Python Mundo Hola"
    """
    words = sentence.split()
    return " ".join(reversed(words))


def ejercicio_invertir_palabras():
    """Demuestra la inversión del orden de las palabras en diferentes oraciones."""
    print("\n--- EJERCICIO 1: Invertir Palabras de una Oración ---")
    sentences = [
        "Hola Mundo Python",
        "El rápido zorro marrón salta sobre el perro perezoso",
        "Primero lo primero",
        "   múltiples   espacios   entre   palabras   ",
    ]
    for s in sentences:
        print(f"  Original:  '{s}'")
        print(f"  Invertida: '{invertir_palabras(s)}'\n")


# =============================================================================
# EJERCICIO 2: Capitalizar solo la primera letra de cada oración
# (No confundir con .title() que capitaliza cada palabra)
# =============================================================================
def capitalizar_oraciones(text: str) -> str:
    """
    Capitaliza únicamente la primera letra de cada oración.
    Las oraciones se separan por '. ', '! ' o '? '.

    Args:
        text: El texto a procesar.

    Returns:
        Texto con la primera letra de cada oración en mayúscula.
    """
    # Dividir en oraciones usando un patrón que conserve el delimitador
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    capitalized = [s[0].upper() + s[1:] if s else s for s in sentences]
    return " ".join(capitalized)


def ejercicio_capitalizar_oraciones():
    """Demuestra la capitalización de oraciones en un bloque de texto."""
    print("\n--- EJERCICIO 2: Capitalizar Primera Letra de cada Oración ---")
    text = "hola mundo. esto es python. ¡es increíble! ¿lo sabías?"
    print(f"  Original:   '{text}'")
    print(f"  Procesado:  '{capitalizar_oraciones(text)}'")

    # Comparación con .title() para ver la diferencia
    print(f"\n  .title():   '{text.title()}'  ← capitaliza cada palabra")
    print(f"  Correcto:   '{capitalizar_oraciones(text)}'  ← solo inicio de oración")


# =============================================================================
# EJERCICIO 3: Contar vocales y consonantes
# =============================================================================
def contar_vocales_consonantes(text: str) -> dict:
    """
    Cuenta vocales y consonantes en un texto, ignorando espacios
    y caracteres especiales.

    Args:
        text: El texto a analizar.

    Returns:
        Diccionario con 'vocales', 'consonantes' y 'otros'.
    """
    vowels = set("aeiouáéíóúüAEIOUÁÉÍÓÚÜ")
    consonants_count = 0
    vowels_count = 0
    others_count = 0

    for char in text:
        if char.isalpha():
            if char in vowels:
                vowels_count += 1
            else:
                consonants_count += 1
        elif not char.isspace():
            others_count += 1

    return {"vocales": vowels_count, "consonantes": consonants_count, "otros": others_count}


def ejercicio_contar_vocales():
    """Cuenta vocales y consonantes en un texto de ejemplo."""
    print("\n--- EJERCICIO 3: Contar Vocales y Consonantes ---")
    text = input("Ingresa un texto (o ENTER para usar ejemplo): ").strip()
    if not text:
        text = "Python es un lenguaje de programación poderoso."

    result = contar_vocales_consonantes(text)
    total_letters = result["vocales"] + result["consonantes"]

    print(f"\n  Texto: '{text}'")
    print(f"  Vocales:     {result['vocales']} ({result['vocales']/total_letters*100:.1f}%)")
    print(f"  Consonantes: {result['consonantes']} ({result['consonantes']/total_letters*100:.1f}%)")
    print(f"  Otros chars: {result['otros']}")


# =============================================================================
# EJERCICIO 4: Comprimir string (Run-Length Encoding)
# "aabbbcccc" → "a2b3c4"
# =============================================================================
def comprimir_string(text: str) -> str:
    """
    Comprime un string usando Run-Length Encoding (RLE).
    Cada grupo de caracteres iguales se reemplaza por el carácter
    seguido de cuántas veces se repite.
    Si el comprimido no es más corto, retorna el original.

    Args:
        text: String a comprimir.

    Returns:
        String comprimido o el original si no hay ganancia.

    Ejemplo:
        comprimir_string("aabbbcccc") → "a2b3c4"
        comprimir_string("abc")       → "abc"  (no comprime)
    """
    if not text:
        return text

    result = []
    count = 1

    for i in range(1, len(text)):
        if text[i] == text[i - 1]:
            count += 1
        else:
            # Agregar el carácter y su conteo (omitir '1' si count == 1)
            result.append(text[i - 1] + (str(count) if count > 1 else ""))
            count = 1

    # Último grupo
    result.append(text[-1] + (str(count) if count > 1 else ""))
    compressed = "".join(result)

    # Retornar el original si no se comprimió
    return compressed if len(compressed) < len(text) else text


def ejercicio_comprimir_string():
    """Demuestra la compresión RLE con varios ejemplos."""
    print("\n--- EJERCICIO 4: Comprimir String (Run-Length Encoding) ---")
    examples = ["aabbbcccc", "aaabbaaa", "abcd", "aaaaaaaaaa", "aAbBccCC"]
    for s in examples:
        compressed = comprimir_string(s)
        ratio = len(compressed) / len(s) * 100
        print(f"  '{s:<15}' → '{compressed:<12}' ({ratio:.0f}% del original)")


# =============================================================================
# EJERCICIO 5: Validar contraseña fuerte
# Requisitos: mayúscula, minúscula, número, carácter especial, mínimo 8 chars.
# =============================================================================
def validar_contrasena(password: str) -> tuple:
    """
    Valida si una contraseña cumple los criterios de seguridad.

    Criterios:
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un dígito
    - Al menos un carácter especial (!@#$%^&*...)

    Args:
        password: La contraseña a validar.

    Returns:
        Tupla (es_valida: bool, errores: list[str]).
    """
    errors = []

    if len(password) < 8:
        errors.append("Mínimo 8 caracteres")
    if not re.search(r'[A-Z]', password):
        errors.append("Al menos una mayúscula")
    if not re.search(r'[a-z]', password):
        errors.append("Al menos una minúscula")
    if not re.search(r'\d', password):
        errors.append("Al menos un número")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password):
        errors.append("Al menos un carácter especial (!@#$%...)")

    return len(errors) == 0, errors


def ejercicio_validar_contrasena():
    """Valida varias contraseñas de ejemplo y una ingresada por el usuario."""
    print("\n--- EJERCICIO 5: Validar Contraseña Fuerte ---")
    test_passwords = ["abc", "password", "Password1", "P@ssw0rd!", "12345678"]

    for pwd in test_passwords:
        is_valid, errors = validar_contrasena(pwd)
        status = "✓ VÁLIDA" if is_valid else "✗ INVÁLIDA"
        print(f"\n  '{pwd}': {status}")
        if errors:
            for error in errors:
                print(f"    - {error}")


# =============================================================================
# EJERCICIO 6: Extraer emails de un texto usando regex
# =============================================================================
def extraer_emails(text: str) -> list:
    """
    Extrae todas las direcciones de email válidas encontradas en un texto.

    Args:
        text: El texto donde buscar emails.

    Returns:
        Lista de emails encontrados (sin duplicados, en orden).
    """
    pattern = r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b'
    emails = re.findall(pattern, text)
    # Eliminar duplicados preservando el orden
    seen = set()
    unique = []
    for email in emails:
        if email.lower() not in seen:
            seen.add(email.lower())
            unique.append(email)
    return unique


def ejercicio_extraer_emails():
    """Demuestra la extracción de emails de un texto con regex."""
    print("\n--- EJERCICIO 6: Extraer Emails con Regex ---")
    text = """
    Contacta al equipo en soporte@empresa.com o ventas@empresa.com.
    También puedes escribir a admin@test.org o al CEO: john.doe@company.co.uk
    Emails inválidos: @invalido.com, sindominio@, texto normal, no_es_email
    El correo duplicado soporte@empresa.com ya fue listado.
    """
    emails = extraer_emails(text)
    print(f"  Emails encontrados ({len(emails)}):")
    for email in emails:
        print(f"    - {email}")


# =============================================================================
# EJERCICIO 7: Censurar palabras en un texto
# =============================================================================
def censurar_palabras(text: str, banned_words: list, replacement: str = "***") -> str:
    """
    Reemplaza palabras prohibidas en un texto por un símbolo de censura.
    La comparación ignora mayúsculas/minúsculas pero preserva la posición.

    Args:
        text:         Texto original.
        banned_words: Lista de palabras a censurar.
        replacement:  Texto de reemplazo (por defecto '***').

    Returns:
        Texto con las palabras censuradas.
    """
    result = text
    for word in banned_words:
        # Reemplazar preservando la capitalización con regex insensible a mayúsculas
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        result = pattern.sub(replacement, result)
    return result


def ejercicio_censurar():
    """Demuestra la censura de palabras en textos de ejemplo."""
    print("\n--- EJERCICIO 7: Censurar Palabras ---")
    text = "El spam y el SPAM son malos. También el Spam molesta a los usuarios."
    banned = ["spam", "molesta"]
    censored = censurar_palabras(text, banned)
    print(f"  Original:  '{text}'")
    print(f"  Censurado: '{censored}'")


# =============================================================================
# EJERCICIO 8: Formatear número de teléfono
# Limpia y formatea cualquier número a formato estándar (XXX) XXX-XXXX.
# =============================================================================
def formatear_telefono(phone: str, country_code: str = "+1") -> str:
    """
    Limpia un número de teléfono y lo formatea al estándar (XXX) XXX-XXXX.
    Elimina espacios, guiones, paréntesis y otros caracteres no numéricos.

    Args:
        phone:        String con el número de teléfono en cualquier formato.
        country_code: Código de país a anteponer (por defecto '+1' para EE.UU.)

    Returns:
        Número formateado, o mensaje de error si el formato es inválido.

    Ejemplo:
        formatear_telefono("5551234567")    → "+1 (555) 123-4567"
        formatear_telefono("555-123-4567")  → "+1 (555) 123-4567"
    """
    # Extraer solo los dígitos
    digits = re.sub(r'\D', '', phone)

    # Eliminar el 1 inicial si es un número de EE.UU. de 11 dígitos
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]

    if len(digits) == 10:
        return f"{country_code} ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    else:
        return f"Formato inválido: se esperaban 10 dígitos, se obtuvieron {len(digits)}"


def ejercicio_formatear_telefono():
    """Formatea números de teléfono desde varios formatos de entrada."""
    print("\n--- EJERCICIO 8: Formatear Número de Teléfono ---")
    phones = ["5551234567", "555-123-4567", "(555) 123 4567",
              "1-555-123-4567", "555.123.4567", "12345"]
    for phone in phones:
        formatted = formatear_telefono(phone)
        print(f"  '{phone:<20}' → '{formatted}'")


# =============================================================================
# EJERCICIO 9: Convertir entre snake_case, camelCase y PascalCase
# =============================================================================
def to_snake_case(text: str) -> str:
    """Convierte cualquier formato a snake_case."""
    # Insertar guión bajo antes de mayúsculas en camelCase/PascalCase
    s = re.sub(r'([A-Z])', r'_\1', text)
    # Reemplazar espacios y guiones por guión bajo
    s = re.sub(r'[\s\-]+', '_', s)
    return s.strip('_').lower()


def to_camel_case(text: str) -> str:
    """Convierte cualquier formato a camelCase."""
    words = re.split(r'[\s_\-]+', to_snake_case(text))
    return words[0].lower() + ''.join(w.capitalize() for w in words[1:])


def to_pascal_case(text: str) -> str:
    """Convierte cualquier formato a PascalCase."""
    words = re.split(r'[\s_\-]+', to_snake_case(text))
    return ''.join(w.capitalize() for w in words)


def ejercicio_convertir_casos():
    """Demuestra la conversión entre los tres formatos de nomenclatura."""
    print("\n--- EJERCICIO 9: Convertir snake_case ↔ camelCase ↔ PascalCase ---")
    examples = ["hello world", "my_variable_name", "myVariableName",
                "MyClassName", "convert-this-string"]

    print(f"  {'Original':<25} {'snake_case':<25} {'camelCase':<25} {'PascalCase'}")
    print("  " + "-" * 90)
    for text in examples:
        snake = to_snake_case(text)
        camel = to_camel_case(text)
        pascal = to_pascal_case(text)
        print(f"  {text:<25} {snake:<25} {camel:<25} {pascal}")


# =============================================================================
# MENÚ PRINCIPAL
# =============================================================================
def main():
    """Menú para ejecutar cada ejercicio del capítulo de strings."""
    exercises = {
        "1": ("Invertir palabras de una oración", ejercicio_invertir_palabras),
        "2": ("Capitalizar inicio de oraciones", ejercicio_capitalizar_oraciones),
        "3": ("Contar vocales y consonantes", ejercicio_contar_vocales),
        "4": ("Comprimir string (RLE)", ejercicio_comprimir_string),
        "5": ("Validar contraseña fuerte", ejercicio_validar_contrasena),
        "6": ("Extraer emails con regex", ejercicio_extraer_emails),
        "7": ("Censurar palabras", ejercicio_censurar),
        "8": ("Formatear teléfono", ejercicio_formatear_telefono),
        "9": ("Convertir snake/camel/pascal", ejercicio_convertir_casos),
        "0": ("Salir", None),
    }

    print("=" * 50)
    print("   EJERCICIOS - CAPÍTULO 06: STRINGS")
    print("=" * 50)

    while True:
        print("\nElige un ejercicio:")
        for key, (name, _) in exercises.items():
            print(f"  [{key}] {name}")

        choice = input("\nOpción: ").strip()

        if choice == "0":
            print("¡Hasta luego!")
            break
        elif choice in exercises:
            _, func = exercises[choice]
            func()
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
