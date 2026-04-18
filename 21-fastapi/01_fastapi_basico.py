# =============================================================================
# CAPÍTULO 21 — FastAPI
# Archivo 01: FastAPI básico — rutas, parámetros y response models
# =============================================================================
# Este archivo muestra los fundamentos de FastAPI:
# - Crear una app y definir rutas HTTP
# - Path parameters, query parameters y request body
# - Response models con Pydantic
# - Documentación automática
#
# Instalación: pip install "fastapi[standard]"
#
# Para ejecutar:
#   uvicorn 01_fastapi_basico:app --reload
#
# Luego visita:
#   http://127.0.0.1:8000          → Página principal
#   http://127.0.0.1:8000/docs     → Swagger UI interactivo
#   http://127.0.0.1:8000/redoc    → ReDoc documentación
# =============================================================================

try:
    from fastapi import FastAPI, HTTPException, Query, Path, status
    from pydantic import BaseModel, Field
    from typing import Optional
    import uvicorn
    FASTAPI_DISPONIBLE = True
except ImportError:
    FASTAPI_DISPONIBLE = False
    print("FastAPI no instalado.")
    print('Instala con: pip install "fastapi[standard]"')
    print()

from datetime import datetime


# =============================================================================
# CREAR LA APLICACIÓN FASTAPI
# =============================================================================

# FastAPI() crea la instancia principal de la aplicación
# Los parámetros son metadata que aparece en la documentación automática
app = FastAPI(
    title="API del Libro de Python",
    description="""
    API de ejemplo para aprender FastAPI.

    ## Características demostradas
    - Rutas GET, POST, PUT, PATCH, DELETE
    - Path parameters, query parameters
    - Request body con Pydantic
    - Response models y status codes
    - Documentación automática
    """,
    version="1.0.0",
    # contact y license son metadata para la documentación
    contact={
        "name": "Libro de Python",
        "url": "https://github.com/tu-usuario/libro-python",
    },
)


# =============================================================================
# MODELOS PYDANTIC — definen la estructura de los datos
# =============================================================================

class ProductoBase(BaseModel):
    """
    Modelo base con los campos comunes de un producto.

    Por qué clase base: reutilizamos campos comunes entre
    ProductoCreate (sin ID), ProductoUpdate (campos opcionales)
    y ProductoResponse (con ID y timestamps).
    """
    nombre: str = Field(
        ...,                    # "..." significa que es OBLIGATORIO
        min_length=2,
        max_length=100,
        description="Nombre del producto",
        examples=["Laptop HP"],
    )
    precio: float = Field(
        ...,
        gt=0,                   # greater than 0 — precio debe ser positivo
        description="Precio en euros",
    )
    stock: int = Field(
        default=0,
        ge=0,                   # greater or equal 0 — no puede ser negativo
        description="Unidades disponibles",
    )
    categoria: str = Field(default="general", description="Categoría del producto")


class ProductoCreate(ProductoBase):
    """Schema para CREAR un producto (enviado por el cliente en el body)."""
    pass  # Hereda todos los campos de ProductoBase


class ProductoUpdate(BaseModel):
    """
    Schema para ACTUALIZAR un producto (PATCH — todos los campos opcionales).

    Por qué Optional: en PATCH el cliente puede enviar solo los campos
    que quiere cambiar — no tiene que enviar todos.
    """
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    precio: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    categoria: Optional[str] = None


class ProductoResponse(ProductoBase):
    """
    Schema de respuesta — lo que la API devuelve al cliente.

    Incluye campos adicionales que el servidor genera: ID y timestamps.
    Por qué separar request/response: el cliente no envía el ID ni las fechas.
    """
    id: int
    creado_en: datetime

    # model_config permite configuración del modelo
    # from_attributes=True: el modelo puede crearse desde un ORM object
    model_config = {"from_attributes": True}


# Base de datos simulada en memoria — lista de dicts
# En producción usaríamos SQLAlchemy con una DB real (ver archivo 04)
_productos_db: dict[int, dict] = {
    1: {"id": 1, "nombre": "Laptop HP", "precio": 899.99, "stock": 15,
        "categoria": "electrónica", "creado_en": datetime(2024, 1, 15)},
    2: {"id": 2, "nombre": "Teclado mecánico", "precio": 89.99, "stock": 30,
        "categoria": "periféricos", "creado_en": datetime(2024, 2, 1)},
    3: {"id": 3, "nombre": "Monitor 4K", "precio": 449.99, "stock": 8,
        "categoria": "electrónica", "creado_en": datetime(2024, 3, 10)},
}
_proximo_id = 4


# =============================================================================
# RUTAS — cada función decorada con @app.get/post/put/etc es un endpoint
# =============================================================================

@app.get(
    "/",
    summary="Página de bienvenida",
    tags=["General"],   # tags agrupa endpoints en la documentación
)
def raiz():
    """
    Endpoint raíz de la API.

    Por qué retornar un dict: FastAPI convierte automáticamente el dict a JSON.
    También puedes retornar Pydantic models — FastAPI los serializa.
    """
    return {
        "mensaje": "API del Libro de Python funcionando",
        "version": "1.0.0",
        "documentacion": "/docs",
    }


@app.get(
    "/productos",
    response_model=list[ProductoResponse],  # Tipo de respuesta para docs y validación
    summary="Listar productos",
    tags=["Productos"],
)
def listar_productos(
    # Query parameters: ?skip=0&limit=10&categoria=electrónica
    skip: int = Query(default=0, ge=0, description="Productos a saltar (paginación)"),
    limit: int = Query(default=10, ge=1, le=100, description="Máximo de productos a retornar"),
    categoria: Optional[str] = Query(default=None, description="Filtrar por categoría"),
    busqueda: Optional[str] = Query(default=None, description="Buscar por nombre"),
):
    """
    Retorna la lista de productos con soporte para paginación y filtros.

    Query parameters son opcionales y se pasan en la URL:
    - `?skip=10&limit=5` para paginación
    - `?categoria=electrónica` para filtrar
    - `?busqueda=laptop` para buscar por nombre
    """
    productos = list(_productos_db.values())

    # Aplicamos filtros si se proporcionaron
    if categoria:
        productos = [p for p in productos if p["categoria"].lower() == categoria.lower()]

    if busqueda:
        productos = [p for p in productos if busqueda.lower() in p["nombre"].lower()]

    # Paginación — slice del resultado
    return productos[skip : skip + limit]


@app.get(
    "/productos/{producto_id}",
    response_model=ProductoResponse,
    summary="Obtener producto por ID",
    tags=["Productos"],
)
def obtener_producto(
    # Path parameter: parte de la URL capturada como variable
    # Path() permite validar y documentar parámetros de ruta
    producto_id: int = Path(
        ...,            # Obligatorio
        gt=0,           # El ID debe ser positivo
        description="ID único del producto",
    ),
):
    """
    Retorna un producto específico por su ID.

    Si el producto no existe, retorna **404 Not Found** automáticamente.
    """
    if producto_id not in _productos_db:
        # HTTPException genera la respuesta de error correcta
        # detail es el mensaje que aparece en la respuesta JSON
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {producto_id} no encontrado.",
        )
    return _productos_db[producto_id]


@app.post(
    "/productos",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,  # 201 Created para nuevos recursos
    summary="Crear producto",
    tags=["Productos"],
)
def crear_producto(producto: ProductoCreate):
    """
    Crea un nuevo producto.

    El body de la petición debe ser JSON que cumpla el schema ProductoCreate.
    FastAPI valida automáticamente los datos y devuelve 422 si hay errores.

    Body de ejemplo:
    ```json
    {
        "nombre": "Ratón inalámbrico",
        "precio": 29.99,
        "stock": 50,
        "categoria": "periféricos"
    }
    ```
    """
    global _proximo_id

    nuevo_producto = {
        "id": _proximo_id,
        **producto.model_dump(),  # model_dump() convierte Pydantic → dict
        "creado_en": datetime.now(),
    }

    _productos_db[_proximo_id] = nuevo_producto
    _proximo_id += 1

    return nuevo_producto


@app.put(
    "/productos/{producto_id}",
    response_model=ProductoResponse,
    summary="Reemplazar producto completo",
    tags=["Productos"],
)
def reemplazar_producto(producto_id: int, producto: ProductoCreate):
    """
    Reemplaza TODOS los campos de un producto (PUT — reemplazo completo).

    A diferencia de PATCH, aquí el cliente debe enviar todos los campos.
    """
    if producto_id not in _productos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto {producto_id} no encontrado.",
        )

    # Reemplazamos el producto completo — mantenemos ID y fecha de creación
    producto_existente = _productos_db[producto_id]
    _productos_db[producto_id] = {
        "id": producto_id,
        **producto.model_dump(),
        "creado_en": producto_existente["creado_en"],  # Preservamos la fecha original
    }

    return _productos_db[producto_id]


@app.patch(
    "/productos/{producto_id}",
    response_model=ProductoResponse,
    summary="Actualizar campos específicos",
    tags=["Productos"],
)
def actualizar_producto(producto_id: int, producto: ProductoUpdate):
    """
    Actualiza SOLO los campos enviados (PATCH — actualización parcial).

    Solo los campos incluidos en el body se modifican.
    Los campos no enviados mantienen su valor actual.
    """
    if producto_id not in _productos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto {producto_id} no encontrado.",
        )

    producto_actual = _productos_db[producto_id].copy()

    # model_dump(exclude_unset=True): solo los campos que el cliente envió
    # Evita sobreescribir con None campos no incluidos en el body
    cambios = producto.model_dump(exclude_unset=True)
    producto_actual.update(cambios)

    _productos_db[producto_id] = producto_actual
    return producto_actual


@app.delete(
    "/productos/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,  # 204 No Content — sin body en respuesta
    summary="Eliminar producto",
    tags=["Productos"],
)
def eliminar_producto(producto_id: int):
    """
    Elimina un producto. Retorna 204 No Content si fue exitoso.
    """
    if producto_id not in _productos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto {producto_id} no encontrado.",
        )

    del _productos_db[producto_id]
    # Al retornar None con status 204, FastAPI no incluye body en la respuesta


# =============================================================================
# EJECUTAR LA APLICACIÓN DIRECTAMENTE
# =============================================================================

if __name__ == "__main__":
    if not FASTAPI_DISPONIBLE:
        print('Instala FastAPI con: pip install "fastapi[standard]"')
    else:
        print("Iniciando servidor FastAPI...")
        print("Documentación: http://127.0.0.1:8000/docs")
        # uvicorn.run inicia el servidor ASGI
        # reload=True reinicia al detectar cambios (solo desarrollo)
        uvicorn.run(
            "01_fastapi_basico:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
        )
