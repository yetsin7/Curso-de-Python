# =============================================================================
# ARCHIVO: 01_funciones_basicas.py
# TEMA: Funciones básicas — definir y llamar funciones
# =============================================================================
#
# Una función se define con la palabra clave 'def'.
# Para ejecutar la función, la "llamas" usando su nombre seguido de ().
#
# Estructura:
#   def nombre_de_la_funcion():
#       código que hace la función
#
# IMPORTANTE: definir una función NO la ejecuta.
# La función se ejecuta solo cuando la llamas.
# =============================================================================


# --- FUNCIÓN SIN PARÁMETROS ---

def saludar():
    """Imprime un saludo genérico."""
    # Las triple comillas al inicio son la 'docstring' — documentación de la función
    print("¡Hola! Bienvenido al programa.")
    print("Espero que estés aprendiendo mucho.")

# Llamar la función (ejecutarla):
saludar()
saludar()    # se puede llamar cuantas veces quieras
saludar()


# --- FUNCIÓN CON PARÁMETROS BÁSICOS ---

def saludar_persona(nombre):
    """Saluda a una persona por su nombre."""
    print(f"¡Hola, {nombre}! ¿Cómo estás?")

# Al llamarla, pasamos el argumento (el valor real)
saludar_persona("Ana")
saludar_persona("Carlos")
saludar_persona("María")


# --- FUNCIÓN QUE REALIZA UNA TAREA ---

def mostrar_separador():
    """Imprime una línea decorativa como separador visual."""
    print("-" * 40)

mostrar_separador()
print("Contenido entre separadores")
mostrar_separador()


# --- FUNCIÓN COMO UNIDAD DE LÓGICA ---
# Incluso si solo la usas una vez, encapsular lógica en funciones
# hace el código más legible y fácil de entender.

def mostrar_bienvenida():
    """Muestra el mensaje de bienvenida del programa."""
    mostrar_separador()
    print("   SISTEMA DE GESTIÓN v1.0")
    print("   Creado con Python")
    mostrar_separador()

mostrar_bienvenida()


# --- ORDEN IMPORTA: definir antes de llamar ---
# En Python, debes definir una función ANTES de llamarla.

# ❌ Esto daría error (llamar antes de definir):
# decir_adios()
# def decir_adios():
#     print("Adiós!")

# ✅ Esto funciona (definir primero, llamar después):
def decir_adios():
    """Se despide del usuario."""
    print("¡Hasta pronto!")

decir_adios()


# --- BUENAS PRÁCTICAS para nombres de funciones ---
# - Usa verbos (describe la acción que hace la función)
# - Snake_case: palabras separadas con guión bajo
# - Nombres descriptivos y claros

# ✅ Buenos nombres:
# calcular_total()
# enviar_correo()
# validar_contraseña()
# mostrar_menu()

# ❌ Malos nombres:
# f()           → ¿qué hace?
# cosa()        → demasiado vago
# hacerTodo()   → hace demasiado (una función = una responsabilidad)
