# =============================================================================
# CAPÍTULO 21 — FastAPI
# Archivo 02: Pydantic v2 — Validación de datos en profundidad
# =============================================================================
# Pydantic es la librería de validación de datos de Python más popular.
# FastAPI la usa internamente pero Pydantic funciona de forma independiente.
#
# Instalación: pip install pydantic   (incluida con fastapi[standard])
#
# Este archivo NO requiere FastAPI — solo Pydantic.
# =============================================================================

try:
    from pydantic import (
        BaseModel,
        Field,
        field_validator,
        model_validator,
        EmailStr,
        HttpUrl,
        ConfigDict,
        ValidationError,
    )
    from pydantic import field_validator
    PYDANTIC_DISPONIBLE = True
except ImportError:
    PYDANTIC_DISPONIBLE = False
    print("Pydantic no instalado.")
    print("Instala con: pip install pydantic")
    print("Para EmailStr: pip install pydantic[email]")
    raise SystemExit(1)

from typing import Optional, Annotated
from datetime import datetime, date
from enum import Enum


# =============================================================================
# SECCIÓN 1: BaseModel básico
# =============================================================================

class Direccion(BaseModel):
    """
    Modelo anidado para la dirección.

    Por qué anidado: Pydantic soporta modelos dentro de modelos.
    La validación es recursiva — valida todos los niveles.
    """
    calle: str = Field(..., min_length=3)
    ciudad: str
    codigo_postal: str = Field(..., pattern=r"^\d{5}$")  # Solo 5 dígitos
    pais: str = Field(default="España")


class Usuario(BaseModel):
    """
    Modelo de usuario con validaciones básicas.

    Por qué BaseModel: definir la estructura una vez garantiza que
    todos los objetos Usuario tienen los mismos campos y tipos.
    Pydantic valida automáticamente en la construcción del objeto.
    """

    # Campos obligatorios (sin default)
    nombre: str = Field(..., min_length=2, max_length=50)
    apellido: str = Field(..., min_length=2, max_length=50)
    edad: int = Field(..., ge=0, le=150)

    # Campos opcionales (con default o Optional)
    email: Optional[str] = None
    activo: bool = True  # Valor por defecto

    # Modelo anidado
    direccion: Optional[Direccion] = None

    # Lista de strings
    roles: list[str] = Field(default_factory=list)

    # Fecha
    fecha_registro: datetime = Field(default_factory=datetime.now)

    # model_config reemplaza a class Config de Pydantic v1
    model_config = ConfigDict(
        # Permite crear el modelo desde objetos con atributos (ORM, dataclasses)
        from_attributes=True,
        # No permite campos extra no definidos en el modelo
        extra="forbid",
        # Documentación del modelo para el schema JSON
        json_schema_extra={
            "example": {
                "nombre": "Ana",
                "apellido": "García",
                "edad": 28,
                "email": "ana@ejemplo.com",
            }
        },
    )


def demo_basemodel_basico() -> None:
    """
    Demuestra la creación y validación de modelos Pydantic básicos.
    """
    print("\n--- BaseModel básico ---")

    # Creación exitosa
    usuario = Usuario(
        nombre="Carlos",
        apellido="Rodríguez",
        edad=35,
        email="carlos@ejemplo.com",
        direccion=Direccion(
            calle="Calle Gran Vía 10",
            ciudad="Madrid",
            codigo_postal="28013",
        ),
    )

    print(f"  Nombre: {usuario.nombre} {usuario.apellido}")
    print(f"  Edad: {usuario.edad}")
    print(f"  Ciudad: {usuario.direccion.ciudad}")
    print(f"  Roles: {usuario.roles}")

    # model_dump() convierte el modelo a dict
    datos = usuario.model_dump()
    print(f"  Dict keys: {list(datos.keys())}")

    # model_dump_json() convierte a JSON string
    json_str = usuario.model_dump_json(indent=2)
    print(f"  JSON (primeros 100 chars): {json_str[:100]}...")

    # Validación automática — Pydantic captura errores de tipo
    print("\n  Intentando crear usuario inválido...")
    try:
        invalido = Usuario(
            nombre="X",         # Muy corto (min_length=2)
            apellido="Test",
            edad=200,            # Supera el máximo (le=150)
        )
    except ValidationError as e:
        print(f"  Errores encontrados: {e.error_count()}")
        for error in e.errors():
            print(f"    Campo: {error['loc']} → {error['msg']}")


# =============================================================================
# SECCIÓN 2: Field() — validaciones avanzadas
# =============================================================================

class Producto(BaseModel):
    """
    Modelo de producto con todas las opciones de Field().
    """

    # str con restricciones de longitud
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=200,
        title="Nombre del producto",
        description="Nombre comercial del producto",
    )

    # str con expresión regular — el precio debe ser formato válido
    codigo_sku: str = Field(
        ...,
        pattern=r"^[A-Z]{3}-\d{6}$",  # Ej: LAP-123456
        description="Código SKU en formato ABC-123456",
    )

    # float con rango
    precio: float = Field(..., gt=0, le=999999.99)
    precio_costo: float = Field(..., gt=0)

    # int con múltiplo
    stock: int = Field(default=0, ge=0, multiple_of=1)

    # Campos calculados o derivados — se incluyen en serialización
    descuento_pct: float = Field(default=0.0, ge=0.0, le=100.0)

    @field_validator("nombre")
    @classmethod
    def nombre_no_puede_ser_solo_numeros(cls, v: str) -> str:
        """
        Validator de campo: se ejecuta después de la validación de tipo.

        @classmethod porque Pydantic v2 lo requiere así.
        Debe retornar el valor (posiblemente transformado) o lanzar ValueError.
        """
        if v.replace(" ", "").isdigit():
            raise ValueError("El nombre no puede ser solo números.")
        return v.strip().title()  # Normalizamos a Title Case


def demo_field_avanzado() -> None:
    """Demuestra validaciones avanzadas con Field."""
    print("\n--- Field() con validaciones avanzadas ---")

    try:
        producto = Producto(
            nombre="laptop gaming pro",
            codigo_sku="LAP-123456",
            precio=1299.99,
            precio_costo=800.00,
        )
        print(f"  Nombre normalizado: '{producto.nombre}'")
        print(f"  SKU: {producto.codigo_sku}")
        print(f"  Precio: {producto.precio}€")

    except ValidationError as e:
        print(f"  Error: {e}")

    # SKU inválido
    try:
        Producto(nombre="Test", codigo_sku="INVALIDO", precio=10, precio_costo=5)
    except ValidationError as e:
        print(f"\n  SKU inválido → {e.errors()[0]['msg']}")


# =============================================================================
# SECCIÓN 3: Enum en modelos Pydantic
# =============================================================================

class EstadoPedido(str, Enum):
    """
    Enum para el estado de un pedido.

    Por qué (str, Enum): al heredar de str, el valor del enum ES un string.
    Pydantic lo serializa como el string, no como el objeto Enum.
    Esto facilita la serialización JSON y la comparación.
    """
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    ENVIADO = "enviado"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"


class LineaPedido(BaseModel):
    """Línea individual de un pedido."""
    producto_id: int
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., gt=0)

    @property
    def subtotal(self) -> float:
        """Property calculada — no se almacena, se calcula al acceder."""
        return self.cantidad * self.precio_unitario


class Pedido(BaseModel):
    """
    Modelo de pedido con Enum, modelos anidados y validator cruzado.
    """
    id: Optional[int] = None
    cliente_email: str
    estado: EstadoPedido = EstadoPedido.PENDIENTE
    lineas: list[LineaPedido] = Field(default_factory=list, min_length=1)
    fecha_pedido: datetime = Field(default_factory=datetime.now)
    fecha_entrega_estimada: Optional[date] = None
    notas: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def validar_fecha_entrega(self) -> "Pedido":
        """
        Validator del modelo completo — se ejecuta después de todos los campos.
        mode="after": tiene acceso al objeto ya construido (self).
        mode="before": recibiría los datos crudos como dict.

        Aquí verificamos que la fecha de entrega sea futura si se proporciona.
        """
        if self.fecha_entrega_estimada:
            if self.fecha_entrega_estimada < date.today():
                raise ValueError("La fecha de entrega debe ser futura.")
        return self

    def total(self) -> float:
        """Calcula el total del pedido sumando todas las líneas."""
        return sum(linea.subtotal for linea in self.lineas)


def demo_enum_y_nested() -> None:
    """Demuestra Enum, modelos anidados y model_validator."""
    print("\n--- Enum y modelos anidados ---")

    from datetime import timedelta

    pedido = Pedido(
        cliente_email="cliente@ejemplo.com",
        estado=EstadoPedido.PROCESANDO,
        lineas=[
            LineaPedido(producto_id=1, cantidad=2, precio_unitario=89.99),
            LineaPedido(producto_id=3, cantidad=1, precio_unitario=449.99),
        ],
        fecha_entrega_estimada=date.today() + timedelta(days=5),
    )

    print(f"  Estado: {pedido.estado}")
    print(f"  Líneas: {len(pedido.lineas)}")
    print(f"  Total: {pedido.total():.2f}€")

    # Comparar con el valor string del enum
    print(f"  ¿Está procesando? {pedido.estado == 'procesando'}")

    # Serialización incluye el valor string del enum (no el objeto)
    datos = pedido.model_dump()
    print(f"  Estado en dict: {datos['estado']} (tipo: {type(datos['estado']).__name__})")


# =============================================================================
# SECCIÓN 4: model_config — configuración avanzada
# =============================================================================

class ConfiguracionAvanzada(BaseModel):
    """
    Demuestra opciones avanzadas de ConfigDict.
    """

    model_config = ConfigDict(
        # Permite campos extra (los incluye en el modelo)
        extra="ignore",          # "allow", "ignore" o "forbid"
        # Valida al asignar: mi_obj.campo = valor también se valida
        validate_assignment=True,
        # Serialización: usa el alias en lugar del nombre Python
        populate_by_name=True,
        # Ignora case en los nombres de campos
        str_strip_whitespace=True,  # Elimina espacios en strings automáticamente
    )

    # alias: nombre alternativo para serialización/deserialización
    nombre_completo: str = Field(..., alias="fullName")
    fecha_creacion: datetime = Field(
        default_factory=datetime.now,
        alias="createdAt",
    )


def demo_config_avanzada() -> None:
    """Demuestra ConfigDict con aliases."""
    print("\n--- ConfigDict y aliases ---")

    # Podemos usar tanto el nombre Python como el alias
    obj = ConfiguracionAvanzada(**{"fullName": "María López"})
    print(f"  nombre_completo: {obj.nombre_completo}")

    # Serializar con aliases
    con_alias = obj.model_dump(by_alias=True)
    sin_alias = obj.model_dump(by_alias=False)
    print(f"  Con alias: {list(con_alias.keys())}")
    print(f"  Sin alias: {list(sin_alias.keys())}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PYDANTIC v2 — VALIDACIÓN DE DATOS EN PROFUNDIDAD")
    print("=" * 60)

    demo_basemodel_basico()
    demo_field_avanzado()
    demo_enum_y_nested()
    demo_config_avanzada()

    print("\n" + "=" * 60)
    print("Resumen de Pydantic v2:")
    print("  BaseModel      → Define estructura y tipos")
    print("  Field()        → Validaciones: min/max, pattern, gt/ge/lt/le")
    print("  @field_validator → Lógica de validación personalizada por campo")
    print("  @model_validator → Validación cruzada entre campos")
    print("  ConfigDict     → Configuración del modelo (alias, extra, etc.)")
    print("  model_dump()   → Modelo → dict")
    print("  model_dump_json() → Modelo → JSON string")
    print("  ValidationError → Contiene todos los errores de validación")
    print("=" * 60)
