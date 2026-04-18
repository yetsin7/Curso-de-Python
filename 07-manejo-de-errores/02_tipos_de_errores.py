# =============================================================================
# ARCHIVO: 02_tipos_de_errores.py
# TEMA: Los errores más comunes en Python — cuándo y por qué ocurren
# =============================================================================
#
# Saber reconocer el tipo de error en el mensaje de Python te ahorrará
# mucho tiempo al depurar. Cada error tiene un nombre descriptivo.
# =============================================================================


# --- ValueError: valor incorrecto para el tipo ---
# Ocurre cuando la operación es válida pero el valor no lo es.

try:
    int("hola")           # "hola" no puede convertirse a entero
except ValueError as e:
    print(f"ValueError: {e}")

try:
    int("3.14")           # tampoco, aunque sea número
except ValueError as e:
    print(f"ValueError: {e}")


# --- TypeError: tipo de dato incorrecto ---
# Ocurre cuando usas un tipo donde se espera otro.

try:
    resultado = "5" + 3   # no puedes sumar texto y número directamente
except TypeError as e:
    print(f"TypeError: {e}")

try:
    len(42)               # len() solo funciona con secuencias, no con números
except TypeError as e:
    print(f"TypeError: {e}")


# --- IndexError: índice fuera de rango ---
# Ocurre cuando accedes a un índice que no existe en la lista/tupla/string.

try:
    lista = [1, 2, 3]
    print(lista[10])      # solo existen índices 0, 1, 2
except IndexError as e:
    print(f"IndexError: {e}")


# --- KeyError: clave no existe en diccionario ---
# Ocurre al acceder a una clave que no está en el diccionario.

try:
    config = {"debug": True}
    print(config["puerto"])   # "puerto" no existe
except KeyError as e:
    print(f"KeyError: {e}")


# --- ZeroDivisionError: división entre cero ---

try:
    resultado = 10 / 0
except ZeroDivisionError as e:
    print(f"ZeroDivisionError: {e}")


# --- AttributeError: el objeto no tiene ese atributo/método ---
# Ocurre cuando llamas un método que no existe en ese tipo.

try:
    numero = 42
    numero.upper()    # los enteros no tienen método upper()
except AttributeError as e:
    print(f"AttributeError: {e}")


# --- NameError: variable no definida ---
# Ocurre cuando usas una variable que no existe.

try:
    print(variable_inexistente)
except NameError as e:
    print(f"NameError: {e}")


# --- FileNotFoundError: archivo no encontrado ---
# Ocurre al intentar abrir un archivo que no existe.

try:
    with open("archivo_que_no_existe.txt", "r") as f:
        contenido = f.read()
except FileNotFoundError as e:
    print(f"FileNotFoundError: {e}")


# --- ImportError / ModuleNotFoundError: módulo no encontrado ---
# Ocurre al importar un módulo que no está instalado.

try:
    import modulo_que_no_existe
except ModuleNotFoundError as e:
    print(f"ModuleNotFoundError: {e}")


# --- CÓMO LEER UN MENSAJE DE ERROR EN PYTHON ---
#
# Cuando Python muestra un error, el formato es:
#
#   Traceback (most recent call last):
#     File "archivo.py", line 10, in nombre_funcion
#       codigo_que_falló
#   TipoDeError: descripción del error
#
# Cómo leerlo:
#   1. Ve al FINAL del mensaje — ahí está el tipo y la descripción del error
#   2. Mira la línea indicada ("line 10") en tu archivo
#   3. Entiende qué tipo de error es (ValueError, TypeError, etc.)
#   4. Lee la descripción para entender qué salió mal

print("\n--- Resumen de errores comunes ---")
errores = {
    "ValueError":         "valor incorrecto para la operación",
    "TypeError":          "tipo de dato incorrecto",
    "IndexError":         "índice fuera del rango de la lista",
    "KeyError":           "clave no encontrada en el diccionario",
    "ZeroDivisionError":  "intento de dividir entre cero",
    "AttributeError":     "el objeto no tiene ese método o atributo",
    "NameError":          "variable o función no definida",
    "FileNotFoundError":  "el archivo no existe",
    "ModuleNotFoundError":"el módulo no está instalado",
}

for error, descripcion in errores.items():
    print(f"  {error:<25} → {descripcion}")
