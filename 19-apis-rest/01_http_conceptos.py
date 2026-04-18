# =============================================================================
# CAPÍTULO 19 — APIs REST y Requests
# Archivo 01: Conceptos HTTP con urllib (módulo nativo de Python)
# =============================================================================
# Por qué usar urllib aquí: es el módulo estándar de Python para HTTP.
# No requiere instalar nada. Es útil para entender los conceptos base
# antes de usar librerías de alto nivel como requests.
# =============================================================================

import urllib.request    # Para hacer peticiones HTTP
import urllib.parse      # Para codificar parámetros de URL
import urllib.error      # Para capturar errores HTTP específicos
import json              # Para parsear las respuestas JSON
import ssl               # Para configurar contexto SSL si es necesario

# =============================================================================
# SECCIÓN 1: GET básico
# =============================================================================

def hacer_get_simple(url: str) -> dict | None:
    """
    Realiza una petición GET simple a una URL y devuelve el JSON parseado.

    Por qué: es la operación más común en APIs REST — solo leer datos.
    urllib.request.urlopen abre la URL y retorna un objeto tipo archivo.

    Args:
        url: La URL completa del endpoint a consultar.

    Returns:
        Un diccionario con la respuesta JSON, o None si hubo error.
    """
    try:
        # urllib.request.urlopen devuelve un objeto HTTPResponse
        # El bloque with garantiza que la conexión se cierre correctamente
        with urllib.request.urlopen(url, timeout=10) as respuesta:
            # El status code indica si la petición fue exitosa
            codigo = respuesta.getcode()
            print(f"  Status code: {codigo}")

            # La respuesta llega como bytes — hay que decodificarla a texto
            # UTF-8 es la codificación estándar en APIs REST modernas
            contenido_bytes = respuesta.read()
            contenido_texto = contenido_bytes.decode("utf-8")

            # json.loads convierte el string JSON a un diccionario Python
            datos = json.loads(contenido_texto)
            return datos

    except urllib.error.HTTPError as e:
        # HTTPError ocurre cuando el servidor responde con un código de error
        # (4xx cliente, 5xx servidor). El objeto 'e' tiene el código y razón.
        print(f"  Error HTTP {e.code}: {e.reason}")
        return None

    except urllib.error.URLError as e:
        # URLError ocurre cuando no se puede conectar al servidor
        # (sin internet, DNS fallido, timeout de conexión, etc.)
        print(f"  Error de conexión: {e.reason}")
        return None


# =============================================================================
# SECCIÓN 2: GET con parámetros de query
# =============================================================================

def hacer_get_con_parametros(url_base: str, parametros: dict) -> dict | None:
    """
    Realiza una petición GET con parámetros codificados en la URL.

    Por qué: muchas APIs reciben filtros y opciones como query params.
    urllib.parse.urlencode convierte el dict a formato ?clave=valor&clave2=valor2
    y maneja el escape de caracteres especiales automáticamente.

    Args:
        url_base: La URL base del endpoint sin parámetros.
        parametros: Diccionario con los parámetros a enviar.

    Returns:
        Un diccionario con la respuesta JSON, o None si hubo error.
    """
    # urlencode toma un dict y genera una cadena de query string
    # Ejemplo: {"q": "python", "per_page": 5} → "q=python&per_page=5"
    query_string = urllib.parse.urlencode(parametros)

    # Construimos la URL completa uniendo la base con los parámetros
    url_completa = f"{url_base}?{query_string}"
    print(f"  URL construida: {url_completa}")

    return hacer_get_simple(url_completa)


# =============================================================================
# SECCIÓN 3: GET con headers personalizados
# =============================================================================

def hacer_get_con_headers(url: str, headers: dict) -> dict | None:
    """
    Realiza una petición GET enviando headers HTTP personalizados.

    Por qué: los headers permiten enviar metadatos como el tipo de contenido
    esperado, tokens de autenticación, versión de la API, idioma, etc.
    Con urllib hay que crear un objeto Request explícito para añadir headers.

    Args:
        url: La URL del endpoint.
        headers: Diccionario con los headers a incluir en la petición.

    Returns:
        Un diccionario con la respuesta JSON, o None si hubo error.
    """
    # urllib.request.Request encapsula la URL y los headers juntos
    # Por defecto el método es GET cuando no se especifica data
    peticion = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(peticion, timeout=10) as respuesta:
            # Podemos leer los headers de respuesta también
            headers_respuesta = dict(respuesta.headers)
            tipo_contenido = headers_respuesta.get("Content-Type", "desconocido")
            print(f"  Content-Type de respuesta: {tipo_contenido}")

            datos = json.loads(respuesta.read().decode("utf-8"))
            return datos

    except urllib.error.HTTPError as e:
        print(f"  Error HTTP {e.code}: {e.reason}")
        # Algunos errores incluyen un cuerpo con detalles — intentamos leerlo
        try:
            detalle = e.read().decode("utf-8")
            print(f"  Detalle del error: {detalle[:200]}")
        except Exception:
            pass
        return None

    except urllib.error.URLError as e:
        print(f"  Error de conexión: {e.reason}")
        return None


# =============================================================================
# SECCIÓN 4: POST con cuerpo JSON
# =============================================================================

def hacer_post_json(url: str, datos: dict, headers_extra: dict | None = None) -> dict | None:
    """
    Realiza una petición POST enviando datos en formato JSON.

    Por qué: POST se usa para crear nuevos recursos. El cuerpo de la petición
    lleva los datos del nuevo objeto en JSON. urllib requiere codificar
    manualmente los datos y especificar el Content-Type.

    Args:
        url: La URL del endpoint donde crear el recurso.
        datos: Diccionario con los datos del nuevo recurso.
        headers_extra: Headers adicionales opcionales.

    Returns:
        Un diccionario con la respuesta del servidor, o None si hubo error.
    """
    # Convertimos el dict Python a una cadena JSON
    cuerpo_json = json.dumps(datos)

    # El cuerpo HTTP debe ser bytes, no string
    cuerpo_bytes = cuerpo_json.encode("utf-8")

    # Los headers base necesarios para enviar JSON
    headers = {
        # Content-Type le dice al servidor qué formato estamos enviando
        "Content-Type": "application/json",
        # Accept le dice al servidor qué formato queremos recibir
        "Accept": "application/json",
        # User-Agent identifica nuestro cliente (buena práctica)
        "User-Agent": "LibroPython/1.0 (aprendizaje)",
    }

    # Añadimos cualquier header extra proporcionado
    if headers_extra:
        headers.update(headers_extra)

    # Cuando se pasa 'data' a Request, automáticamente usa método POST
    peticion = urllib.request.Request(url, data=cuerpo_bytes, headers=headers)

    try:
        with urllib.request.urlopen(peticion, timeout=10) as respuesta:
            codigo = respuesta.getcode()
            print(f"  Status code: {codigo}")
            # 201 Created es el código esperado cuando se crea un recurso
            if codigo == 201:
                print("  Recurso creado exitosamente.")
            datos_respuesta = json.loads(respuesta.read().decode("utf-8"))
            return datos_respuesta

    except urllib.error.HTTPError as e:
        print(f"  Error HTTP {e.code}: {e.reason}")
        try:
            detalle = e.read().decode("utf-8")
            print(f"  Detalle: {detalle[:300]}")
        except Exception:
            pass
        return None

    except urllib.error.URLError as e:
        print(f"  Error de conexión: {e.reason}")
        return None


# =============================================================================
# SECCIÓN 5: Manejo detallado de errores HTTP por código
# =============================================================================

def demostrar_errores_http() -> None:
    """
    Demuestra cómo se comportan distintos códigos de error HTTP.

    Por qué: entender los códigos de error permite dar feedback claro
    al usuario y decidir si reintentar, redirigir o mostrar un mensaje.
    HTTPBin tiene endpoints especiales que retornan cualquier código.
    """
    # Códigos de error comunes que queremos demostrar
    codigos_a_probar = [
        (404, "Recurso no encontrado"),
        (500, "Error interno del servidor"),
        (401, "No autorizado"),
        (403, "Acceso prohibido"),
    ]

    for codigo, descripcion in codigos_a_probar:
        # HTTPBin tiene el endpoint /status/{code} que retorna ese código
        url = f"https://httpbin.org/status/{codigo}"
        print(f"\n  Probando error {codigo} ({descripcion}):")
        print(f"  URL: {url}")

        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                print(f"  Respuesta inesperadamente exitosa: {r.getcode()}")

        except urllib.error.HTTPError as e:
            # Diferenciamos el comportamiento según el tipo de error
            if e.code == 400:
                print("  → Datos de la petición incorrectos. Revisa el body/params.")
            elif e.code == 401:
                print("  → Necesitas autenticarte. Incluye un token válido.")
            elif e.code == 403:
                print("  → No tienes permisos para este recurso.")
            elif e.code == 404:
                print("  → El recurso no existe. Verifica la URL.")
            elif e.code >= 500:
                print("  → Error en el servidor. No es tu culpa. Intenta más tarde.")
            else:
                print(f"  → Error {e.code}: {e.reason}")

        except urllib.error.URLError as e:
            print(f"  Error de conexión: {e.reason}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CONCEPTOS HTTP CON URLLIB (módulo nativo de Python)")
    print("=" * 60)

    # --- Ejemplo 1: GET simple a la API de GitHub ---
    print("\n[1] GET simple — Información de un usuario en GitHub:")
    # La API de GitHub es pública para leer info básica (sin auth)
    resultado = hacer_get_simple("https://api.github.com/users/torvalds")
    if resultado:
        print(f"  Nombre: {resultado.get('name')}")
        print(f"  Seguidores: {resultado.get('followers')}")
        print(f"  Repos públicos: {resultado.get('public_repos')}")

    # --- Ejemplo 2: GET con parámetros ---
    print("\n[2] GET con parámetros — Buscar repos en GitHub:")
    resultado = hacer_get_con_parametros(
        "https://api.github.com/search/repositories",
        {"q": "python tutorial", "sort": "stars", "per_page": 3},
    )
    if resultado:
        items = resultado.get("items", [])
        print(f"  Encontrados (mostrando 3):")
        for repo in items[:3]:
            print(f"    - {repo['full_name']} ⭐ {repo['stargazers_count']}")

    # --- Ejemplo 3: GET con headers ---
    print("\n[3] GET con headers personalizados — HTTPBin:")
    # HTTPBin /headers devuelve los headers que recibió — ideal para verificar
    resultado = hacer_get_con_headers(
        "https://httpbin.org/headers",
        {
            "User-Agent": "LibroPython/1.0",
            "Accept": "application/json",
            "X-Custom-Header": "valor-personalizado",
        },
    )
    if resultado:
        headers_recibidos = resultado.get("headers", {})
        print(f"  Headers recibidos por el servidor:")
        for k, v in headers_recibidos.items():
            print(f"    {k}: {v}")

    # --- Ejemplo 4: POST con JSON ---
    print("\n[4] POST con body JSON — JSONPlaceholder (API de prueba):")
    # JSONPlaceholder simula operaciones CRUD — no guarda los datos realmente
    nuevo_post = {
        "title": "Mi primer post desde Python",
        "body": "Aprendiendo a consumir APIs REST con urllib",
        "userId": 1,
    }
    resultado = hacer_post_json(
        "https://jsonplaceholder.typicode.com/posts",
        nuevo_post,
    )
    if resultado:
        print(f"  Post creado con ID: {resultado.get('id')}")
        print(f"  Título: {resultado.get('title')}")

    # --- Ejemplo 5: Errores HTTP ---
    print("\n[5] Demostración de errores HTTP:")
    demostrar_errores_http()

    print("\n" + "=" * 60)
    print("Fin del ejemplo urllib — siguiente: 02_requests_avanzado.py")
    print("=" * 60)
