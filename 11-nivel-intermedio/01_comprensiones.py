# =============================================================================
# ARCHIVO: 01_comprensiones.py
# TEMA: Comprensiones — crear colecciones de forma concisa y pythónica
# =============================================================================
#
# Una comprensión es una sintaxis especial de Python para crear listas,
# diccionarios o conjuntos en una sola línea expresiva.
#
# Son más cortas y, en general, más rápidas que los bucles equivalentes.
# Se consideran "pythónicas" — es la forma idiomática de Python.
# =============================================================================


# ============================================================
# COMPRENSIÓN DE LISTA (List Comprehension)
# ============================================================

# Forma larga:
cuadrados_largo = []
for i in range(1, 11):
    cuadrados_largo.append(i ** 2)

# Comprensión equivalente:
cuadrados = [i ** 2 for i in range(1, 11)]
print(cuadrados)   # [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

# Forma de leerla: "dame [i al cuadrado] para cada [i] en [range(1,11)]"


# --- CON CONDICIÓN (filtro) ---

# Solo los números pares del 1 al 20
pares = [n for n in range(1, 21) if n % 2 == 0]
print(pares)   # [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

# Solo palabras con más de 4 letras
palabras = ["sol", "luna", "estrella", "mar", "montaña", "río"]
largas = [p for p in palabras if len(p) > 4]
print(largas)  # ['estrella', 'montaña']


# --- TRANSFORMACIÓN ---

# Convertir a mayúsculas
nombres = ["ana", "carlos", "maría"]
en_mayus = [n.upper() for n in nombres]
print(en_mayus)

# Limpiar y transformar en un paso
datos_sucios = ["  Ana  ", " Carlos", "María "]
limpios = [d.strip().title() for d in datos_sucios]
print(limpios)   # ['Ana', 'Carlos', 'María']


# --- COMPRENSIÓN ANIDADA ---

# Combinaciones de color y talla
colores = ["rojo", "azul"]
tallas = ["S", "M", "L"]
combinaciones = [f"{c}-{t}" for c in colores for t in tallas]
print(combinaciones)
# ['rojo-S', 'rojo-M', 'rojo-L', 'azul-S', 'azul-M', 'azul-L']

# Aplanar una lista de listas
matriz = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
plana = [elemento for fila in matriz for elemento in fila]
print(plana)   # [1, 2, 3, 4, 5, 6, 7, 8, 9]


# ============================================================
# COMPRENSIÓN DE DICCIONARIO (Dict Comprehension)
# ============================================================

# Cuadrado de cada número como diccionario {número: cuadrado}
cuadrados_dict = {n: n**2 for n in range(1, 6)}
print(cuadrados_dict)   # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Invertir un diccionario (claves ↔ valores)
original = {"a": 1, "b": 2, "c": 3}
invertido = {v: k for k, v in original.items()}
print(invertido)   # {1: 'a', 2: 'b', 3: 'c'}

# Crear diccionario a partir de dos listas
nombres = ["Ana", "Carlos", "María"]
edades  = [28, 35, 22]
personas = {n: e for n, e in zip(nombres, edades)}
print(personas)   # {'Ana': 28, 'Carlos': 35, 'María': 22}

# Filtrar diccionario (solo activos)
usuarios = {"ana": True, "carlos": False, "maría": True, "pedro": False}
activos = {u: a for u, a in usuarios.items() if a}
print(activos)   # {'ana': True, 'maría': True}


# ============================================================
# COMPRENSIÓN DE CONJUNTO (Set Comprehension)
# ============================================================

# Letras únicas de una palabra
letras = {c for c in "mississippi"}
print(letras)   # {'m', 'i', 's', 'p'}  (sin duplicados, orden arbitrario)

# Cuadrados únicos (algunos se repiten si el input tiene negativos)
nums = [-3, -2, -1, 0, 1, 2, 3]
cuadrados_unicos = {n**2 for n in nums}
print(cuadrados_unicos)   # {0, 1, 4, 9}


# ============================================================
# CUÁNDO USAR Y CUÁNDO NO
# ============================================================

# ✅ Usar comprensión cuando:
# - La transformación es simple y cabe en una línea legible
# - Estás creando una nueva colección a partir de otra

# ❌ Evitar comprensión cuando:
# - La lógica es compleja (múltiples condiciones, más de 2 niveles)
# - La línea se vuelve difícil de leer
# - Necesitas usar el resultado parcial del bucle en cada iteración

# ❌ Comprensión demasiado compleja (usa un for loop en su lugar):
# resultado = [func(x) for x in lista if condicion1(x) and condicion2(x) and condicion3(x)]

# ✅ En ese caso, mejor así:
resultado = []
for x in range(20):
    if x % 2 == 0 and x % 3 == 0 and x > 0:
        resultado.append(x)
print(resultado)   # [6, 12, 18]
