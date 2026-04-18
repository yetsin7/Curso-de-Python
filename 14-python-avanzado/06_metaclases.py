# =============================================================================
# CAPÍTULO 14 - PYTHON AVANZADO
# Archivo: 06_metaclases.py
# Descripción: La magia interna de Python: dunder methods, metaclases,
#              __slots__, ABCs, descriptor protocol y class decorators.
# =============================================================================

import sys
from abc import ABC, abstractmethod


# =============================================================================
# SECCIÓN 1: DUNDER METHODS — Vector 2D completo
# Integran objetos propios con operadores y funciones built-in de Python.
# =============================================================================

class Vector:
    """
    Vector 2D que implementa los dunder methods más importantes.
    Permite usar el objeto como un tipo nativo de Python.
    """
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self): return f"Vector({self.x}, {self.y})"
    def __str__(self): return f"({self.x}, {self.y})"
    def __len__(self): return 2
    def __getitem__(self, i): return [self.x, self.y][i]
    def __setitem__(self, i, v):
        if i == 0: self.x = v
        elif i == 1: self.y = v
        else: raise IndexError(i)
    def __contains__(self, v): return v == self.x or v == self.y
    def __iter__(self): yield self.x; yield self.y
    def __add__(self, o): return Vector(self.x + o.x, self.y + o.y)
    def __mul__(self, s): return Vector(self.x * s, self.y * s)
    def __rmul__(self, s): return self.__mul__(s)
    def __eq__(self, o): return isinstance(o, Vector) and self.x == o.x and self.y == o.y
    def __abs__(self): return (self.x**2 + self.y**2)**0.5
    def __bool__(self): return self.x != 0 or self.y != 0
    def __call__(self, escala): return Vector(self.x * escala, self.y * escala)

    def __enter__(self):
        """Permite usar Vector como context manager para operaciones en bloque."""
        print(f"  [+] Iniciando operación con {self}")
        return self

    def __exit__(self, *args):
        """Se ejecuta al salir del bloque with, manejando errores si los hay."""
        print(f"  [-] Operación finalizada con {self}")
        return False


def demo_dunder():
    """Demuestra todos los dunder methods del Vector."""
    print("\n" + "=" * 50)
    print("1. DUNDER METHODS - Vector 2D")
    print("=" * 50)
    v1, v2 = Vector(3, 4), Vector(1, 2)
    print(f"  repr={repr(v1)}, str={str(v1)}, len={len(v1)}")
    print(f"  v1[0]={v1[0]}, 3.0 in v1={3.0 in v1}, list={list(v1)}")
    print(f"  v1+v2={v1+v2}, v1*2={v1*2}, 3*v1={3*v1}")
    print(f"  eq={v1==v2}, abs={abs(v1):.2f}, bool={bool(v1)}")
    print(f"  v1(0.5)={v1(0.5)}  ← llamado como función")
    with v1:
        print(f"    Dentro del bloque: {v1}")


# =============================================================================
# SECCIÓN 2: METACLASES — Registro automático de clases
# Una metaclase es "la clase de una clase". type es la metaclase por defecto.
# =============================================================================

class RegistroMeta(type):
    """
    Metaclase que registra automáticamente cada subclase al definirla.
    Útil para sistemas de plugins o registros de handlers.
    """
    _registro: dict = {}

    def __new__(mcs, nombre, bases, namespace):
        """Intercepta la creación de la clase para registrarla."""
        clase = super().__new__(mcs, nombre, bases, namespace)
        if bases:  # No registrar la clase base abstracta
            mcs._registro[nombre] = clase
        return clase


class HandlerBase(metaclass=RegistroMeta):
    """Clase base abstracta del sistema de handlers."""
    def procesar(self, dato): raise NotImplementedError


class HandlerTexto(HandlerBase):
    """Handler para procesar strings."""
    def procesar(self, dato): return f"[Texto]: {str(dato).upper()}"


class HandlerNumero(HandlerBase):
    """Handler para procesar números."""
    def procesar(self, dato): return f"[Número]: {dato * 2}"


def demo_metaclases():
    """Demuestra registro automático y creación dinámica de clases."""
    print("\n" + "=" * 50)
    print("2. METACLASES - Registro Automático")
    print("=" * 50)
    print(f"  Clases registradas: {list(RegistroMeta._registro)}")
    for nombre, clase in RegistroMeta._registro.items():
        print(f"    {nombre}: {clase().procesar(42)}")

    # Crear una clase dinámicamente con type()
    Dinamica = type("Dinamica", (object,), {
        "version": "1.0",
        "saludar": lambda self: f"Clase dinámica v{self.version}"
    })
    print(f"\n  Clase dinámica: {Dinamica().saludar()}")


# =============================================================================
# SECCIÓN 3: __slots__ — Optimización de memoria
# Reemplaza el __dict__ dinámico por un esquema fijo más eficiente.
# =============================================================================

class PuntoNormal:
    """Punto 2D normal con __dict__ por defecto."""
    def __init__(self, x, y): self.x = x; self.y = y


class PuntoSlots:
    """
    Punto 2D con __slots__: hasta 3x menos memoria que la versión normal.
    Ideal para clases que generan millones de instancias.
    No permite agregar atributos fuera de __slots__.
    """
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x = x; self.y = y


def demo_slots():
    """Compara memoria entre clase normal y clase con __slots__."""
    print("\n" + "=" * 50)
    print("3. __slots__ - Optimización de Memoria")
    print("=" * 50)
    pn = PuntoNormal(1.0, 2.0)
    ps = PuntoSlots(1.0, 2.0)
    print(f"  Normal:  {sys.getsizeof(pn)} bytes, tiene __dict__: {hasattr(pn, '__dict__')}")
    print(f"  Slots:   {sys.getsizeof(ps)} bytes, tiene __dict__: {hasattr(ps, '__dict__')}")
    try:
        ps.z = 3
    except AttributeError as e:
        print(f"  Intentar agregar ps.z → AttributeError: {e}")


# =============================================================================
# SECCIÓN 4: ABSTRACT BASE CLASSES (ABC)
# Definen interfaces que las subclases DEBEN implementar.
# =============================================================================

class Figura(ABC):
    """Clase abstracta para figuras geométricas. No se puede instanciar."""

    @abstractmethod
    def area(self) -> float:
        """Calcula el área de la figura."""

    @abstractmethod
    def perimetro(self) -> float:
        """Calcula el perímetro de la figura."""

    def describir(self) -> str:
        """Descripción estándar disponible en todas las subclases."""
        return f"{self.__class__.__name__}: área={self.area():.2f}, perímetro={self.perimetro():.2f}"


class Circulo(Figura):
    """Figura circular que implementa los métodos abstractos."""
    def __init__(self, radio: float): self.radio = radio
    def area(self):
        import math; return math.pi * self.radio ** 2
    def perimetro(self):
        import math; return 2 * math.pi * self.radio


class Rectangulo(Figura):
    """Figura rectangular que implementa los métodos abstractos."""
    def __init__(self, ancho, alto): self.ancho = ancho; self.alto = alto
    def area(self): return self.ancho * self.alto
    def perimetro(self): return 2 * (self.ancho + self.alto)


def demo_abc():
    """Demuestra ABCs, métodos abstractos e instanciación concretas."""
    print("\n" + "=" * 50)
    print("4. ABSTRACT BASE CLASSES (ABC)")
    print("=" * 50)
    try:
        Figura()
    except TypeError as e:
        print(f"  Intentar Figura() → TypeError: {e}")
    for f in [Circulo(5), Rectangulo(4, 6)]:
        print(f"  {f.describir()}")


# =============================================================================
# SECCIÓN 5: DESCRIPTOR PROTOCOL
# Controla el acceso, modificación y eliminación de atributos.
# =============================================================================

class Validado:
    """
    Descriptor que valida que el atributo sea un número positivo.
    Reutilizable en cualquier clase y cualquier atributo.
    """
    def __set_name__(self, owner, name):
        """Guarda el nombre del atributo al definir la clase."""
        self._name = name
        self._priv = f"_{name}"

    def __get__(self, obj, objtype=None):
        """Retorna el valor al leer el atributo."""
        return None if obj is None else getattr(obj, self._priv, None)

    def __set__(self, obj, value):
        """Valida y almacena el valor al asignarlo."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"'{self._name}' debe ser numérico")
        if value < 0:
            raise ValueError(f"'{self._name}' debe ser positivo, recibido: {value}")
        setattr(obj, self._priv, value)


class Producto:
    """Clase que usa el descriptor Validado para sus atributos numéricos."""
    precio = Validado()
    stock = Validado()

    def __init__(self, nombre, precio, stock):
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def __repr__(self): return f"Producto('{self.nombre}', {self.precio}, {self.stock})"


def demo_descriptors():
    """Demuestra el descriptor Validado con casos exitosos y de error."""
    print("\n" + "=" * 50)
    print("5. DESCRIPTOR PROTOCOL")
    print("=" * 50)
    p = Producto("Laptop", 999.99, 10)
    print(f"  Creado: {p}")
    p.precio = 1199.99
    print(f"  Precio actualizado: {p.precio}")
    try: p.precio = -50
    except ValueError as e: print(f"  ValueError: {e}")
    try: p.stock = "muchos"
    except TypeError as e: print(f"  TypeError: {e}")


# =============================================================================
# SECCIÓN 6: CLASS DECORATORS vs METACLASES
# Los decoradores modifican la clase DESPUÉS de crearla.
# Las metaclases modifican la clase DURANTE su creación.
# =============================================================================

def agregar_repr(clase):
    """Decorador que añade __repr__ automático basado en vars() de la instancia."""
    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{clase.__name__}({attrs})"
    clase.__repr__ = __repr__
    return clase


def inmutable(clase):
    """Decorador que bloquea la modificación de atributos después de __init__."""
    init_orig = clase.__init__

    def nuevo_init(self, *a, **kw):
        init_orig(self, *a, **kw)
        object.__setattr__(self, "_init_done", True)

    def setattr_bloqueado(self, nombre, valor):
        if getattr(self, "_init_done", False):
            raise AttributeError(f"Objeto inmutable: no se puede modificar '{nombre}'")
        object.__setattr__(self, nombre, valor)

    clase.__init__ = nuevo_init
    clase.__setattr__ = setattr_bloqueado
    return clase


@agregar_repr
class Config:
    """Configuración con __repr__ automático."""
    def __init__(self, host, port, debug):
        self.host = host; self.port = port; self.debug = debug


@inmutable
class Punto3D:
    """Punto tridimensional inmutable."""
    def __init__(self, x, y, z): self.x = x; self.y = y; self.z = z


def demo_class_decorators():
    """Demuestra decoradores de clase para añadir comportamiento."""
    print("\n" + "=" * 50)
    print("6. CLASS DECORATORS vs METACLASES")
    print("=" * 50)
    print(f"  @agregar_repr: {Config('localhost', 8080, True)}")
    p = Punto3D(1, 2, 3)
    print(f"  @inmutable Punto3D creado: x={p.x}, y={p.y}, z={p.z}")
    try: p.x = 99
    except AttributeError as e: print(f"  Intentar p.x=99 → AttributeError: {e}")
    print("\n  Diferencia clave:")
    print("    • Decorador: modifica DESPUÉS de crear la clase")
    print("    • Metaclase: modifica DURANTE la creación")


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

def main():
    """Ejecuta todas las demostraciones del módulo."""
    print("=" * 50)
    print("   METACLASES Y MAGIA DE PYTHON - CAPÍTULO 14")
    print("=" * 50)
    demo_dunder()
    demo_metaclases()
    demo_slots()
    demo_abc()
    demo_descriptors()
    demo_class_decorators()
    print("\n" + "=" * 50)
    print("   Fin de demostraciones.")
    print("=" * 50)


if __name__ == "__main__":
    main()
