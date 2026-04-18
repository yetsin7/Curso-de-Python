"""
Capítulo 15 — Testing
Archivo: calculadora.py

Módulo de calculadora que será probado en los tests.

Este módulo contiene funciones matemáticas deliberadamente
simples para que los tests sean fáciles de entender.
El énfasis está en los TESTS, no en la lógica de negocio.

Cada función está diseñada para:
  - Tener casos de éxito claros
  - Tener casos de error bien definidos
  - Ser testeable de forma aislada (sin dependencias externas)

Ejecución directa (verifica que funciona):
    python calculadora.py
"""

import math     # Para factorial y otras operaciones matemáticas


# ==============================================================
# FUNCIONES MATEMÁTICAS BÁSICAS
# ==============================================================

def sumar(a: float, b: float) -> float:
    """
    Suma dos números.

    Args:
        a: primer operando
        b: segundo operando

    Returns:
        La suma a + b

    Examples:
        >>> sumar(2, 3)
        5
        >>> sumar(-1, 1)
        0
        >>> sumar(0.1, 0.2)
        0.30000000000000004
    """
    return a + b


def restar(a: float, b: float) -> float:
    """
    Resta b de a.

    Args:
        a: minuendo
        b: sustraendo

    Returns:
        La diferencia a - b
    """
    return a - b


def multiplicar(a: float, b: float) -> float:
    """
    Multiplica dos números.

    Args:
        a: primer factor
        b: segundo factor

    Returns:
        El producto a * b
    """
    return a * b


def dividir(a: float, b: float) -> float:
    """
    Divide a entre b.

    Args:
        a: dividendo
        b: divisor (no puede ser cero)

    Returns:
        El cociente a / b

    Raises:
        ValueError: si b es cero (división por cero no definida)

    Examples:
        >>> dividir(10, 2)
        5.0
        >>> dividir(7, 2)
        3.5
        >>> dividir(5, 0)
        ValueError: No se puede dividir por cero
    """
    # Verificamos explícitamente el caso de división por cero
    # En lugar de dejar que Python lance ZeroDivisionError,
    # lanzamos ValueError con un mensaje claro
    if b == 0:
        raise ValueError("No se puede dividir por cero")
    return a / b


def potencia(base: float, exponente: float) -> float:
    """
    Calcula base elevado al exponente.

    Args:
        base:      número base
        exponente: potencia a la que se eleva

    Returns:
        base ** exponente

    Examples:
        >>> potencia(2, 10)
        1024.0
        >>> potencia(9, 0.5)
        3.0
        >>> potencia(2, -1)
        0.5
    """
    return base ** exponente


def factorial(n: int) -> int:
    """
    Calcula el factorial de n (n!).

    n! = n × (n-1) × (n-2) × ... × 2 × 1
    0! = 1  (por definición matemática)

    Args:
        n: número entero no negativo

    Returns:
        El factorial de n

    Raises:
        TypeError:  si n no es entero
        ValueError: si n es negativo

    Examples:
        >>> factorial(5)
        120
        >>> factorial(0)
        1
        >>> factorial(-1)
        ValueError
    """
    # Validamos que n sea entero
    if not isinstance(n, int):
        raise TypeError(f"factorial requiere un entero, no {type(n).__name__}")

    # El factorial no está definido para negativos
    if n < 0:
        raise ValueError(f"El factorial no está definido para números negativos: {n}")

    # Usamos math.factorial que es eficiente y maneja casos especiales
    return math.factorial(n)


def es_primo(n: int) -> bool:
    """
    Determina si un número entero es primo.

    Un número primo es mayor que 1 y solo divisible por 1 y por sí mismo.

    Args:
        n: número entero a verificar

    Returns:
        True si n es primo, False en caso contrario

    Examples:
        >>> es_primo(2)
        True
        >>> es_primo(17)
        True
        >>> es_primo(1)
        False
        >>> es_primo(4)
        False
    """
    # Los números <= 1 no son primos por definición
    if n <= 1:
        return False

    # 2 es el único primo par
    if n == 2:
        return True

    # Los pares mayores que 2 no son primos
    if n % 2 == 0:
        return False

    # Solo necesitamos verificar divisores hasta sqrt(n)
    # Si n = a × b y ambos > sqrt(n), entonces a × b > n — contradicción
    limite = int(math.sqrt(n)) + 1
    for i in range(3, limite, 2):
        if n % i == 0:
            return False

    return True


def maximo(valores: list[float]) -> float:
    """
    Devuelve el valor máximo de una lista.

    Args:
        valores: lista de números (no puede estar vacía)

    Returns:
        El valor máximo de la lista

    Raises:
        ValueError: si la lista está vacía

    Examples:
        >>> maximo([3, 1, 4, 1, 5, 9, 2, 6])
        9
        >>> maximo([])
        ValueError
    """
    if not valores:
        raise ValueError("No se puede calcular el máximo de una lista vacía")
    return max(valores)


def promedio(valores: list[float]) -> float:
    """
    Calcula el promedio aritmético de una lista de números.

    Args:
        valores: lista de números (no puede estar vacía)

    Returns:
        La media aritmética de los valores

    Raises:
        ValueError: si la lista está vacía
    """
    if not valores:
        raise ValueError("No se puede calcular el promedio de una lista vacía")
    return sum(valores) / len(valores)


# ==============================================================
# VERIFICACIÓN BÁSICA AL EJECUTAR DIRECTAMENTE
# ==============================================================

if __name__ == "__main__":
    """
    Cuando ejecutas este archivo directamente, se hacen verificaciones
    básicas para confirmar que las funciones retornan valores correctos.
    Este no es un framework de testing — los tests reales están en
    los otros archivos del capítulo.
    """
    print("Verificando módulo calculadora...")

    assert sumar(2, 3) == 5,             "sumar falló"
    assert restar(10, 4) == 6,           "restar falló"
    assert multiplicar(3, 4) == 12,      "multiplicar falló"
    assert dividir(10, 2) == 5.0,        "dividir falló"
    assert potencia(2, 8) == 256.0,      "potencia falló"
    assert factorial(5) == 120,          "factorial falló"
    assert factorial(0) == 1,            "factorial(0) falló"
    assert es_primo(17) is True,         "es_primo(17) falló"
    assert es_primo(4) is False,         "es_primo(4) falló"
    assert maximo([3, 1, 9, 2]) == 9,    "maximo falló"
    assert promedio([1, 2, 3, 4]) == 2.5, "promedio falló"

    print("Todas las verificaciones pasaron correctamente.")
    print("\nFunciones disponibles:")
    funciones = [sumar, restar, multiplicar, dividir,
                 potencia, factorial, es_primo, maximo, promedio]
    for f in funciones:
        print(f"  - {f.__name__}: {f.__doc__.split(chr(10))[1].strip()}")
