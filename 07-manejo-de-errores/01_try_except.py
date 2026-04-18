# =============================================================================
# ARCHIVO: 01_try_except.py
# TEMA: try/except — capturar y manejar errores
# =============================================================================
#
# try/except te permite "intentar" ejecutar código que podría fallar,
# y manejar el error si ocurre sin que el programa se detenga.
#
# Estructura completa:
#   try:
#       código que puede fallar
#   except TipoDeError:
#       qué hacer si ocurre ese error
#   else:
#       qué hacer si NO ocurrió ningún error
#   finally:
#       siempre se ejecuta, ocurra o no un error
# =============================================================================


# --- TRY/EXCEPT BÁSICO ---

# Sin manejo de errores, esto detiene el programa:
# resultado = 10 / 0   # ZeroDivisionError

# Con manejo de errores:
try:
    resultado = 10 / 0
except ZeroDivisionError:
    print("Error: no puedes dividir entre cero")
    resultado = None

print(f"Resultado: {resultado}")


# --- CAPTURAR EL OBJETO DEL ERROR ---
# Usando 'as e' puedes acceder al mensaje del error.

try:
    numero = int("hola")
except ValueError as e:
    print(f"Error de conversión: {e}")    # invalid literal for int()...


# --- MÚLTIPLES EXCEPT ---
# Puedes manejar distintos tipos de error de forma diferente.

def dividir_seguro(a, b):
    """Divide dos números con manejo de errores."""
    try:
        resultado = a / b
    except ZeroDivisionError:
        print("Error: división entre cero")
        return None
    except TypeError:
        print("Error: los argumentos deben ser números")
        return None
    else:
        # Este bloque se ejecuta SOLO si no hubo error
        print(f"Éxito: {a} / {b} = {resultado}")
        return resultado

dividir_seguro(10, 2)     # Éxito
dividir_seguro(10, 0)     # ZeroDivisionError
dividir_seguro(10, "a")   # TypeError


# --- FINALLY: siempre se ejecuta ---
# Útil para "limpiar" recursos (cerrar archivos, conexiones, etc.)

def leer_dato(texto):
    """Convierte texto a número, siempre imprime que terminó."""
    try:
        numero = int(texto)
        print(f"Convertido: {numero}")
        return numero
    except ValueError:
        print(f"'{texto}' no es un número válido")
        return None
    finally:
        print("--- operación finalizada ---")   # siempre se ejecuta

leer_dato("42")
leer_dato("hola")


# --- CAPTURAR CUALQUIER EXCEPCIÓN ---
# Usa Exception para atrapar cualquier error (con precaución).

try:
    x = int(input("Ingresa un número: "))
    print(f"El doble es: {x * 2}")
except ValueError:
    print("Eso no es un número entero válido")
except Exception as e:
    # Captura cualquier otro error inesperado
    print(f"Error inesperado: {type(e).__name__}: {e}")


# --- RAISE: lanzar errores propios ---
# A veces necesitas lanzar un error intencionalmente para señalar un problema.

def calcular_descuento(precio, descuento):
    """
    Aplica un descuento al precio.
    Lanza ValueError si los argumentos no son válidos.
    """
    if precio < 0:
        raise ValueError("El precio no puede ser negativo")
    if not 0 <= descuento <= 1:
        raise ValueError("El descuento debe estar entre 0 y 1")

    return precio * (1 - descuento)

# Usando la función con manejo de errores:
try:
    resultado = calcular_descuento(100, 0.20)
    print(f"Precio con descuento: ${resultado}")
except ValueError as e:
    print(f"Error: {e}")

try:
    resultado = calcular_descuento(-50, 0.10)
except ValueError as e:
    print(f"Error: {e}")


# --- EJEMPLO PRÁCTICO: solicitar número al usuario de forma segura ---

def pedir_numero(mensaje, minimo=None, maximo=None):
    """
    Solicita un número entero al usuario con validación.
    Repite hasta obtener una entrada válida.
    """
    while True:
        try:
            numero = int(input(mensaje))

            if minimo is not None and numero < minimo:
                print(f"El número debe ser mayor o igual a {minimo}")
                continue

            if maximo is not None and numero > maximo:
                print(f"El número debe ser menor o igual a {maximo}")
                continue

            return numero

        except ValueError:
            print("Por favor, ingresa un número entero válido")

edad = pedir_numero("¿Cuántos años tienes? (1-120): ", minimo=1, maximo=120)
print(f"Registrado: {edad} años")
