# =============================================================================
# CAPÍTULO 01 - FUNDAMENTOS
# Archivo: 06_ejercicios.py
# Descripción: 10 ejercicios resueltos que consolidan los fundamentos
#              de Python: variables, tipos, input/output y operaciones básicas.
# =============================================================================

import math  # Para operaciones matemáticas como pi y sqrt


# =============================================================================
# EJERCICIO 1: Calculadora de IMC
# Pide peso y altura al usuario, calcula el Índice de Masa Corporal
# y categoriza el resultado según la escala de la OMS.
# =============================================================================
def ejercicio_imc():
    """
    Calcula el Índice de Masa Corporal (IMC) del usuario.
    Fórmula: IMC = peso (kg) / altura (m)^2
    """
    print("\n--- EJERCICIO 1: Calculadora de IMC ---")
    weight = float(input("Ingresa tu peso en kilogramos (ej: 70.5): "))
    height = float(input("Ingresa tu altura en metros (ej: 1.75): "))

    imc = weight / (height ** 2)

    # Categorización según la OMS
    if imc < 18.5:
        category = "Bajo peso"
    elif imc < 25:
        category = "Peso normal"
    elif imc < 30:
        category = "Sobrepeso"
    else:
        category = "Obesidad"

    print(f"\nTu IMC es: {imc:.2f}")
    print(f"Categoría: {category}")


# =============================================================================
# EJERCICIO 2: Conversor de temperatura
# Convierte entre Celsius, Fahrenheit y Kelvin.
# =============================================================================
def celsius_to_fahrenheit(celsius):
    """Convierte grados Celsius a Fahrenheit."""
    return (celsius * 9 / 5) + 32


def celsius_to_kelvin(celsius):
    """Convierte grados Celsius a Kelvin."""
    return celsius + 273.15


def fahrenheit_to_celsius(fahrenheit):
    """Convierte grados Fahrenheit a Celsius."""
    return (fahrenheit - 32) * 5 / 9


def ejercicio_temperatura():
    """
    Conversor completo de temperaturas.
    El usuario ingresa un valor en Celsius y recibe la equivalencia
    en Fahrenheit y Kelvin.
    """
    print("\n--- EJERCICIO 2: Conversor de Temperatura ---")
    celsius = float(input("Ingresa la temperatura en Celsius: "))

    fahrenheit = celsius_to_fahrenheit(celsius)
    kelvin = celsius_to_kelvin(celsius)

    print(f"\n{celsius}°C equivale a:")
    print(f"  → {fahrenheit:.2f}°F")
    print(f"  → {kelvin:.2f} K")


# =============================================================================
# EJERCICIO 3: Detector de número par o impar
# El usuario ingresa un número y el programa determina si es par o impar.
# =============================================================================
def ejercicio_par_impar():
    """
    Detecta si el número ingresado por el usuario es par o impar
    usando el operador módulo (%).
    """
    print("\n--- EJERCICIO 3: Par o Impar ---")
    number = int(input("Ingresa un número entero: "))

    if number % 2 == 0:
        print(f"{number} es PAR")
    else:
        print(f"{number} es IMPAR")


# =============================================================================
# EJERCICIO 4: Calculadora de propina
# Calcula cuánto pagar de propina dado el total de la cuenta y el porcentaje.
# =============================================================================
def ejercicio_propina():
    """
    Calcula la propina y el total a pagar dado un porcentaje.
    Muestra el monto de la propina y el total con propina incluida.
    """
    print("\n--- EJERCICIO 4: Calculadora de Propina ---")
    bill = float(input("Total de la cuenta: $"))
    tip_percent = float(input("Porcentaje de propina (ej: 15): "))

    tip_amount = bill * (tip_percent / 100)
    total = bill + tip_amount

    print(f"\nCuenta: ${bill:.2f}")
    print(f"Propina ({tip_percent}%): ${tip_amount:.2f}")
    print(f"Total a pagar: ${total:.2f}")


# =============================================================================
# EJERCICIO 5: Edad en días, horas, minutos y segundos
# Convierte la edad en años a otras unidades de tiempo.
# =============================================================================
def ejercicio_edad_en_tiempo():
    """
    Toma la edad del usuario en años y la convierte a:
    días, horas, minutos y segundos (de forma aproximada).
    """
    print("\n--- EJERCICIO 5: Edad en Unidades de Tiempo ---")
    age_years = int(input("¿Cuántos años tienes? "))

    days = age_years * 365
    hours = days * 24
    minutes = hours * 60
    seconds = minutes * 60

    print(f"\nTienes aproximadamente:")
    print(f"  {days:,} días")
    print(f"  {hours:,} horas")
    print(f"  {minutes:,} minutos")
    print(f"  {seconds:,} segundos")


# =============================================================================
# EJERCICIO 6: Nombre completo en diferentes formatos
# Pide nombre y apellido y los muestra de varias formas.
# =============================================================================
def ejercicio_nombre_completo():
    """
    Solicita nombre y apellido al usuario y los presenta
    en múltiples formatos: normal, invertido, mayúsculas, etc.
    """
    print("\n--- EJERCICIO 6: Formato de Nombre ---")
    first_name = input("Ingresa tu nombre: ").strip()
    last_name = input("Ingresa tu apellido: ").strip()

    print("\nFormatos disponibles:")
    print(f"  Completo:      {first_name} {last_name}")
    print(f"  Invertido:     {last_name}, {first_name}")
    print(f"  Mayúsculas:    {(first_name + ' ' + last_name).upper()}")
    print(f"  Minúsculas:    {(first_name + ' ' + last_name).lower()}")
    print(f"  Iniciales:     {first_name[0].upper()}.{last_name[0].upper()}.")
    print(f"  Con guión:     {first_name}-{last_name}")


# =============================================================================
# EJERCICIO 7: Verificador de año bisiesto
# Un año es bisiesto si es divisible por 4, excepto los múltiplos de 100,
# a menos que también sean múltiplos de 400.
# =============================================================================
def is_leap_year(year):
    """
    Determina si un año es bisiesto.
    Regla: divisible por 4, excepto múltiplos de 100,
    salvo que también sean múltiplos de 400.
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def ejercicio_bisiesto():
    """
    Pide un año al usuario y verifica si es bisiesto o no.
    """
    print("\n--- EJERCICIO 7: Año Bisiesto ---")
    year = int(input("Ingresa un año (ej: 2024): "))

    if is_leap_year(year):
        print(f"{year} SÍ es un año bisiesto (tiene 366 días).")
    else:
        print(f"{year} NO es un año bisiesto (tiene 365 días).")


# =============================================================================
# EJERCICIO 8: Convertir segundos a horas:minutos:segundos
# Toma un número de segundos y lo descompone en h:mm:ss.
# =============================================================================
def seconds_to_hms(total_seconds):
    """
    Convierte un total de segundos al formato horas:minutos:segundos.
    Retorna una tupla (horas, minutos, segundos).
    """
    hours = total_seconds // 3600
    remaining = total_seconds % 3600
    minutes = remaining // 60
    seconds = remaining % 60
    return hours, minutes, seconds


def ejercicio_convertir_segundos():
    """
    Solicita segundos al usuario y los convierte al formato h:mm:ss.
    """
    print("\n--- EJERCICIO 8: Segundos a H:MM:SS ---")
    total = int(input("Ingresa la cantidad de segundos: "))

    h, m, s = seconds_to_hms(total)
    print(f"{total} segundos = {h}h {m:02d}m {s:02d}s")
    print(f"Formato reloj: {h:02d}:{m:02d}:{s:02d}")


# =============================================================================
# EJERCICIO 9: Área y perímetro de un círculo
# Calcula ambas medidas dado el radio.
# =============================================================================
def ejercicio_circulo():
    """
    Calcula el área y el perímetro (circunferencia) de un círculo
    a partir del radio ingresado por el usuario.
    Fórmulas: área = π*r², perímetro = 2*π*r
    """
    print("\n--- EJERCICIO 9: Área y Perímetro del Círculo ---")
    radius = float(input("Ingresa el radio del círculo: "))

    area = math.pi * radius ** 2
    perimeter = 2 * math.pi * radius

    print(f"\nCírculo con radio = {radius}")
    print(f"  Área:      {area:.4f} unidades²")
    print(f"  Perímetro: {perimeter:.4f} unidades")


# =============================================================================
# EJERCICIO 10: Verificar palíndromo
# Comprueba si una palabra se lee igual de izquierda a derecha
# que de derecha a izquierda.
# =============================================================================
def is_palindrome(word):
    """
    Verifica si una palabra es un palíndromo.
    Ignora mayúsculas/minúsculas y espacios en los extremos.
    Retorna True si lo es, False en caso contrario.
    """
    cleaned = word.strip().lower()
    return cleaned == cleaned[::-1]


def ejercicio_palindromo():
    """
    Pide una palabra al usuario y determina si es un palíndromo.
    Ejemplos de palíndromos: 'oso', 'radar', 'reconocer', 'anilina'.
    """
    print("\n--- EJERCICIO 10: Verificador de Palíndromo ---")
    word = input("Ingresa una palabra: ")

    if is_palindrome(word):
        print(f'"{word}" SÍ es un palíndromo.')
    else:
        reversed_word = word.strip().lower()[::-1]
        print(f'"{word}" NO es un palíndromo.')
        print(f'  Al revés se escribe: "{reversed_word}"')


# =============================================================================
# MENÚ PRINCIPAL
# Permite al usuario elegir qué ejercicio ejecutar.
# =============================================================================
def main():
    """
    Punto de entrada del programa. Muestra un menú y ejecuta
    el ejercicio que el usuario seleccione.
    """
    exercises = {
        "1": ("Calculadora de IMC", ejercicio_imc),
        "2": ("Conversor de Temperatura", ejercicio_temperatura),
        "3": ("Par o Impar", ejercicio_par_impar),
        "4": ("Calculadora de Propina", ejercicio_propina),
        "5": ("Edad en Unidades de Tiempo", ejercicio_edad_en_tiempo),
        "6": ("Formato de Nombre", ejercicio_nombre_completo),
        "7": ("Año Bisiesto", ejercicio_bisiesto),
        "8": ("Segundos a H:MM:SS", ejercicio_convertir_segundos),
        "9": ("Área y Perímetro del Círculo", ejercicio_circulo),
        "10": ("Verificador de Palíndromo", ejercicio_palindromo),
        "0": ("Salir", None),
    }

    print("=" * 50)
    print("   EJERCICIOS - CAPÍTULO 01: FUNDAMENTOS")
    print("=" * 50)

    while True:
        print("\nElige un ejercicio:")
        for key, (name, _) in exercises.items():
            print(f"  [{key}] {name}")

        choice = input("\nOpción: ").strip()

        if choice == "0":
            print("¡Hasta luego!")
            break
        elif choice in exercises:
            _, func = exercises[choice]
            func()
        else:
            print("Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    main()
