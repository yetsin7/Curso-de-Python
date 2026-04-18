# =============================================================================
# CAPÍTULO 21 — FastAPI
# Archivo 05: Autenticación con JWT en FastAPI
# =============================================================================
# La autenticación JWT (JSON Web Token) es el estándar para APIs modernas.
# El flujo es:
# 1. El cliente envía usuario + contraseña
# 2. La API verifica y devuelve un JWT firmado
# 3. El cliente incluye ese JWT en peticiones futuras
# 4. La API verifica la firma del JWT sin consultar la DB
#
# Instalación:
#   pip install "fastapi[standard]" python-jose[cryptography] passlib[bcrypt]
# =============================================================================

try:
    from fastapi import FastAPI, HTTPException, Depends, status
    from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
    FASTAPI_DISPONIBLE = True
except ImportError:
    FASTAPI_DISPONIBLE = False
    print('FastAPI no instalado. Instala: pip install "fastapi[standard]"')

try:
    from jose import JWTError, jwt
    JOSE_DISPONIBLE = True
except ImportError:
    JOSE_DISPONIBLE = False
    print("python-jose no instalado. Instala: pip install python-jose[cryptography]")

try:
    from passlib.context import CryptContext
    PASSLIB_DISPONIBLE = True
except ImportError:
    PASSLIB_DISPONIBLE = False
    print("passlib no instalado. Instala: pip install passlib[bcrypt]")

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
import os


# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# =============================================================================

# SECRET_KEY: clave para firmar los JWT — NUNCA hardcodeada en producción
# En producción: os.environ.get("JWT_SECRET_KEY") con un valor generado:
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = os.environ.get(
    "JWT_SECRET_KEY",
    "clave-super-secreta-solo-para-desarrollo-cambiar-en-produccion",
)

# ALGORITHM: algoritmo de firma del JWT
# HS256 = HMAC con SHA-256 — estándar y seguro para la mayoría de casos
ALGORITHM = "HS256"

# Tiempo de vida del token de acceso
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto de passlib para hashear contraseñas con bcrypt
# bcrypt es el algoritmo recomendado — adaptativo (se puede hacer más lento)
if PASSLIB_DISPONIBLE:
    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",  # Migra automáticamente hashes de algoritmos viejos
    )

# OAuth2PasswordBearer: extrae el token del header Authorization: Bearer <token>
# tokenUrl indica el endpoint donde el cliente obtiene el token
if FASTAPI_DISPONIBLE:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# =============================================================================
# BASE DE DATOS SIMULADA DE USUARIOS
# =============================================================================

# En producción esto sería SQLAlchemy + PostgreSQL
# La contraseña está hasheada con bcrypt — nunca en texto plano
_usuarios_db: dict[str, dict] = {}


def _crear_usuarios_ejemplo():
    """Crea usuarios de ejemplo si passlib está disponible."""
    if not PASSLIB_DISPONIBLE:
        return

    usuarios = [
        ("ana", "Ana García", "ana@ejemplo.com", "password123", True),
        ("pedro", "Pedro López", "pedro@ejemplo.com", "password456", False),
    ]

    for username, nombre, email, password, es_admin in usuarios:
        _usuarios_db[username] = {
            "username": username,
            "nombre_completo": nombre,
            "email": email,
            "hashed_password": pwd_context.hash(password),
            "activo": True,
            "es_admin": es_admin,
        }


_crear_usuarios_ejemplo()


# =============================================================================
# SCHEMAS PYDANTIC
# =============================================================================

class Token(BaseModel):
    """
    Schema de respuesta del endpoint de login.
    El cliente guarda estos valores y los usa en peticiones futuras.
    """
    access_token: str         # El JWT firmado
    token_type: str = "bearer"  # Siempre "bearer" para OAuth2


class TokenData(BaseModel):
    """
    Datos extraídos del payload del JWT al verificarlo.
    'sub' (subject) es el campo estándar para el identificador del usuario.
    """
    username: Optional[str] = None


class UsuarioPublico(BaseModel):
    """Datos del usuario que se exponen en la API — sin password."""
    username: str
    nombre_completo: str
    email: str
    activo: bool
    es_admin: bool


class RegistroRequest(BaseModel):
    """Schema para registrar un nuevo usuario."""
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    nombre_completo: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, description="Mínimo 8 caracteres")


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def verificar_password(password_plano: str, password_hash: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.

    Por qué no comparar directo: el hash incluye salt aleatorio.
    pwd_context.verify() hace la comparación correcta.

    Args:
        password_plano: La contraseña que el usuario envió.
        password_hash: El hash almacenado en la DB.

    Returns:
        True si coinciden, False si no.
    """
    if not PASSLIB_DISPONIBLE:
        return False
    return pwd_context.verify(password_plano, password_hash)


def hashear_password(password: str) -> str:
    """
    Genera el hash bcrypt de una contraseña.

    Cada llamada genera un hash diferente (salt aleatorio incluido).
    Nunca almacenes contraseñas en texto plano.

    Args:
        password: Contraseña en texto plano.

    Returns:
        Hash bcrypt listo para almacenar en la DB.
    """
    if not PASSLIB_DISPONIBLE:
        return f"sin_hash_{password}"
    return pwd_context.hash(password)


def crear_access_token(
    datos: dict,
    expira_en: Optional[timedelta] = None,
) -> str:
    """
    Crea un JWT firmado con los datos proporcionados.

    El JWT tiene 3 partes separadas por puntos:
    - Header: algoritmo y tipo
    - Payload: los datos (sub, exp, etc.)
    - Signature: firma HMAC con SECRET_KEY

    Args:
        datos: Dict con los datos a incluir en el payload.
        expira_en: Tiempo de vida del token (por defecto 30 minutos).

    Returns:
        JWT firmado como string.
    """
    if not JOSE_DISPONIBLE:
        return "jwt_no_disponible"

    # Copiamos para no modificar el original
    payload = datos.copy()

    # Añadimos el tiempo de expiración
    ahora = datetime.utcnow()
    if expira_en:
        expiracion = ahora + expira_en
    else:
        expiracion = ahora + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 'exp' es el campo estándar JWT para expiración (timestamp Unix)
    payload["exp"] = expiracion

    # jwt.encode firma el payload con la clave y el algoritmo
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verificar_token(token: str) -> TokenData:
    """
    Verifica y decodifica un JWT.

    Verifica: que la firma sea válida y que no haya expirado.
    Si falla cualquier verificación, lanza HTTPException 401.

    Args:
        token: El JWT recibido del cliente.

    Returns:
        TokenData con los datos del payload.

    Raises:
        HTTPException 401 si el token es inválido o expirado.
    """
    if not JOSE_DISPONIBLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="python-jose no está instalado.",
        )

    excepcion_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado.",
        # WWW-Authenticate es el header estándar para respuestas 401
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # jwt.decode verifica firma y expiración automáticamente
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 'sub' (subject) es el campo estándar para el ID del usuario
        username: str = payload.get("sub")
        if username is None:
            raise excepcion_credenciales

        return TokenData(username=username)

    except JWTError:
        # JWTError cubre: firma inválida, token expirado, formato incorrecto
        raise excepcion_credenciales


def autenticar_usuario(username: str, password: str) -> Optional[dict]:
    """
    Verifica las credenciales y retorna el usuario si son correctas.

    Args:
        username: Nombre de usuario.
        password: Contraseña en texto plano.

    Returns:
        El dict del usuario si las credenciales son válidas, None si no.
    """
    usuario = _usuarios_db.get(username)
    if not usuario:
        return None
    if not verificar_password(password, usuario["hashed_password"]):
        return None
    return usuario


# =============================================================================
# DEPENDENCIAS DE SEGURIDAD
# =============================================================================

def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme) if FASTAPI_DISPONIBLE else None,
) -> dict:
    """
    Dependencia que extrae y verifica el usuario del JWT.

    oauth2_scheme extrae automáticamente el token del header:
    Authorization: Bearer <token>

    Este es el patrón estándar para proteger endpoints en FastAPI.
    Cualquier endpoint que declare Depends(obtener_usuario_actual)
    requiere autenticación automáticamente.

    Args:
        token: JWT extraído del header Authorization por oauth2_scheme.

    Returns:
        Dict del usuario autenticado.

    Raises:
        HTTPException 401 si el token es inválido.
    """
    token_data = verificar_token(token)
    usuario = _usuarios_db.get(token_data.username)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.get("activo", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada.",
        )

    return usuario


def requerir_admin(
    usuario_actual: dict = Depends(obtener_usuario_actual),
) -> dict:
    """
    Dependencia que verifica que el usuario sea administrador.

    Composición de dependencias: requerir_admin usa obtener_usuario_actual.
    FastAPI resuelve la cadena automáticamente.

    Args:
        usuario_actual: Usuario autenticado (inyectado automáticamente).

    Returns:
        El usuario si es admin.

    Raises:
        HTTPException 403 si no tiene permisos de admin.
    """
    if not usuario_actual.get("es_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a este recurso.",
        )
    return usuario_actual


# =============================================================================
# APLICACIÓN FASTAPI
# =============================================================================

app = FastAPI(
    title="FastAPI con Autenticación JWT",
    description="""
    Ejemplo de autenticación con JWT (JSON Web Tokens).

    ## Flujo de autenticación:
    1. Obtén un token en `/auth/token` con tu usuario y contraseña
    2. Haz clic en "Authorize" en Swagger UI e ingresa el token
    3. Ahora puedes acceder a los endpoints protegidos

    ## Usuarios de prueba:
    - `ana` / `password123` (administrador)
    - `pedro` / `password456` (usuario normal)
    """,
    version="1.0.0",
)


# =============================================================================
# ENDPOINTS DE AUTENTICACIÓN
# =============================================================================

@app.post(
    "/auth/token",
    response_model=Token,
    tags=["Autenticación"],
    summary="Obtener token de acceso",
)
def login(
    # OAuth2PasswordRequestForm espera un form con campos 'username' y 'password'
    # Es el estándar OAuth2 — el cliente envía como application/x-www-form-urlencoded
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Endpoint de login — intercambia credenciales por un JWT.

    **Importante**: El body se envía como form data, no JSON.
    En Swagger UI usa el botón "Authorize" para hacer login.

    - **username**: nombre de usuario
    - **password**: contraseña
    """
    usuario = autenticar_usuario(form_data.username, form_data.password)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Creamos el token con 'sub' (subject) = username
    token = crear_access_token(
        datos={"sub": usuario["username"]},
        expira_en=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return Token(access_token=token)


@app.post(
    "/auth/registro",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
    tags=["Autenticación"],
)
def registrar_usuario(datos: RegistroRequest):
    """Registra un nuevo usuario en el sistema."""
    if datos.username in _usuarios_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El username '{datos.username}' ya existe.",
        )

    nuevo_usuario = {
        "username": datos.username,
        "nombre_completo": datos.nombre_completo,
        "email": datos.email,
        "hashed_password": hashear_password(datos.password),
        "activo": True,
        "es_admin": False,
    }

    _usuarios_db[datos.username] = nuevo_usuario
    return nuevo_usuario


# =============================================================================
# ENDPOINTS PROTEGIDOS
# =============================================================================

@app.get(
    "/auth/yo",
    response_model=UsuarioPublico,
    tags=["Usuarios"],
    summary="Mi perfil",
)
def obtener_mi_perfil(
    # Depends(obtener_usuario_actual) hace que este endpoint requiera auth
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Retorna el perfil del usuario autenticado.
    Requiere: Authorization: Bearer <token>
    """
    return usuario_actual


@app.get(
    "/usuarios",
    response_model=list[UsuarioPublico],
    tags=["Usuarios"],
    summary="Listar usuarios (solo admin)",
)
def listar_todos_usuarios(
    # Cadena de dependencias: primero verifica auth, luego verifica admin
    admin: dict = Depends(requerir_admin),
):
    """
    Lista todos los usuarios. Solo accesible para administradores.
    Requiere usuario con `es_admin=True`.
    """
    return list(_usuarios_db.values())


@app.get(
    "/privado",
    tags=["Ejemplo"],
    summary="Endpoint privado",
)
def ruta_privada(usuario: dict = Depends(obtener_usuario_actual)):
    """Cualquier usuario autenticado puede acceder."""
    return {
        "mensaje": f"Hola {usuario['nombre_completo']}! Este endpoint es privado.",
        "username": usuario["username"],
        "es_admin": usuario["es_admin"],
    }


@app.get(
    "/publico",
    tags=["Ejemplo"],
    summary="Endpoint público",
)
def ruta_publica():
    """Sin autenticación — cualquiera puede acceder."""
    return {"mensaje": "Este endpoint es público. No requiere token."}


# =============================================================================
# EJECUTAR
# =============================================================================

if __name__ == "__main__":
    dependencias_ok = FASTAPI_DISPONIBLE and JOSE_DISPONIBLE and PASSLIB_DISPONIBLE

    if not dependencias_ok:
        print("\nFaltan dependencias. Instala:")
        print('  pip install "fastapi[standard]" python-jose[cryptography] passlib[bcrypt]')
    else:
        import uvicorn
        print("Iniciando FastAPI con JWT Auth...")
        print("Docs: http://127.0.0.1:8000/docs")
        print("\nUsuarios de prueba:")
        print("  ana / password123 (admin)")
        print("  pedro / password456 (usuario normal)")
        uvicorn.run("05_fastapi_auth:app", host="127.0.0.1", port=8000, reload=True)
