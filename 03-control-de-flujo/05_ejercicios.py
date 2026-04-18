# =============================================================================
# CAPÍTULO 03 - CONTROL DE FLUJO
# Archivo: 05_ejercicios.py
# Descripción: 10 ejercicios clásicos que dominan if/elif/else, for y while.
#              Cada ejercicio incluye explicación de la lógica utilizada.
# =============================================================================

import random  # Para el juego de adivinar el número y piedra-papel-tijera


# =============================================================================
# EJERCICIO 1: FizzBuzz clásico
# Por cada número del 1 al 100:
#   - Si es múltiplo de 3: "Fizz"
#   - Si es múltiplo de 5: "Buzz"
#   - Si es múltiplo de ambos: "FizzBuzz"
#   - Si no: el número mismo
# =============================================================================
def ejercicio_fizzbuzz():
    """
    Implementación clásica de FizzBuzz del 1 al 100.
    Es uno de los ejercicios más conocidos en programación.
    """
    print("\n--- EJERCICIO 1: FizzBuzz (1-100) ---")
    results = []
    for i in range(1, 101):
        if i % 15 == 0:          # múltiplo de 3 y 5 a la vez
            results.append("FizzBuzz")
        elif i % 3 == 0:
            results.append("Fizz")
        elif i % 5 == 0:
            results.append("Buzz")
        else:
            results.append(str(i))

    # Imprimir en columnas para mejor lectura
    for idx, val in enumerate(results):
        print(f"{val:>8}", end="")
        if (idx + 1) % 10 == 0:
            print()


# =============================================================================
# EJERCICIO 2: Tabla de multiplicar interactiva
# El usuario elige un número y el programa muestra su tabla completa.
# =============================================================================
def ejercicio_tabla_multiplicar():
    """
    Genera la tabla de multiplicar del número que elija el usuario.
    Muestra los primeros 10 múltiplos con formato alineado.
    """
    print("\n--- EJERCICIO 2: Tabla de Multiplicar ---")
    number = int(input("¿De qué número quieres la tabla? "))

    print(f"\nTabla del {number}:")
    print("-" * 25)
    for i in range(1, 11):
        result = number * i
        print(f"  {number} x {i:2d} = {result:4d}")


# =============================================================================
# EJERCICIO 3: Verificar si un número es primo
# Un número primo es mayor que 1 y solo divisible entre 1 y él mismo.
# =============================================================================
def is_prime(n):
    """
    Verifica si n es un número primo.
    Optimización: solo verificar hasta la raíz cuadrada de n,
    ya que si n tiene un divisor mayor que √n, también tiene uno menor.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    # Solo verificar divisores impares hasta √n
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def ejercicio_numero_primo():
    """
    Solicita un número al usuario y verifica si es primo.
    También muestra los primeros 20 números primos como referencia.
    """
    print("\n--- EJERCICIO 3: Número Primo ---")
    number = int(input("Ingresa un número entero positivo: "))

    if is_prime(number):
        print(f"\n{number} SÍ es un número primo.")
    else:
        print(f"\n{number} NO es un número primo.")
        # Encontrar los divisores
        divisors = [i for i in range(1, number + 1) if number % i == 0]
        print(f"Sus divisores son: {divisors}")

    # Bonus: listar los primeros 20 primos
    primes_20 = [n for n in range(2, 100) if is_prime(n)][:20]
    print(f"\nPrimeros 20 primos: {primes_20}")


# =============================================================================
# EJERCICIO 4: Pirámide de asteriscos
# Dibuja una pirámide con N filas usando for anidado.
# =============================================================================
def ejercicio_piramide():
    """
    Dibuja una pirámide de asteriscos con el número de filas
    que el usuario especifique. Usa bucles for anidados.
    La fila N tiene 2*N-1 asteriscos, centrados.
    """
    print("\n--- EJERCICIO 4: Pirámide de Asteriscos ---")
    rows = int(input("¿Cuántas filas? (recomendado: 5-10): "))

    print()
    for i in range(1, rows + 1):
        # Espacios para centrar: (rows - i) espacios a la izquierda
        spaces = " " * (rows - i)
        stars = "*" * (2 * i - 1)
        print(spaces + stars)

    # También mostrar pirámide invertida
    print("\nPirámide invertida:")
    for i in range(rows, 0, -1):
        spaces = " " * (rows - i)
        stars = "*" * (2 * i - 1)
        print(spaces + stars)


# =============================================================================
# EJERCICIO 5: Adivina el número
# El programa genera un número aleatorio y el usuario debe adivinarlo.
# El programa da pistas (mayor/menor) con while.
# =============================================================================
def ejercicio_adivina_numero():
    """
    Juego de adivinar un número entre 1 y 100.
    Usa while para mantener el juego activo hasta acertar.
    El programa da pistas de mayor/menor en cada intento.
    """
    print("\n--- EJERCICIO 5: Adivina el Número ---")
    secret = random.randint(1, 100)
    attempts = 0
    max_attempts = 7  # log2(100) ≈ 7 intentos son suficientes con búsqueda binaria

    print(f"Piensa en un número entre 1 y 100.")
    print(f"Tienes {max_attempts} intentos.\n")

    while attempts < max_attempts:
        guess = int(input(f"Intento {attempts + 1}/{max_attempts}: "))
        attempts += 1

        if guess == secret:
            print(f"¡Correcto! Adivinaste en {attempts} intento(s). 🎉")
            break
        elif guess < secret:
            print("  → El número secreto es MAYOR.")
        else:
            print("  → El número secreto es MENOR.")
    else:
        print(f"\nAgotaste los intentos. El número era: {secret}")


# =============================================================================
# EJERCICIO 6: Calculadora con menú usando while
# El usuario puede realizar múltiples operaciones sin reiniciar el programa.
# =============================================================================
def ejercicio_calculadora_menu():
    """
    Mini calculadora interactiva con menú de opciones.
    Usa while True para mantener el menú activo hasta que
    el usuario elija salir.
    """
    print("\n--- EJERCICIO 6: Calculadora con Menú ---")

    while True:
        print("\nOperaciones disponibles:")
        print("  [1] Suma")
        print("  [2] Resta")
        print("  [3] Multiplicación")
        print("  [4] División")
        print("  [0] Salir")

        option = input("Elige una operación: ").strip()

        if option == "0":
            print("Saliendo de la calculadora.")
            break

        if option not in ("1", "2", "3", "4"):
            print("Opción inválida.")
            continue

        a = float(input("Primer número: "))
        b = float(input("Segundo número: "))

        if option == "1":
            print(f"Resultado: {a} + {b} = {a + b}")
        elif option == "2":
            print(f"Resultado: {a} - {b} = {a - b}")
        elif option == "3":
            print(f"Resultado: {a} × {b} = {a * b}")
        elif option == "4":
            if b == 0:
                print("Error: no se puede dividir entre 0.")
            else:
                print(f"Resultado: {a} / {b} = {a / b:.4f}")


# =============================================================================
# EJERCICIO 7: Suma de dígitos de un número
# Extrae cada dígito de un número y los suma.
# =============================================================================
def sum_of_digits(n):
    """
    Calcula la suma de los dígitos de un número entero.
    Usa el operador módulo y división entera para extraer cada dígito.
    Ejemplo: 1234 → 1+2+3+4 = 10
    """
    n = abs(n)  # Ignorar el signo negativo
    total = 0
    while n > 0:
        total += n % 10   # El último dígito
        n //= 10          # Eliminar el último dígito
    return total


def ejercicio_suma_digitos():
    """
    Solicita un número y muestra la suma de sus dígitos paso a paso.
    """
    print("\n--- EJERCICIO 7: Suma de Dígitos ---")
    number = int(input("Ingresa un número entero: "))

    digits = [int(d) for d in str(abs(number))]
    result = sum_of_digits(number)

    print(f"\nDígitos de {number}: {digits}")
    print(f"Suma: {' + '.join(map(str, digits))} = {result}")


# =============================================================================
# EJERCICIO 8: Invertir un número entero
# Invierte el orden de los dígitos de un número.
# =============================================================================
def reverse_number(n):
    """
    Invierte los dígitos de un número entero.
    Maneja números negativos preservando el signo.
    Ejemplo: 12345 → 54321, -987 → -789
    """
    sign = -1 if n < 0 else 1
    n = abs(n)
    reversed_n = 0
    while n > 0:
        reversed_n = reversed_n * 10 + (n % 10)
        n //= 10
    return sign * reversed_n


def ejercicio_invertir_numero():
    """
    Invierte los dígitos de un número ingresado por el usuario.
    Muestra el proceso paso a paso.
    """
    print("\n--- EJERCICIO 8: Invertir Número ---")
    number = int(input("Ingresa un número entero: "))
    result = reverse_number(number)

    print(f"\n{number} → invertido → {result}")

    # Curiosidad: verificar si es palíndromo numérico
    if number == result:
        print(f"¡{number} es un palíndromo numérico!")


# =============================================================================
# EJERCICIO 9: Serie de Fibonacci hasta N
# Genera los números de Fibonacci hasta un límite dado por el usuario.
# =============================================================================
def fibonacci_up_to(limit):
    """
    Genera la serie de Fibonacci desde 0 hasta el valor límite.
    Cada número es la suma de los dos anteriores: 0, 1, 1, 2, 3, 5, 8...
    Retorna una lista con todos los valores <= limit.
    """
    series = []
    a, b = 0, 1
    while a <= limit:
        series.append(a)
        a, b = b, a + b
    return series


def ejercicio_fibonacci():
    """
    Solicita un límite y muestra la serie de Fibonacci hasta ese valor.
    """
    print("\n--- EJERCICIO 9: Serie de Fibonacci ---")
    limit = int(input("Mostrar Fibonacci hasta el número: "))

    series = fibonacci_up_to(limit)
    print(f"\nFibonacci hasta {limit}:")
    print("  " + ", ".join(map(str, series)))
    print(f"\nTotal de términos: {len(series)}")
    print(f"Último término: {series[-1]}")


# =============================================================================
# EJERCICIO 10: Piedra, Papel, Tijeras con reintentos
# El jugador compite contra la computadora. while permite reintentar.
# =============================================================================
def ejercicio_piedra_papel_tijeras():
    """
    Juego de piedra, papel y tijeras contra la computadora.
    Usa while para preguntar si el usuario quiere jugar otra vez.
    Registra el puntaje acumulado de la sesión.
    """
    print("\n--- EJERCICIO 10: Piedra, Papel, Tijeras ---")

    options = ["piedra", "papel", "tijeras"]
    # Qué gana a qué: la clave gana al valor
    wins_against = {
        "piedra": "tijeras",
        "papel": "piedra",
        "tijeras": "papel"
    }

    player_score = 0
    cpu_score = 0
    ties = 0

    while True:
        print(f"\nMarcador → Tú: {player_score} | CPU: {cpu_score} | Empates: {ties}")
        player_choice = input("Elige (piedra/papel/tijeras) o 'salir': ").strip().lower()

        if player_choice == "salir":
            break

        if player_choice not in options:
            print("Opción no válida. Elige: piedra, papel o tijeras.")
            continue

        cpu_choice = random.choice(options)
        print(f"La CPU eligió: {cpu_choice}")

        if player_choice == cpu_choice:
            print("¡Empate!")
            ties += 1
        elif wins_against[player_choice] == cpu_choice:
            print(f"¡Ganaste! {player_choice} vence a {cpu_choice}.")
            player_score += 1
        else:
            print(f"Perdiste. {cpu_choice} vence a {player_choice}.")
            cpu_score += 1

    print(f"\nResultado final → Tú: {player_score} | CPU: {cpu_score} | Empates: {ties}")


# =============================================================================
# MENÚ PRINCIPAL
# =============================================================================
def main():
    """Menú para elegir y ejecutar cada ejercicio del capítulo."""
    exercises = {
        "1": ("FizzBuzz clásico (1-100)", ejercicio_fizzbuzz),
        "2": ("Tabla de multiplicar", ejercicio_tabla_multiplicar),
        "3": ("Verificar número primo", ejercicio_numero_primo),
        "4": ("Pirámide de asteriscos", ejercicio_piramide),
        "5": ("Adivina el número", ejercicio_adivina_numero),
        "6": ("Calculadora con menú", ejercicio_calculadora_menu),
        "7": ("Suma de dígitos", ejercicio_suma_digitos),
        "8": ("Invertir número entero", ejercicio_invertir_numero),
        "9": ("Serie de Fibonacci hasta N", ejercicio_fibonacci),
        "10": ("Piedra, Papel, Tijeras", ejercicio_piedra_papel_tijeras),
        "0": ("Salir", None),
    }

    print("=" * 52)
    print("   EJERCICIOS - CAPÍTULO 03: CONTROL DE FLUJO")
    print("=" * 52)

    while True:
        print("\nElige un ejercicio:")
        for key, (name, _) in exercises.items():
            print(f"  [{key:>2}] {name}")

        choice = input("\nOpción: ").strip()

        if choice == "0":
            print("¡Hasta luego!")
            break
        elif choice in exercises:
            _, func = exercises[choice]
            func()
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
