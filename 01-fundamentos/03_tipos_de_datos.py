# =============================================================================
# ARCHIVO: 03_tipos_de_datos.py
# TEMA: Tipos de datos — las categorías de valores en Python
# =============================================================================
#
# En Python, cada valor tiene un TIPO. El tipo determina:
#   - Qué clase de información representa
#   - Qué operaciones puedes hacer con él
#
# Los tipos básicos son:
#   int     → número entero:        1, -5, 100, 0
#   float   → número decimal:       3.14, -0.5, 2.0
#   str     → texto (string):       "hola", 'mundo', "123"
#   bool    → verdadero/falso:      True, False
#   NoneType→ ausencia de valor:    None
# =============================================================================


# --- int (entero) ---
# Números sin parte decimal. Pueden ser positivos o negativos.

cantidad = 10
temperatura_bajo_cero = -3
año = 2024

print(type(cantidad))          # <class 'int'>
# type() es una función que te dice el tipo de cualquier valor


# --- float (decimal) ---
# Números con punto decimal. En Python se usa punto (.) no coma (,).

precio = 19.99
pi = 3.14159
porcentaje = 0.75

print(type(precio))            # <class 'float'>

# Nota: aunque 2.0 parece entero, el punto lo hace float
es_float = 2.0
print(type(es_float))          # <class 'float'>


# --- str (string / texto) ---
# Texto entre comillas simples '' o dobles "".
# Ambas formas son equivalentes en Python.

saludo = "Hola"
apellido = 'García'
frase = "Python es genial"
numero_como_texto = "42"       # OJO: esto es texto, NO un número

print(type(saludo))            # <class 'str'>

# La diferencia importa:
# "42" + "8" da "428" (unión de texto)
# 42 + 8 da 50 (suma matemática)
print("42" + "8")              # 428
print(42 + 8)                  # 50


# --- bool (booleano) ---
# Solo puede ser True (verdadero) o False (falso).
# Se usan mucho para tomar decisiones (lo verás en el capítulo 03).
# IMPORTANTE: la primera letra es MAYÚSCULA: True, False (no true ni false)

tiene_cuenta = True
esta_conectado = False
mayor_de_edad = True

print(type(tiene_cuenta))      # <class 'bool'>


# --- None ---
# Representa "nada", la ausencia de un valor.
# Se usa cuando una variable no tiene valor todavía.

resultado = None
print(resultado)               # None
print(type(resultado))         # <class 'NoneType'>


# --- CONVERSIÓN ENTRE TIPOS ---
# Python permite convertir un tipo en otro.

# Texto a número entero
texto_numero = "25"
numero = int(texto_numero)
print(numero + 5)              # 30

# Número a texto
edad = 30
texto = str(edad)
print("Tengo " + texto + " años")

# Entero a decimal
entero = 5
decimal = float(entero)
print(decimal)                 # 5.0

# Texto a booleano (casi cualquier texto no vacío es True)
print(bool("hola"))            # True
print(bool(""))                # False — string vacío es False

# Número a booleano (0 es False, cualquier otro número es True)
print(bool(0))                 # False
print(bool(1))                 # True
print(bool(-99))               # True


# =============================================================================
# PRUEBA: ¿Qué pasa si intentas hacer int("hola")? Quita el # de abajo y corre.
# int("hola")
# Verás un error. Eso está bien — así aprendes a leer errores también.
# =============================================================================
