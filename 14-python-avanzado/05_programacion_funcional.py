"""
Capítulo 14 — Python Avanzado
Archivo: 05_programacion_funcional.py

Programación funcional en Python.

Python no es un lenguaje puramente funcional, pero adopta muchos
conceptos funcionales que hacen el código más expresivo, composable
y fácil de razonar. Este archivo cubre:
  - map, filter, zip y comprensiones
  - functools: reduce, partial, lru_cache, cache
  - Closures y funciones de orden superior
  - Currying y composición de funciones
  - El módulo operator como alternativa a lambdas simples

Ejecución:
    python 05_programacion_funcional.py
"""

import functools    # Herramientas para programación funcional
import operator     # Operadores como funciones (add, mul, lt, etc.)
import time         # Para demostrar el efecto del caché
from typing import Callable, TypeVar, Any

T = TypeVar("T")
R = TypeVar("R")


# ==============================================================
# SECCIÓN 1: map, filter, zip — procesamiento de colecciones
# ==============================================================

def demo_map_filter_zip():
    """
    map(), filter() y zip() son funciones de orden superior:
    reciben funciones como argumentos.

    En Python moderno, las comprensiones de lista son generalmente
    más legibles que map/filter. Pero map/filter son útiles cuando
    ya tienes una función definida que quieres aplicar.
    """
    print("--- map, filter, zip ---")

    numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # map(función, iterable): aplica función a cada elemento
    # Devuelve un iterador (lazy), no una lista
    cuadrados_map = list(map(lambda x: x ** 2, numeros))
    # Equivalente más pythónico:
    cuadrados_comp = [x ** 2 for x in numeros]
    print(f"  map (cuadrados):  {cuadrados_map}")

    # filter(función, iterable): devuelve elementos donde función retorna True
    pares_filter = list(filter(lambda x: x % 2 == 0, numeros))
    pares_comp = [x for x in numeros if x % 2 == 0]
    print(f"  filter (pares):   {pares_filter}")

    # zip(*iterables): empareja elementos posicionalmente
    nombres = ["Ana", "Luis", "María"]
    edades = [25, 30, 28]
    ciudades = ["Madrid", "Lima", "Buenos Aires"]

    combinado = list(zip(nombres, edades, ciudades))
    print(f"  zip:              {combinado}")

    # zip se puede desempaquetar con * (unzip)
    nombres_rec, edades_rec, ciudades_rec = zip(*combinado)
    print(f"  unzip nombres:    {list(nombres_rec)}")

    # Usar map con función ya definida (más limpio que lambda)
    palabras = ["  hola  ", "  mundo  ", "  python  "]
    limpias = list(map(str.strip, palabras))
    mayusculas = list(map(str.upper, limpias))
    print(f"  map(str.strip):   {limpias}")
    print(f"  map(str.upper):   {mayusculas}")


# ==============================================================
# SECCIÓN 2: functools.reduce — reducción de una secuencia
# ==============================================================

def demo_reduce():
    """
    reduce(función, iterable): aplica función acumulativamente.
    reduce(f, [a, b, c, d]) → f(f(f(a, b), c), d)

    En Python 3, reduce está en functools (no es built-in).
    Para operaciones comunes, usa sum(), max(), min(), all(), any()
    que son más claras. reduce es útil para operaciones personalizadas.
    """
    print("\n--- functools.reduce ---")

    numeros = [1, 2, 3, 4, 5]

    # Suma con reduce (hay que entenderlo, pero usa sum() en código real)
    suma = functools.reduce(lambda acc, x: acc + x, numeros)
    print(f"  reduce suma {numeros}: {suma}")

    # Producto de todos los elementos
    producto = functools.reduce(operator.mul, numeros, 1)
    print(f"  reduce producto: {producto}")

    # Máximo de una lista (usa max() en código real)
    maximo = functools.reduce(lambda a, b: a if a > b else b, numeros)
    print(f"  reduce máximo: {maximo}")

    # Ejemplo útil: aplanar lista de listas
    listas = [[1, 2], [3, 4], [5, 6]]
    aplanada = functools.reduce(lambda acc, x: acc + x, listas, [])
    print(f"  reduce aplanar: {aplanada}")

    # Construir un diccionario desde una lista de pares
    pares = [("a", 1), ("b", 2), ("c", 3)]
    diccionario = functools.reduce(
        lambda acc, kv: {**acc, kv[0]: kv[1]}, pares, {}
    )
    print(f"  reduce a dict: {diccionario}")


# ==============================================================
# SECCIÓN 3: functools.partial — aplicación parcial de funciones
# ==============================================================

def demo_partial():
    """
    partial(función, *args, **kwargs): crea una nueva función con
    algunos argumentos ya fijados. Es una forma de especializar
    una función genérica.

    Útil cuando tienes una función configurable y quieres
    versiones específicas de ella sin repetir los argumentos.
    """
    print("\n--- functools.partial ---")

    # Función genérica de potencia
    def potencia(base: float, exponente: float) -> float:
        """Calcula base elevado a exponente."""
        return base ** exponente

    # partial fija el argumento 'exponente' para crear versiones específicas
    cuadrado = functools.partial(potencia, exponente=2)
    cubo = functools.partial(potencia, exponente=3)
    raiz_cuadrada = functools.partial(potencia, exponente=0.5)

    print(f"  cuadrado(5):       {cuadrado(5)}")
    print(f"  cubo(3):           {cubo(3)}")
    print(f"  raiz_cuadrada(16): {raiz_cuadrada(16)}")

    # partial con funciones de la librería estándar
    import math

    # log con base específica
    # math.log(x, base) recibe base como argumento posicional, no keyword
    # Creamos una función wrapper para poder usar partial correctamente
    def log_con_base(x: float, base: float) -> float:
        """Logaritmo de x en la base indicada."""
        return math.log(x, base)

    log_base_2 = functools.partial(log_con_base, base=2)
    log_base_10 = functools.partial(log_con_base, base=10)
    print(f"  log2(8):    {log_base_2(8)}")
    print(f"  log10(100): {log_base_10(100)}")

    # partial para configurar print
    print_error = functools.partial(print, "[ERROR]", end="\n", flush=True)
    print_ok = functools.partial(print, "[OK]")
    print_error("Algo salió mal")
    print_ok("Todo bien")

    # partial es útil con map para pasar funciones con más de un argumento
    multiplicar = functools.partial(operator.mul, 3)
    triplicados = list(map(multiplicar, [1, 2, 3, 4, 5]))
    print(f"  map con partial (×3): {triplicados}")


# ==============================================================
# SECCIÓN 4: Closures — funciones que capturan su entorno
# ==============================================================

def demo_closures():
    """
    Un closure es una función interna que "recuerda" las variables
    del scope en el que fue creada, incluso después de que esa
    función exterior haya terminado de ejecutarse.

    Los closures son la base de los decoradores y de muchos
    patrones funcionales en Python.
    """
    print("\n--- Closures ---")

    def hacer_multiplicador(factor: float) -> Callable[[float], float]:
        """
        Devuelve una función que multiplica por 'factor'.
        'factor' es capturado por el closure y persiste.
        """
        def multiplicar(x: float) -> float:
            # 'factor' viene del scope exterior — closure
            return x * factor
        return multiplicar

    doblar = hacer_multiplicador(2)
    triplicar = hacer_multiplicador(3)
    decuplicar = hacer_multiplicador(10)

    print(f"  doblar(7):     {doblar(7)}")
    print(f"  triplicar(4):  {triplicar(4)}")
    print(f"  decuplicar(5): {decuplicar(5)}")

    # Closure como contador con estado
    def hacer_contador(inicio: int = 0) -> Callable[[], int]:
        """
        Devuelve una función que lleva un contador.
        El estado (cuenta) persiste entre llamadas gracias al closure.
        La palabra 'nonlocal' permite modificar la variable del scope exterior.
        """
        cuenta = inicio

        def incrementar() -> int:
            nonlocal cuenta  # Indica que 'cuenta' pertenece al scope exterior
            cuenta += 1
            return cuenta

        return incrementar

    contador_a = hacer_contador(0)
    contador_b = hacer_contador(100)  # Cada closure tiene su propio estado

    print(f"\n  contador_a: {contador_a()}, {contador_a()}, {contador_a()}")
    print(f"  contador_b: {contador_b()}, {contador_b()}")
    print(f"  contador_a: {contador_a()}")  # Sigue desde donde estaba


# ==============================================================
# SECCIÓN 5: lru_cache y cache — memoización
# ==============================================================

def demo_cache():
    """
    @lru_cache(maxsize) memoriza los resultados de una función.
    Si llamas la función con los mismos argumentos, devuelve
    el resultado guardado en lugar de calcularlo de nuevo.

    LRU = Least Recently Used: cuando el caché está lleno,
    descarta el resultado menos recientemente usado.

    @cache (Python 3.9+) es igual a @lru_cache(maxsize=None)
    — caché ilimitado, más simple para la mayoría de casos.
    """
    print("\n--- @lru_cache y @cache ---")

    # Sin caché: Fibonacci es exponencialmente lento por recalcular
    def fibonacci_lento(n: int) -> int:
        """O(2^n) — muy ineficiente para n grande."""
        if n <= 1:
            return n
        return fibonacci_lento(n - 1) + fibonacci_lento(n - 2)

    # Con caché: cada valor solo se calcula una vez → O(n)
    @functools.lru_cache(maxsize=None)
    def fibonacci_rapido(n: int) -> int:
        """O(n) gracias al caché — cada valor se calcula exactamente una vez."""
        if n <= 1:
            return n
        return fibonacci_rapido(n - 1) + fibonacci_rapido(n - 2)

    # Comparamos el tiempo de ejecución
    n = 30

    inicio = time.perf_counter()
    resultado_lento = fibonacci_lento(n)
    tiempo_lento = time.perf_counter() - inicio

    inicio = time.perf_counter()
    resultado_rapido = fibonacci_rapido(n)
    tiempo_rapido = time.perf_counter() - inicio

    print(f"  fibonacci({n}) sin caché:  {resultado_lento} en {tiempo_lento:.4f}s")
    print(f"  fibonacci({n}) con caché:  {resultado_rapido} en {tiempo_rapido:.6f}s")
    print(f"  Aceleración: {tiempo_lento / max(tiempo_rapido, 0.000001):.0f}x más rápido")
    print(f"  Info del caché: {fibonacci_rapido.cache_info()}")

    # @cache para funciones donde el caché debe ser persistente
    # (Python 3.9+, equivale a lru_cache(maxsize=None))
    @functools.cache
    def factorial_cache(n: int) -> int:
        """Factorial con caché permanente."""
        if n <= 1:
            return 1
        return n * factorial_cache(n - 1)

    print(f"\n  factorial_cache(10): {factorial_cache(10)}")
    print(f"  factorial_cache(5):  {factorial_cache(5)}")
    print(f"  Info: {factorial_cache.cache_info()}")


# ==============================================================
# SECCIÓN 6: El módulo operator — operadores como funciones
# ==============================================================

def demo_operator():
    """
    El módulo 'operator' provee versiones funcionales de todos
    los operadores de Python. Son más eficientes que lambdas y
    más legibles en contextos de programación funcional.
    """
    print("\n--- módulo operator ---")

    # Operadores aritméticos
    print(f"  operator.add(3, 4):    {operator.add(3, 4)}")
    print(f"  operator.mul(3, 4):    {operator.mul(3, 4)}")
    print(f"  operator.pow(2, 10):   {operator.pow(2, 10)}")
    print(f"  operator.floordiv(7,2):{operator.floordiv(7, 2)}")

    # operator.itemgetter: obtiene un elemento por índice o clave
    # Mucho más rápido que lambda x: x[key] para uso con sorted/max/min
    estudiantes = [
        {"nombre": "Ana", "nota": 9.5, "grado": 3},
        {"nombre": "Luis", "nota": 7.2, "grado": 2},
        {"nombre": "María", "nota": 8.8, "grado": 3},
        {"nombre": "Carlos", "nota": 9.5, "grado": 2},
    ]

    por_nota = sorted(estudiantes, key=operator.itemgetter("nota"), reverse=True)
    print(f"\n  Por nota (desc): {[e['nombre'] for e in por_nota]}")

    # itemgetter con múltiples claves: ordena por nota desc, luego por nombre
    por_nota_nombre = sorted(
        estudiantes,
        key=operator.itemgetter("nota", "nombre"),
        reverse=True
    )
    print(f"  Por nota+nombre: {[(e['nombre'], e['nota']) for e in por_nota_nombre]}")

    # operator.attrgetter: obtiene un atributo de un objeto
    from dataclasses import dataclass

    @dataclass
    class Punto:
        x: float
        y: float

    puntos = [Punto(3, 1), Punto(1, 4), Punto(2, 2)]
    por_x = sorted(puntos, key=operator.attrgetter("x"))
    print(f"\n  Puntos por x: {[(p.x, p.y) for p in por_x]}")

    # operator con functools.reduce
    numeros = [1, 2, 3, 4, 5]
    producto = functools.reduce(operator.mul, numeros)
    print(f"\n  reduce(operator.mul, {numeros}): {producto}")


# ==============================================================
# SECCIÓN 7: Composición de funciones y currying
# ==============================================================

def demo_composicion():
    """
    Composición: combinar dos o más funciones en una nueva.
    compose(f, g)(x) == f(g(x))

    Currying: transformar una función de múltiples argumentos
    en una cadena de funciones de un argumento.
    curry(f)(a)(b) == f(a, b)

    Python no tiene estas funciones built-in, pero se implementan
    fácilmente con closures.
    """
    print("\n--- Composición y currying ---")

    def componer(*funciones: Callable) -> Callable:
        """
        Compone múltiples funciones en una sola.
        Las funciones se aplican de derecha a izquierda:
        componer(f, g, h)(x) == f(g(h(x)))
        """
        def aplicar(valor: Any) -> Any:
            # reduce aplica las funciones de derecha a izquierda
            return functools.reduce(lambda v, f: f(v), reversed(funciones), valor)
        return aplicar

    # Funciones simples para componer
    agregar_iva = lambda precio: precio * 1.21
    redondear_2 = lambda n: round(n, 2)
    formatear_euro = lambda n: f"€{n}"

    # Composición: precio → precio con IVA → redondeado → formateado
    precio_final = componer(formatear_euro, redondear_2, agregar_iva)
    print(f"  precio_final(100): {precio_final(100)}")
    print(f"  precio_final(49.99): {precio_final(49.99)}")

    # Currying manual con closures
    def curry_suma(a: float) -> Callable[[float], float]:
        """Versión curried de la suma: curry_suma(3)(4) == 7."""
        def inner(b: float) -> float:
            return a + b
        return inner

    sumar_10 = curry_suma(10)
    sumar_100 = curry_suma(100)

    print(f"\n  sumar_10(5):  {sumar_10(5)}")
    print(f"  sumar_100(25): {sumar_100(25)}")

    # Combinar currying con map
    numeros = [1, 2, 3, 4, 5]
    con_base_1000 = list(map(curry_suma(1000), numeros))
    print(f"  map(curry_suma(1000), {numeros}): {con_base_1000}")


# ==============================================================
# DEMOSTRACIÓN COMPLETA
# ==============================================================

def demo():
    sep = "─" * 50
    print("=== PROGRAMACIÓN FUNCIONAL EN PYTHON ===\n")

    print(f"{sep}\n1. MAP, FILTER, ZIP\n")
    demo_map_filter_zip()

    print(f"\n{sep}\n2. REDUCE\n")
    demo_reduce()

    print(f"\n{sep}\n3. PARTIAL\n")
    demo_partial()

    print(f"\n{sep}\n4. CLOSURES\n")
    demo_closures()

    print(f"\n{sep}\n5. LRU_CACHE Y CACHE\n")
    demo_cache()

    print(f"\n{sep}\n6. MÓDULO OPERATOR\n")
    demo_operator()

    print(f"\n{sep}\n7. COMPOSICIÓN Y CURRYING\n")
    demo_composicion()


if __name__ == "__main__":
    demo()
