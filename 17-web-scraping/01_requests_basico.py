# =============================================================================
# 01_requests_basico.py — La librería requests para peticiones HTTP
# =============================================================================
# requests es la librería HTTP más popular de Python.
# Hace que interactuar con servidores web sea sencillo y elegante.
#
# Instalación:
#   pip install requests
#
# Este archivo usa httpbin.org — un servicio público diseñado especialmente
# para probar peticiones HTTP. No hacemos scraping real, solo probamos
# la librería requests de forma confiable y ética.
#
# Contenido:
#   - GET básico y con parámetros
#   - POST con datos
#   - Headers personalizados
#   - Manejo de errores HTTP
#   - Sesiones para reutilizar conexiones
#   - Timeout para evitar bloqueos
#   - Respuestas JSON
# =============================================================================

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

import json


# =============================================================================
# VERIFICACIÓN DE INSTALACIÓN
# =============================================================================

def check_requests():
    """
    Verifica que requests esté instalado.

    Retorna:
        bool: True si está disponible, False si no
    """
    if not REQUESTS_AVAILABLE:
        print("=" * 55)
        print("  La librería 'requests' no está instalada.")
        print("=" * 55)
        print("\nInstala con:")
        print("    pip install requests")
        return False
    return True


# =============================================================================
# GET BÁSICO
# =============================================================================

def demo_get_basico():
    """
    Demuestra una petición GET simple.

    GET es el método HTTP para obtener datos.
    Es el que usa tu navegador cuando visitas una URL.
    La respuesta incluye el código de estado, headers y el cuerpo (body).
    """
    print("\n--- GET Básico ---")

    # httpbin.org/get devuelve información sobre la petición que hicimos
    url = "https://httpbin.org/get"

    try:
        # timeout evita que el programa se quede esperando para siempre
        # Si el servidor no responde en 10 segundos, lanza Timeout exception
        response = requests.get(url, timeout=10)

        # status_code indica el resultado de la petición
        # 200 = éxito, 404 = no encontrado, 500 = error del servidor
        print(f"  URL: {url}")
        print(f"  Status code: {response.status_code}")
        print(f"  Tipo de contenido: {response.headers.get('Content-Type', 'N/A')}")

        # raise_for_status() lanza una excepción si el código no es 2xx
        # Es la forma más limpia de verificar que la petición fue exitosa
        response.raise_for_status()

        # .json() parsea el body JSON automáticamente a diccionario Python
        data = response.json()
        print(f"  IP del servidor de origen: {data.get('origin', 'N/A')}")
        print(f"  URL devuelta: {data.get('url', 'N/A')}")

    except requests.exceptions.ConnectionError:
        print("  Error: No se pudo conectar. Verifica tu conexión a internet.")
    except requests.exceptions.Timeout:
        print("  Error: La petición tardó demasiado (timeout).")
    except requests.exceptions.HTTPError as e:
        print(f"  Error HTTP: {e}")


# =============================================================================
# GET CON PARÁMETROS
# =============================================================================

def demo_get_con_params():
    """
    Demuestra cómo enviar parámetros en una petición GET.

    Los parámetros GET se añaden a la URL como query string:
    https://api.com/search?q=python&limit=10&page=1

    Con requests, pasas los parámetros como diccionario
    y la librería construye la URL correctamente (con encoding incluido).
    """
    print("\n--- GET con Parámetros ---")

    # httpbin.org/get devuelve los parámetros que le enviamos
    url = "https://httpbin.org/get"

    params = {
        "q": "python tutorial",   # palabra de búsqueda (con espacio)
        "limit": 10,
        "page": 1,
        "lang": "es"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Verificamos que los parámetros llegaron correctamente al servidor
        print(f"  URL construida: {response.url}")
        print(f"  Parámetros recibidos por el servidor:")
        for key, value in data.get("args", {}).items():
            print(f"    {key}: {value}")

    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")


# =============================================================================
# POST CON DATOS
# =============================================================================

def demo_post():
    """
    Demuestra peticiones POST para enviar datos al servidor.

    POST se usa cuando enviamos datos que el servidor debe procesar:
    formularios de login, crear recursos, enviar archivos, etc.

    Diferencia con GET:
    - GET: los datos van en la URL (visibles, limitados en tamaño)
    - POST: los datos van en el body (ocultos, sin límite de tamaño)
    """
    print("\n--- POST: Enviar Datos ---")

    url = "https://httpbin.org/post"

    # Datos de formulario (application/x-www-form-urlencoded)
    form_data = {
        "username": "usuario_demo",
        "email": "demo@example.com",
        "action": "register"
    }

    try:
        # data= envía como formulario HTML
        response = requests.post(url, data=form_data, timeout=10)
        response.raise_for_status()

        data = response.json()
        print("  POST con datos de formulario:")
        print(f"    Datos recibidos: {data.get('form', {})}")

        # También podemos enviar JSON directamente
        json_payload = {
            "user": {
                "name": "Ana García",
                "age": 30,
                "skills": ["Python", "SQL", "Git"]
            },
            "action": "create_user"
        }

        # json= serializa el diccionario a JSON y añade Content-Type: application/json
        response_json = requests.post(url, json=json_payload, timeout=10)
        response_json.raise_for_status()

        data_json = response_json.json()
        print("\n  POST con payload JSON:")
        received_json = json.loads(data_json.get("data", "{}"))
        print(f"    Usuario enviado: {received_json.get('user', {}).get('name', 'N/A')}")
        print(f"    Skills: {received_json.get('user', {}).get('skills', [])}")

    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")


# =============================================================================
# HEADERS PERSONALIZADOS
# =============================================================================

def demo_headers():
    """
    Demuestra cómo enviar headers personalizados en las peticiones.

    Los headers HTTP son metadatos de la petición:
    - User-Agent: identifica quién hace la petición
    - Authorization: tokens de autenticación
    - Accept: qué tipo de contenido acepta el cliente
    - Content-Type: qué tipo de datos envía el cliente

    En scraping, el User-Agent es importante: muchos sitios bloquean
    peticiones que no simulan un navegador real.
    """
    print("\n--- Headers Personalizados ---")

    url = "https://httpbin.org/headers"

    # Simulamos ser un navegador Chrome para evitar bloqueos simples
    custom_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/json",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "X-Custom-Header": "mi-scraper-educativo",
    }

    try:
        response = requests.get(url, headers=custom_headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        received_headers = data.get("headers", {})
        print("  Headers enviados y recibidos por el servidor:")
        for header_name in ["User-Agent", "Accept", "Accept-Language", "X-Custom-Header"]:
            value = received_headers.get(header_name, "NO RECIBIDO")
            # Truncamos el User-Agent para que quepa en pantalla
            if len(value) > 50:
                value = value[:50] + "..."
            print(f"    {header_name}: {value}")

    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")


# =============================================================================
# MANEJO COMPLETO DE ERRORES HTTP
# =============================================================================

def demo_manejo_errores():
    """
    Demuestra el manejo de los distintos tipos de errores HTTP.

    Códigos HTTP importantes para scraping:
    - 200: OK — todo bien
    - 301/302: Redirect — la página se movió (requests lo maneja automáticamente)
    - 403: Forbidden — acceso denegado (quizás bloqueó el bot)
    - 404: Not Found — la página no existe
    - 429: Too Many Requests — demasiadas peticiones (rate limiting)
    - 500: Internal Server Error — error del servidor
    """
    print("\n--- Manejo de Errores HTTP ---")

    # httpbin.org/status/{codigo} devuelve el código que le pedimos
    test_cases = [
        (200, "Éxito"),
        (404, "No encontrado"),
        (403, "Acceso denegado"),
        (500, "Error del servidor"),
    ]

    for status_code, description in test_cases:
        url = f"https://httpbin.org/status/{status_code}"

        try:
            response = requests.get(url, timeout=10)

            # raise_for_status() lanza HTTPError para códigos 4xx y 5xx
            response.raise_for_status()

            print(f"  {status_code} ({description}): OK")

        except requests.exceptions.HTTPError as e:
            # e.response.status_code tiene el código exacto
            print(f"  {status_code} ({description}): HTTPError — {e}")

        except requests.exceptions.ConnectionError:
            print(f"  {status_code}: Error de conexión")

        except requests.exceptions.Timeout:
            print(f"  {status_code}: Timeout — servidor no respondió")

        except requests.exceptions.RequestException as e:
            # RequestException es la clase base de todos los errores de requests
            print(f"  {status_code}: Error inesperado — {e}")


# =============================================================================
# SESIONES — Reutilizar conexiones y cookies
# =============================================================================

def demo_session():
    """
    Demuestra el uso de Session para reutilizar conexiones y headers.

    Una Session permite:
    1. Reutilizar la conexión TCP (más rápido que crear una nueva por petición)
    2. Mantener cookies automáticamente entre peticiones
    3. Configurar headers/params que se aplican a todas las peticiones
    4. Autenticación persistente

    Ideal para scraping de múltiples páginas del mismo sitio.
    """
    print("\n--- Session: Reutilizar Conexión ---")

    # Crear una sesión compartida
    with requests.Session() as session:

        # Configurar headers que se aplicarán a TODAS las peticiones de la sesión
        session.headers.update({
            "User-Agent": "Python-Scraper-Educativo/1.0",
            "Accept": "application/json",
        })

        # Primera petición — establece la conexión
        try:
            response1 = session.get("https://httpbin.org/get", timeout=10)
            response1.raise_for_status()
            data1 = response1.json()
            print(f"  Petición 1 - Headers enviados: {list(data1['headers'].keys())}")

            # Segunda petición — reutiliza la conexión establecida
            response2 = session.get(
                "https://httpbin.org/get",
                params={"desde_sesion": "true"},
                timeout=10
            )
            response2.raise_for_status()
            data2 = response2.json()
            print(f"  Petición 2 - Parámetros: {data2.get('args', {})}")

            print("  Ambas peticiones usaron la misma sesión y headers.")

        except requests.exceptions.RequestException as e:
            print(f"  Error en sesión: {e}")


# =============================================================================
# RESPUESTAS JSON — La base de las APIs modernas
# =============================================================================

def demo_json_response():
    """
    Demuestra el manejo de respuestas JSON, el formato estándar de las APIs.

    La mayoría de APIs web modernas devuelven JSON.
    requests tiene soporte nativo para parsear JSON automáticamente.
    """
    print("\n--- Respuestas JSON ---")

    # httpbin.org/json devuelve un JSON de ejemplo
    url = "https://httpbin.org/json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Verificar que la respuesta es JSON antes de parsear
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type or "json" in content_type:
            data = response.json()
            print(f"  Tipo de contenido: {content_type}")
            print(f"  Datos recibidos (primeras 2 claves):")

            # Mostrar las primeras claves del JSON de respuesta
            for key in list(data.keys())[:2]:
                value = data[key]
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"    {key}: {value}")
        else:
            print(f"  La respuesta no es JSON: {content_type}")
            print(f"  Contenido (primeros 100 chars): {response.text[:100]}")

    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")
    except json.JSONDecodeError:
        print("  Error: La respuesta no es JSON válido.")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal que ejecuta todas las demostraciones de requests."""

    if not check_requests():
        return

    print("=" * 55)
    print("  DEMO: requests — Peticiones HTTP con Python")
    print("=" * 55)
    print("\nUsando httpbin.org para pruebas seguras y éticas.")
    print("httpbin.org es un servicio diseñado para probar HTTP.")

    demo_get_basico()
    demo_get_con_params()
    demo_post()
    demo_headers()
    demo_manejo_errores()
    demo_session()
    demo_json_response()

    print("\n" + "=" * 55)
    print("  Todas las demostraciones completadas.")
    print("=" * 55)


if __name__ == "__main__":
    main()
