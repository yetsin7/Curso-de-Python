"""
Capítulo 14 — Python Avanzado
Archivo: 03_dataclasses.py

Dataclasses — generación automática de clases de datos.

El decorador @dataclass (PEP 557, Python 3.7+) genera automáticamente
métodos especiales para clases cuyo propósito principal es almacenar
datos: __init__, __repr__, __eq__, y más opcionales.

Sin dataclass, una clase simple requiere mucho código repetitivo
(boilerplate). Con @dataclass, la misma clase es mucho más concisa.

Ejecución:
    python 03_dataclasses.py
"""

from dataclasses import (
    dataclass,      # Decorador principal
    field,          # Para configurar campos individuales
    fields,         # Función para inspeccionar campos de una dataclass
    asdict,         # Convierte una dataclass a diccionario
    astuple,        # Convierte una dataclass a tupla
    replace,        # Crea una copia con campos modificados
    InitVar,        # Campo que solo existe en __init__, no como atributo
    KW_ONLY,        # Todos los campos siguientes son keyword-only
)
from typing import ClassVar, Optional
import math


# ==============================================================
# SECCIÓN 1: El problema — clase sin dataclass
# ==============================================================

class PuntoSinDataclass:
    """
    Clase punto 2D sin @dataclass.
    Para tener repr, eq e init, hay que escribir todo manualmente.
    Esto es boilerplate: código repetitivo que no aporta lógica.
    """

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        # Representación legible para debugging
        return f"PuntoSinDataclass(x={self.x}, y={self.y})"

    def __eq__(self, other: object) -> bool:
        # Comparación por valor, no por identidad de objeto
        if not isinstance(other, PuntoSinDataclass):
            return NotImplemented
        return self.x == other.x and self.y == other.y


# ==============================================================
# SECCIÓN 2: La solución — @dataclass básico
# ==============================================================

@dataclass
class Punto:
    """
    Clase punto 2D CON @dataclass.
    @dataclass genera automáticamente:
      - __init__(self, x: float, y: float)
      - __repr__: muestra Punto(x=1.0, y=2.0)
      - __eq__: compara campo por campo

    La anotación de tipo es obligatoria para que @dataclass
    reconozca el campo. Si no tiene tipo, no es un campo.
    """
    x: float
    y: float

    def distancia_origen(self) -> float:
        """Puedes agregar métodos normalmente."""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def distancia_a(self, otro: "Punto") -> float:
        """Distancia euclidiana a otro punto."""
        return math.sqrt((self.x - otro.x) ** 2 + (self.y - otro.y) ** 2)


# ==============================================================
# SECCIÓN 3: Valores por defecto y field()
# ==============================================================

@dataclass
class Producto:
    """
    Dataclass con valores por defecto.

    REGLA IMPORTANTE: Los campos CON default deben ir DESPUÉS
    de los campos SIN default (igual que en funciones Python).
    Si pones un campo con default antes de uno sin default,
    Python lanza un TypeError.
    """
    nombre: str                          # Sin default — obligatorio
    precio: float                        # Sin default — obligatorio
    categoria: str = "General"           # Con default simple
    activo: bool = True                  # Con default simple

    # field() es necesario cuando el default es mutable (list, dict, set)
    # NO puedes hacer: etiquetas: list[str] = []
    # Porque todas las instancias compartirían la MISMA lista
    # field(default_factory=list) crea una lista nueva por instancia
    etiquetas: list[str] = field(default_factory=list)

    # repr=False excluye este campo del __repr__ generado
    # útil para campos de metadatos internos que no quieres ver siempre
    _id_interno: int = field(default=0, repr=False)

    # compare=False excluye este campo de las comparaciones __eq__ y __lt__
    fecha_creacion: str = field(default="2024-01-01", compare=False)

    # init=False: el campo NO aparece en __init__, se asigna en __post_init__
    precio_con_iva: float = field(init=False, repr=True)

    def __post_init__(self) -> None:
        """
        __post_init__ se ejecuta automáticamente DESPUÉS de __init__.
        Úsalo para:
          - Calcular campos derivados de otros campos
          - Validar los datos recibidos
          - Transformar valores (normalizar strings, etc.)
        """
        # Calculamos el precio con IVA a partir del precio base
        self.precio_con_iva = round(self.precio * 1.21, 2)

        # Validación: el precio no puede ser negativo
        if self.precio < 0:
            raise ValueError(f"El precio no puede ser negativo: {self.precio}")

        # Normalizamos el nombre
        self.nombre = self.nombre.strip().title()


# ==============================================================
# SECCIÓN 4: Dataclass frozen (inmutable)
# ==============================================================

@dataclass(frozen=True)
class Coordenada:
    """
    frozen=True hace que la dataclass sea INMUTABLE.
    Una vez creada, no se puede modificar ningún campo.

    Ventajas de frozen:
      - Se puede usar como clave de diccionario (es hashable)
      - Se puede agregar a sets
      - Garantiza que nadie modifica accidentalmente el objeto
      - Útil para representar valores matemáticos, claves, etc.

    Si intentas asignar un campo, Python lanza FrozenInstanceError.
    """
    latitud: float
    longitud: float

    def __post_init__(self) -> None:
        """Validamos que las coordenadas estén en rangos válidos."""
        if not (-90 <= self.latitud <= 90):
            raise ValueError(f"Latitud inválida: {self.latitud}")
        if not (-180 <= self.longitud <= 180):
            raise ValueError(f"Longitud inválida: {self.longitud}")

    def distancia_km(self, otra: "Coordenada") -> float:
        """
        Fórmula de Haversine para distancia entre coordenadas.
        Aproximación simplificada para el ejemplo.
        """
        radio_tierra = 6371
        dlat = math.radians(otra.latitud - self.latitud)
        dlon = math.radians(otra.longitud - self.longitud)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(self.latitud)) *
             math.cos(math.radians(otra.latitud)) *
             math.sin(dlon / 2) ** 2)
        return radio_tierra * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ==============================================================
# SECCIÓN 5: Dataclass con orden (order=True)
# ==============================================================

@dataclass(order=True)
class Estudiante:
    """
    order=True genera: __lt__, __le__, __gt__, __ge__.
    Permite ordenar con sorted() y comparar con <, >.
    La comparación se hace campo por campo, en orden de declaración.

    sort_index es un campo calculado en __post_init__ que controla
    el orden de comparación. Usando field(compare=False) en los otros
    campos, solo sort_index se usa para comparar.
    """
    # sort_index debe ir PRIMERO para que sea el campo de comparación
    sort_index: float = field(init=False, repr=False)

    nombre: str = field(compare=False)
    promedio: float = field(compare=False)
    grado: int = field(compare=False)

    def __post_init__(self) -> None:
        # Ordenamos por promedio descendente (negativo para invertir el orden)
        self.sort_index = -self.promedio


# ==============================================================
# SECCIÓN 6: Herencia entre dataclasses
# ==============================================================

@dataclass
class Animal:
    """Dataclass base para herencia."""
    nombre: str
    especie: str
    edad: int = 0


@dataclass
class Mascota(Animal):
    """
    Herencia de dataclass.
    La subclase puede agregar nuevos campos.
    Los campos del padre van primero en __init__.

    REGLA: Si el padre tiene campos con default, todos los campos
    del hijo también deben tener default (porque vienen después).
    """
    duenio: str = "Sin dueño"
    vacunado: bool = False

    def presentarse(self) -> str:
        return (f"Soy {self.nombre}, {self.especie} de {self.edad} años. "
                f"Mi dueño es {self.duenio}.")


# ==============================================================
# SECCIÓN 7: InitVar — parámetro solo en __init__
# ==============================================================

@dataclass
class ConfiguracionDB:
    """
    InitVar permite pasar parámetros a __init__ que no se guardan
    como atributos. Son solo para usarse en __post_init__.
    Útil para datos de construcción que no necesitas después.
    """
    host: str
    puerto: int = 5432
    # password_plain es solo para __init__, no se guarda en el objeto
    password_plain: InitVar[Optional[str]] = None
    # El hash de la contraseña SÍ se guarda
    _password_hash: str = field(init=False, repr=False, default="")

    def __post_init__(self, password_plain: Optional[str]) -> None:
        """password_plain viene de InitVar, no del campo self."""
        if password_plain:
            # En producción usarías bcrypt o argon2, no esto
            self._password_hash = f"hash_{hash(password_plain)}"


# ==============================================================
# SECCIÓN 8: ClassVar y campos de clase
# ==============================================================

@dataclass
class Contador:
    """
    ClassVar no es tratado como campo de dataclass.
    No aparece en __init__, __repr__ ni __eq__.
    Es simplemente una variable de clase normal.
    """
    nombre: str
    valor: int = 0

    # ClassVar: variable de clase, no de instancia
    # @dataclass la ignora completamente
    total_instancias: ClassVar[int] = 0

    def __post_init__(self) -> None:
        Contador.total_instancias += 1


# ==============================================================
# DEMOSTRACIÓN
# ==============================================================

def demo():
    sep = "─" * 50
    print("=== DATACLASSES ===\n")

    # Sección 1 vs 2: comparación
    print(f"{sep}\n1. SIN vs CON @dataclass\n")
    p_viejo = PuntoSinDataclass(1.0, 2.0)
    p_nuevo = Punto(1.0, 2.0)
    print(f"  Sin dataclass: {p_viejo}")
    print(f"  Con dataclass: {p_nuevo}")
    print(f"  Igualdad (1,2)==(1,2): {Punto(1, 2) == Punto(1, 2)}")
    print(f"  Distancia al origen: {Punto(3, 4).distancia_origen()}")

    # Sección 3: field() y __post_init__
    print(f"\n{sep}\n3. field() y __post_init__\n")
    prod = Producto("  laptop  ", 1000.0, etiquetas=["tech", "office"])
    print(f"  {prod}")
    print(f"  Precio con IVA calculado automáticamente: {prod.precio_con_iva}")
    try:
        Producto("error", -50.0)
    except ValueError as e:
        print(f"  Validación: {e}")

    # Sección 4: frozen
    print(f"\n{sep}\n4. FROZEN (inmutable)\n")
    madrid = Coordenada(40.4168, -3.7038)
    barcelona = Coordenada(41.3851, 2.1734)
    print(f"  Madrid: {madrid}")
    print(f"  Barcelona: {barcelona}")
    print(f"  Distancia: {madrid.distancia_km(barcelona):.0f} km")
    print(f"  Es hashable (puede ser clave de dict): {hash(madrid)}")
    try:
        madrid.latitud = 0  # type: ignore
    except Exception as e:
        print(f"  Inmutable: {type(e).__name__}")

    # replace() para crear copia con cambios (porque frozen)
    madrid_modificado = replace(madrid, latitud=41.0)
    print(f"  replace(): {madrid_modificado}")

    # Sección 5: order
    print(f"\n{sep}\n5. ORDER — ordenación\n")
    estudiantes = [
        Estudiante("Carlos", 7.5, 3),
        Estudiante("Ana", 9.8, 3),
        Estudiante("Luis", 6.2, 2),
        Estudiante("María", 9.8, 4),
    ]
    ordenados = sorted(estudiantes)
    for e in ordenados:
        print(f"  {e.nombre}: {e.promedio}")

    # Sección 6: herencia
    print(f"\n{sep}\n6. HERENCIA\n")
    perro = Mascota("Rex", "Perro", 3, duenio="Juan", vacunado=True)
    print(f"  {perro}")
    print(f"  {perro.presentarse()}")

    # Sección 7: asdict, astuple, fields
    print(f"\n{sep}\n7. UTILIDADES: asdict, astuple, fields\n")
    punto = Punto(3.0, 4.0)
    print(f"  asdict:  {asdict(punto)}")
    print(f"  astuple: {astuple(punto)}")
    print(f"  fields:  {[f.name for f in fields(punto)]}")

    # Sección 8: ClassVar
    print(f"\n{sep}\n8. CLASSVAR\n")
    c1 = Contador("primero")
    c2 = Contador("segundo")
    c3 = Contador("tercero")
    print(f"  Total instancias creadas: {Contador.total_instancias}")


if __name__ == "__main__":
    demo()
