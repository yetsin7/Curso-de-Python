# =============================================================================
# CAPÍTULO 02 - OPERADORES
# Archivo: 05_ejercicios.py
# Descripción: 8 ejercicios que cubren todos los tipos de operadores de Python:
#              aritméticos, lógicos, bit a bit, comparación y pertenencia.
# =============================================================================


# =============================================================================
# EJERCICIO 1: Calculadora básica con todos los operadores
# Solicita dos números y muestra el resultado de todas las operaciones.
# =============================================================================
def ejercicio_calculadora():
    """
    Calculadora que demuestra todos los operadores aritméticos de Python:
    suma, resta, multiplicación, división, división entera, módulo y potencia.
    """
    print("\n--- EJERCICIO 1: Calculadora Completa ---")
    a = float(input("Primer número: "))
    b = float(input("Segundo número: "))

    print(f"\nResultados con a={a} y b={b}:")
    print(f"  Suma           (a + b)  = {a + b}")
    print(f"  Resta          (a - b)  = {a - b}")
    print(f"  Multiplicación (a * b)  = {a * b}")

    # Proteger la división por cero
    if b != 0:
        print(f"  División       (a / b)  = {a / b:.4f}")
        print(f"  División entera(a // b) = {a // b}")
        print(f"  Módulo         (a % b)  = {a % b}")
    else:
        print("  División: no se puede dividir entre 0")

    print(f"  Potencia       (a ** b) = {a ** b}")


# =============================================================================
# EJERCICIO 2: Tabla de verdad de and, or, not
# Muestra todas las combinaciones posibles de True/False con cada operador.
# =============================================================================
def ejercicio_tabla_verdad():
    """
    Genera e imprime las tablas de verdad completas para los operadores
    lógicos: and, or y not. Fundamental para entender lógica booleana.
    """
    print("\n--- EJERCICIO 2: Tabla de Verdad ---")
    valores = [True, False]

    # Tabla para AND
    print("\nTabla AND (ambos deben ser True):")
    print(f"  {'A':<7} {'B':<7} {'A and B'}")
    print("  " + "-" * 22)
    for a in valores:
        for b in valores:
            print(f"  {str(a):<7} {str(b):<7} {str(a and b)}")

    # Tabla para OR
    print("\nTabla OR (al menos uno debe ser True):")
    print(f"  {'A':<7} {'B':<7} {'A or B'}")
    print("  " + "-" * 22)
    for a in valores:
        for b in valores:
            print(f"  {str(a):<7} {str(b):<7} {str(a or b)}")

    # Tabla para NOT
    print("\nTabla NOT (invierte el valor):")
    print(f"  {'A':<7} {'not A'}")
    print("  " + "-" * 15)
    for a in valores:
        print(f"  {str(a):<7} {str(not a)}")


# =============================================================================
# EJERCICIO 3: Conversor de bases numéricas
# Convierte un número decimal a binario, octal y hexadecimal.
# =============================================================================
def ejercicio_conversor_bases():
    """
    Convierte un número decimal a sus representaciones en:
    - Base 2  (binario)
    - Base 8  (octal)
    - Base 16 (hexadecimal)
    Usa las funciones built-in bin(), oct(), hex() de Python.
    """
    print("\n--- EJERCICIO 3: Conversor de Bases Numéricas ---")
    number = int(input("Ingresa un número decimal positivo: "))

    print(f"\n{number} en diferentes bases:")
    print(f"  Binario      (base 2):  {bin(number)}   → solo con dígitos: {number:b}")
    print(f"  Octal        (base 8):  {oct(number)}  → solo con dígitos: {number:o}")
    print(f"  Hexadecimal  (base 16): {hex(number)}  → solo con dígitos: {number:x}")
    print(f"  Hexadecimal mayúsculas: {number:X}")

    # Verificación: volver a decimal
    print(f"\nVerificación (volver a decimal):")
    print(f"  int('{number:b}', 2) = {int(str(number), 10)}")


# =============================================================================
# EJERCICIO 4: Verificador de divisibilidad (FizzBuzz extendido)
# Versión mejorada de FizzBuzz con más condiciones y uso del operador %.
# =============================================================================
def ejercicio_fizzbuzz():
    """
    Versión extendida de FizzBuzz que muestra el uso del operador módulo
    para verificar divisibilidad entre múltiples números a la vez.
    Rango: 1 a 30.
    """
    print("\n--- EJERCICIO 4: FizzBuzz Extendido ---")
    print("Reglas: Fizz=div 3, Buzz=div 5, Bazz=div 7")
    print("-" * 40)

    for i in range(1, 31):
        result = ""
        if i % 3 == 0:
            result += "Fizz"
        if i % 5 == 0:
            result += "Buzz"
        if i % 7 == 0:
            result += "Bazz"
        # Si no aplica ninguna regla, mostrar el número
        print(f"  {i:3d} → {result if result else i}")


# =============================================================================
# EJERCICIO 5: Operaciones bit a bit con ejemplos reales
# Explica los operadores &, |, ^, ~, <<, >> con contexto práctico.
# =============================================================================
def ejercicio_bitwise():
    """
    Demuestra los operadores bit a bit de Python con dos números enteros.
    Muestra la representación en binario para visualizar el resultado.
    Casos de uso real: permisos de archivos, máscaras de red, flags.
    """
    print("\n--- EJERCICIO 5: Operadores Bit a Bit ---")
    a, b = 60, 13  # 60 = 0b111100, 13 = 0b001101

    print(f"\na = {a}  ({bin(a)})")
    print(f"b = {b}  ({bin(b)})")
    print("-" * 40)
    print(f"  AND  (a & b)  = {a & b:3d}  ({bin(a & b)})  → bits comunes")
    print(f"  OR   (a | b)  = {a | b:3d}  ({bin(a | b)}) → unión de bits")
    print(f"  XOR  (a ^ b)  = {a ^ b:3d}  ({bin(a ^ b)}) → bits diferentes")
    print(f"  NOT  (~a)     = {~a:3d} ({bin(~a)})  → invertir todos")
    print(f"  LEFT (a << 2) = {a << 2:3d}  ({bin(a << 2)}) → multiplicar por 4")
    print(f"  RIGHT(a >> 2) = {a >> 2:3d}   ({bin(a >> 2)})  → dividir por 4")

    print("\nCaso real: verificar permisos con máscaras")
    # Ejemplo: sistema de permisos estilo Unix simplificado
    READ = 0b100    # 4
    WRITE = 0b010   # 2
    EXECUTE = 0b001 # 1

    user_permissions = READ | WRITE  # El usuario tiene lectura y escritura
    print(f"  Permisos: lectura={bool(user_permissions & READ)}, "
          f"escritura={bool(user_permissions & WRITE)}, "
          f"ejecución={bool(user_permissions & EXECUTE)}")


# =============================================================================
# EJERCICIO 6: Precedencia de operadores con casos sorprendentes
# Muestra cómo Python evalúa expresiones complejas según precedencia.
# =============================================================================
def ejercicio_precedencia():
    """
    Ilustra la precedencia de operadores en Python con ejemplos
    que suelen generar confusión. El orden es: ** > +/- unario >
    * / // % > + - > << >> > & > ^ > | > comparaciones > not > and > or
    """
    print("\n--- EJERCICIO 6: Precedencia de Operadores ---")
    print("Casos sorprendentes:\n")

    # Caso 1: ** tiene mayor precedencia que -
    print(f"  -2 ** 2 = {-2 ** 2}    (no es 4, es -(2**2) = -4)")
    print(f"  (-2) ** 2 = {(-2) ** 2}   (ahora sí es 4)")

    # Caso 2: and tiene mayor precedencia que or
    result = True or False and False
    print(f"\n  True or False and False = {result}")
    print(f"  Se evalúa como: True or (False and False) = True or False = True")

    # Caso 3: comparaciones encadenadas
    x = 5
    print(f"\n  x = {x}")
    print(f"  1 < x < 10 = {1 < x < 10}  (encadenamiento: 1<5 and 5<10)")
    print(f"  10 > x > 1 = {10 > x > 1}  (equivalente al anterior)")

    # Caso 4: división vs multiplicación (misma precedencia, izq a der)
    print(f"\n  6 / 2 * 3 = {6 / 2 * 3}  (se evalúa de izq a der: (6/2)*3 = 9)")
    print(f"  6 / (2 * 3) = {6 / (2 * 3)}  (con paréntesis: diferente resultado)")


# =============================================================================
# EJERCICIO 7: Comparación de flotantes con tolerancia
# Los floats no deben compararse con == debido a errores de precisión.
# =============================================================================
def floats_are_equal(a, b, tolerance=1e-9):
    """
    Compara dos números flotantes con una tolerancia dada.
    Retorna True si la diferencia absoluta es menor que la tolerancia.
    Esto evita falsos negativos por errores de precisión binaria.
    """
    return abs(a - b) < tolerance


def ejercicio_comparacion_floats():
    """
    Demuestra el problema clásico de comparar flotantes con ==
    y la solución correcta usando tolerancia (epsilon).
    """
    print("\n--- EJERCICIO 7: Comparación de Flotantes ---")

    # El problema clásico
    result = 0.1 + 0.2
    print(f"  0.1 + 0.2 = {result}")
    print(f"  0.1 + 0.2 == 0.3 → {result == 0.3}  (¡sorpresa!)")
    print(f"  Valor exacto: {result:.20f}")

    # La solución correcta
    print(f"\n  Usando tolerancia (1e-9):")
    print(f"  floats_are_equal(0.1+0.2, 0.3) → {floats_are_equal(0.1 + 0.2, 0.3)}")

    # Comparación con math.isclose (la solución estándar de Python)
    import math
    print(f"\n  math.isclose(0.1+0.2, 0.3) → {math.isclose(0.1 + 0.2, 0.3)}")
    print("  Recomendado: usar math.isclose() en producción.")


# =============================================================================
# EJERCICIO 8: Operadores de pertenencia (in, not in)
# Verifica si un elemento existe dentro de una colección o cadena.
# =============================================================================
def ejercicio_pertenencia():
    """
    Demuestra los operadores 'in' y 'not in' con diferentes
    tipos de colecciones: strings, listas, tuplas, diccionarios y conjuntos.
    """
    print("\n--- EJERCICIO 8: Operadores de Pertenencia (in / not in) ---")

    # En strings
    sentence = "Python es poderoso y elegante"
    print(f"\nString: '{sentence}'")
    print(f"  'Python' in sentence → {'Python' in sentence}")
    print(f"  'Java' not in sentence → {'Java' not in sentence}")

    # En listas
    fruits = ["manzana", "banana", "cereza", "mango"]
    print(f"\nLista: {fruits}")
    print(f"  'banana' in fruits → {'banana' in fruits}")
    print(f"  'pera' in fruits → {'pera' in fruits}")

    # En diccionarios (busca en las CLAVES, no en los valores)
    person = {"nombre": "Ana", "edad": 30, "ciudad": "Madrid"}
    print(f"\nDiccionario: {person}")
    print(f"  'nombre' in person → {'nombre' in person}  (busca en claves)")
    print(f"  'Ana' in person → {'Ana' in person}  (¡no busca en valores!)")
    print(f"  'Ana' in person.values() → {'Ana' in person.values()}")

    # Caso práctico: validar entrada de usuario
    valid_options = {"s", "n", "si", "no"}
    user_input = "si"
    print(f"\nCaso práctico: validar opción '{user_input}'")
    print(f"  '{user_input}' in {valid_options} → {user_input in valid_options}")


# =============================================================================
# MENÚ PRINCIPAL
# =============================================================================
def main():
    """Ejecuta todos los ejercicios del capítulo de operadores en secuencia."""
    exercises = {
        "1": ("Calculadora con todos los operadores", ejercicio_calculadora),
        "2": ("Tabla de verdad and/or/not", ejercicio_tabla_verdad),
        "3": ("Conversor de bases numéricas", ejercicio_conversor_bases),
        "4": ("FizzBuzz extendido (módulo)", ejercicio_fizzbuzz),
        "5": ("Operaciones bit a bit", ejercicio_bitwise),
        "6": ("Precedencia de operadores", ejercicio_precedencia),
        "7": ("Comparación de flotantes", ejercicio_comparacion_floats),
        "8": ("Operadores de pertenencia", ejercicio_pertenencia),
        "0": ("Salir", None),
    }

    print("=" * 50)
    print("   EJERCICIOS - CAPÍTULO 02: OPERADORES")
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
            print("Opción no válida.")


if __name__ == "__main__":
    main()
