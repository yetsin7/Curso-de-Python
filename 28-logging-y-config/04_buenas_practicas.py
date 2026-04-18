# =============================================================================
# CAPÍTULO 28 — Logging, Configuración y Buenas Prácticas
# Archivo 4: Buenas prácticas — PEP 8, SOLID, type hints, code smells
# =============================================================================
# Temas: PEP 8 con ejemplos, type hints, mypy, principios SOLID en Python,
# code smells comunes y cómo refactorizarlos, patrones de diseño básicos.
# =============================================================================

from __future__ import annotations  # Permite anotaciones de tipo forward

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Protocol
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# SECCIÓN 1: PEP 8 — La guía de estilo oficial de Python
# =============================================================================

print("=" * 60)
print("1. PEP 8 — Estilo de código Python")
print("=" * 60)

# ---- NOMBRES ----

# ❌ MAL — nombres crípticos, inconsistentes, sin convención
def Calcular(x, Y, z2):
    n = x+Y
    return n*z2

# ✅ BIEN — snake_case, nombres descriptivos
def calcular_precio_total(precio_unitario: float, cantidad: int, descuento: float = 0.0) -> float:
    """
    Calcula el precio total aplicando descuento.

    Args:
        precio_unitario: Precio de un solo artículo
        cantidad: Número de artículos
        descuento: Porcentaje de descuento (0.0 a 1.0)
    Returns:
        Precio total después de descuento
    """
    subtotal = precio_unitario * cantidad
    return subtotal * (1 - descuento)


# Convenciones de nombres:
# snake_case          → variables, funciones, métodos, módulos, paquetes
# UPPER_SNAKE_CASE    → constantes
# PascalCase          → clases
# _privado            → uso interno (convención, no forzado)
# __muy_privado       → name mangling (evitar en la práctica)

MAX_REINTENTOS = 3          # ✅ Constante
TIMEOUT_SEGUNDOS = 30       # ✅ Constante
class UsuarioServicio:      # ✅ Clase
    pass

# ---- ESPACIOS Y FORMATO ----

# ❌ MAL
x=1+2
lista=[1,2,3]
if x==3 :
    pass

# ✅ BIEN
x = 1 + 2
lista = [1, 2, 3]
if x == 3:
    pass

# ---- LONGITUD DE LÍNEA (máximo 88 caracteres con Black, 79 con PEP 8 puro) ----

# ❌ MAL — línea demasiado larga
nombre_completo = f"El usuario {x} tiene acceso a {lista} y puede realizar {MAX_REINTENTOS} intentos de login"

# ✅ BIEN — dividir lógicamente
nombre_completo = (
    f"El usuario {x} tiene acceso a {lista} "
    f"y puede realizar {MAX_REINTENTOS} intentos"
)

# ---- IMPORTS — PEP 8 ordena imports en 3 grupos separados por línea en blanco ----
# 1. Librería estándar (import os, import sys)
# 2. Librerías de terceros (import requests, import numpy)
# 3. Módulos locales del proyecto (from mi_app import utils)

# isort automatiza este orden — instala con: pip install isort
# black formatea el código automáticamente — instala con: pip install black

# ---- COMPRENSIONES vs BUCLES ----

numeros = range(20)

# ❌ MAL — bucle cuando una comprensión es más limpio
pares = []
for n in numeros:
    if n % 2 == 0:
        pares.append(n * 2)

# ✅ BIEN — comprensión de lista
pares = [n * 2 for n in numeros if n % 2 == 0]

# ⚠️ CUIDADO — comprensiones anidadas complejas son peores que un bucle
# Si la comprensión tiene más de 2 condiciones o 2 niveles de anidamiento, usa bucle

print(f"  Pares: {pares[:5]}...")
print(f"  Precio total: {calcular_precio_total(10.0, 5, 0.1)}")


# =============================================================================
# SECCIÓN 2: Type hints — Tipado estático opcional en Python
# =============================================================================

print("\n" + "=" * 60)
print("2. Type hints — Documentación ejecutable")
print("=" * 60)

# Los type hints son opcionales pero invaluables:
# - mypy verifica tipos en tiempo de desarrollo (no en runtime)
# - Los IDEs los usan para autocompletado y detección de errores
# - Son documentación que no puede quedar desactualizada

# Sin type hints — ¿Qué acepta esta función? ¿Qué retorna?
def procesar(datos, modo):  # type: ignore
    pass

# Con type hints — inmediatamente claro
def procesar_pedido(
    items: List[Dict[str, Any]],
    descuento: Optional[float] = None,
    envio_expres: bool = False,
) -> Dict[str, Any]:
    """
    Procesa los items de un pedido calculando el total.

    Args:
        items: Lista de dicts con 'precio' y 'cantidad'
        descuento: Porcentaje de descuento o None
        envio_expres: Si se aplica tarifa de envío expres
    Returns:
        Dict con 'subtotal', 'descuento_aplicado', 'envio', 'total'
    """
    subtotal = sum(item["precio"] * item["cantidad"] for item in items)
    descuento_aplicado = subtotal * (descuento or 0)
    envio = 150.0 if envio_expres else (0.0 if subtotal > 500 else 50.0)
    total = subtotal - descuento_aplicado + envio

    return {
        "subtotal": subtotal,
        "descuento_aplicado": descuento_aplicado,
        "envio": envio,
        "total": total,
    }


# Dataclasses — la forma moderna de clases de datos con type hints
@dataclass
class Producto:
    """Representa un producto en el catálogo."""
    id: int
    nombre: str
    precio: float
    stock: int = 0
    activo: bool = True
    etiquetas: List[str] = field(default_factory=list)

    def tiene_stock(self) -> bool:
        """Verifica si el producto tiene unidades disponibles."""
        return self.stock > 0

    def aplicar_descuento(self, porcentaje: float) -> float:
        """Calcula el precio con descuento aplicado."""
        if not 0 <= porcentaje <= 1:
            raise ValueError(f"El descuento debe estar entre 0 y 1, recibido: {porcentaje}")
        return self.precio * (1 - porcentaje)


producto = Producto(id=1, nombre="Laptop", precio=15000.0, stock=5, etiquetas=["tech", "nueva"])
print(f"  Producto: {producto.nombre}, Precio: ${producto.precio}")
print(f"  Con 20% descuento: ${producto.aplicar_descuento(0.20)}")
print(f"  Tiene stock: {producto.tiene_stock()}")


# =============================================================================
# SECCIÓN 3: Principios SOLID en Python
# =============================================================================

print("\n" + "=" * 60)
print("3. Principios SOLID con ejemplos Python")
print("=" * 60)

# ---- S: Single Responsibility Principle ----
# Cada clase debe tener UNA sola razón para cambiar.

# ❌ MAL — esta clase hace todo: maneja lógica de negocio, BD y envío de email
class PedidoMal:
    def crear(self, items):
        # Lógica de negocio + acceso a BD + envío de email en un solo lugar
        total = sum(i["precio"] for i in items)
        # self.db.save({"items": items, "total": total})  # BD
        # self.email.send("pedido creado")                # Email
        return total

# ✅ BIEN — responsabilidades separadas
class CalculadorPedido:
    """Solo calcula totales y aplica reglas de negocio."""

    def calcular_total(self, items: List[Dict]) -> float:
        return sum(item["precio"] * item.get("cantidad", 1) for item in items)

    def aplicar_descuento(self, total: float, codigo: str) -> float:
        descuentos = {"VERANO20": 0.20, "BIENVENIDO10": 0.10}
        return total * (1 - descuentos.get(codigo, 0))


# ---- O: Open/Closed Principle ----
# Abierto para extensión, cerrado para modificación.
# Agregar comportamiento sin cambiar el código existente.

class CalculadorDescuento(ABC):
    """Interfaz abstracta para calcular descuentos."""

    @abstractmethod
    def calcular(self, precio: float) -> float:
        """Retorna el precio final después del descuento."""
        ...


class SinDescuento(CalculadorDescuento):
    """Precio sin modificación."""
    def calcular(self, precio: float) -> float:
        return precio


class DescuentoPorcentaje(CalculadorDescuento):
    """Descuento por porcentaje fijo."""
    def __init__(self, porcentaje: float):
        self.porcentaje = porcentaje

    def calcular(self, precio: float) -> float:
        return precio * (1 - self.porcentaje)


class DescuentoTemporada(CalculadorDescuento):
    """Descuento especial de temporada — agregado SIN modificar las clases anteriores."""
    def __init__(self, porcentaje: float, precio_minimo: float):
        self.porcentaje = porcentaje
        self.precio_minimo = precio_minimo

    def calcular(self, precio: float) -> float:
        if precio >= self.precio_minimo:
            return precio * (1 - self.porcentaje)
        return precio


# ---- L: Liskov Substitution Principle ----
# Las subclases deben ser intercambiables con sus clases base.


class Animal(ABC):
    @abstractmethod
    def hacer_sonido(self) -> str: ...
    @abstractmethod
    def moverse(self) -> str: ...


class Perro(Animal):
    def hacer_sonido(self) -> str: return "¡Guau!"
    def moverse(self) -> str: return "corre en 4 patas"


class Pajaro(Animal):
    def hacer_sonido(self) -> str: return "¡Pío!"
    def moverse(self) -> str: return "vuela"


def describir_animal(animal: Animal) -> str:
    """Funciona con CUALQUIER subclase de Animal — LSP en acción."""
    return f"{type(animal).__name__}: '{animal.hacer_sonido()}' y {animal.moverse()}"


for a in [Perro(), Pajaro()]:
    print(f"  {describir_animal(a)}")


# ---- I: Interface Segregation Principle ----
# Interfaces pequeñas y específicas en lugar de una grande y genérica.

# ❌ MAL — interfaz demasiado grande, no todas las clases implementan todo
class ServicioNotificacionesMAL(ABC):
    @abstractmethod
    def enviar_email(self, a: str, asunto: str): ...
    @abstractmethod
    def enviar_sms(self, numero: str, mensaje: str): ...
    @abstractmethod
    def enviar_push(self, token: str, mensaje: str): ...
    @abstractmethod
    def enviar_whatsapp(self, numero: str, mensaje: str): ...

# ✅ BIEN — interfaces pequeñas y específicas (usando Protocol en Python moderno)
class EnviadorEmail(Protocol):
    def enviar_email(self, destinatario: str, asunto: str, cuerpo: str) -> bool: ...

class EnviadorSMS(Protocol):
    def enviar_sms(self, numero: str, mensaje: str) -> bool: ...

class ServicioEmailBasico:
    """Solo implementa email — no fuerza implementar SMS."""
    def enviar_email(self, destinatario: str, asunto: str, cuerpo: str) -> bool:
        print(f"  Email → {destinatario}: '{asunto}'")
        return True


# ---- D: Dependency Inversion Principle ----
# Depender de abstracciones, no de implementaciones concretas.

class RepositorioPedidosProtocol(Protocol):
    """Abstracción del repositorio — no dependemos de SQL, MongoDB, etc."""
    def guardar(self, pedido: dict) -> str: ...
    def buscar(self, pedido_id: str) -> Optional[dict]: ...


class RepositorioPedidosMemoria:
    """Implementación en memoria para pruebas."""
    def __init__(self):
        self._datos: Dict[str, dict] = {}

    def guardar(self, pedido: dict) -> str:
        pid = f"PED-{len(self._datos)+1:04d}"
        self._datos[pid] = pedido
        return pid

    def buscar(self, pedido_id: str) -> Optional[dict]:
        return self._datos.get(pedido_id)


class ServicioPedidos:
    """
    Depende de la abstracción RepositorioPedidosProtocol, no de la implementación.
    En producción inyectas RepositorioPedidosSQL, en tests RepositorioPedidosMemoria.
    """
    def __init__(self, repositorio: RepositorioPedidosProtocol):
        self._repo = repositorio

    def crear_pedido(self, items: List[dict], usuario_id: int) -> str:
        total = sum(i["precio"] * i.get("cantidad", 1) for i in items)
        pedido = {"items": items, "usuario_id": usuario_id, "total": total}
        pid = self._repo.guardar(pedido)
        logger.info(f"Pedido creado: {pid} por usuario {usuario_id}")
        return pid


# Demostrar DIP con inyección de dependencias
repo = RepositorioPedidosMemoria()
servicio = ServicioPedidos(repositorio=repo)  # Inyección de dependencia
pid = servicio.crear_pedido(
    items=[{"nombre": "Laptop", "precio": 15000, "cantidad": 1}],
    usuario_id=42
)
print(f"\n  Pedido creado: {pid}")


# =============================================================================
# SECCIÓN 4: Code Smells — Olores de código y cómo eliminarlos
# =============================================================================

print("\n" + "=" * 60)
print("4. Code Smells y refactorizaciones")
print("=" * 60)

# ---- SMELL 1: Magic Numbers ----

# ❌ MAL — ¿Qué significan 0.16, 1.5, 30?
def calcular_precio_mal(precio, tipo):
    if tipo == 1:
        return precio * 1.16
    elif tipo == 2:
        return precio * 1.5
    return precio * 1.30

# ✅ BIEN — constantes con nombres descriptivos
IVA_ESTÁNDAR = 0.16
MARGEN_PREMIUM = 1.50
MARGEN_ESTANDAR = 1.30

class TipoProducto(Enum):
    ESTANDAR = "estandar"
    PREMIUM = "premium"
    IMPORTADO = "importado"

MARGENES: Dict[TipoProducto, float] = {
    TipoProducto.ESTANDAR: MARGEN_ESTANDAR,
    TipoProducto.PREMIUM: MARGEN_PREMIUM,
    TipoProducto.IMPORTADO: 1.45,
}

def calcular_precio(precio_base: float, tipo: TipoProducto) -> float:
    margen = MARGENES.get(tipo, 1.0)
    return precio_base * margen * (1 + IVA_ESTÁNDAR)

print(f"  Precio premium (sin smells): ${calcular_precio(1000, TipoProducto.PREMIUM):.2f}")

# ---- SMELL 2: Long Method ----
# Una función que hace demasiado — dividir en funciones más pequeñas

# ❌ MAL — función de 30+ líneas que hace todo
def procesar_usuario_mal(datos):
    # Validar...
    if not datos.get("nombre"): return None
    if not datos.get("email"): return None
    if "@" not in datos.get("email", ""): return None
    # Transformar...
    nombre_limpio = datos["nombre"].strip().title()
    email_lower = datos["email"].lower().strip()
    # Construir...
    return {"nombre": nombre_limpio, "email": email_lower}

# ✅ BIEN — funciones pequeñas y con una sola responsabilidad
def validar_datos_usuario(datos: dict) -> bool:
    """Verifica que los datos del usuario tengan el formato correcto."""
    return bool(datos.get("nombre")) and "@" in datos.get("email", "")

def normalizar_datos_usuario(datos: dict) -> dict:
    """Limpia y normaliza los datos del usuario."""
    return {
        "nombre": datos["nombre"].strip().title(),
        "email": datos["email"].lower().strip(),
    }

def procesar_usuario(datos: dict) -> Optional[dict]:
    """Procesa los datos del usuario validando y normalizando."""
    if not validar_datos_usuario(datos):
        return None
    return normalizar_datos_usuario(datos)

resultado = procesar_usuario({"nombre": "  juan GARCÍA  ", "email": "  JUAN@EJEMPLO.COM  "})
print(f"  Usuario procesado: {resultado}")

# ---- SMELL 3: Duplicate Code ----
# Copiar y pegar = problemas multiplicados. Extraer a función reutilizable.

# ❌ MAL — lógica duplicada
def descuento_cliente_regular(precio):
    if precio > 1000:
        return precio * 0.05
    return 0

def descuento_cliente_premium(precio):
    if precio > 500:
        return precio * 0.10
    return 0

# ✅ BIEN — parámetros en lugar de duplicación
def calcular_descuento(precio: float, umbral: float, porcentaje: float) -> float:
    """Calcula el descuento si el precio supera el umbral."""
    return precio * porcentaje if precio > umbral else 0.0

# Configuración declarativa en lugar de lógica duplicada
TIPOS_CLIENTE = {
    "regular": {"umbral": 1000, "porcentaje": 0.05},
    "premium": {"umbral": 500, "porcentaje": 0.10},
    "vip": {"umbral": 100, "porcentaje": 0.15},
}

def obtener_descuento_cliente(precio: float, tipo_cliente: str) -> float:
    config = TIPOS_CLIENTE.get(tipo_cliente, {"umbral": float("inf"), "porcentaje": 0})
    return calcular_descuento(precio, config["umbral"], config["porcentaje"])

print(f"  Descuento cliente regular (precio=1500): ${obtener_descuento_cliente(1500, 'regular')}")
print(f"  Descuento cliente vip (precio=200): ${obtener_descuento_cliente(200, 'vip')}")


# =============================================================================
# SECCIÓN 5: Herramientas de calidad de código
# =============================================================================

print("\n" + "=" * 60)
print("5. Herramientas de calidad de código")
print("=" * 60)

print("""
  HERRAMIENTAS ESENCIALES:

  1. black — Formateador automático (sin configuración)
     pip install black
     black mi_archivo.py
     black . --line-length 88

  2. isort — Ordena imports automáticamente
     pip install isort
     isort mi_archivo.py
     isort --profile black .

  3. mypy — Verificación de tipos estáticos
     pip install mypy
     mypy mi_archivo.py
     mypy . --ignore-missing-imports

  4. flake8 — Linter (estilo + errores básicos)
     pip install flake8
     flake8 mi_archivo.py --max-line-length 88

  5. pylint — Linter más completo (más estricto)
     pip install pylint
     pylint mi_archivo.py

  PRE-COMMIT HOOK (automatiza todo antes de cada commit):
  pip install pre-commit

  Archivo .pre-commit-config.yaml:
  ─────────────────────────────────
  repos:
    - repo: https://github.com/psf/black
      rev: 23.12.0
      hooks:
        - id: black
    - repo: https://github.com/pycqa/isort
      rev: 5.13.2
      hooks:
        - id: isort
          args: [--profile, black]
    - repo: https://github.com/pycqa/flake8
      rev: 7.0.0
      hooks:
        - id: flake8
  ─────────────────────────────────
  pre-commit install
  pre-commit run --all-files
""")

print("FIN: 04_buenas_practicas.py completado")
