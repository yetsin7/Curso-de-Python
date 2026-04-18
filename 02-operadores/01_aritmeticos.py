# =============================================================================
# ARCHIVO: 01_aritmeticos.py
# TEMA: Operadores aritmeticos en Python
# EJECUCION: python 01_aritmeticos.py
# =============================================================================
#
# Este archivo muestra como Python realiza calculos.
# Cada operador toma valores de entrada, produce un resultado y ese resultado
# puede imprimirse, guardarse en memoria o usarse para seguir calculando.
# =============================================================================

a = 10
b = 3

# Suma: combina ambos valores.
print(a + b)        # 13

# Resta: calcula la diferencia.
print(a - b)        # 7

# Multiplicacion: repite sumas de forma abreviada.
print(a * b)        # 30

# Division: en Python produce float aunque la division sea exacta.
print(a / b)        # 3.3333...

# Division entera: corta la parte decimal.
print(a // b)       # 3   → cuántas veces cabe 3 en 10

# Modulo: devuelve el sobrante de la division.
print(a % b)        # 1   → 10 / 3 = 3 y sobra 1

# Potencia: eleva un numero a otro.
print(a ** b)       # 1000  → 10³ = 1000


# --- ¿Para qué sirve el módulo (%)? ---
# Es util para saber si un numero es par o impar.

numero = 8
if numero % 2 == 0:
    print(f"{numero} es par")
else:
    print(f"{numero} es impar")

# Tambien sirve para revisar divisibilidad.
print(15 % 5)   # 0  → 15 es divisible por 5 (no sobra nada)
print(17 % 5)   # 2  → 17 no es divisible por 5 (sobran 2)


# --- ORDEN DE OPERACIONES ---
# Python sigue reglas de precedencia.
# Si una expresion se vuelve confusa, los parentesis ayudan mucho.

resultado1 = 2 + 3 * 4       # 14 (primero multiplica, luego suma)
resultado2 = (2 + 3) * 4     # 20 (los paréntesis van primero)

print(resultado1)   # 14
print(resultado2)   # 20


# --- OPERACIONES CON FLOATS ---
# Los float representan decimales, utiles para medidas, precios y promedios.
precio = 150.0
descuento = 0.10          # 10% de descuento

ahorro = precio * descuento
precio_final = precio - ahorro

print(f"Precio original: ${precio}")
print(f"Descuento (10%): ${ahorro}")
print(f"Precio final: ${precio_final}")


# --- NOTA SOBRE PRECISION DECIMAL ---
# Muchos decimales no se representan de forma exacta en binario.
print(0.1 + 0.2)     # 0.30000000000000004  ← error de precisión flotante
# Esto es normal en muchos lenguajes.
# Para calculos financieros exactos existe decimal.


# =============================================================================
# QUE DEBERIAS ENTENDER AL TERMINAR
# - Un operador toma valores y genera un resultado.
# - /, // y % resuelven problemas distintos.
# - Los parentesis mejoran claridad y control.
# - Los decimales en computacion no siempre son exactos.
#
# PRACTICA GUIADA
# 1. Cambia a y b por otros valores.
# 2. Prueba un numero par y uno impar.
# 3. Calcula un descuento diferente.
# 4. Explica la diferencia entre /, // y %.
# =============================================================================
