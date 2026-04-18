# =============================================================================
# ARCHIVO: 02_variables.py
# TEMA: Variables — guardar información en memoria
# =============================================================================
#
# Una VARIABLE es un nombre que le das a un espacio en memoria donde
# guardas un valor. Piénsala como una caja con una etiqueta.
#
# Ejemplo real:
#   edad = 25
#   ^---^   ^--^
#   nombre  valor
#   de la
#   caja
#
# En Python, crear una variable es tan simple como escribir:
#   nombre_de_la_variable = valor
#
# El signo = en programación NO significa "igual" como en matemáticas.
# Significa "guarda este valor en esta variable" (asignación).
# =============================================================================


# --- CREAR VARIABLES ---

# Variable que guarda un número entero
edad = 20

# Variable que guarda un número decimal
altura = 1.75

# Variable que guarda texto (string)
nombre = "Ana"

# Variable que guarda verdadero o falso (booleano)
es_estudiante = True

# Mostrar las variables con print()
print(nombre)
print(edad)
print(altura)
print(es_estudiante)


# --- CAMBIAR EL VALOR DE UNA VARIABLE ---

# Las variables pueden cambiar su valor en cualquier momento.
# Por eso se llaman "variables" — su valor puede variar.

puntos = 0
print("Puntos iniciales:", puntos)

puntos = 10
print("Después de ganar puntos:", puntos)

puntos = puntos + 5     # Toma el valor actual (10) y le suma 5
print("Después de sumar 5 más:", puntos)


# --- REGLAS PARA NOMBRES DE VARIABLES ---

# ✅ VÁLIDO: letras, números (no al inicio), guión bajo _
mi_nombre = "Carlos"
nombre2 = "Pedro"
_privado = "esto funciona"

# ✅ Python distingue mayúsculas de minúsculas
# Estas son THREE variables DISTINTAS:
color = "rojo"
Color = "verde"
COLOR = "azul"
print(color, Color, COLOR)   # rojo verde azul

# ❌ INVÁLIDO (esto causaría un error, está comentado a propósito):
# 2nombre = "error"      # no puede empezar con número
# mi-nombre = "error"    # el guión - no está permitido (solo el guión bajo _)
# class = "error"        # "class" es una palabra reservada de Python


# --- ASIGNAR MÚLTIPLES VARIABLES EN UNA LÍNEA ---

# Puedes asignar varias variables a la vez
x, y, z = 1, 2, 3
print(x, y, z)   # 1 2 3

# O asignar el mismo valor a varias variables
a = b = c = 0
print(a, b, c)   # 0 0 0


# =============================================================================
# EXPERIMENTA: Crea tus propias variables con tu nombre, edad y ciudad.
# Luego imprímelas con print().
# =============================================================================
