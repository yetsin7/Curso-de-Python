# =============================================================================
# CAPÍTULO 28 — Logging, Configuración y Buenas Prácticas
# Archivo 1: logging básico
# =============================================================================
# Temas: basicConfig, getLogger, FileHandler, StreamHandler, Formatter,
# RotatingFileHandler, logging en múltiples módulos, jerarquía de loggers,
# filtros personalizados.
# =============================================================================

import logging
import logging.handlers
import sys
import os
import tempfile


# =============================================================================
# SECCIÓN 1: El problema con basicConfig — Solo para scripts simples
# =============================================================================

print("=" * 60)
print("1. logging.basicConfig — Configuración rápida")
print("=" * 60)

# basicConfig configura el logger raíz (root logger)
# Solo tiene efecto si no se ha configurado nada antes
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Los 5 niveles de log
logging.debug("Mensaje de depuración — solo en desarrollo")
logging.info("Usuario inició sesión correctamente")
logging.warning("El caché está al 90% de capacidad")
logging.error("No se pudo conectar a la base de datos")
logging.critical("Servidor sin espacio en disco — apagando servicios")

# PROBLEMA: basicConfig es global y no permite configuración por módulo
# Para aplicaciones reales, siempre usa getLogger con nombre de módulo


# =============================================================================
# SECCIÓN 2: getLogger — La forma correcta en aplicaciones
# =============================================================================

print("\n" + "=" * 60)
print("2. logging.getLogger — Loggers nombrados")
print("=" * 60)

# Convención: usar __name__ como nombre del logger
# Esto crea automáticamente la jerarquía: paquete.modulo.clase
logger = logging.getLogger(__name__)

# Obtener un logger específico para un componente
logger_bd = logging.getLogger("app.database")
logger_api = logging.getLogger("app.api")
logger_auth = logging.getLogger("app.auth")

# Los loggers heredan la configuración de su padre en la jerarquía
# app.database hereda de app, que hereda del root logger
logger_bd.info("Conexión a la base de datos establecida")
logger_api.info("API iniciada en puerto 8080")
logger_auth.warning("Intento de login con contraseña incorrecta")


# =============================================================================
# SECCIÓN 3: Handlers — Dónde van los logs
# =============================================================================

print("\n" + "=" * 60)
print("3. Handlers — Consola + Archivo simultáneamente")
print("=" * 60)

# Crear un logger limpio (sin heredar configuración anterior)
logger_app = logging.getLogger("mi_aplicacion")
logger_app.setLevel(logging.DEBUG)
logger_app.propagate = False  # No propagar al root logger

# Handler 1: Consola (stdout) — para INFO y superior
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Consola: solo INFO+

# Formatter para consola: simple y legible
fmt_consola = logging.Formatter(
    fmt="[%(levelname)-8s] %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
console_handler.setFormatter(fmt_consola)

# Handler 2: Archivo — para DEBUG y superior (más detallado)
archivo_log = os.path.join(tempfile.gettempdir(), "app_demo.log")
file_handler = logging.FileHandler(archivo_log, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)  # Archivo: todo, incluyendo DEBUG

# Formatter para archivo: más detallado
fmt_archivo = logging.Formatter(
    fmt="%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(fmt_archivo)

# Agregar ambos handlers al logger
logger_app.addHandler(console_handler)
logger_app.addHandler(file_handler)

# Probar: aparece en consola (INFO+) y en archivo (DEBUG+)
logger_app.debug("Esto solo va al archivo")
logger_app.info("Esto va a consola Y archivo")
logger_app.warning("Advertencia importante")
logger_app.error("Error en el proceso de pago")

print(f"  (Log guardado en: {archivo_log})")


# =============================================================================
# SECCIÓN 4: RotatingFileHandler — Rotación automática de archivos
# =============================================================================

print("\n" + "=" * 60)
print("4. RotatingFileHandler — Rotación por tamaño")
print("=" * 60)

archivo_rotativo = os.path.join(tempfile.gettempdir(), "app_rotativo.log")

logger_rotativo = logging.getLogger("app.rotativo")
logger_rotativo.setLevel(logging.DEBUG)
logger_rotativo.propagate = False

# Crea hasta 5 archivos de backup, cada uno de máximo 1KB (en demo)
# En producción: maxBytes=10*1024*1024 (10 MB), backupCount=7
handler_rotativo = logging.handlers.RotatingFileHandler(
    filename=archivo_rotativo,
    maxBytes=1024,     # Rota cuando el archivo llega a 1KB (demo)
    backupCount=3,     # Guarda hasta 3 archivos de backup: .1, .2, .3
    encoding="utf-8"
)
handler_rotativo.setFormatter(fmt_archivo)
logger_rotativo.addHandler(handler_rotativo)

# Escribir suficientes logs para forzar la rotación
for i in range(50):
    logger_rotativo.info(f"Línea de log #{i:03d} — datos de prueba para demostrar rotación")

print(f"  Log rotativo en: {archivo_rotativo}")
print(f"  (Se crean archivos .1, .2, .3 al rotar)")

# TimedRotatingFileHandler — rota por tiempo en lugar de tamaño
archivo_timed = os.path.join(tempfile.gettempdir(), "app_timed.log")
handler_timed = logging.handlers.TimedRotatingFileHandler(
    filename=archivo_timed,
    when="midnight",    # Opciones: 'S', 'M', 'H', 'D', 'midnight', 'W0'-'W6'
    interval=1,         # Cada 1 día
    backupCount=30,     # Conservar 30 días de logs
    encoding="utf-8"
)
print(f"  Log por tiempo (midnight) en: {archivo_timed}")


# =============================================================================
# SECCIÓN 5: Jerarquía de loggers — Logger hierarchy
# =============================================================================

print("\n" + "=" * 60)
print("5. Jerarquía de loggers — propagación")
print("=" * 60)

# La jerarquía funciona por puntos en el nombre:
# "app" → padre de "app.api" → padre de "app.api.users"
# Los mensajes se propagan HACIA ARRIBA por defecto

# Configurar solo el padre — los hijos heredan
logger_padre = logging.getLogger("empresa")
logger_padre.setLevel(logging.WARNING)
logger_padre.propagate = False

handler_padre = logging.StreamHandler(sys.stdout)
handler_padre.setFormatter(logging.Formatter("[PADRE] %(name)s: %(message)s"))
logger_padre.addHandler(handler_padre)

# Loggers hijos — no tienen handlers propios, usan el del padre
logger_hijo_api = logging.getLogger("empresa.api")
logger_hijo_bd = logging.getLogger("empresa.database")
logger_nieto = logging.getLogger("empresa.api.auth")

# Estos mensajes suben al padre (empresa) que tiene nivel WARNING
logger_hijo_api.info("Esto NO aparece — INFO < WARNING del padre")
logger_hijo_api.warning("Esto SÍ aparece — viene del padre empresa.api")
logger_hijo_bd.error("Error en BD — aparece también")
logger_nieto.critical("Falla crítica en auth — aparece desde el nieto")

# Propagar = False detiene la propagación en ese nivel
logger_hijo_api.propagate = False  # Los mensajes de empresa.api ya no suben
logger_hijo_api.warning("Este mensaje ya NO sube al padre (propagate=False)")


# =============================================================================
# SECCIÓN 6: Filtros — Control fino de qué se loguea
# =============================================================================

print("\n" + "=" * 60)
print("6. Filtros personalizados")
print("=" * 60)


class FiltroNoDebug(logging.Filter):
    """
    Filtro que bloquea mensajes de nivel DEBUG.
    Un Filter.filter() debe retornar True para dejar pasar el mensaje.
    """

    def filter(self, record):
        # record.levelno es el número del nivel: DEBUG=10, INFO=20, etc.
        return record.levelno > logging.DEBUG


class FiltroKeyword(logging.Filter):
    """
    Filtro que solo deja pasar mensajes que contengan una palabra clave.
    Útil para aislar logs de un subsistema específico.
    """

    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword.lower()

    def filter(self, record):
        return self.keyword in record.getMessage().lower()


# Demostrar filtros
logger_filtrado = logging.getLogger("app.filtrado")
logger_filtrado.setLevel(logging.DEBUG)
logger_filtrado.propagate = False

handler_filtrado = logging.StreamHandler(sys.stdout)
handler_filtrado.setFormatter(logging.Formatter("  %(levelname)s: %(message)s"))
handler_filtrado.addFilter(FiltroKeyword("pago"))  # Solo logs que digan "pago"

logger_filtrado.addHandler(handler_filtrado)

logger_filtrado.debug("Debug: inicializando módulo")         # Filtrado (no contiene "pago")
logger_filtrado.info("Usuario inició sesión")                # Filtrado
logger_filtrado.info("Procesando pago con tarjeta")          # Pasa el filtro
logger_filtrado.error("Error al procesar pago #12345")       # Pasa el filtro
logger_filtrado.warning("Timeout en servidor de pagos")      # Pasa el filtro
logger_filtrado.critical("Base de datos no disponible")      # Filtrado (no contiene "pago")


# =============================================================================
# SECCIÓN 7: Logging de excepciones correctamente
# =============================================================================

print("\n" + "=" * 60)
print("7. Logging de excepciones — exc_info y stack trace")
print("=" * 60)

logger_exc = logging.getLogger("app.exceptions")
logger_exc.setLevel(logging.DEBUG)
logger_exc.propagate = False
handler_exc = logging.StreamHandler(sys.stdout)
handler_exc.setFormatter(logging.Formatter("  %(levelname)s: %(message)s"))
logger_exc.addHandler(handler_exc)


def dividir(a, b):
    """Función que puede lanzar una excepción."""
    return a / b


# FORMA CORRECTA: exc_info=True incluye el traceback completo en el log
try:
    resultado = dividir(10, 0)
except ZeroDivisionError:
    logger_exc.error("No se pudo dividir", exc_info=True)

# También se puede usar logger.exception() — equivalente a error(exc_info=True)
try:
    int("no_es_numero")
except ValueError:
    logger_exc.exception("Error de conversión de tipo")

# FORMA INCORRECTA — pierde el traceback
try:
    dividir(5, 0)
except ZeroDivisionError as e:
    logger_exc.error(f"Error: {e}")  # Solo el mensaje, sin traceback

print("\nFIN: 01_logging_basico.py completado")
