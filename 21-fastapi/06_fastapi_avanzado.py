# =============================================================================
# CAPÍTULO 21 — FastAPI
# Archivo 06: FastAPI Avanzado
# =============================================================================
# Temas avanzados que completan el conocimiento de FastAPI:
# - Background Tasks: tareas en segundo plano sin bloquear la respuesta
# - Middleware: procesamiento de cada petición/respuesta
# - CORS: permitir peticiones desde otros dominios
# - File Uploads: recibir archivos desde el cliente
# - WebSockets: comunicación bidireccional en tiempo real (conceptual)
# - Testing: cómo probar la API con TestClient
#
# Instalación: pip install "fastapi[standard]" python-multipart
# =============================================================================

try:
    from fastapi import (
        FastAPI, BackgroundTasks, File, UploadFile, Form,
        Request, Response, HTTPException, WebSocket,
        WebSocketDisconnect, status,
    )
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    from fastapi.responses import JSONResponse, FileResponse
    FASTAPI_DISPONIBLE = True
except ImportError:
    FASTAPI_DISPONIBLE = False
    print('FastAPI no instalado. Instala: pip install "fastapi[standard]"')

from pydantic import BaseModel, EmailStr
from typing import Optional
from contextlib import asynccontextmanager
import time
import logging
import os
import tempfile


# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("fastapi_avanzado")


# =============================================================================
# LIFESPAN — inicialización y limpieza
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Código de arranque y apagado de la aplicación.
    Aquí inicializamos: conexiones a DB, cache, configuraciones globales.
    """
    logger.info("Aplicación arrancando — inicializando recursos...")

    # Simulamos inicialización de un pool de conexiones
    app.state.inicio = time.time()

    yield  # La app está corriendo

    duracion = time.time() - app.state.inicio
    logger.info(f"Aplicación apagándose — estuvo corriendo {duracion:.1f}s")


# =============================================================================
# APLICACIÓN
# =============================================================================

app = FastAPI(
    title="FastAPI Avanzado",
    description="Background Tasks, Middleware, CORS, File Uploads, WebSockets",
    version="1.0.0",
    lifespan=lifespan,
)


# =============================================================================
# MIDDLEWARE
# =============================================================================

# CORS — Cross-Origin Resource Sharing
# Por qué: los navegadores bloquean peticiones de un dominio a otro por seguridad.
# CORS le dice al navegador qué orígenes están permitidos.
app.add_middleware(
    CORSMiddleware,
    # origins: lista de dominios que pueden hacer peticiones a esta API
    # En desarrollo podemos usar ["*"] para permitir todos
    # En producción especifica solo los dominios reales: ["https://tuapp.com"]
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,   # Permite cookies en peticiones cross-origin
    allow_methods=["*"],       # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],       # Authorization, Content-Type, etc.
)

# GZip — comprime respuestas grandes automáticamente
# Reduce el ancho de banda para respuestas JSON grandes
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Middleware personalizado — intercepta todas las peticiones
@app.middleware("http")
async def middleware_logging_y_tiempo(request: Request, call_next):
    """
    Middleware personalizado que:
    1. Registra cada petición recibida
    2. Mide el tiempo de procesamiento
    3. Añade el tiempo como header en la respuesta

    Por qué middleware y no decorador en cada endpoint: el middleware
    se ejecuta para TODAS las peticiones automáticamente — DRY.

    Args:
        request: La petición HTTP recibida.
        call_next: Función que pasa la petición al siguiente middleware o endpoint.

    Returns:
        La respuesta HTTP con headers adicionales.
    """
    inicio = time.time()

    # Logueamos la petición entrante
    logger.info(f"→ {request.method} {request.url.path}")

    # call_next ejecuta el endpoint y obtiene la respuesta
    respuesta = await call_next(request)

    # Calculamos el tiempo total de procesamiento
    duracion_ms = (time.time() - inicio) * 1000

    # Añadimos el tiempo como header de respuesta personalizado
    respuesta.headers["X-Process-Time"] = f"{duracion_ms:.2f}ms"

    logger.info(
        f"← {respuesta.status_code} en {duracion_ms:.2f}ms"
    )

    return respuesta


# =============================================================================
# SECCIÓN 1: BACKGROUND TASKS
# =============================================================================

# Simulamos una base de datos de emails enviados
_emails_enviados: list[dict] = []


def tarea_enviar_email(destinatario: str, asunto: str, cuerpo: str) -> None:
    """
    Función que simula el envío de un email.

    Por qué background task: enviar emails es lento (conexión SMTP, etc.).
    Si lo hacemos en el endpoint, el cliente espera innecesariamente.
    Con BackgroundTasks, la respuesta HTTP se envía de inmediato
    y el email se envía después en segundo plano.

    Args:
        destinatario: Email del destinatario.
        asunto: Asunto del email.
        cuerpo: Contenido del email.
    """
    # Simulamos el tiempo que tarda enviar un email
    logger.info(f"Enviando email a {destinatario}...")
    time.sleep(2)  # Simula latencia del servidor SMTP

    _emails_enviados.append({
        "destinatario": destinatario,
        "asunto": asunto,
        "enviado_en": time.strftime("%Y-%m-%d %H:%M:%S"),
    })

    logger.info(f"Email enviado a {destinatario}")


def tarea_generar_reporte(usuario_id: int) -> None:
    """
    Genera un reporte pesado en segundo plano.
    El cliente no espera — la respuesta ya fue enviada.
    """
    logger.info(f"Generando reporte para usuario {usuario_id}...")
    time.sleep(5)  # Simula procesamiento pesado
    logger.info(f"Reporte de usuario {usuario_id} completado.")


class ContactoRequest(BaseModel):
    """Schema para el formulario de contacto."""
    nombre: str
    email: str
    mensaje: str


@app.post(
    "/contacto",
    status_code=status.HTTP_202_ACCEPTED,  # 202 Accepted: recibido, procesando en bg
    tags=["Background Tasks"],
)
async def formulario_contacto(
    contacto: ContactoRequest,
    background_tasks: BackgroundTasks,  # FastAPI inyecta esto automáticamente
):
    """
    Procesa el formulario de contacto y envía email en segundo plano.

    Retorna 202 Accepted inmediatamente — no espera el envío del email.
    El cliente recibe la respuesta en ~0ms en lugar de ~2000ms.
    """
    # Añadimos la tarea al queue de background tasks
    # La tarea se ejecuta DESPUÉS de enviar la respuesta HTTP
    background_tasks.add_task(
        tarea_enviar_email,                    # La función a ejecutar
        contacto.email,                         # Primer argumento
        f"Mensaje de {contacto.nombre}",        # Segundo argumento
        contacto.mensaje,                       # Tercer argumento
    )

    background_tasks.add_task(
        tarea_generar_reporte,
        usuario_id=1,
    )

    return {
        "mensaje": "Formulario recibido. Te contactaremos pronto.",
        "email": contacto.email,
    }


@app.get("/emails-enviados", tags=["Background Tasks"])
def ver_emails_enviados():
    """Muestra los emails enviados en background (para verificar que funcionó)."""
    return {
        "total": len(_emails_enviados),
        "emails": _emails_enviados,
    }


# =============================================================================
# SECCIÓN 2: FILE UPLOADS
# =============================================================================

@app.post(
    "/archivos/subir",
    tags=["Archivos"],
    summary="Subir un archivo",
)
async def subir_archivo(
    # UploadFile: el archivo subido — contiene metadata y el contenido
    archivo: UploadFile = File(..., description="Archivo a subir"),
    descripcion: Optional[str] = Form(None, description="Descripción del archivo"),
):
    """
    Recibe un archivo subido desde el cliente.

    Por qué python-multipart: los archivos se envían como multipart/form-data.
    Requiere `pip install python-multipart`.

    UploadFile tiene:
    - .filename: nombre original del archivo
    - .content_type: MIME type (image/jpeg, text/csv, etc.)
    - .size: tamaño en bytes (si está disponible)
    - .read(): lee el contenido completo (await en async)
    - .file: objeto tipo archivo para streaming
    """
    # Validación del tipo de archivo
    tipos_permitidos = {"image/jpeg", "image/png", "image/webp", "text/plain", "application/pdf"}
    if archivo.content_type not in tipos_permitidos:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no permitido: {archivo.content_type}",
        )

    # Limitamos el tamaño a 5MB
    MAX_SIZE = 5 * 1024 * 1024  # 5MB en bytes

    # Leemos el contenido del archivo
    contenido = await archivo.read()

    if len(contenido) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el límite de {MAX_SIZE // 1024 // 1024}MB.",
        )

    # En producción guardaríamos en S3, GCS, o disco con ruta configurada
    # Aquí solo retornamos la información
    return {
        "nombre_archivo": archivo.filename,
        "tipo": archivo.content_type,
        "tamaño_bytes": len(contenido),
        "tamaño_kb": round(len(contenido) / 1024, 2),
        "descripcion": descripcion,
        "mensaje": "Archivo recibido correctamente.",
    }


@app.post(
    "/archivos/subir-multiples",
    tags=["Archivos"],
    summary="Subir múltiples archivos",
)
async def subir_multiples(
    archivos: list[UploadFile] = File(..., description="Lista de archivos"),
):
    """Recibe múltiples archivos en una sola petición."""
    resultados = []
    for archivo in archivos:
        contenido = await archivo.read()
        resultados.append({
            "nombre": archivo.filename,
            "tipo": archivo.content_type,
            "tamaño_kb": round(len(contenido) / 1024, 2),
        })

    return {
        "archivos_recibidos": len(resultados),
        "archivos": resultados,
    }


# =============================================================================
# SECCIÓN 3: WEBSOCKETS (comunicación en tiempo real)
# =============================================================================

# Gestión de conexiones WebSocket activas
class GestorConexiones:
    """
    Gestiona las conexiones WebSocket activas.

    Por qué una clase: necesitamos mantener estado (lista de conexiones)
    y operaciones comunes (conectar, desconectar, broadcast).
    """

    def __init__(self):
        self.conexiones_activas: list[WebSocket] = []

    async def conectar(self, websocket: WebSocket) -> None:
        """Acepta y registra una nueva conexión."""
        await websocket.accept()
        self.conexiones_activas.append(websocket)
        logger.info(f"WebSocket conectado. Total: {len(self.conexiones_activas)}")

    def desconectar(self, websocket: WebSocket) -> None:
        """Elimina una conexión al cerrarse."""
        self.conexiones_activas.remove(websocket)
        logger.info(f"WebSocket desconectado. Total: {len(self.conexiones_activas)}")

    async def enviar_a_todos(self, mensaje: str) -> None:
        """Envía un mensaje a TODAS las conexiones activas (broadcast)."""
        for conexion in self.conexiones_activas:
            try:
                await conexion.send_text(mensaje)
            except Exception:
                # Si falla, la conexión probablemente ya se cerró
                pass


gestor = GestorConexiones()


@app.websocket("/ws/chat/{usuario_id}")
async def websocket_chat(websocket: WebSocket, usuario_id: str):
    """
    Endpoint WebSocket para chat en tiempo real.

    Por qué WebSocket: HTTP es request/response — el servidor no puede
    enviar mensajes al cliente sin que el cliente los pida.
    WebSocket abre un canal bidireccional permanente.

    Para conectar desde JavaScript:
        const ws = new WebSocket("ws://localhost:8000/ws/chat/ana");
        ws.onmessage = (event) => console.log(event.data);
        ws.send("Hola a todos!");

    Args:
        websocket: La conexión WebSocket.
        usuario_id: Identificador del usuario conectado.
    """
    await gestor.conectar(websocket)

    # Notificamos a todos que el usuario se conectó
    await gestor.enviar_a_todos(f"[Sistema] {usuario_id} se conectó al chat.")

    try:
        while True:
            # Esperamos un mensaje del cliente (bloquea hasta recibirlo)
            mensaje = await websocket.receive_text()

            # Formateamos y hacemos broadcast a todos
            mensaje_formateado = f"[{usuario_id}]: {mensaje}"
            await gestor.enviar_a_todos(mensaje_formateado)

    except WebSocketDisconnect:
        # Se lanza cuando el cliente cierra la conexión
        gestor.desconectar(websocket)
        await gestor.enviar_a_todos(f"[Sistema] {usuario_id} se desconectó.")


@app.get("/ws/info", tags=["WebSockets"])
def info_websocket():
    """Información sobre las conexiones WebSocket activas."""
    return {
        "conexiones_activas": len(gestor.conexiones_activas),
        "endpoint": "ws://localhost:8000/ws/chat/{usuario_id}",
        "instrucciones": "Conecta con un cliente WebSocket para probar el chat en tiempo real.",
    }


# =============================================================================
# SECCIÓN 4: TESTING con TestClient
# =============================================================================

CODIGO_TESTING = '''
# ============================================================
# test_api.py — Tests con TestClient de FastAPI
# ============================================================
# TestClient usa requests internamente para hacer peticiones
# a la API sin necesidad de un servidor real en ejecución.
# Es sincrónico aunque la app sea async.
#
# Instalación: pip install pytest httpx
# Ejecutar: pytest test_api.py -v
# ============================================================

import pytest
from fastapi.testclient import TestClient
from 06_fastapi_avanzado import app  # Importamos la app

# TestClient crea un cliente HTTP que apunta a nuestra app
client = TestClient(app)


def test_raiz():
    """Prueba que la ruta raíz responde correctamente."""
    respuesta = client.get("/")
    # TestClient hace disponible status_code, json(), headers, etc.
    assert respuesta.status_code == 200


def test_contacto_acepta_form():
    """Prueba el endpoint de contacto con datos válidos."""
    respuesta = client.post("/contacto", json={
        "nombre": "Ana Test",
        "email": "ana@test.com",
        "mensaje": "Mensaje de prueba",
    })
    assert respuesta.status_code == 202
    assert "email" in respuesta.json()


def test_subir_archivo():
    """Prueba la subida de archivos."""
    import io
    # Creamos un "archivo" en memoria para la prueba
    archivo_falso = io.BytesIO(b"contenido del archivo de prueba")

    respuesta = client.post(
        "/archivos/subir",
        files={"archivo": ("test.txt", archivo_falso, "text/plain")},
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["nombre_archivo"] == "test.txt"


def test_archivo_tipo_invalido():
    """Prueba que archivos de tipo no permitido son rechazados."""
    import io
    archivo_exe = io.BytesIO(b"contenido exe")
    respuesta = client.post(
        "/archivos/subir",
        files={"archivo": ("virus.exe", archivo_exe, "application/x-msdownload")},
    )
    assert respuesta.status_code == 415


# Uso de fixtures de pytest para reutilizar el client
@pytest.fixture
def api_client():
    """Fixture que proporciona el TestClient para los tests."""
    with TestClient(app) as c:
        yield c


def test_info_websocket(api_client):
    """Prueba el endpoint de info WebSocket."""
    respuesta = api_client.get("/ws/info")
    assert respuesta.status_code == 200
    assert "conexiones_activas" in respuesta.json()
'''


# =============================================================================
# ENDPOINTS ADICIONALES
# =============================================================================

@app.get("/", tags=["General"])
def raiz():
    """Página de bienvenida con información de la app."""
    return {
        "app": "FastAPI Avanzado",
        "version": "1.0.0",
        "endpoints_disponibles": {
            "docs": "/docs",
            "contacto": "POST /contacto",
            "subir_archivo": "POST /archivos/subir",
            "websocket_chat": "ws:// /ws/chat/{usuario_id}",
            "emails_enviados": "GET /emails-enviados",
        },
    }


@app.exception_handler(HTTPException)
async def manejador_http_exception(request: Request, exc: HTTPException):
    """
    Manejador global de excepciones HTTP.

    Personaliza el formato de todas las respuestas de error.
    Por qué: da un formato consistente a todos los errores de la API.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "codigo": exc.status_code,
            "detalle": exc.detail,
            "ruta": str(request.url),
        },
    )


@app.get("/testing-info", tags=["Testing"])
def info_testing():
    """Muestra el código de ejemplo para tests."""
    return {
        "mensaje": "Ver el código de testing en este archivo",
        "instrucciones": [
            "pip install pytest httpx",
            "Crea test_api.py con el código del atributo 'CODIGO_TESTING'",
            "pytest test_api.py -v",
        ],
    }


# =============================================================================
# EJECUTAR
# =============================================================================

if __name__ == "__main__":
    if not FASTAPI_DISPONIBLE:
        print('FastAPI no instalado. Instala: pip install "fastapi[standard]" python-multipart')
    else:
        import uvicorn
        print("Iniciando FastAPI Avanzado...")
        print("Docs: http://127.0.0.1:8000/docs")
        print("WebSocket chat: ws://127.0.0.1:8000/ws/chat/tu_nombre")
        uvicorn.run("06_fastapi_avanzado:app", host="127.0.0.1", port=8000, reload=True)
