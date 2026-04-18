# =============================================================================
# CAPÍTULO 07 - MANEJO DE ERRORES
# Archivo: 03_excepciones_personalizadas.py
# Descripción: Cómo crear jerarquías de excepciones propias para modelar
#              errores de dominio específicos de una aplicación.
#              Incluye un sistema centralizado de manejo, context managers
#              y logging completo con traceback.
# =============================================================================

import logging
import traceback
from contextlib import contextmanager
from datetime import datetime


# =============================================================================
# CONFIGURACIÓN DEL SISTEMA DE LOGGING
# Registra todos los errores en consola Y en un archivo de log.
# =============================================================================
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),                   # Salida en consola
        logging.FileHandler("app_errors.log"),     # Archivo de log
    ]
)
logger = logging.getLogger("api_usuarios")


# =============================================================================
# JERARQUÍA DE EXCEPCIONES PERSONALIZADAS
# Todas heredan de AppError para facilitar el manejo centralizado.
# =============================================================================

class AppError(Exception):
    """
    Excepción base de la aplicación. Todas las excepciones personalizadas
    heredan de esta clase para permitir un catch genérico con 'AppError'.

    Atributos:
        mensaje:    Descripción legible del error.
        codigo:     Código de error único (útil para APIs y logs).
        timestamp:  Fecha y hora en que ocurrió el error.
    """
    def __init__(self, mensaje: str, codigo: int = 500):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo
        self.timestamp = datetime.now().isoformat()

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.mensaje} (en {self.timestamp})"

    def to_dict(self) -> dict:
        """Convierte el error a diccionario, útil para respuestas JSON en APIs."""
        return {
            "error": self.__class__.__name__,
            "mensaje": self.mensaje,
            "codigo": self.codigo,
            "timestamp": self.timestamp,
        }


class ValidacionError(AppError):
    """
    Error de validación de datos de entrada.
    Se lanza cuando los datos del usuario no cumplen las reglas de negocio.
    Código HTTP equivalente: 400 Bad Request.
    """
    def __init__(self, campo: str, mensaje: str):
        super().__init__(f"Validación fallida en '{campo}': {mensaje}", codigo=400)
        self.campo = campo


class AutenticacionError(AppError):
    """
    Error de autenticación.
    Se lanza cuando las credenciales son incorrectas o el token ha expirado.
    Código HTTP equivalente: 401 Unauthorized.
    """
    def __init__(self, mensaje: str = "Credenciales inválidas o sesión expirada"):
        super().__init__(mensaje, codigo=401)


class RecursoNoEncontrado(AppError):
    """
    Error cuando se intenta acceder a un recurso que no existe.
    Código HTTP equivalente: 404 Not Found.
    """
    def __init__(self, recurso: str, identificador):
        super().__init__(
            f"'{recurso}' con identificador '{identificador}' no fue encontrado.",
            codigo=404
        )
        self.recurso = recurso
        self.identificador = identificador


class PermisoDenegado(AppError):
    """
    Error cuando el usuario no tiene permisos para ejecutar la acción.
    Código HTTP equivalente: 403 Forbidden.
    """
    def __init__(self, accion: str, usuario: str = "anónimo"):
        super().__init__(
            f"El usuario '{usuario}' no tiene permiso para: {accion}",
            codigo=403
        )
        self.accion = accion
        self.usuario = usuario


# =============================================================================
# MANEJADOR CENTRALIZADO DE ERRORES
# Recibe cualquier excepción y la maneja según su tipo.
# Simula el middleware de manejo de errores en un framework web.
# =============================================================================

def manejar_error(error: Exception) -> dict:
    """
    Manejador centralizado de excepciones de la aplicación.
    Registra el error en el log y retorna una respuesta estructurada.

    Args:
        error: La excepción capturada.

    Returns:
        Diccionario con la información del error para enviar al cliente.
    """
    if isinstance(error, AppError):
        # Error conocido de la aplicación → log de advertencia
        logger.warning(f"AppError capturado: {error}")
        return error.to_dict()
    else:
        # Error inesperado → log de error crítico con traceback completo
        logger.error(f"Error inesperado: {error}")
        logger.error(traceback.format_exc())
        return {
            "error": "ErrorInternoDelServidor",
            "mensaje": "Ocurrió un error inesperado. Por favor intenta más tarde.",
            "codigo": 500,
        }


# =============================================================================
# SIMULACIÓN DE API DE USUARIOS
# Muestra cómo los errores tipados modelan los casos de fallo reales.
# =============================================================================

# Base de datos simulada en memoria
_usuarios_db = {
    "u1": {"nombre": "Ana García", "email": "ana@example.com", "rol": "admin"},
    "u2": {"nombre": "Luis Pérez", "email": "luis@example.com", "rol": "usuario"},
}
_sesiones_activas = {"token_admin_123": "u1"}


def validar_usuario_datos(nombre: str, email: str):
    """
    Valida los datos de entrada para crear un usuario.
    Lanza ValidacionError si algún campo no cumple las reglas.
    """
    if not nombre or len(nombre.strip()) < 2:
        raise ValidacionError("nombre", "Debe tener al menos 2 caracteres")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValidacionError("email", "El formato del email no es válido")
    # Verificar email duplicado
    for usuario in _usuarios_db.values():
        if usuario["email"].lower() == email.lower():
            raise ValidacionError("email", f"El email '{email}' ya está registrado")


def autenticar(token: str) -> str:
    """
    Verifica que el token de sesión sea válido.
    Retorna el ID del usuario autenticado.
    Lanza AutenticacionError si el token no existe.
    """
    if token not in _sesiones_activas:
        raise AutenticacionError(f"Token inválido o sesión expirada: '{token}'")
    return _sesiones_activas[token]


def obtener_usuario(user_id: str) -> dict:
    """
    Obtiene los datos de un usuario por su ID.
    Lanza RecursoNoEncontrado si el ID no existe.
    """
    if user_id not in _usuarios_db:
        raise RecursoNoEncontrado("Usuario", user_id)
    return _usuarios_db[user_id]


def eliminar_usuario(token: str, user_id_objetivo: str):
    """
    Elimina un usuario. Solo los admins pueden realizar esta acción.
    Lanza PermisoDenegado si el usuario no tiene el rol correcto.
    """
    solicitante_id = autenticar(token)
    solicitante = obtener_usuario(solicitante_id)

    if solicitante["rol"] != "admin":
        raise PermisoDenegado(
            accion=f"eliminar usuario '{user_id_objetivo}'",
            usuario=solicitante["nombre"]
        )

    if user_id_objetivo not in _usuarios_db:
        raise RecursoNoEncontrado("Usuario", user_id_objetivo)

    del _usuarios_db[user_id_objetivo]
    return {"mensaje": f"Usuario '{user_id_objetivo}' eliminado correctamente."}


# =============================================================================
# CONTEXT MANAGER CON MANEJO DE ERRORES
# Permite ejecutar un bloque de código y manejar errores automáticamente.
# =============================================================================

@contextmanager
def manejar_operacion(nombre_operacion: str):
    """
    Context manager que envuelve una operación en manejo centralizado de errores.
    Registra el inicio, fin y cualquier excepción de la operación.

    Uso:
        with manejar_operacion("crear usuario"):
            # código que puede lanzar excepciones

    Args:
        nombre_operacion: Nombre descriptivo para el log.
    """
    logger.info(f"Iniciando operación: '{nombre_operacion}'")
    try:
        yield  # Ejecutar el bloque `with`
        logger.info(f"Operación exitosa: '{nombre_operacion}'")
    except AppError as e:
        # Error de dominio conocido
        respuesta = manejar_error(e)
        print(f"  → Error controlado: {respuesta}")
    except Exception as e:
        # Error inesperado
        respuesta = manejar_error(e)
        print(f"  → Error inesperado: {respuesta}")


# =============================================================================
# DEMO PRINCIPAL
# Ejecuta distintos escenarios de error para mostrar la jerarquía en acción.
# =============================================================================

def demo():
    """
    Ejecuta escenarios reales que disparan cada tipo de excepción personalizada.
    Muestra cómo el manejador centralizado procesa cada caso.
    """
    print("=" * 60)
    print("   EXCEPCIONES PERSONALIZADAS - CAPÍTULO 07")
    print("=" * 60)

    # --- Escenario 1: Validación de datos ---
    print("\n1. ValidacionError - Datos de usuario inválidos")
    with manejar_operacion("registrar usuario"):
        validar_usuario_datos("A", "correo_invalido")

    with manejar_operacion("registrar usuario con email duplicado"):
        validar_usuario_datos("Pedro López", "ana@example.com")

    # --- Escenario 2: Autenticación fallida ---
    print("\n2. AutenticacionError - Token inválido")
    with manejar_operacion("operación autenticada"):
        autenticar("token_que_no_existe_xyz")

    # --- Escenario 3: Recurso no encontrado ---
    print("\n3. RecursoNoEncontrado - ID de usuario inexistente")
    with manejar_operacion("obtener usuario"):
        obtener_usuario("u999")

    # --- Escenario 4: Permiso denegado ---
    print("\n4. PermisoDenegado - Usuario sin rol de admin")
    # Crear sesión temporal para usuario sin permisos de admin
    _sesiones_activas["token_user_456"] = "u2"
    with manejar_operacion("eliminar usuario"):
        eliminar_usuario("token_user_456", "u1")

    # --- Escenario 5: Operación exitosa ---
    print("\n5. Operación exitosa - Sin errores")
    with manejar_operacion("obtener usuario existente"):
        user = obtener_usuario("u1")
        print(f"  Usuario encontrado: {user}")

    # --- Escenario 6: Error inesperado (no controlado) ---
    print("\n6. Error inesperado (ZeroDivisionError)")
    with manejar_operacion("operación matemática"):
        resultado = 10 / 0  # ZeroDivisionError

    # --- Escenario 7: Eliminar con permisos (admin) ---
    print("\n7. Eliminar usuario - Con permisos de admin")
    with manejar_operacion("eliminar usuario u2"):
        resultado = eliminar_usuario("token_admin_123", "u2")
        print(f"  → {resultado}")

    print("\n✓ Revisa 'app_errors.log' para ver el registro completo.")


if __name__ == "__main__":
    demo()
