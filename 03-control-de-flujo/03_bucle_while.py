# =============================================================================
# ARCHIVO: 03_bucle_while.py
# TEMA: Bucle while — repetir mientras una condición sea verdadera
# =============================================================================
#
# El bucle WHILE repite un bloque de código MIENTRAS una condición sea True.
# Se usa cuando NO sabes cuántas veces se va a repetir algo.
#
# Estructura:
#   while condición:
#       código a repetir
#
# ⚠️ CUIDADO: si la condición nunca se vuelve False, el bucle es infinito
# y el programa se cuelga. Siempre asegúrate de que la condición eventualmente
# sea False.
# =============================================================================


# --- WHILE BÁSICO ---

contador = 0

while contador < 5:
    print(f"Contador: {contador}")
    contador += 1    # ← MUY IMPORTANTE: sin esto el bucle nunca termina

print("El bucle terminó")


# --- EQUIVALENCIA CON FOR ---
# Este while y este for hacen lo mismo:

# Con for:
for i in range(5):
    print(i)

# Con while:
i = 0
while i < 5:
    print(i)
    i += 1

# Regla práctica:
# - Usa FOR cuando sabes cuántas veces repetir
# - Usa WHILE cuando dependes de una condición que puede cambiar en cualquier momento


# --- WHILE CON INPUT DEL USUARIO ---
# Ideal para validar entradas: repetir hasta que el usuario ingrese algo válido.

print("\n--- Adivina el número ---")
numero_secreto = 42
intento = 0

while intento != numero_secreto:
    intento = int(input("Adivina el número (entre 1 y 100): "))

    if intento < numero_secreto:
        print("Demasiado bajo")
    elif intento > numero_secreto:
        print("Demasiado alto")

print(f"¡Correcto! El número era {numero_secreto}")


# --- WHILE True (bucle infinito intencional) ---
# A veces es más claro escribir while True y salir con break.

print("\n--- Menú de opciones ---")
while True:
    print("\n1. Ver saldo")
    print("2. Depositar")
    print("3. Salir")
    opcion = input("Elige una opción: ")

    if opcion == "1":
        print("Tu saldo es $500")
    elif opcion == "2":
        print("Depósito realizado")
    elif opcion == "3":
        print("¡Hasta luego!")
        break    # break sale del bucle while True
    else:
        print("Opción no válida, intenta de nuevo")


# --- CONTAR INTENTOS ---

print("\n--- Control de intentos ---")
intentos_maximos = 3
intentos = 0
contrasena_correcta = "python123"

while intentos < intentos_maximos:
    intento = input(f"Contraseña (intento {intentos + 1}/{intentos_maximos}): ")

    if intento == contrasena_correcta:
        print("Acceso concedido")
        break
    else:
        intentos += 1
        print("Contraseña incorrecta")

# Si se agotaron los intentos sin un break exitoso
if intentos == intentos_maximos:
    print("Cuenta bloqueada por seguridad")
