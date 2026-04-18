"""
Capítulo 14 — Python Avanzado
Archivo: 04_iteradores_avanzados.py

Iteradores personalizados e itertools.

Un iterable es cualquier objeto sobre el que puedes hacer 'for x in objeto'.
Un iterador es un objeto que sabe cuál es el "siguiente" elemento.

Python separa estas dos responsabilidades con dos protocolos:
  - Protocolo iterable: __iter__() → devuelve un iterador
  - Protocolo iterador: __next__() → devuelve el siguiente elemento
                                     lanza StopIteration al terminar

itertools es la librería estándar de Python para combinación,
filtrado y transformación eficiente de iterables.

Ejecución:
    python 04_iteradores_avanzados.py
"""

import itertools    # Librería estándar con iteradores eficientes
from typing import Iterator, Iterable, TypeVar, Generator

T = TypeVar("T")


# ==============================================================
# SECCIÓN 1: Protocolo iterador — __iter__ y __next__
# ==============================================================

class RangoPersonalizado:
    """
    Implementación de un rango numérico como clase iterable.
    Equivalente simplificado de range() para entender el protocolo.

    Esta clase implementa AMBOS protocolos en uno:
      - Es iterable (__iter__ devuelve self)
      - Es iterador (__next__ devuelve el siguiente valor)

    Nota: normalmente conviene separar el iterable del iterador
    para poder tener múltiples iteradores sobre el mismo iterable.
    """

    def __init__(self, inicio: int, fin: int, paso: int = 1) -> None:
        """
        Args:
            inicio: primer valor inclusive
            fin:    límite superior exclusive (como range())
            paso:   incremento en cada paso
        """
        self.inicio = inicio
        self.fin = fin
        self.paso = paso
        self._actual = inicio  # Estado interno del iterador

    def __iter__(self) -> "RangoPersonalizado":
        """
        __iter__ se llama cuando empiezas un for o llamas iter().
        Debe devolver un iterador. Como implementamos ambos protocolos
        en la misma clase, devolvemos self.

        Resetear _actual aquí permite reutilizar el iterador:
        for x in mi_rango: ...
        for x in mi_rango: ...  ← funciona de nuevo
        """
        self._actual = self.inicio
        return self

    def __next__(self) -> int:
        """
        __next__ se llama en cada iteración para obtener el próximo valor.
        Cuando no hay más elementos, DEBE lanzar StopIteration.
        El for loop atrapa StopIteration y termina silenciosamente.
        """
        if self._actual >= self.fin:
            raise StopIteration  # Señal de "ya no hay más elementos"

        valor = self._actual
        self._actual += self.paso
        return valor

    def __len__(self) -> int:
        """Longitud del rango (opcional pero útil)."""
        return max(0, (self.fin - self.inicio + self.paso - 1) // self.paso)


# ==============================================================
# SECCIÓN 2: Separar iterable de iterador (patrón correcto)
# ==============================================================

class NodosArbol:
    """
    Árbol binario simple. El iterable (árbol) y el iterador
    (recorrido) están separados. Esto permite múltiples iteradores
    independientes sobre el mismo árbol.
    """

    def __init__(self, valor: int,
                 izq: "NodosArbol | None" = None,
                 der: "NodosArbol | None" = None) -> None:
        self.valor = valor
        self.izq = izq
        self.der = der

    def __iter__(self) -> Iterator[int]:
        """
        Usamos un generador para el recorrido inorden.
        yield from delega la iteración a otro iterable.
        """
        # Recorrido inorden: izquierda → raíz → derecha
        if self.izq:
            yield from self.izq  # Recursión con generador
        yield self.valor
        if self.der:
            yield from self.der


# ==============================================================
# SECCIÓN 3: Generadores — la forma pythónica de crear iteradores
# ==============================================================

def fibonacci() -> Generator[int, None, None]:
    """
    Generador infinito de la secuencia de Fibonacci.

    Un generador es una función con 'yield'. Cuando Python ejecuta
    'yield valor', pausa la función y devuelve el valor. La próxima
    vez que se llama __next__, continúa desde donde se pausó.

    Los generadores son iteradores sin necesidad de escribir
    __iter__ y __next__ manualmente.

    Generator[YieldType, SendType, ReturnType]
    """
    a, b = 0, 1
    while True:  # Generador infinito — no lanza StopIteration nunca
        yield a   # Pausa aquí y devuelve 'a'
        a, b = b, a + b  # Continúa aquí en la siguiente llamada


def generar_cuadrados(limite: int) -> Generator[int, None, None]:
    """Generador finito de cuadrados perfectos."""
    for n in range(limite):
        yield n * n


# ==============================================================
# SECCIÓN 4: itertools — la librería estándar de combinatoria
# ==============================================================

def demo_itertools_infinitos():
    """
    itertools tiene iteradores INFINITOS que se usan con islice
    para tomar solo los elementos que necesitamos.
    """
    print("\n--- itertools: iteradores infinitos ---")

    # count(start, step): 0, 1, 2, 3, ...  (infinito)
    conteo = itertools.count(10, 5)  # 10, 15, 20, 25, ...
    primeros_5 = list(itertools.islice(conteo, 5))
    print(f"  count(10, 5) → primeros 5: {primeros_5}")

    # cycle(iterable): repite el iterable infinitamente
    ciclo = itertools.cycle(["A", "B", "C"])
    primeros_7 = list(itertools.islice(ciclo, 7))
    print(f"  cycle(['A','B','C']) → 7 elementos: {primeros_7}")

    # repeat(elemento, n): repite n veces (o infinito si no se da n)
    repetido = list(itertools.repeat("x", 4))
    print(f"  repeat('x', 4): {repetido}")


def demo_itertools_combinacion():
    """
    Funciones de itertools para combinar iterables.
    """
    print("\n--- itertools: combinación de iterables ---")

    # chain(*iterables): encadena múltiples iterables como uno solo
    # Útil para procesar varias listas sin crear una nueva lista grande
    lista_a = [1, 2, 3]
    lista_b = [4, 5, 6]
    lista_c = [7, 8, 9]
    encadenado = list(itertools.chain(lista_a, lista_b, lista_c))
    print(f"  chain: {encadenado}")

    # chain.from_iterable: recibe un iterable de iterables
    listas = [[1, 2], [3, 4], [5, 6]]
    aplanado = list(itertools.chain.from_iterable(listas))
    print(f"  chain.from_iterable: {aplanado}")

    # zip_longest: zip que no termina con el iterable más corto
    # fillvalue rellena los elementos faltantes
    corta = [1, 2, 3]
    larga = ["a", "b", "c", "d", "e"]
    zipped = list(itertools.zip_longest(corta, larga, fillvalue=0))
    print(f"  zip_longest: {zipped}")


def demo_itertools_combinatoria():
    """
    Funciones combinatorias de itertools para permutaciones,
    combinaciones y productos cartesianos.
    """
    print("\n--- itertools: combinatoria ---")

    letras = ["A", "B", "C"]

    # product: producto cartesiano (todas las combinaciones con repetición)
    # Equivalente a bucles for anidados
    productos = list(itertools.product(letras, repeat=2))
    print(f"  product('ABC', repeat=2): {productos}")

    # permutations: todas las permutaciones (sin repetición)
    # Orden importa: AB y BA son distintas
    perms = list(itertools.permutations(letras, 2))
    print(f"  permutations('ABC', 2): {perms}")

    # combinations: combinaciones sin repetición
    # Orden NO importa: AB y BA son la misma
    combis = list(itertools.combinations(letras, 2))
    print(f"  combinations('ABC', 2): {combis}")

    # combinations_with_replacement: combinaciones con repetición
    combis_rep = list(itertools.combinations_with_replacement(letras, 2))
    print(f"  combinations_with_replacement: {combis_rep}")


def demo_itertools_filtrado():
    """
    Funciones de itertools para filtrar y transformar iterables.
    """
    print("\n--- itertools: filtrado y transformación ---")

    numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # islice(iterable, stop): toma los primeros N elementos
    # islice(iterable, start, stop, step): más control
    primeros_3 = list(itertools.islice(numeros, 3))
    print(f"  islice(numeros, 3): {primeros_3}")
    cada_dos = list(itertools.islice(numeros, 0, None, 2))
    print(f"  islice(numeros, 0, None, 2): {cada_dos}")

    # takewhile: toma elementos MIENTRAS la condición sea True
    # Para en cuanto encuentra el primer False
    menores_5 = list(itertools.takewhile(lambda x: x < 5, numeros))
    print(f"  takewhile(x<5): {menores_5}")

    # dropwhile: DESCARTA elementos mientras la condición sea True
    # Devuelve desde el primer False en adelante
    desde_5 = list(itertools.dropwhile(lambda x: x < 5, numeros))
    print(f"  dropwhile(x<5): {desde_5}")

    # filterfalse: opuesto a filter(), devuelve donde la condición es False
    impares = list(itertools.filterfalse(lambda x: x % 2 == 0, numeros))
    print(f"  filterfalse(par): {impares}")

    # compress(data, selectors): filtra con una máscara binaria
    datos = ["a", "b", "c", "d", "e"]
    mascara = [1, 0, 1, 0, 1]
    filtrado = list(itertools.compress(datos, mascara))
    print(f"  compress(['a','b','c','d','e'], [1,0,1,0,1]): {filtrado}")


def demo_itertools_agrupacion():
    """
    groupby: agrupa elementos consecutivos con el mismo valor de clave.
    IMPORTANTE: la secuencia debe estar ORDENADA por la clave antes
    de pasar a groupby, de lo contrario los grupos no serán correctos.
    """
    print("\n--- itertools: agrupación con groupby ---")

    # Ejemplo: agrupar ventas por mes
    ventas = [
        {"mes": "enero",    "importe": 100},
        {"mes": "enero",    "importe": 200},
        {"mes": "febrero",  "importe": 150},
        {"mes": "febrero",  "importe": 300},
        {"mes": "marzo",    "importe": 50},
    ]

    # groupby requiere que los datos estén ordenados por la clave
    ventas_ordenadas = sorted(ventas, key=lambda v: v["mes"])

    print("  Total por mes:")
    for mes, grupo in itertools.groupby(ventas_ordenadas, key=lambda v: v["mes"]):
        # grupo es un iterador — solo se puede recorrer UNA vez
        total = sum(v["importe"] for v in grupo)
        print(f"    {mes}: ${total}")


def demo_itertools_acumulacion():
    """
    accumulate: aplica una función acumulativamente.
    """
    print("\n--- itertools: acumulación ---")
    import operator

    numeros = [1, 2, 3, 4, 5]

    # Suma acumulada (comportamiento por defecto)
    acumulado = list(itertools.accumulate(numeros))
    print(f"  accumulate (suma): {acumulado}")

    # Producto acumulado
    productos = list(itertools.accumulate(numeros, operator.mul))
    print(f"  accumulate (producto): {productos}")

    # Máximo acumulado
    datos = [3, 1, 4, 1, 5, 9, 2, 6]
    maximos = list(itertools.accumulate(datos, max))
    print(f"  accumulate (max de {datos}): {maximos}")


# ==============================================================
# DEMOSTRACIÓN COMPLETA
# ==============================================================

def demo():
    sep = "─" * 50
    print("=== ITERADORES AVANZADOS E ITERTOOLS ===\n")

    # Sección 1: protocolo iterador
    print(f"{sep}\n1. PROTOCOLO ITERADOR PERSONALIZADO\n")
    rango = RangoPersonalizado(0, 10, 2)
    print(f"  RangoPersonalizado(0, 10, 2): {list(rango)}")
    print(f"  Reutilizable: {list(rango)}")  # Funciona de nuevo
    print(f"  Longitud: {len(rango)}")

    # Sección 2: árbol con __iter__
    print(f"\n{sep}\n2. ÁRBOL CON __iter__ (recorrido inorden)\n")
    #       4
    #      / \
    #     2   6
    #    / \ / \
    #   1  3 5  7
    arbol = NodosArbol(4,
                       NodosArbol(2, NodosArbol(1), NodosArbol(3)),
                       NodosArbol(6, NodosArbol(5), NodosArbol(7)))
    print(f"  Inorden: {list(arbol)}")

    # Sección 3: generadores
    print(f"\n{sep}\n3. GENERADORES\n")
    gen_fib = fibonacci()
    primeros_10 = [next(gen_fib) for _ in range(10)]
    print(f"  Fibonacci (primeros 10): {primeros_10}")
    print(f"  Cuadrados hasta 8: {list(generar_cuadrados(8))}")

    # Sección 4: itertools
    demo_itertools_infinitos()
    demo_itertools_combinacion()
    demo_itertools_combinatoria()
    demo_itertools_filtrado()
    demo_itertools_agrupacion()
    demo_itertools_acumulacion()


if __name__ == "__main__":
    demo()
