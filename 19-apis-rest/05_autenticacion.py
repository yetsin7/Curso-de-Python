# =============================================================================
# CAPÍTULO 19 — APIs REST y Requests
# Archivo 05: Patrones de autenticación en APIs REST
# =============================================================================
# Por qué importa la autenticación: la mayoría de APIs en producción
# requieren identificar quién hace cada petición para controlar acceso,
# registrar uso y proteger datos sensibles.
#
# IMPORTANTE DE SEGURIDAD: NUNCA escribas credenciales directamente
# en el código fuente. Siempre usa variables de entorno.
#
# Instalación: pip install requests python-dotenv
# =============================================================================

try:
    import requests
except ImportError:
    print("ERROR: Instala requests con:  pip install requests")
    raise SystemExit(1)

import os           # Para acceder a variables de entorno
import base64       # Para codificar credenciales en Basic Auth
import json         # Para trabajar con respuestas JSON

# python-dotenv es opcional — solo para cargar archivos .env automáticamente
try:
    from dotenv import load_dotenv
    # Carga variables del archivo .env si existe en el directorio actual
    load_dotenv()
    print("dotenv cargado correctamente.")
except ImportError:
    # Si no está instalado, las variables de entorno del sistema igualmente
    # se leen con os.environ — dotenv solo facilita el desarrollo local
    print("Nota: python-dotenv no instalado (pip install python-dotenv).")
    print("Usando variables de entorno del sistema operativo.\n")


# =============================================================================
# PATRÓN 1: API Key en header
# =============================================================================

def demo_api_key_en_header() -> None:
    """
    Demuestra el patrón de autenticación con API Key en header HTTP.

    Por qué header y no query param: los headers no aparecen en logs
    del servidor web ni en el historial del navegador. Más seguro.
    El nombre del header varía por API: X-API-Key, api-key, X-Auth-Token...

    Usamos HTTPBin que acepta cualquier header y lo devuelve en la respuesta,
    lo que nos permite verificar que el header llegó correctamente.
    """
    print("\n--- Patrón 1: API Key en header ---")

    # Leemos la clave desde variable de entorno — NUNCA hardcodeada
    api_key = os.environ.get("MI_API_KEY", "demo_key_12345")

    if api_key == "demo_key_12345":
        print("  AVISO: Usando clave demo. En producción, configura MI_API_KEY.")

    headers = {
        # El nombre del header depende de la API — revisa su documentación
        "X-API-Key": api_key,
        "Accept": "application/json",
    }

    try:
        # HTTPBin /headers nos devuelve exactamente los headers que enviamos
        respuesta = requests.get(
            "https://httpbin.org/headers",
            headers=headers,
            timeout=10,
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

        # Verificamos que el header llegó al servidor
        header_recibido = datos.get("headers", {}).get("X-Api-Key", "NO RECIBIDO")
        print(f"  API Key enviada: {api_key[:8]}***")
        print(f"  Header recibido por servidor: {header_recibido[:8]}***")
        print("  Autenticación por header: OK")

    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")


# =============================================================================
# PATRÓN 2: API Key como query parameter
# =============================================================================

def demo_api_key_en_query_param() -> None:
    """
    Demuestra API Key como parámetro de URL (query param).

    Por qué a veces se usa: algunas APIs antiguas o simples la usan así.
    Es menos seguro que el header porque la URL puede quedar en logs.
    Ejemplo: Open-Meteo no usa key, pero otras APIs sí: ?api_key=xxx

    HTTPBin /get devuelve los query params recibidos.
    """
    print("\n--- Patrón 2: API Key en query param ---")

    api_key = os.environ.get("MI_API_KEY", "demo_key_12345")

    try:
        respuesta = requests.get(
            "https://httpbin.org/get",
            # params construye automáticamente ?api_key=valor en la URL
            params={"api_key": api_key, "formato": "json"},
            timeout=10,
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

        params_recibidos = datos.get("args", {})
        print(f"  URL usada: {respuesta.url.replace(api_key, '***OCULTA***')}")
        print(f"  Params recibidos: {list(params_recibidos.keys())}")
        print("  ADVERTENCIA: La URL con API Key puede quedar en logs del servidor.")

    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")


# =============================================================================
# PATRÓN 3: Bearer Token en Authorization header
# =============================================================================

def demo_bearer_token() -> None:
    """
    Demuestra autenticación con Bearer Token en el header Authorization.

    Por qué Bearer: es el estándar para OAuth2 y JWT. El token se obtiene
    normalmente haciendo login primero y luego se usa en peticiones.
    El formato exacto es: Authorization: Bearer <token>

    En este ejemplo simulamos tener un token y lo enviamos a HTTPBin
    para verificar que llega correctamente al servidor.
    """
    print("\n--- Patrón 3: Bearer Token ---")

    # En producción este token vendría de un proceso de login
    # o del archivo .env — nunca hardcodeado en el código
    token = os.environ.get("MI_BEARER_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo")

    headers = {
        # El formato estándar de Bearer Token — espaciado exacto importa
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    try:
        respuesta = requests.get(
            "https://httpbin.org/bearer",  # Endpoint especial de HTTPBin para Bearer
            headers=headers,
            timeout=10,
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

        print(f"  Token enviado: {token[:30]}...")
        print(f"  HTTPBin respuesta: authenticated={datos.get('authenticated')}")
        print(f"  Token recibido (truncado): {str(datos.get('token', ''))[:30]}...")

    except requests.exceptions.HTTPError as e:
        print(f"  Error HTTP {e.response.status_code}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")


# =============================================================================
# PATRÓN 4: HTTP Basic Authentication
# =============================================================================

def demo_basic_auth() -> None:
    """
    Demuestra autenticación HTTP Basic (usuario + contraseña).

    Por qué Basic Auth: es el mecanismo más simple. Las credenciales se
    codifican en Base64 (NO encriptadas — solo codificadas) y se envían
    en el header Authorization. SOLO seguro sobre HTTPS.

    requests tiene soporte nativo con el parámetro auth=(user, password).
    """
    print("\n--- Patrón 4: HTTP Basic Auth ---")

    # Leemos credenciales de variables de entorno
    usuario = os.environ.get("API_USUARIO", "usuario_demo")
    password = os.environ.get("API_PASSWORD", "contrasena_demo")

    # Cómo requests maneja Basic Auth internamente:
    # Codifica "usuario:password" en Base64 y lo pone en el header
    credenciales_raw = f"{usuario}:{password}"
    credenciales_b64 = base64.b64encode(credenciales_raw.encode()).decode()
    print(f"  Credenciales en Base64: {credenciales_b64}")
    print(f"  Header generado: Authorization: Basic {credenciales_b64}")

    try:
        # requests hace todo esto automáticamente con auth=(user, pass)
        respuesta = requests.get(
            "https://httpbin.org/basic-auth/usuario_demo/contrasena_demo",
            auth=(usuario, password),  # requests codifica en Base64 automáticamente
            timeout=10,
        )

        if respuesta.status_code == 200:
            datos = respuesta.json()
            print(f"  Autenticado: {datos.get('authenticated')}")
            print(f"  Usuario: {datos.get('user')}")
        elif respuesta.status_code == 401:
            print("  Error 401: Credenciales incorrectas.")
        else:
            print(f"  Status inesperado: {respuesta.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")


# =============================================================================
# PATRÓN 5: OAuth2 — flujo conceptual con código real
# =============================================================================

def explicar_oauth2_flow() -> None:
    """
    Explica el flujo OAuth2 Authorization Code con código real donde es posible.

    Por qué OAuth2: es el estándar para delegar autorización sin compartir
    contraseñas. "Iniciar sesión con Google/GitHub" usa OAuth2.

    El flujo completo requiere un servidor real. Aquí mostramos las partes
    del flujo con código Python y comentarios detallados.
    """
    print("\n--- Patrón 5: OAuth2 — flujo Authorization Code ---")

    print("""
  FLUJO OAUTH2 AUTHORIZATION CODE (conceptual):

  1. Tu app redirige al usuario a la página de autorización del proveedor:
     https://github.com/login/oauth/authorize
       ?client_id=TU_CLIENT_ID
       &redirect_uri=https://tuapp.com/callback
       &scope=user:email
       &state=VALOR_ALEATORIO_CSRF

  2. El usuario acepta → el proveedor redirige a:
     https://tuapp.com/callback?code=CODIGO_TEMPORAL&state=VALOR_CSRF

  3. Tu servidor (backend) intercambia el código por un token:
     POST https://github.com/login/oauth/access_token
     Body: client_id, client_secret, code, redirect_uri

  4. Recibes el access_token y lo guardas de forma segura.

  5. Usas el access_token para hacer peticiones en nombre del usuario:
     GET https://api.github.com/user
     Authorization: Bearer ACCESS_TOKEN_AQUI
    """)

    # Simulamos el paso 3 — intercambiar código por token
    # (En producción esto se hace en el servidor, nunca en el cliente)
    print("  Simulación del paso 3 — intercambio de código por token:")

    # Variables que vendrían de variables de entorno en producción
    client_id = os.environ.get("GITHUB_CLIENT_ID", "Iv1.demo_client_id")
    client_secret = os.environ.get("GITHUB_CLIENT_SECRET", "demo_secret")
    codigo_temporal = "codigo_del_callback_123"  # Vendría del redirect

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": codigo_temporal,
    }

    print(f"  POST a token endpoint con payload:")
    print(f"    client_id: {client_id[:15]}...")
    print(f"    client_secret: ***OCULTO***")
    print(f"    code: {codigo_temporal}")
    print("""
  En un flujo real recibirías:
    access_token: gho_xxxxxxxxxxxxxxxxxxxx
    token_type: bearer
    scope: user:email

  Luego usarías ese token como Bearer Token (Patrón 3).
    """)


# =============================================================================
# PATRÓN 6: Uso seguro de variables de entorno con .env
# =============================================================================

def demo_variables_entorno() -> None:
    """
    Demuestra las buenas prácticas para manejar credenciales con variables
    de entorno y archivos .env.

    Por qué variables de entorno:
    - El código fuente puede compartirse (GitHub) — las claves NO deben estar ahí
    - Cada ambiente (dev, staging, prod) tiene sus propias claves
    - Las herramientas de CI/CD las inyectan de forma segura

    Estructura de un archivo .env (NUNCA lo subas a git):
    MI_API_KEY=tu_clave_aqui
    MI_BEARER_TOKEN=tu_token_aqui
    API_USUARIO=tu_usuario
    API_PASSWORD=tu_password

    En .gitignore siempre agrega: .env
    """
    print("\n--- Buenas prácticas: variables de entorno ---")

    # Ejemplo de cómo leer credenciales de forma segura
    claves_configuracion = {
        "API_KEY": os.environ.get("MI_API_KEY"),
        "TOKEN": os.environ.get("MI_BEARER_TOKEN"),
        "USUARIO": os.environ.get("API_USUARIO"),
    }

    print("  Variables de entorno configuradas:")
    for nombre, valor in claves_configuracion.items():
        if valor:
            # Mostramos solo los primeros caracteres para verificar que existe
            print(f"    {nombre}: {valor[:6]}*** (configurada)")
        else:
            print(f"    {nombre}: NO CONFIGURADA")

    print("""
  Cómo configurar variables de entorno:

  En Linux/Mac (terminal):
    export MI_API_KEY="tu_clave_aqui"

  En Windows (PowerShell):
    $env:MI_API_KEY = "tu_clave_aqui"

  Con archivo .env (requiere python-dotenv):
    pip install python-dotenv
    Crear archivo .env con: MI_API_KEY=tu_clave
    En el código: from dotenv import load_dotenv; load_dotenv()

  REGLAS DE ORO:
    1. NUNCA escribas credenciales directamente en el código
    2. SIEMPRE agrega .env a tu .gitignore
    3. Crea un archivo .env.example sin valores reales para documentar
    4. Usa gestores de secretos (AWS Secrets Manager, Vault) en producción
    """)


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PATRONES DE AUTENTICACIÓN EN APIs REST")
    print("=" * 60)

    demo_api_key_en_header()
    demo_api_key_en_query_param()
    demo_bearer_token()
    demo_basic_auth()
    explicar_oauth2_flow()
    demo_variables_entorno()

    print("\n" + "=" * 60)
    print("RESUMEN DE PATRONES:")
    print("  1. API Key en header    → X-API-Key: tu_clave")
    print("  2. API Key en URL       → ?api_key=tu_clave  (menos seguro)")
    print("  3. Bearer Token         → Authorization: Bearer token")
    print("  4. Basic Auth           → Authorization: Basic b64(user:pass)")
    print("  5. OAuth2               → Flujo de 3 pasos con redirect")
    print("  Regla universal: credenciales siempre en variables de entorno")
    print("=" * 60)
