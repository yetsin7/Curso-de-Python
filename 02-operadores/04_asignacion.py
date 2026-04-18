# =============================================================================
# ARCHIVO: 04_asignacion.py
# TEMA: Operadores de asignación — atajos para actualizar variables
# =============================================================================
#
# Ya conoces el operador básico de asignación: =
# Python tiene operadores compuestos que combinan una operación con asignación.
# Son atajos que hacen el código más corto y legible.
# =============================================================================

# Forma larga vs. forma corta:

puntos = 100

# Forma larga (sin atajo):
puntos = puntos + 10
print(puntos)    # 110

# Forma corta con operador de asignación:
puntos += 10     # equivale a: puntos = puntos + 10
print(puntos)    # 120

puntos -= 5      # equivale a: puntos = puntos - 5
print(puntos)    # 115

puntos *= 2      # equivale a: puntos = puntos * 2
print(puntos)    # 230

puntos //= 3     # equivale a: puntos = puntos // 3  (división entera)
print(puntos)    # 76

puntos %= 10     # equivale a: puntos = puntos % 10  (módulo)
print(puntos)    # 6

puntos **= 2     # equivale a: puntos = puntos ** 2  (potencia)
print(puntos)    # 36


# --- EJEMPLO PRÁCTICO: acumulador de ventas ---

total_ventas = 0.0

# Cada venta se agrega al total
total_ventas += 150.00
total_ventas += 89.50
total_ventas += 210.75

print(f"Total de ventas del día: ${total_ventas:.2f}")   # $450.25


# --- EJEMPLO PRÁCTICO: contador ---

contador = 0

# Simula que algo ocurrió 5 veces
contador += 1   # ocurrencia 1
contador += 1   # ocurrencia 2
contador += 1   # ocurrencia 3
contador += 1   # ocurrencia 4
contador += 1   # ocurrencia 5

print(f"El evento ocurrió {contador} veces")    # 5


# --- RESUMEN DE OPERADORES DE ASIGNACIÓN ---
# +=   suma y asigna
# -=   resta y asigna
# *=   multiplica y asigna
# /=   divide y asigna
# //=  divide entero y asigna
# %=   módulo y asigna
# **=  potencia y asigna

# =============================================================================
# CONSEJO: += y -= son los más usados en el día a día.
# Los demás los usarás cuando los necesites.
# =============================================================================
