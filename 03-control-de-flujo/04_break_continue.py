# =============================================================================
# ARCHIVO: 04_break_continue.py
# TEMA: break y continue — controlar el flujo dentro de bucles
# =============================================================================
#
# break    → sale del bucle inmediatamente, sin ejecutar el resto
# continue → salta al siguiente ciclo del bucle, ignora lo que sigue
#
# Ambos funcionan con for y with while.
# =============================================================================


# --- BREAK: salir del bucle ---

print("--- break: buscar el primer número par ---")
numeros = [1, 3, 7, 4, 9, 2, 6]

for numero in numeros:
    if numero % 2 == 0:
        print(f"Encontré el primer par: {numero}")
        break    # salimos apenas encontramos lo que buscamos
    print(f"{numero} es impar, sigo buscando...")


# --- CONTINUE: saltarse una iteración ---

print("\n--- continue: imprimir solo impares ---")
for i in range(1, 11):
    if i % 2 == 0:
        continue    # si es par, salta al siguiente número sin imprimir
    print(i)        # solo llega aquí si no se ejecutó el continue


# --- BREAK EN WHILE ---

print("\n--- break en while: buscar en lista ---")
lista_compras = ["pan", "leche", "huevos", "mantequilla", "queso"]
buscar = "huevos"
posicion = 0

while posicion < len(lista_compras):
    if lista_compras[posicion] == buscar:
        print(f"'{buscar}' encontrado en la posición {posicion}")
        break
    posicion += 1
else:
    # El bloque else de un bucle se ejecuta SOLO si el bucle terminó sin break
    print(f"'{buscar}' no está en la lista")


# --- FOR/WHILE CON ELSE ---
# Este es un patrón especial de Python: el else en un bucle.
# Se ejecuta cuando el bucle termina normalmente (sin break).

print("\n--- Bucle con else ---")
for i in range(5):
    if i == 10:     # esto nunca es True para i en range(5)
        print("Encontré el 10")
        break
else:
    print("El bucle terminó sin encontrar el 10")    # esto sí se ejecuta


# --- EJEMPLO PRÁCTICO: validar entrada del usuario ---

print("\n--- Solo acepta números positivos ---")
while True:
    texto = input("Ingresa un número positivo: ")

    # Si no es un número, continúa pidiendo
    if not texto.isdigit():
        print("Eso no es un número válido")
        continue    # vuelve al inicio del while

    numero = int(texto)

    # Si es cero o negativo, continúa pidiendo
    if numero <= 0:
        print("Debe ser mayor que cero")
        continue

    # Si llegamos aquí, el número es válido
    print(f"Perfecto, ingresaste: {numero}")
    break   # salimos del bucle


# --- RESUMEN ---
# break    → úsalo para salir cuando ya encontraste lo que buscabas
# continue → úsalo para saltar casos que no quieres procesar
# else     → úsalo cuando necesitas saber si el bucle terminó sin break
