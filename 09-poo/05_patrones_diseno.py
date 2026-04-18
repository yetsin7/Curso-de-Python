# =============================================================================
# CAPÍTULO 09 - PROGRAMACIÓN ORIENTADA A OBJETOS
# Archivo: 05_patrones_diseno.py
# Descripción: Los 6 patrones de diseño más importantes implementados en Python.
#              Patrones GoF adaptados al idioma de Python con ejemplos reales.
#              Nota: Archivo educativo. Excede 250 líneas intencionalmente
#              porque contiene 6 secciones completamente independientes.
# =============================================================================


# =============================================================================
# PATRÓN 1: SINGLETON
# Garantiza que una clase tenga una única instancia en todo el programa.
# =============================================================================

class ConfigManager:
    """
    Gestor de configuración global (Singleton).
    Solo existe UNA instancia en todo el programa.
    """
    _instance = None

    def __new__(cls):
        """Retorna la instancia existente o crea una nueva si no hay."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
        return cls._instance

    def set(self, key: str, value):
        """Almacena un valor de configuración."""
        self._config[key] = value

    def get(self, key: str, default=None):
        """Recupera un valor de configuración."""
        return self._config.get(key, default)

    def __repr__(self):
        return f"ConfigManager(id={id(self)}, config={self._config})"


def demo_singleton():
    """Demuestra que dos 'instancias' son el mismo objeto."""
    print("\n" + "=" * 50)
    print("PATRÓN 1: SINGLETON - ConfigManager")
    print("=" * 50)
    config1 = ConfigManager()
    config2 = ConfigManager()
    config1.set("debug", True)
    print(f"config1 es config2: {config1 is config2}")
    print(f"config2.get('debug'): {config2.get('debug')}")
    print(repr(config1))


# =============================================================================
# PATRÓN 2: FACTORY METHOD
# Delega la creación de objetos a métodos o subclases.
# =============================================================================

class Vehiculo:
    """Interfaz base para todos los vehículos."""
    def descripcion(self): raise NotImplementedError
    def velocidad_maxima(self): raise NotImplementedError


class Automovil(Vehiculo):
    """Vehículo de 4 ruedas."""
    def descripcion(self): return "Automóvil: 4 ruedas"
    def velocidad_maxima(self): return 220


class Motocicleta(Vehiculo):
    """Vehículo de 2 ruedas motorizado."""
    def descripcion(self): return "Motocicleta: 2 ruedas"
    def velocidad_maxima(self): return 180


class Bicicleta(Vehiculo):
    """Vehículo de 2 ruedas sin motor."""
    def descripcion(self): return "Bicicleta: ecológica"
    def velocidad_maxima(self): return 40


class VehiculoFactory:
    """Factory que crea vehículos por tipo sin exponer las clases concretas."""
    _registry = {"auto": Automovil, "moto": Motocicleta, "bici": Bicicleta}

    @classmethod
    def crear(cls, tipo: str) -> Vehiculo:
        """Crea un vehículo del tipo dado. Lanza ValueError si es desconocido."""
        klass = cls._registry.get(tipo.lower())
        if not klass:
            raise ValueError(f"Tipo desconocido: '{tipo}'. Válidos: {list(cls._registry)}")
        return klass()


def demo_factory():
    """Demuestra la creación de vehículos con Factory."""
    print("\n" + "=" * 50)
    print("PATRÓN 2: FACTORY METHOD - Vehículos")
    print("=" * 50)
    for tipo in ["auto", "moto", "bici"]:
        v = VehiculoFactory.crear(tipo)
        print(f"  {v.descripcion()} → max {v.velocidad_maxima()} km/h")


# =============================================================================
# PATRÓN 3: OBSERVER
# Uno-a-muchos: cuando el sujeto cambia, notifica a todos sus oyentes.
# =============================================================================

class EventBus:
    """Bus de eventos. Los suscriptores se registran por nombre de evento."""
    def __init__(self):
        self._subs: dict = {}

    def suscribir(self, evento: str, callback):
        """Registra una función como oyente del evento dado."""
        self._subs.setdefault(evento, []).append(callback)

    def publicar(self, evento: str, datos=None):
        """Notifica a todos los oyentes del evento con los datos dados."""
        oyentes = self._subs.get(evento, [])
        print(f"  ['{evento}'] Notificando {len(oyentes)} suscriptor(es)...")
        for cb in oyentes:
            cb(datos)


def demo_observer():
    """Demuestra publicación de eventos y notificación de suscriptores."""
    print("\n" + "=" * 50)
    print("PATRÓN 3: OBSERVER - Sistema de Eventos")
    print("=" * 50)
    bus = EventBus()
    bus.suscribir("usuario.creado", lambda d: print(f"    [Email] Bienvenida a {d['email']}"))
    bus.suscribir("usuario.creado", lambda d: print(f"    [Log]   Creado: {d['nombre']}"))
    bus.suscribir("compra", lambda d: print(f"    [Stock] Reducir: {d['producto']}"))
    bus.publicar("usuario.creado", {"nombre": "Ana", "email": "ana@example.com"})
    bus.publicar("compra", {"producto": "Laptop"})
    bus.publicar("evento.sin.oyentes")


# =============================================================================
# PATRÓN 4: STRATEGY
# Encapsula algoritmos intercambiables. El contexto los usa sin conocer detalles.
# =============================================================================

class EstrategiaOrdenamiento:
    """Interfaz base para estrategias de ordenamiento."""
    def ordenar(self, data: list) -> list: raise NotImplementedError
    def nombre(self) -> str: raise NotImplementedError


class OrdenamientoBurbuja(EstrategiaOrdenamiento):
    """Burbuja O(n²): compara e intercambia elementos adyacentes."""
    def ordenar(self, data: list) -> list:
        arr = list(data)
        for i in range(len(arr)):
            for j in range(len(arr) - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

    def nombre(self): return "Burbuja O(n²)"


class OrdenamientoNativo(EstrategiaOrdenamiento):
    """Timsort nativo O(n log n): altamente optimizado."""
    def ordenar(self, data: list) -> list: return sorted(data)
    def nombre(self): return "Timsort nativo O(n log n)"


class Ordenador:
    """Contexto que delega el ordenamiento a la estrategia activa."""
    def __init__(self, estrategia: EstrategiaOrdenamiento):
        self._estrategia = estrategia

    def cambiar(self, estrategia: EstrategiaOrdenamiento):
        """Intercambia la estrategia en tiempo de ejecución."""
        self._estrategia = estrategia

    def ordenar(self, data: list) -> list:
        return self._estrategia.ordenar(data)


def demo_strategy():
    """Demuestra el intercambio de algoritmos de ordenamiento."""
    print("\n" + "=" * 50)
    print("PATRÓN 4: STRATEGY - Ordenamiento")
    print("=" * 50)
    data = [64, 34, 25, 12, 22, 11, 90]
    print(f"  Original: {data}")
    ord_ = Ordenador(OrdenamientoBurbuja())
    for est in [OrdenamientoBurbuja(), OrdenamientoNativo()]:
        ord_.cambiar(est)
        print(f"  [{est.nombre()}]: {ord_.ordenar(data)}")


# =============================================================================
# PATRÓN 5: DECORATOR (GoF)
# Añade funcionalidad a objetos en tiempo de ejecución sin alterar la clase.
# =============================================================================

class TextoSimple:
    """Componente base: texto sin formato."""
    def __init__(self, contenido: str):
        self._contenido = contenido

    def renderizar(self) -> str: return self._contenido
    def costo(self) -> float: return 0.0


class DecoradorBase:
    """Base de decoradores: envuelve cualquier componente."""
    def __init__(self, comp):
        self._comp = comp

    def renderizar(self) -> str: return self._comp.renderizar()
    def costo(self) -> float: return self._comp.costo()


class DecoradorNegrita(DecoradorBase):
    """Añade etiqueta HTML negrita."""
    def renderizar(self): return f"<b>{self._comp.renderizar()}</b>"
    def costo(self): return self._comp.costo() + 1.0


class DecoradorColor(DecoradorBase):
    """Añade color de texto HTML."""
    def __init__(self, comp, color: str):
        super().__init__(comp)
        self._color = color

    def renderizar(self): return f'<span style="color:{self._color}">{self._comp.renderizar()}</span>'
    def costo(self): return self._comp.costo() + 2.0


def demo_decorator():
    """Demuestra el apilamiento de decoradores."""
    print("\n" + "=" * 50)
    print("PATRÓN 5: DECORATOR (GoF) - Texto con formato")
    print("=" * 50)
    texto = TextoSimple("Hola Python")
    print(f"  Sin decorar: {texto.renderizar()} (costo: {texto.costo()})")
    negrita = DecoradorNegrita(texto)
    print(f"  Negrita:     {negrita.renderizar()} (costo: {negrita.costo()})")
    color = DecoradorColor(negrita, "red")
    print(f"  + Color:     {color.renderizar()} (costo: {color.costo()})")


# =============================================================================
# PATRÓN 6: BUILDER
# Construye objetos complejos paso a paso con API fluida.
# =============================================================================

class QueryBuilder:
    """Constructor de consultas SQL con encadenamiento de métodos."""
    def __init__(self, tabla: str):
        self._tabla = tabla
        self._campos = ["*"]
        self._condiciones = []
        self._orden = None
        self._limite = None

    def seleccionar(self, *campos) -> "QueryBuilder":
        """Define las columnas a seleccionar."""
        self._campos = list(campos)
        return self

    def donde(self, condicion: str) -> "QueryBuilder":
        """Añade una cláusula WHERE."""
        self._condiciones.append(condicion)
        return self

    def ordenar_por(self, campo: str, dir: str = "ASC") -> "QueryBuilder":
        """Define el orden de resultados."""
        self._orden = f"{campo} {dir.upper()}"
        return self

    def limitar(self, n: int) -> "QueryBuilder":
        """Limita el número de filas retornadas."""
        self._limite = n
        return self

    def construir(self) -> str:
        """Construye y retorna el string SQL final."""
        q = f"SELECT {', '.join(self._campos)} FROM {self._tabla}"
        if self._condiciones:
            q += f"\n  WHERE {' AND '.join(self._condiciones)}"
        if self._orden:
            q += f"\n  ORDER BY {self._orden}"
        if self._limite:
            q += f"\n  LIMIT {self._limite}"
        return q + ";"


def demo_builder():
    """Demuestra la construcción de queries SQL con encadenamiento."""
    print("\n" + "=" * 50)
    print("PATRÓN 6: BUILDER - QueryBuilder SQL")
    print("=" * 50)
    q = (QueryBuilder("usuarios")
         .seleccionar("nombre", "email")
         .donde("activo = TRUE")
         .donde("edad >= 18")
         .ordenar_por("nombre")
         .limitar(10)
         .construir())
    print(f"\n{q}")


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

def main():
    """Ejecuta la demostración de todos los patrones de diseño."""
    print("=" * 50)
    print("   PATRONES DE DISEÑO (GoF) EN PYTHON")
    print("   Capítulo 09 - POO")
    print("=" * 50)
    demo_singleton()
    demo_factory()
    demo_observer()
    demo_strategy()
    demo_decorator()
    demo_builder()
    print("\n" + "=" * 50)
    print("   Todos los patrones ejecutados.")
    print("=" * 50)


if __name__ == "__main__":
    main()
