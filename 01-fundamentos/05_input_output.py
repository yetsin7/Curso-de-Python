# =============================================================================
# ARCHIVO: 05_input_output.py
# TEMA: input() y output — interactuar con el usuario
# =============================================================================
#
# Hasta ahora solo hemos mostrado cosas (output = salida).
# Ahora aprenderemos a pedirle datos al usuario (input = entrada).
#
# input()  → pide al usuario que escriba algo y lo captura como texto
# print()  → muestra algo en la consola (ya lo conoces)
#
# IMPORTANTE: input() SIEMPRE devuelve texto (str), incluso si el usuario
# escribe un número. Tendrás que convertirlo si necesitas hacer cálculos.
# =============================================================================


# --- USO BÁSICO DE input() ---

# Pide al usuario que escriba su nombre
# El texto dentro de las comillas es el "mensaje de invitación" (prompt)
nombre = input("¿Cómo te llamas? ")

# Ahora la variable 'nombre' tiene lo que el usuario escribió
print("Hola,", nombre)
print(f"¡Bienvenido, {nombre}!")   # usando f-string


# --- input() SIEMPRE DEVUELVE TEXTO ---

# Aunque el usuario escriba "25", lo que llega es el texto "25", no el número 25
edad_texto = input("¿Cuántos años tienes? ")

# Esto funcionaría para mostrarlo:
print("Tienes", edad_texto, "años")

# Pero esto daría ERROR porque no puedes sumar texto y número:
# print(edad_texto + 1)   # ❌ Error

# La solución: convertir el texto a número con int()
edad_numero = int(edad_texto)
print("El año que viene tendrás", edad_numero + 1, "años")


# --- FORMA MÁS CORTA: convertir en la misma línea ---

# En lugar de hacer dos pasos, se puede hacer en uno:
precio = float(input("Ingresa el precio del producto: "))
# float() convierte a decimal, int() convierte a entero

cantidad = int(input("¿Cuántas unidades quieres? "))

total = precio * cantidad
print(f"El total es: ${total:.2f}")   # :.2f muestra solo 2 decimales


# --- EJEMPLO COMPLETO: mini calculadora ---

print("\n--- Mini Calculadora ---")
numero1 = float(input("Primer número: "))
numero2 = float(input("Segundo número: "))

suma = numero1 + numero2
print(f"{numero1} + {numero2} = {suma}")


# --- PAUSAR EL PROGRAMA con input() ---
# A veces se usa input() sin guardar el resultado, solo para pausar.
input("\nPresiona Enter para continuar...")
print("¡Continuamos!")


# =============================================================================
# EJERCICIO: Crea un programa que le pregunte al usuario:
#   1. Su nombre
#   2. El año en que nació
# Y luego imprima: "Hola [nombre], tienes aproximadamente [edad] años."
# Pista: edad = 2024 - año_de_nacimiento
# =============================================================================
