# =============================================================================
# CAPÍTULO 28 — Logging, Configuración y Buenas Prácticas
# Archivo 3: Configuración de aplicaciones
# =============================================================================
# Temas: python-dotenv, configparser para .ini, pydantic-settings para
# configuración tipada. Patrón de configuración por entorno (dev/staging/prod).
# Variables de entorno: buenas prácticas de seguridad.
# =============================================================================

import os
import sys
import configparser
import json
import tempfile
import logging

logger = logging.getLogger(__name__)

# Intentar importar librerías externas con instrucciones de instalación
try:
    from dotenv import load_dotenv, dotenv_values
    DOTENV_DISPONIBLE = True
except ImportError:
    DOTENV_DISPONIBLE = False
    print("NOTA: python-dotenv no instalado. Instala con: pip install python-dotenv\n")

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator, field_validator
    PYDANTIC_SETTINGS_DISPONIBLE = True
except ImportError:
    PYDANTIC_SETTINGS_DISPONIBLE = False
    print("NOTA: pydantic-settings no instalado.")
    print("      Instala con: pip install pydantic-settings\n")


# =============================================================================
# SECCIÓN 1: Variables de entorno — La base de todo
# =============================================================================

print("=" * 60)
print("1. Variables de entorno del sistema")
print("=" * 60)

# os.getenv con valor por defecto — siempre proporcionar uno para dev
db_host = os.getenv("DATABASE_HOST", "localhost")
db_port = int(os.getenv("DATABASE_PORT", "5432"))
debug_mode = os.getenv("DEBUG", "false").lower() == "true"
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

print(f"  DATABASE_HOST: {db_host}")
print(f"  DATABASE_PORT: {db_port}")
print(f"  DEBUG:         {debug_mode}")
print(f"  LOG_LEVEL:     {log_level}")

# Acceder a variable de entorno que DEBE existir (sin valor por defecto)
api_key = os.getenv("API_KEY")
if api_key is None:
    print("  API_KEY:       [no configurada] ← En producción esto debería fallar")
else:
    # NUNCA loguear el valor completo de un secreto
    print(f"  API_KEY:       {api_key[:4]}...{api_key[-4:]} (enmascarada)")

# Patrón: validar variables críticas al inicio (fail-fast)
VARIABLES_REQUERIDAS_PRODUCCION = ["DATABASE_URL", "SECRET_KEY", "API_KEY"]

def validar_config_produccion():
    """
    Verifica que todas las variables de entorno críticas estén configuradas.
    Debe llamarse al arranque del servidor para fallar rápido si falta algo.
    """
    entorno = os.getenv("APP_ENV", "development")
    if entorno != "production":
        print(f"  Entorno: {entorno} — omitiendo validación de producción")
        return

    faltantes = [v for v in VARIABLES_REQUERIDAS_PRODUCCION if not os.getenv(v)]
    if faltantes:
        raise EnvironmentError(
            f"Variables de entorno requeridas no configuradas: {faltantes}\n"
            f"Configúralas antes de arrancar en producción."
        )
    print("  Todas las variables de producción están configuradas ✓")


validar_config_produccion()


# =============================================================================
# SECCIÓN 2: python-dotenv — Archivos .env para desarrollo
# =============================================================================

print("\n" + "=" * 60)
print("2. python-dotenv — Archivos .env para desarrollo local")
print("=" * 60)

# Crear un .env de ejemplo en un directorio temporal
CONTENIDO_ENV = """
# Configuración de desarrollo local
# IMPORTANTE: Este archivo NUNCA debe commitarse al repositorio
# Agrega .env a tu .gitignore

APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG

# Base de datos
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=mi_app_dev
DATABASE_USER=dev_user
DATABASE_PASSWORD=dev_password_local_solo

# API Keys (simuladas)
API_KEY=sk-dev-1234567890abcdef
SECRET_KEY=super-secret-key-only-for-local-dev-32chars

# Redis
REDIS_URL=redis://localhost:6379/0
"""

# Guardar el .env temporal para la demo
env_path = os.path.join(tempfile.gettempdir(), ".env_demo")
with open(env_path, "w", encoding="utf-8") as f:
    f.write(CONTENIDO_ENV)

print(f"  Archivo .env de demo creado en: {env_path}")

if DOTENV_DISPONIBLE:
    # load_dotenv carga el archivo y seta las variables de entorno del proceso
    load_dotenv(env_path, override=True)

    app_env = os.getenv("APP_ENV")
    debug = os.getenv("DEBUG")
    db_name = os.getenv("DATABASE_NAME")
    print(f"  APP_ENV cargado: {app_env}")
    print(f"  DEBUG cargado:   {debug}")
    print(f"  DB_NAME cargado: {db_name}")

    # dotenv_values retorna un dict sin modificar el entorno del proceso
    valores = dotenv_values(env_path)
    print(f"  Total variables en .env: {len(valores)}")
    print("  Variables (sin mostrar secretos):")
    for clave, valor in valores.items():
        if any(s in clave.lower() for s in ["password", "secret", "key", "token"]):
            print(f"    {clave} = {'*' * 8} (oculto)")
        else:
            print(f"    {clave} = {valor}")

else:
    print("  python-dotenv no disponible — instala con: pip install python-dotenv")


# =============================================================================
# SECCIÓN 3: configparser — Archivos .ini para configuración estructurada
# =============================================================================

print("\n" + "=" * 60)
print("3. configparser — Archivos .ini")
print("=" * 60)

# Crear archivo .ini de ejemplo
CONTENIDO_INI = """
[DEFAULT]
log_level = INFO
debug = false
version = 1.0.0

[database]
host = localhost
port = 5432
name = mi_app
pool_size = 5
pool_timeout = 30

[cache]
backend = redis
host = localhost
port = 6379
ttl_segundos = 3600

[email]
smtp_host = smtp.gmail.com
smtp_port = 587
use_tls = true
from_address = noreply@miapp.com

[api]
rate_limit = 100
rate_limit_window = 60
timeout = 30
"""

ini_path = os.path.join(tempfile.gettempdir(), "config_demo.ini")
with open(ini_path, "w", encoding="utf-8") as f:
    f.write(CONTENIDO_INI)

# Leer el archivo .ini
config = configparser.ConfigParser()
config.read(ini_path, encoding="utf-8")

print(f"  Secciones disponibles: {config.sections()}")

# Leer valores con tipos apropiados
db_host_ini = config.get("database", "host")
db_port_ini = config.getint("database", "port")          # Convierte a int
pool_size = config.getint("database", "pool_size")
debug_ini = config.getboolean("DEFAULT", "debug")         # Convierte a bool
use_tls = config.getboolean("email", "use_tls")
rate_limit = config.getint("api", "rate_limit")

print(f"\n  [database] host={db_host_ini}, port={db_port_ini}, pool_size={pool_size}")
print(f"  [email]    smtp={config.get('email', 'smtp_host')}, tls={use_tls}")
print(f"  [api]      rate_limit={rate_limit}/min")
print(f"  [DEFAULT]  debug={debug_ini}, version={config.get('DEFAULT', 'version')}")

# Verificar si una sección/opción existe
print(f"\n  ¿Existe sección 'cache'? {config.has_section('cache')}")
print(f"  ¿Existe opción 'database/replica_host'? {config.has_option('database', 'replica_host')}")

# Valor con fallback si no existe
replica_host = config.get("database", "replica_host", fallback="no configurado")
print(f"  database/replica_host (con fallback): {replica_host}")

# Escribir configuración actualizada
config.set("cache", "ttl_segundos", "7200")
config.add_section("monitoring") if not config.has_section("monitoring") else None
config.set("monitoring", "sentry_dsn", "")
config.set("monitoring", "metrics_enabled", "false")

ini_actualizado = os.path.join(tempfile.gettempdir(), "config_actualizado.ini")
with open(ini_actualizado, "w", encoding="utf-8") as f:
    config.write(f)
print(f"\n  Config actualizado guardado en: {ini_actualizado}")


# =============================================================================
# SECCIÓN 4: pydantic-settings — Configuración tipada y validada
# =============================================================================

print("\n" + "=" * 60)
print("4. pydantic-settings — Configuración tipada con validación")
print("=" * 60)

if PYDANTIC_SETTINGS_DISPONIBLE:
    from typing import Optional, List
    from enum import Enum

    class Entorno(str, Enum):
        """Entornos válidos de la aplicación."""
        DEVELOPMENT = "development"
        STAGING = "staging"
        PRODUCTION = "production"
        TESTING = "testing"

    class ConfiguracionBaseDatos(BaseSettings):
        """Configuración de la base de datos con validación automática."""

        host: str = Field(default="localhost", description="Host del servidor de BD")
        port: int = Field(default=5432, ge=1, le=65535)
        name: str = Field(default="app_db")
        user: str = Field(default="postgres")
        password: str = Field(default="")
        pool_size: int = Field(default=5, ge=1, le=100)

        @property
        def url(self) -> str:
            """Construye la URL de conexión a la base de datos."""
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

        model_config = {"env_prefix": "DATABASE_"}

    class ConfiguracionApp(BaseSettings):
        """
        Configuración principal de la aplicación.
        pydantic-settings lee automáticamente de:
        1. Variables de entorno del sistema
        2. Archivo .env (si se especifica)
        """
        # Entorno y debug
        app_env: Entorno = Field(default=Entorno.DEVELOPMENT, alias="APP_ENV")
        debug: bool = Field(default=False, alias="DEBUG")
        log_level: str = Field(default="INFO", alias="LOG_LEVEL")
        version: str = Field(default="0.0.0")

        # Servidor
        host: str = Field(default="0.0.0.0")
        port: int = Field(default=8000, ge=1, le=65535)

        # Base de datos (objeto anidado)
        db: ConfiguracionBaseDatos = ConfiguracionBaseDatos()

        # Seguridad
        secret_key: str = Field(default="cambiar-en-produccion")
        allowed_hosts: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
        cors_origins: List[str] = Field(default_factory=list)

        # Opcionales
        sentry_dsn: Optional[str] = Field(default=None)
        redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

        model_config = {
            "env_file": env_path,       # Leer desde .env
            "env_file_encoding": "utf-8",
            "case_sensitive": False,
            "extra": "ignore",          # Ignorar variables de entorno extra
        }

        @property
        def es_produccion(self) -> bool:
            return self.app_env == Entorno.PRODUCTION

        @property
        def es_desarrollo(self) -> bool:
            return self.app_env == Entorno.DEVELOPMENT

        def resumen_seguro(self) -> dict:
            """Retorna un resumen de la config sin exponer secretos."""
            return {
                "entorno": self.app_env.value,
                "debug": self.debug,
                "log_level": self.log_level,
                "servidor": f"{self.host}:{self.port}",
                "base_de_datos": f"{self.db.host}:{self.db.port}/{self.db.name}",
                "sentry_activo": self.sentry_dsn is not None,
                "secret_key": "[configurada]" if self.secret_key else "[FALTA]",
            }

    # Cargar configuración desde variables de entorno y .env
    config_app = ConfiguracionApp()
    print("  Configuración cargada con pydantic-settings:")
    for clave, valor in config_app.resumen_seguro().items():
        print(f"    {clave}: {valor}")

    print(f"\n  URL de base de datos: {config_app.db.url[:30]}...")
    print(f"  ¿Es producción? {config_app.es_produccion}")
    print(f"  ¿Es desarrollo? {config_app.es_desarrollo}")

else:
    print("  pydantic-settings no disponible.")
    print("  Instala con: pip install pydantic-settings")


# =============================================================================
# SECCIÓN 5: Patrón de configuración por entorno
# =============================================================================

print("\n" + "=" * 60)
print("5. Patrón de configuración por entorno")
print("=" * 60)

# Estructura recomendada para proyectos reales:
# config/
#   __init__.py
#   base.py        ← Configuración común a todos los entornos
#   development.py ← Sobreescribe para desarrollo
#   staging.py     ← Sobreescribe para staging
#   production.py  ← Sobreescribe para producción


class ConfigBase:
    """Configuración base común a todos los entornos."""
    VERSION = "1.0.0"
    DEBUG = False
    LOG_LEVEL = "INFO"
    ITEMS_POR_PAGINA = 20
    TIMEOUT_SEGUNDOS = 30
    CACHE_TTL = 3600  # 1 hora


class ConfigDesarrollo(ConfigBase):
    """Configuración para desarrollo local. No usar en producción."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DATABASE_URL = "sqlite:///dev.db"  # SQLite en memoria para dev
    CACHE_TTL = 60  # Cache breve en desarrollo
    ENVIAR_EMAILS = False  # No enviar emails reales en desarrollo
    STRIPE_KEY = "sk_test_..."  # Clave de prueba de Stripe


class ConfigStaging(ConfigBase):
    """Configuración para ambiente de pruebas/QA."""
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://staging_db")
    LOG_LEVEL = "INFO"
    ENVIAR_EMAILS = True
    STRIPE_KEY = os.getenv("STRIPE_KEY", "")


class ConfigProduccion(ConfigBase):
    """Configuración para producción. Valida que todo esté configurado."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ENVIAR_EMAILS = True
    STRIPE_KEY = os.getenv("STRIPE_KEY", "")
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

    def __init__(self):
        # Validación estricta en producción
        if not self.DATABASE_URL:
            raise EnvironmentError("DATABASE_URL requerida en producción")
        if not self.SECRET_KEY:
            raise EnvironmentError("SECRET_KEY requerida en producción")


def obtener_configuracion():
    """
    Factory que retorna la configuración correcta según APP_ENV.
    Patrón de fábrica para configuración por entorno.
    """
    entorno = os.getenv("APP_ENV", "development").lower()

    mapa_configs = {
        "development": ConfigDesarrollo,
        "staging": ConfigStaging,
        "production": ConfigProduccion,
    }

    clase_config = mapa_configs.get(entorno, ConfigDesarrollo)
    return clase_config()


# Demostrar el patrón
config_actual = obtener_configuracion()
print(f"  Configuración activa: {type(config_actual).__name__}")
print(f"  Debug: {config_actual.DEBUG}")
print(f"  Log level: {config_actual.LOG_LEVEL}")
print(f"  Cache TTL: {config_actual.CACHE_TTL}s")

print("\nFIN: 03_configuracion_app.py completado")
