"""
Capítulo 14 — Python Avanzado
Archivo: 01_type_hints.py

Type Hints (anotaciones de tipos) en Python.

Los type hints son anotaciones opcionales que documentan qué tipos
de datos espera y devuelve una función o variable. Python NO los
verifica en tiempo de ejecución por defecto — son para herramientas
como mypy, pyright/pylance, y para que los IDEs den autocompletado.

PEP 484 (2015) introdujo el módulo 'typing' con los tipos genéricos.
PEP 585 (3.9+) permite usar list[int] en lugar de List[int].
PEP 604 (3.10+) permite usar int | str en lugar de Union[int, str].

Ejecución:
    python 01_type_hints.py
"""

from __future__ import annotations  # Activa evaluación diferida de anotaciones

# typing: módulo estándar con tipos para anotaciones avanzadas
# A partir de Python 3.9+, muchos de estos ya están en los built-ins
from typing import (
    Optional,      # Para valores que pueden ser None: Optional[X] == X | None
    Union,         # Para valores de múltiples tipos: Union[X, Y] == X | Y
    TypeVar,       # Para crear tipos genéricos
    Generic,       # Clase base para clases genéricas
    Protocol,      # Para duck typing con verificación estática
    Callable,      # Para anotar funciones como tipo
    Any,           # Desactiva verificación de tipos (usar con moderación)
    ClassVar,      # Para variables de clase (no de instancia)
    Final,         # Para constantes que no deben modificarse
    TypedDict,     # Para diccionarios con claves de tipos conocidos
    overload,      # Para funciones con múltiples firmas
    TYPE_CHECKING, # True solo cuando mypy/pyright analiza, False en runtime
)
from typing import get_type_hints  # Para inspeccionar anotaciones en runtime


# ==============================================================
# SECCIÓN 1: Anotaciones básicas de variables y funciones
# ==============================================================

# Variables: la anotación va después de : y antes del =
nombre: str = "Python"
version: int = 3
precio: float = 9.99
activo: bool = True

# Sin valor inicial (solo declara el tipo esperado)
titulo: str   # mypy sabe que esto debe ser str cuando se asigne


def saludar(nombre: str) -> str:
    """
    Función simple con anotaciones.
    nombre: str indica que el parámetro debe ser cadena.
    -> str indica que la función devuelve una cadena.
    """
    return f"Hola, {nombre}!"


def sumar(a: int, b: int) -> int:
    """Suma dos enteros y devuelve un entero."""
    return a + b


def dividir(a: float, b: float) -> float:
    """División de punto flotante."""
    if b == 0:
        raise ValueError("No se puede dividir por cero")
    return a / b


def sin_retorno(mensaje: str) -> None:
    """
    -> None indica que la función no devuelve ningún valor útil.
    Es equivalente a no poner -> en Python, pero más explícito.
    """
    print(mensaje)


# ==============================================================
# SECCIÓN 2: Tipos de colecciones
# ==============================================================

# Python 3.9+: se puede usar list, dict, tuple, set directamente
# Python 3.8 y anteriores: hay que importar List, Dict, Tuple, Set de typing

def procesar_nombres(nombres: list[str]) -> list[str]:
    """
    list[str]: lista donde cada elemento es str.
    Antes de 3.9 se usaba: List[str] (de typing).
    """
    return [n.strip().title() for n in nombres]


def contar_palabras(texto: str) -> dict[str, int]:
    """
    dict[str, int]: diccionario con claves str y valores int.
    Antes de 3.9: Dict[str, int].
    """
    palabras = texto.lower().split()
    conteo: dict[str, int] = {}
    for palabra in palabras:
        conteo[palabra] = conteo.get(palabra, 0) + 1
    return conteo


def primera_y_ultima(items: list[int]) -> tuple[int, int]:
    """
    tuple[int, int]: tupla con exactamente dos enteros.
    tuple[int, ...]: tupla de longitud variable con enteros.
    """
    return (items[0], items[-1])


def elementos_unicos(items: list[int]) -> set[int]:
    """set[int]: conjunto de enteros sin duplicados."""
    return set(items)


# ==============================================================
# SECCIÓN 3: Optional y Union — valores que pueden ser None
# ==============================================================

def buscar_usuario(user_id: int) -> Optional[str]:
    """
    Optional[str] es equivalente a Union[str, None] o str | None.
    Indica que la función puede devolver str o None.

    Usar Optional es IMPORTANTE: fuerza al llamador a verificar
    si el resultado es None antes de usarlo, evitando NullPointerErrors.
    """
    usuarios = {1: "Ana", 2: "Luis", 3: "María"}
    return usuarios.get(user_id)  # Devuelve None si no existe


def procesar_dato(valor: Union[int, str]) -> str:
    """
    Union[int, str] indica que 'valor' puede ser int O str.
    Python 3.10+ permite escribirlo como: int | str
    """
    if isinstance(valor, int):
        return f"Número: {valor}"
    return f"Texto: {valor}"


# Sintaxis moderna (Python 3.10+) — más legible
def procesar_moderno(valor: int | str | None) -> str:
    """La barra | es el operador Union de Python 3.10+."""
    if valor is None:
        return "Sin valor"
    if isinstance(valor, int):
        return f"Entero: {valor}"
    return f"Cadena: {valor}"


# ==============================================================
# SECCIÓN 4: Callable — funciones como parámetros
# ==============================================================

def aplicar_funcion(
    valores: list[int],
    funcion: Callable[[int], int]  # Función que recibe int y devuelve int
) -> list[int]:
    """
    Callable[[ParamTypes], ReturnType] anota parámetros que son funciones.
    Callable[[int], int]: función que recibe un int y devuelve un int.
    Callable[[], str]: función sin parámetros que devuelve str.
    Callable[..., Any]: función con cualquier firma.
    """
    return [funcion(v) for v in valores]


# ==============================================================
# SECCIÓN 5: TypeVar — tipos genéricos
# ==============================================================

# TypeVar crea un "placeholder" de tipo que se resuelve en tiempo de análisis
# T es el nombre convencional para un TypeVar genérico
T = TypeVar("T")


def primer_elemento(lista: list[T]) -> T:
    """
    T es un TypeVar: significa "el tipo que sea la lista".
    Si llamas primer_elemento([1, 2, 3]), T se resuelve a int.
    Si llamas primer_elemento(["a", "b"]), T se resuelve a str.
    mypy verifica que el tipo de retorno coincide con el de la lista.
    """
    if not lista:
        raise ValueError("La lista está vacía")
    return lista[0]


def invertir(lista: list[T]) -> list[T]:
    """Invierte una lista manteniendo el tipo de sus elementos."""
    return lista[::-1]


# TypeVar con restricciones: solo acepta ciertos tipos
Numero = TypeVar("Numero", int, float)


def maximo(a: Numero, b: Numero) -> Numero:
    """Solo acepta int o float, no str ni otros tipos."""
    return a if a > b else b


# ==============================================================
# SECCIÓN 6: Generic — clases genéricas
# ==============================================================

class Pila(Generic[T]):
    """
    Pila (stack) genérica: puede ser Pila[int], Pila[str], etc.
    Generic[T] permite que mypy verifique que siempre se usa
    el mismo tipo dentro de la pila.
    """

    def __init__(self) -> None:
        # El tipo de _items se infiere de T gracias a Generic[T]
        self._items: list[T] = []

    def push(self, item: T) -> None:
        """Agrega un elemento a la cima de la pila."""
        self._items.append(item)

    def pop(self) -> T:
        """Extrae y devuelve el elemento de la cima."""
        if not self._items:
            raise IndexError("La pila está vacía")
        return self._items.pop()

    def peek(self) -> Optional[T]:
        """Ve el elemento de la cima sin extraerlo."""
        return self._items[-1] if self._items else None

    def __len__(self) -> int:
        return len(self._items)


# ==============================================================
# SECCIÓN 7: Protocol — duck typing con verificación estática
# ==============================================================

class Serializable(Protocol):
    """
    Protocol define una "interfaz" sin herencia.
    Cualquier clase que implemente estos métodos cumple el protocolo,
    sin necesidad de heredar de Serializable explícitamente.
    Esto es "structural subtyping" o duck typing verificable.
    """

    def to_dict(self) -> dict[str, Any]:
        """Convierte el objeto a diccionario."""
        ...

    def to_json(self) -> str:
        """Convierte el objeto a JSON string."""
        ...


class Usuario:
    """Implementa el protocolo Serializable sin heredar de él."""

    def __init__(self, nombre: str, edad: int) -> None:
        self.nombre = nombre
        self.edad = edad

    def to_dict(self) -> dict[str, Any]:
        return {"nombre": self.nombre, "edad": self.edad}

    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict())


def guardar(objeto: Serializable) -> str:
    """
    Acepta cualquier objeto que tenga to_dict() y to_json(),
    sin importar su tipo exacto. Protocol lo verifica estáticamente.
    """
    return objeto.to_json()


# ==============================================================
# SECCIÓN 8: TypedDict — diccionarios con estructura conocida
# ==============================================================

class ConfigApp(TypedDict):
    """
    TypedDict define la estructura esperada de un diccionario.
    mypy verifica que el diccionario tenga exactamente estas claves
    con estos tipos. Útil para configuraciones y respuestas de APIs.
    """
    host: str
    port: int
    debug: bool
    database_url: str


def iniciar_servidor(config: ConfigApp) -> None:
    """Recibe una configuración tipada."""
    print(f"Iniciando en {config['host']}:{config['port']}")
    print(f"Debug: {config['debug']}")


# ==============================================================
# SECCIÓN 9: Final y ClassVar
# ==============================================================

# Final: indica que esta variable NO debe reasignarse
MAX_INTENTOS: Final[int] = 3
VERSION: Final[str] = "1.0.0"


class Configuracion:
    """Demuestra ClassVar (variable de clase) vs variable de instancia."""

    # ClassVar: es compartida por TODAS las instancias (nivel de clase)
    # No se incluye en __init__ ni en los type hints de instancia
    total_instancias: ClassVar[int] = 0

    def __init__(self, nombre: str) -> None:
        self.nombre: str = nombre
        Configuracion.total_instancias += 1


# ==============================================================
# SECCIÓN 10: get_type_hints — inspeccionar tipos en runtime
# ==============================================================

def inspeccionar_tipos():
    """
    get_type_hints() devuelve las anotaciones de una función o clase
    en tiempo de ejecución. Útil para frameworks que usan tipos
    dinámicamente (como Pydantic, FastAPI, SQLModel).
    """
    print("Tipos de 'saludar':", get_type_hints(saludar))
    print("Tipos de 'sumar':", get_type_hints(sumar))
    print("Tipos de 'buscar_usuario':", get_type_hints(buscar_usuario))


# ==============================================================
# DEMOSTRACIÓN
# ==============================================================

def demo():
    """Ejecuta ejemplos de cada sección."""
    separador = "─" * 50

    print("=== TYPE HINTS EN PYTHON ===\n")

    # Sección 1: básico
    print(f"{separador}\n1. FUNCIONES BÁSICAS")
    print(saludar("Mundo"))
    print(sumar(3, 4))

    # Sección 2: colecciones
    print(f"\n{separador}\n2. COLECCIONES")
    print(procesar_nombres(["  ana  ", "LUIS", "María"]))
    print(contar_palabras("hola mundo hola python"))

    # Sección 3: Optional / Union
    print(f"\n{separador}\n3. OPTIONAL / UNION")
    resultado = buscar_usuario(1)
    if resultado is not None:  # Verificación obligatoria con Optional
        print(f"Usuario encontrado: {resultado}")
    print(buscar_usuario(99))  # None
    print(procesar_dato(42))
    print(procesar_dato("texto"))

    # Sección 4: Callable
    print(f"\n{separador}\n4. CALLABLE")
    print(aplicar_funcion([1, 2, 3, 4], lambda x: x * 2))

    # Sección 5: TypeVar
    print(f"\n{separador}\n5. TYPEVAR")
    print(primer_elemento([10, 20, 30]))
    print(primer_elemento(["a", "b", "c"]))
    print(invertir([1, 2, 3, 4, 5]))

    # Sección 6: Generic
    print(f"\n{separador}\n6. PILA GENÉRICA")
    pila_int: Pila[int] = Pila()
    pila_int.push(1)
    pila_int.push(2)
    pila_int.push(3)
    print(f"Cima: {pila_int.peek()}, tamaño: {len(pila_int)}")
    print(f"Pop: {pila_int.pop()}")

    # Sección 7: Protocol
    print(f"\n{separador}\n7. PROTOCOL")
    usuario = Usuario("Ana", 30)
    print(guardar(usuario))

    # Sección 8: TypedDict
    print(f"\n{separador}\n8. TYPEDDICT")
    config: ConfigApp = {
        "host": "localhost",
        "port": 8000,
        "debug": True,
        "database_url": "sqlite:///app.db"
    }
    iniciar_servidor(config)

    # Sección 10: inspección de tipos
    print(f"\n{separador}\n10. INSPECCIÓN EN RUNTIME")
    inspeccionar_tipos()


if __name__ == "__main__":
    demo()
