# =============================================================================
# ARCHIVO: 04_lambda.py
# TEMA: Funciones lambda — funciones anónimas de una línea
# =============================================================================
#
# Una función lambda es una función pequeña sin nombre.
# Se usa para funciones simples de una sola expresión.
#
# Sintaxis:
#   lambda parámetros: expresión
#
# Es equivalente a:
#   def nombre(parámetros):
#       return expresión
#
# Las lambdas son útiles como argumentos de otras funciones (sorted, filter, map).
# Para lógica compleja, siempre usa def en su lugar.
# =============================================================================


# --- LAMBDA BÁSICA ---

# Función normal:
def cuadrado(x):
    return x ** 2

# Equivalente con lambda:
cuadrado_lambda = lambda x: x ** 2

print(cuadrado(5))         # 25
print(cuadrado_lambda(5))  # 25


# Lambda con múltiples parámetros:
sumar = lambda a, b: a + b
print(sumar(3, 4))    # 7

area = lambda base, altura: (base * altura) / 2
print(area(6, 4))     # 12.0


# --- USO REAL: sorted() con key ---
# El principal uso de lambda es como "clave" en sorted(), min(), max().

personas = [
    {"nombre": "Carlos", "edad": 30},
    {"nombre": "Ana",    "edad": 25},
    {"nombre": "María",  "edad": 35},
    {"nombre": "Pedro",  "edad": 28},
]

# Ordenar por edad
por_edad = sorted(personas, key=lambda p: p["edad"])
for p in por_edad:
    print(f"{p['nombre']}: {p['edad']} años")

print()

# Ordenar por nombre
por_nombre = sorted(personas, key=lambda p: p["nombre"])
for p in por_nombre:
    print(p["nombre"])


# --- filter() — filtrar elementos ---
# filter(función, iterable) → devuelve solo los elementos donde función(elemento) es True

numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Filtrar solo los números pares
pares = list(filter(lambda n: n % 2 == 0, numeros))
print(pares)    # [2, 4, 6, 8, 10]

# Filtrar los mayores de 5
mayores = list(filter(lambda n: n > 5, numeros))
print(mayores)  # [6, 7, 8, 9, 10]


# --- map() — transformar elementos ---
# map(función, iterable) → aplica la función a cada elemento

precios = [100, 200, 350, 80, 150]

# Aplicar 10% de descuento a todos
con_descuento = list(map(lambda p: p * 0.90, precios))
print(con_descuento)    # [90.0, 180.0, 315.0, 72.0, 135.0]

# Convertir a mayúsculas
nombres = ["ana", "carlos", "maría"]
en_mayusculas = list(map(lambda n: n.upper(), nombres))
print(en_mayusculas)    # ['ANA', 'CARLOS', 'MARÍA']


# --- CUÁNDO USAR LAMBDA VS DEF ---

# ✅ Usa lambda cuando:
# - La función tiene una sola expresión simple
# - La usas como argumento de otra función (sorted, filter, map)
# - No la necesitas en otro lugar

# ✅ Usa def cuando:
# - La función tiene más de una línea
# - Necesitas documentarla con docstring
# - La usarás en múltiples lugares
# - La lógica es compleja o tiene condiciones

# ❌ Esto sería mal uso de lambda (demasiado complejo):
# calcular = lambda x: x**2 if x > 0 else -x**2 if x < 0 else 0

# ✅ Mejor así:
def calcular(x):
    """Calcula el cuadrado con signo según el valor de x."""
    if x > 0:
        return x ** 2
    elif x < 0:
        return -(x ** 2)
    else:
        return 0
