# =============================================================================
# ARCHIVO: 02_generadores.py
# TEMA: Generadores — producir valores uno a la vez de forma eficiente
# =============================================================================
#
# Un generador es una función especial que produce valores de uno en uno,
# en lugar de crear toda la colección en memoria al mismo tiempo.
#
# Se usa 'yield' en lugar de 'return'.
# Cada vez que se llama, la función se "pausa" en el yield y entrega un valor.
# En la siguiente llamada, continúa desde donde se quedó.
#
# VENTAJA: memoria. Si necesitas 1 millón de números, un generador no crea
# una lista de 1 millón — produce uno a la vez.
# =============================================================================


# --- FUNCIÓN NORMAL vs. GENERADOR ---

# Función normal — crea y devuelve toda la lista en memoria
def cuadrados_lista(n):
    """Devuelve una lista con los cuadrados del 0 al n-1."""
    resultado = []
    for i in range(n):
        resultado.append(i ** 2)
    return resultado

# Generador — produce los cuadrados uno a la vez
def cuadrados_generador(n):
    """Genera los cuadrados del 0 al n-1 de uno en uno."""
    for i in range(n):
        yield i ** 2   # pausa aquí, entrega el valor, y en la siguiente llamada continúa

# Con lista: crea [0, 1, 4, 9, 16] todo en memoria
lista = cuadrados_lista(5)
print(lista)       # [0, 1, 4, 9, 16]
print(type(lista)) # <class 'list'>

# Con generador: no crea nada aún, es un objeto generador
gen = cuadrados_generador(5)
print(gen)         # <generator object cuadrados_generador at 0x...>
print(type(gen))   # <class 'generator'>

# Para obtener valores del generador:
print(next(gen))   # 0  (primer valor)
print(next(gen))   # 1
print(next(gen))   # 4

# O recorrerlo con for (lo más común)
for cuadrado in cuadrados_generador(5):
    print(cuadrado, end=" ")   # 0 1 4 9 16
print()


# --- GENERATOR EXPRESSION (como list comprehension pero con paréntesis) ---

# List comprehension — crea la lista completa
lista_completa = [x**2 for x in range(1000000)]   # usa mucha memoria

# Generator expression — no crea nada hasta que se pide
gen_expr = (x**2 for x in range(1000000))   # casi sin memoria

# Perfecto cuando solo necesitas iterar una vez o calcular una suma
suma = sum(x**2 for x in range(1001))   # suma de cuadrados del 0 al 1000
print(f"\nSuma de cuadrados: {suma}")


# --- GENERADOR CON MÚLTIPLES YIELDS ---

def dias_laborales():
    """Genera los días laborales de la semana."""
    yield "Lunes"
    yield "Martes"
    yield "Miércoles"
    yield "Jueves"
    yield "Viernes"

for dia in dias_laborales():
    print(dia)


# --- GENERADOR INFINITO ---
# Un generador puede ser potencialmente infinito — produce valores para siempre.
# Solo necesitas controlarlo con break o tomar solo los que necesites.

def contador_infinito(inicio=0):
    """Genera números enteros de forma infinita desde 'inicio'."""
    n = inicio
    while True:
        yield n
        n += 1

# Tomar los primeros 5 valores de un generador infinito
gen = contador_infinito(10)
for _ in range(5):
    print(next(gen), end=" ")   # 10 11 12 13 14
print()


# --- EJEMPLO PRÁCTICO: procesar archivo grande línea a línea ---

import os

def leer_lineas(archivo):
    """Genera las líneas de un archivo de una en una (eficiente en memoria)."""
    if not os.path.exists(archivo):
        return
    with open(archivo, "r", encoding="utf-8") as f:
        for linea in f:
            yield linea.strip()

# Crear un archivo de prueba
archivo_prueba = os.path.join(os.path.dirname(__file__), "prueba_gen.txt")
with open(archivo_prueba, "w", encoding="utf-8") as f:
    for i in range(1, 6):
        f.write(f"Línea número {i}\n")

# Leer línea por línea con el generador
print("\nLeyendo archivo con generador:")
for linea in leer_lineas(archivo_prueba):
    print(f"  > {linea}")

os.remove(archivo_prueba)


# --- RESUMEN ---
# Usa generadores cuando:
# - Procesas grandes cantidades de datos (archivos, streams, big data)
# - Solo necesitas iterar una vez sobre los datos
# - Quieres representar secuencias potencialmente infinitas
# - Quieres producir valores de forma perezosa (lazy evaluation)
