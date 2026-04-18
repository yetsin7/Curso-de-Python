# =============================================================================
# ARCHIVO: 02_bucle_for.py
# TEMA: Bucle for — repetir una cantidad definida de veces
# =============================================================================
#
# El bucle FOR repite un bloque de código para cada elemento de una secuencia.
# Se usa cuando sabes de antemano cuántas veces vas a repetir algo.
#
# Estructura:
#   for variable in secuencia:
#       código a repetir
#
# La variable toma el valor de cada elemento en cada iteración.
# =============================================================================


# --- FOR CON range() ---
# range(n) genera los números del 0 al n-1.

print("--- Contar del 0 al 4 ---")
for i in range(5):
    print(i)        # imprime 0, 1, 2, 3, 4


# range(inicio, fin) — del inicio al fin-1
print("\n--- Del 1 al 5 ---")
for i in range(1, 6):
    print(i)        # imprime 1, 2, 3, 4, 5


# range(inicio, fin, paso) — de inicio a fin-1 de paso en paso
print("\n--- Números pares del 0 al 10 ---")
for i in range(0, 11, 2):
    print(i)        # 0, 2, 4, 6, 8, 10

# Contar hacia atrás
print("\n--- Cuenta regresiva ---")
for i in range(5, 0, -1):
    print(i)        # 5, 4, 3, 2, 1
print("¡Despegue!")


# --- FOR SOBRE UNA LISTA ---
# El for recorre cualquier colección, no solo números.

frutas = ["manzana", "banana", "naranja", "uva"]

print("\n--- Mis frutas ---")
for fruta in frutas:
    print(f"- {fruta}")


# --- FOR SOBRE UN STRING ---
# Un string es una secuencia de caracteres — el for puede recorrerlo letra a letra.

palabra = "Python"
print("\n--- Letras de Python ---")
for letra in palabra:
    print(letra)


# --- ACUMULADOR CON FOR ---
# Patrón muy común: usar una variable que acumula resultados.

numeros = [3, 7, 2, 9, 1, 5]

suma = 0
for numero in numeros:
    suma += numero    # suma = suma + numero

print(f"\nSuma de {numeros} = {suma}")


# --- ENCONTRAR EL MÁXIMO (manual, sin usar max()) ---
numeros = [15, 3, 42, 8, 27]
maximo = numeros[0]     # asume que el primero es el máximo

for numero in numeros:
    if numero > maximo:
        maximo = numero   # actualiza si encuentra uno mayor

print(f"El número mayor es: {maximo}")   # 42


# --- enumerate() — obtener índice y valor al mismo tiempo ---
colores = ["rojo", "verde", "azul"]

print("\n--- Colores con índice ---")
for indice, color in enumerate(colores):
    print(f"{indice}: {color}")


# --- FOR ANIDADO (for dentro de for) ---
# Útil para tablas de multiplicar, matrices, combinaciones, etc.

print("\n--- Tabla del 3 ---")
for i in range(1, 11):
    resultado = 3 * i
    print(f"3 x {i} = {resultado}")


# =============================================================================
# EJERCICIO: Usa un for para imprimir los números del 1 al 100
# que sean divisibles por 7.
# Pista: usa el operador % (módulo) y un if dentro del for.
# =============================================================================
