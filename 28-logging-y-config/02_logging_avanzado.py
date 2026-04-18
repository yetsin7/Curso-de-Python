# =============================================================================
# CAPÍTULO 28 — Logging, Configuración y Buenas Prácticas
# Archivo 2: logging avanzado
# =============================================================================
# Temas: logs estructurados en JSON, logging.config.dictConfig,
# structlog (con fallback), integración avanzada con excepciones,
# logger para aplicación real con contexto de request.
# =============================================================================

import logging
import logging.config
import json
import sys
import traceback
import time
import uuid
from datetime import datetime, timezone

# Intentar importar structlog (librería externa)
try:
    import structlog
    STRUCTLOG_DISPONIBLE = True
except ImportError:
    STRUCTLOG_DISPONIBLE = False
    print("NOTA: structlog no instalado. Instala con: pip install structlog")
    print("      Se usará el módulo logging estándar con JSON formatter.\n")


# =============================================================================
# SECCIÓN 1: JSON Formatter — Logs estructurados sin librerías externas
# =============================================================================

print("=" * 60)
print("1. JSON Formatter — Logs estructurados con logging estándar")
print("=" * 60)

# ¿Por qué logs en JSON?
# En producción los logs son consumidos por herramientas como:
# Elasticsearch, Datadog, Splunk, CloudWatch, Loki.
# Estas herramientas ENTIENDEN JSON y permiten filtrar y buscar fácilmente.
# "ERROR" como texto libre es difícil de buscar.
# {"level": "ERROR", "user_id": 123} es consultable con SQL-like queries.


class JSONFormatter(logging.Formatter):
    """
    Formatter que convierte cada registro de log a una línea JSON válida.
    Cada campo es indexable por herramientas de observabilidad.
    """

    def __init__(self, servicio="app", version="1.0.0"):
        super().__init__()
        self.servicio = servicio
        self.version = version

    def format(self, record):
        """
        Convierte el LogRecord en un dict JSON.
        Incluye campos estándar + campos extra del record.
        """
        # Campos base siempre presentes
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "servicio": self.servicio,
            "version": self.version,
            "modulo": record.module,
            "funcion": record.funcName,
            "linea": record.lineno,
        }

        # Incluir excepción si existe
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Incluir campos extra pasados con extra={} al log
        campos_reservados = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "message",
        }
        for clave, valor in record.__dict__.items():
            if clave not in campos_reservados and not clave.startswith("_"):
                log_entry[clave] = valor

        return json.dumps(log_entry, ensure_ascii=False, default=str)


# Configurar logger con JSON formatter
logger_json = logging.getLogger("app.json")
logger_json.setLevel(logging.DEBUG)
logger_json.propagate = False

json_handler = logging.StreamHandler(sys.stdout)
json_handler.setFormatter(JSONFormatter(servicio="ecommerce", version="2.1.0"))
logger_json.addHandler(json_handler)

# Logs básicos en JSON
logger_json.info("Servicio iniciado")
logger_json.warning("Capacidad del caché al 85%", extra={"cache_percent": 85})

# Log con campos de contexto de negocio
logger_json.info(
    "Pedido creado",
    extra={
        "order_id": "ORD-2024-001",
        "user_id": 456,
        "total": 1250.99,
        "items": 3,
    }
)

# Log de error con excepción
try:
    resultado = 10 / 0
except ZeroDivisionError:
    logger_json.error(
        "Error en cálculo de descuento",
        exc_info=True,
        extra={"producto_id": "PROD-789", "descuento": 0}
    )


# =============================================================================
# SECCIÓN 2: logging.config.dictConfig — Configuración desde diccionario/archivo
# =============================================================================

print("\n" + "=" * 60)
print("2. dictConfig — Configuración centralizada")
print("=" * 60)

# dictConfig permite definir TODA la configuración de logging en un solo lugar.
# Puede cargarse desde un archivo YAML o JSON en producción.

CONFIG_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # No deshabilitar loggers ya creados

    # Definir formatters reutilizables
    "formatters": {
        "simple": {
            "format": "[%(levelname)-8s] %(name)s: %(message)s"
        },
        "detallado": {
            "format": "%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d — %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            # Usar nuestro formatter personalizado
            "()": JSONFormatter,
            "servicio": "mi-api",
            "version": "3.0.0",
        }
    },

    # Definir handlers
    "handlers": {
        "consola": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "archivo_errores": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detallado",
            "filename": "/tmp/errores.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },

    # Configurar loggers específicos
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["consola"],
            "propagate": False,
        },
        "app.database": {
            "level": "INFO",  # BD: menos verboso que el resto de la app
            "handlers": ["consola"],
            "propagate": False,
        },
        "urllib3": {
            "level": "WARNING",  # Silenciar logs verbosos de librerías externas
        },
        "requests": {
            "level": "WARNING",
        },
    },

    # Configurar el root logger (fallback)
    "root": {
        "level": "WARNING",
        "handlers": ["consola"],
    }
}

logging.config.dictConfig(CONFIG_LOGGING)

logger_dictconfig = logging.getLogger("app.ejemplo")
logger_dictconfig.info("Logger configurado con dictConfig")
logger_dictconfig.debug("Mensaje debug desde dictConfig")


# =============================================================================
# SECCIÓN 3: structlog — Logging estructurado moderno (si está disponible)
# =============================================================================

print("\n" + "=" * 60)
print("3. structlog — Logging estructurado moderno")
print("=" * 60)

if STRUCTLOG_DISPONIBLE:
    # Configurar structlog para desarrollo (salida colorida y legible)
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%H:%M:%S", utc=False),
            structlog.dev.ConsoleRenderer(),  # Salida colorida para desarrollo
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    slog = structlog.get_logger("app.structlog")

    # Ventaja de structlog: bind() para agregar contexto permanente al logger
    slog_con_contexto = slog.bind(user_id=123, session="abc-def")

    slog_con_contexto.info("Usuario activo", accion="ver_perfil")
    slog_con_contexto.warning("Intento de acceso no autorizado", ruta="/admin")
    slog_con_contexto.error("Error en base de datos", tabla="pedidos", operacion="INSERT")

    # nuevo_bind agrega más contexto sin perder el anterior
    slog_pedido = slog_con_contexto.bind(order_id="ORD-999")
    slog_pedido.info("Pedido iniciado", total=450.00)

else:
    print("  structlog no disponible — usando JSON formatter estándar")
    print("  Instala con: pip install structlog")


# =============================================================================
# SECCIÓN 4: Contexto de request — Logger para aplicación web real
# =============================================================================

print("\n" + "=" * 60)
print("4. Contexto de request — Logger para aplicación web")
print("=" * 60)

# En aplicaciones web, cada petición necesita un identificador único
# para correlacionar todos los logs de esa petición.


class RequestContextLogger:
    """
    Logger con contexto de request HTTP.
    Cada instancia incluye automáticamente el request_id en todos los logs,
    facilitando la correlación de logs en sistemas distribuidos.
    """

    def __init__(self, request_id=None, user_id=None, ip=None):
        self.logger = logging.getLogger("app.request")
        self.request_id = request_id or str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.ip = ip or "0.0.0.0"
        self._inicio = time.time()

        # Configurar handler si no tiene
        if not self.logger.handlers:
            h = logging.StreamHandler(sys.stdout)
            h.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] [req=%(request_id)s] %(message)s",
                datefmt="%H:%M:%S"
            ))
            self.logger.addHandler(h)
            self.logger.setLevel(logging.DEBUG)
            self.logger.propagate = False

    def _extra(self, **kwargs):
        """Construye el dict extra con contexto del request."""
        base = {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "ip": self.ip,
        }
        base.update(kwargs)
        return base

    def info(self, mensaje, **kwargs):
        self.logger.info(mensaje, extra=self._extra(**kwargs))

    def warning(self, mensaje, **kwargs):
        self.logger.warning(mensaje, extra=self._extra(**kwargs))

    def error(self, mensaje, exc_info=False, **kwargs):
        self.logger.error(mensaje, exc_info=exc_info, extra=self._extra(**kwargs))

    def duracion(self):
        """Retorna la duración del request en milisegundos."""
        return (time.time() - self._inicio) * 1000


# Simular procesamiento de requests HTTP
def procesar_request(ruta, user_id):
    """Simula el procesamiento de un request HTTP."""
    req_log = RequestContextLogger(user_id=user_id, ip="192.168.1.100")
    req_log.info(f"Request recibido: GET {ruta}")

    try:
        time.sleep(0.05)  # Simula procesamiento
        if ruta == "/admin" and user_id != 1:
            raise PermissionError(f"Usuario {user_id} no tiene acceso a /admin")
        req_log.info(f"Request completado: GET {ruta}", duracion_ms=req_log.duracion())
    except PermissionError as e:
        req_log.error(f"Acceso denegado: {e}", exc_info=True)


# Simular múltiples requests concurrentes
procesar_request("/productos", user_id=42)
procesar_request("/admin", user_id=99)   # Generará error de permisos
procesar_request("/perfil", user_id=1)

print("\nFIN: 02_logging_avanzado.py completado")
