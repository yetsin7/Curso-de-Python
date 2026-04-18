# =============================================================================
# CAPÍTULO 21 — FastAPI
# Archivo 03: CRUD completo en memoria
# =============================================================================
# CRUD = Create, Read, Update, Delete — las 4 operaciones básicas.
# Este ejemplo implementa un gestor de tareas (To-Do) completo
# usando almacenamiento en memoria (sin base de datos real).
#
# Demuestra:
# - Status codes correctos para cada operación
# - HTTPException con mensajes descriptivos
# - Path y Query parameters
# - Response body vs sin body (204)
# - Listado con filtros y paginación
#
# Ejecutar: uvicorn 03_crud_completo:app --reload
# =============================================================================

try:
    from fastapi import FastAPI, HTTPException, Query, Path, status, Response
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_DISPONIBLE = True
except ImportError:
    FASTAPI_DISPONIBLE = False
    print('FastAPI no instalado. Instala: pip install "fastapi[standard]"')

from typing import Optional
from datetime import datetime
from enum import Enum


# =============================================================================
# MODELOS
# =============================================================================

class PrioridadTarea(str, Enum):
    """Niveles de prioridad de una tarea."""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class TareaCreate(BaseModel):
    """
    Schema para CREAR una tarea.
    El cliente envía este body en el POST.
    """
    titulo: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Título descriptivo de la tarea",
        examples=["Completar el capítulo de FastAPI"],
    )
    descripcion: Optional[str] = Field(
        None,
        max_length=1000,
        description="Descripción detallada de la tarea",
    )
    prioridad: PrioridadTarea = Field(
        default=PrioridadTarea.MEDIA,
        description="Nivel de urgencia de la tarea",
    )
    etiquetas: list[str] = Field(
        default_factory=list,
        description="Etiquetas para clasificar la tarea",
    )
    fecha_limite: Optional[datetime] = Field(
        None,
        description="Fecha y hora límite (ISO 8601)",
    )


class TareaUpdate(BaseModel):
    """
    Schema para ACTUALIZAR parcialmente una tarea (PATCH).
    Todos los campos son opcionales — el cliente envía solo lo que cambia.
    """
    titulo: Optional[str] = Field(None, min_length=3, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=1000)
    completada: Optional[bool] = None
    prioridad: Optional[PrioridadTarea] = None
    etiquetas: Optional[list[str]] = None
    fecha_limite: Optional[datetime] = None


class TareaResponse(BaseModel):
    """
    Schema de respuesta — lo que la API devuelve al cliente.
    Incluye campos generados por el servidor.
    """
    id: int
    titulo: str
    descripcion: Optional[str]
    completada: bool
    prioridad: PrioridadTarea
    etiquetas: list[str]
    fecha_limite: Optional[datetime]
    creada_en: datetime
    actualizada_en: datetime

    model_config = {"from_attributes": True}


class EstadisticasTareas(BaseModel):
    """Schema para el endpoint de estadísticas."""
    total: int
    completadas: int
    pendientes: int
    por_prioridad: dict[str, int]


# =============================================================================
# ALMACENAMIENTO EN MEMORIA
# =============================================================================

# Simula la base de datos con un dict: id → tarea
# En un proyecto real esto sería SQLAlchemy + PostgreSQL (ver archivo 04)
_tareas_db: dict[int, dict] = {}
_contador_id: int = 0


def _siguiente_id() -> int:
    """Genera el siguiente ID autoincremental."""
    global _contador_id
    _contador_id += 1
    return _contador_id


def _tarea_o_404(tarea_id: int) -> dict:
    """
    Helper que retorna la tarea o lanza 404 si no existe.

    Por qué extraer esto a función: evita repetir el mismo try/except
    en cada endpoint. DRY (Don't Repeat Yourself).
    """
    if tarea_id not in _tareas_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con ID {tarea_id} no encontrada.",
        )
    return _tareas_db[tarea_id]


# =============================================================================
# APLICACIÓN FASTAPI
# =============================================================================

app = FastAPI(
    title="Gestor de Tareas API",
    description="CRUD completo de tareas — ejemplo educativo de FastAPI",
    version="1.0.0",
)

# Cargamos algunas tareas de ejemplo al arrancar
@app.on_event("startup")
def cargar_datos_ejemplo():
    """
    Evento de startup: se ejecuta cuando la app arranca.
    Insertamos datos de ejemplo para tener algo en la API.
    """
    tareas_ejemplo = [
        {"titulo": "Leer documentación de FastAPI", "prioridad": "alta"},
        {"titulo": "Practicar Pydantic", "prioridad": "media"},
        {"titulo": "Hacer ejercicios del libro", "prioridad": "alta"},
    ]
    for datos in tareas_ejemplo:
        tarea_id = _siguiente_id()
        ahora = datetime.now()
        _tareas_db[tarea_id] = {
            "id": tarea_id,
            "titulo": datos["titulo"],
            "descripcion": None,
            "completada": False,
            "prioridad": datos["prioridad"],
            "etiquetas": [],
            "fecha_limite": None,
            "creada_en": ahora,
            "actualizada_en": ahora,
        }


# =============================================================================
# ENDPOINTS CRUD
# =============================================================================

@app.get(
    "/tareas",
    response_model=list[TareaResponse],
    summary="Listar tareas",
    tags=["Tareas"],
)
def listar_tareas(
    completada: Optional[bool] = Query(None, description="Filtrar por estado de completado"),
    prioridad: Optional[PrioridadTarea] = Query(None, description="Filtrar por prioridad"),
    busqueda: Optional[str] = Query(None, min_length=2, description="Buscar en título"),
    skip: int = Query(0, ge=0, description="Saltar N registros"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados"),
    orden: str = Query("creada_en", description="Campo por el que ordenar"),
):
    """
    Lista todas las tareas con soporte de filtros, búsqueda y paginación.

    Ejemplos de uso:
    - `GET /tareas` — todas las tareas
    - `GET /tareas?completada=false` — solo pendientes
    - `GET /tareas?prioridad=alta&limit=5` — 5 de alta prioridad
    - `GET /tareas?busqueda=fastapi` — busca en el título
    """
    tareas = list(_tareas_db.values())

    # Aplicar filtros
    if completada is not None:
        tareas = [t for t in tareas if t["completada"] == completada]

    if prioridad is not None:
        tareas = [t for t in tareas if t["prioridad"] == prioridad.value]

    if busqueda:
        busqueda_lower = busqueda.lower()
        tareas = [t for t in tareas if busqueda_lower in t["titulo"].lower()]

    # Ordenar — validamos que el campo exista para evitar errores
    campos_validos = {"creada_en", "titulo", "prioridad", "actualizada_en"}
    if orden in campos_validos:
        tareas = sorted(tareas, key=lambda t: str(t.get(orden, "")))

    # Paginación
    return tareas[skip : skip + limit]


@app.get(
    "/tareas/estadisticas",
    response_model=EstadisticasTareas,
    summary="Estadísticas globales",
    tags=["Tareas"],
)
def obtener_estadisticas():
    """
    Retorna estadísticas agregadas de las tareas.

    IMPORTANTE: este endpoint debe estar ANTES de /tareas/{tarea_id}
    en el código, o FastAPI intentará interpretar "estadisticas" como
    un entero para tarea_id y fallará con 422.
    """
    tareas = list(_tareas_db.values())

    por_prioridad = {}
    for prioridad in PrioridadTarea:
        cantidad = sum(1 for t in tareas if t["prioridad"] == prioridad.value)
        por_prioridad[prioridad.value] = cantidad

    return EstadisticasTareas(
        total=len(tareas),
        completadas=sum(1 for t in tareas if t["completada"]),
        pendientes=sum(1 for t in tareas if not t["completada"]),
        por_prioridad=por_prioridad,
    )


@app.get(
    "/tareas/{tarea_id}",
    response_model=TareaResponse,
    summary="Obtener tarea por ID",
    tags=["Tareas"],
)
def obtener_tarea(
    tarea_id: int = Path(..., gt=0, description="ID de la tarea"),
):
    """Retorna una tarea específica. 404 si no existe."""
    return _tarea_o_404(tarea_id)


@app.post(
    "/tareas",
    response_model=TareaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear tarea",
    tags=["Tareas"],
)
def crear_tarea(tarea: TareaCreate):
    """
    Crea una nueva tarea.

    Retorna 201 Created con el objeto creado, incluyendo el ID asignado.
    """
    tarea_id = _siguiente_id()
    ahora = datetime.now()

    nueva_tarea = {
        "id": tarea_id,
        "completada": False,            # Toda tarea nueva empieza sin completar
        "creada_en": ahora,
        "actualizada_en": ahora,
        **tarea.model_dump(),           # Resto de campos del schema
    }

    _tareas_db[tarea_id] = nueva_tarea
    return nueva_tarea


@app.put(
    "/tareas/{tarea_id}",
    response_model=TareaResponse,
    summary="Reemplazar tarea completa",
    tags=["Tareas"],
)
def reemplazar_tarea(
    tarea_id: int = Path(..., gt=0),
    tarea: TareaCreate = ...,
):
    """
    Reemplaza todos los campos de una tarea (PUT).
    El estado 'completada' se resetea a False.
    """
    tarea_existente = _tarea_o_404(tarea_id)

    tarea_existente.update({
        **tarea.model_dump(),
        "completada": False,
        "actualizada_en": datetime.now(),
    })

    return tarea_existente


@app.patch(
    "/tareas/{tarea_id}",
    response_model=TareaResponse,
    summary="Actualizar campos específicos",
    tags=["Tareas"],
)
def actualizar_tarea(
    tarea_id: int = Path(..., gt=0),
    cambios: TareaUpdate = ...,
):
    """
    Actualiza solo los campos enviados (PATCH).

    Ideal para operaciones como:
    - Marcar como completada: `{"completada": true}`
    - Cambiar prioridad: `{"prioridad": "urgente"}`
    """
    tarea = _tarea_o_404(tarea_id)

    # exclude_unset=True: solo incluye campos que el cliente envió explícitamente
    # Esto evita sobreescribir campos con None cuando no se envían
    datos_a_actualizar = cambios.model_dump(exclude_unset=True)

    if not datos_a_actualizar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar.",
        )

    tarea.update(datos_a_actualizar)
    tarea["actualizada_en"] = datetime.now()

    return tarea


@app.delete(
    "/tareas/{tarea_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar tarea",
    tags=["Tareas"],
)
def eliminar_tarea(
    tarea_id: int = Path(..., gt=0),
):
    """
    Elimina una tarea permanentemente.

    Retorna 204 No Content — sin body en la respuesta.
    Esto es el estándar HTTP para DELETE exitoso.
    """
    _tarea_o_404(tarea_id)
    del _tareas_db[tarea_id]


@app.delete(
    "/tareas",
    status_code=status.HTTP_200_OK,
    summary="Eliminar tareas completadas",
    tags=["Tareas"],
)
def eliminar_completadas():
    """
    Elimina todas las tareas completadas.
    Retorna cuántas tareas se eliminaron.
    """
    ids_completadas = [
        tarea_id for tarea_id, t in _tareas_db.items() if t["completada"]
    ]

    for tarea_id in ids_completadas:
        del _tareas_db[tarea_id]

    return {
        "eliminadas": len(ids_completadas),
        "mensaje": f"Se eliminaron {len(ids_completadas)} tareas completadas.",
    }


# =============================================================================
# EJECUTAR
# =============================================================================

if __name__ == "__main__":
    if not FASTAPI_DISPONIBLE:
        print('Instala FastAPI con: pip install "fastapi[standard]"')
    else:
        print("Iniciando Gestor de Tareas API...")
        print("Docs: http://127.0.0.1:8000/docs")
        import uvicorn
        uvicorn.run("03_crud_completo:app", host="127.0.0.1", port=8000, reload=True)
