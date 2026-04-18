# =============================================================================
# ARCHIVO: 01_listas.py
# TEMA: Listas — colecciones ordenadas y modificables
# =============================================================================
#
# Una lista es una colección ordenada de elementos.
# Puede contener cualquier tipo de dato, incluso mezclados.
# Se define con corchetes [].
# Es la estructura de datos más usada en Python.
# =============================================================================


# --- CREAR LISTAS ---

frutas = ["manzana", "banana", "naranja"]
numeros = [1, 2, 3, 4, 5]
mixta = [42, "hola", True, 3.14, None]   # tipos mezclados
vacia = []                                # lista vacía

print(frutas)
print(len(frutas))    # len() devuelve la cantidad de elementos → 3


# --- ACCEDER A ELEMENTOS (ÍNDICE) ---
# Los índices empiezan en 0, no en 1.
# Índices negativos cuentan desde el final.

#        manzana  banana  naranja
#   índice: 0       1       2
#  negativo: -3     -2      -1

print(frutas[0])     # manzana  (primer elemento)
print(frutas[1])     # banana
print(frutas[-1])    # naranja  (último elemento)
print(frutas[-2])    # banana


# --- SLICING (rebanado) — obtener una parte de la lista ---
# lista[inicio:fin]  → desde inicio hasta fin-1

numeros = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(numeros[2:5])    # [2, 3, 4]   (del índice 2 al 4)
print(numeros[:4])     # [0, 1, 2, 3] (desde el inicio hasta el índice 3)
print(numeros[6:])     # [6, 7, 8, 9] (desde el índice 6 hasta el final)
print(numeros[::2])    # [0, 2, 4, 6, 8] (de 2 en 2)
print(numeros[::-1])   # [9, 8, 7, ... 0] (invertida)


# --- MODIFICAR ELEMENTOS ---

frutas[1] = "mango"        # reemplazar banana por mango
print(frutas)              # ['manzana', 'mango', 'naranja']


# --- MÉTODOS PRINCIPALES ---

# Agregar al final
frutas.append("uva")
print(frutas)   # ['manzana', 'mango', 'naranja', 'uva']

# Insertar en posición específica
frutas.insert(1, "kiwi")   # insertar 'kiwi' en el índice 1
print(frutas)

# Eliminar por valor
frutas.remove("mango")     # elimina la primera ocurrencia de "mango"
print(frutas)

# Eliminar por índice (y obtener el valor eliminado)
eliminado = frutas.pop(0)  # elimina el elemento en índice 0 y lo devuelve
print(f"Eliminé: {eliminado}")
print(frutas)

# Ordenar
numeros = [5, 2, 8, 1, 9, 3]
numeros.sort()              # ordena en el lugar (modifica la lista original)
print(numeros)              # [1, 2, 3, 5, 8, 9]

numeros.sort(reverse=True)  # orden descendente
print(numeros)              # [9, 8, 5, 3, 2, 1]

# sorted() devuelve una nueva lista sin modificar la original
original = [5, 2, 8, 1]
nueva = sorted(original)
print(original)   # [5, 2, 8, 1]  — sin cambios
print(nueva)      # [1, 2, 5, 8]

# Invertir la lista
frutas.reverse()
print(frutas)

# Buscar índice de un elemento
letras = ["a", "b", "c", "d"]
print(letras.index("c"))    # 2

# Contar cuántas veces aparece un elemento
votos = ["si", "no", "si", "si", "no", "si"]
print(votos.count("si"))    # 4


# --- RECORRER UNA LISTA ---

nombres = ["Ana", "Carlos", "María"]

for nombre in nombres:
    print(f"Hola, {nombre}")

# Con índice usando enumerate()
for i, nombre in enumerate(nombres):
    print(f"{i + 1}. {nombre}")


# --- VERIFICAR SI UN ELEMENTO EXISTE ---

print("banana" in frutas)    # True o False
print("mango" not in frutas) # True o False


# --- LISTAS ANIDADAS (lista de listas) ---

matriz = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

print(matriz[1][2])    # 6  → fila 1, columna 2


# --- OPERACIONES ÚTILES ---

a = [1, 2, 3]
b = [4, 5, 6]

# Concatenar
c = a + b
print(c)      # [1, 2, 3, 4, 5, 6]

# Repetir
d = a * 3
print(d)      # [1, 2, 3, 1, 2, 3, 1, 2, 3]

# Funciones nativas
nums = [3, 1, 7, 2, 9]
print(sum(nums))    # 22
print(min(nums))    # 1
print(max(nums))    # 9
