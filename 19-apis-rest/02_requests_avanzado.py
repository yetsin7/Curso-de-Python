# =============================================================================
# CAPÍTULO 19 — APIs REST y Requests
# Archivo 02: La librería requests — uso avanzado con APIs reales
# =============================================================================
# Por qué requests: es la librería HTTP más popular de Python.
# Simplifica enormemente lo que urllib hace manualmente:
# codificación, headers, JSON, cookies, autenticación, etc.
#
# Instalación: pip install requests
# =============================================================================

try:
    import requests
    from requests.adapters import HTTPAdapter
    # urllib3 viene incluido con requests — no requiere instalación aparte
    from urllib3.util.retry import Retry
except ImportError:
    print("ERROR: La librería 'requests' no está instalada.")
    print("Solución: ejecuta  pip install requests  en tu terminal.")
    raise SystemExit(1)

import time   # Para medir tiempos de respuesta y rate limiting

# =============================================================================
# SECCIÓN 1: GET básico con requests — mucho más simple que urllib
# =============================================================================

def ejemplo_get_basico() -> None:
    """
    Demuestra la simplicidad de requests vs urllib para GET.

    Por qué: requests.get() hace todo automáticamente — conexión,
    decodificación, manejo de cookies, redirecciones, etc.
    El método .json() parsea automáticamente la respuesta.
    """
    print("\n--- GET básico con requests ---")

    # Una sola línea reemplaza todo el código de urllib
    respuesta = requests.get(
        "https://jsonplaceholder.typicode.com/posts/1",
        timeout=10,  # Siempre especifica timeout para evitar colgadas
    )

    # raise_for_status() lanza HTTPError si el código es 4xx o 5xx
    # Es la forma idiomática de verificar errores en requests
    respuesta.raise_for_status()

    # .json() decodifica automáticamente el body JSON a dict Python
    datos = respuesta.json()
    print(f"  Status: {respuesta.status_code}")
    print(f"  Título del post: {datos['title']}")
    print(f"  Tiempo de respuesta: {respuesta.elapsed.total_seconds():.3f}s")


# =============================================================================
# SECCIÓN 2: Session — reutilizar conexión y headers
# =============================================================================

def ejemplo_session() -> None:
    """
    Demuestra el uso de requests.Session para múltiples peticiones.

    Por qué usar Session:
    - Reutiliza la conexión TCP (más eficiente — menos latencia)
    - Mantiene headers y cookies entre peticiones automáticamente
    - Ideal cuando haces varias peticiones al mismo servidor
    - Permite configurar defaults una sola vez
    """
    print("\n--- Session con headers persistentes ---")

    # Creamos una session — todas las peticiones desde aquí heredan la config
    with requests.Session() as session:
        # Configuramos headers que se enviarán en TODAS las peticiones
        session.headers.update({
            "User-Agent": "LibroPython/1.0 (aprendizaje de APIs)",
            "Accept": "application/json",
        })

        # Primera petición — los headers ya están configurados
        r1 = session.get("https://jsonplaceholder.typicode.com/users/1", timeout=10)
        r1.raise_for_status()
        usuario = r1.json()
        print(f"  Usuario: {usuario['name']} ({usuario['email']})")

        # Segunda petición — misma sesión, mismos headers, sin reconfigurar
        r2 = session.get(
            "https://jsonplaceholder.typicode.com/posts",
            params={"userId": 1},  # params se codifica automáticamente
            timeout=10,
        )
        r2.raise_for_status()
        posts = r2.json()
        print(f"  Posts del usuario: {len(posts)}")
        print(f"  Primer post: {posts[0]['title'][:50]}...")


# =============================================================================
# SECCIÓN 3: Retry automático con urllib3
# =============================================================================

def crear_session_con_retry(
    max_reintentos: int = 3,
    backoff_factor: float = 0.5,
) -> requests.Session:
    """
    Crea una Session configurada para reintentar automáticamente ante fallos.

    Por qué: las redes son poco confiables. Un timeout o error 503 transitorio
    no debería romper tu programa. El retry automático lo maneja internamente.

    backoff_factor: tiempo de espera entre reintentos (0.5 → 0s, 1s, 2s...)
    Los códigos 500, 502, 503, 504 son errores del servidor que vale reintentar.

    Args:
        max_reintentos: Número máximo de reintentos por petición.
        backoff_factor: Factor multiplicador para el tiempo de espera.

    Returns:
        Session configurada con retry automático.
    """
    session = requests.Session()

    # Retry define cuándo y cómo reintentar
    retry_strategy = Retry(
        total=max_reintentos,               # Máximo de reintentos totales
        backoff_factor=backoff_factor,       # Espera exponencial entre reintentos
        status_forcelist=[500, 502, 503, 504],  # Códigos que activan el retry
        allowed_methods=["GET", "POST", "PUT", "DELETE"],  # Métodos que se reintentan
    )

    # HTTPAdapter aplica la estrategia tanto a HTTP como a HTTPS
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


# =============================================================================
# SECCIÓN 4: Consumir la API de clima Open-Meteo (gratis, sin auth)
# =============================================================================

def obtener_clima(latitud: float, longitud: float, ciudad: str = "") -> None:
    """
    Consulta el clima actual usando la API Open-Meteo.

    Por qué esta API: es completamente gratuita, sin registro ni API key.
    Ideal para practicar con datos reales e interesantes.

    Open-Meteo devuelve temperatura, velocidad del viento y código de clima.
    Los códigos WMO (World Meteorological Organization) indican el estado.

    Args:
        latitud: Coordenada de latitud de la ubicación.
        longitud: Coordenada de longitud de la ubicación.
        ciudad: Nombre de la ciudad (solo para mostrar en pantalla).
    """
    print(f"\n--- Clima actual en {ciudad or f'({latitud}, {longitud})'} ---")

    url = "https://api.open-meteo.com/v1/forecast"
    parametros = {
        "latitude": latitud,
        "longitude": longitud,
        # Qué variables queremos en la respuesta
        "current": "temperature_2m,wind_speed_10m,weather_code",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "timezone": "auto",  # Detecta zona horaria automáticamente
    }

    try:
        session = crear_session_con_retry()
        respuesta = session.get(url, params=parametros, timeout=15)
        respuesta.raise_for_status()

        datos = respuesta.json()
        actual = datos.get("current", {})

        temperatura = actual.get("temperature_2m")
        viento = actual.get("wind_speed_10m")
        codigo_clima = actual.get("weather_code")

        # Interpretación básica del código WMO
        descripcion = interpretar_codigo_wmo(codigo_clima)

        print(f"  Temperatura: {temperatura}°C")
        print(f"  Viento: {viento} km/h")
        print(f"  Condición: {descripcion} (código WMO: {codigo_clima})")

    except requests.exceptions.RequestException as e:
        print(f"  Error al obtener clima: {e}")


def interpretar_codigo_wmo(codigo: int | None) -> str:
    """
    Traduce un código WMO a una descripción legible.

    Los códigos WMO son estándar internacional para describir condiciones
    meteorológicas. Open-Meteo los usa en su respuesta.

    Args:
        codigo: Código WMO del estado del clima.

    Returns:
        Descripción textual del clima.
    """
    if codigo is None:
        return "Desconocido"

    # Mapa simplificado de códigos WMO más comunes
    codigos = {
        0: "Cielo despejado",
        1: "Principalmente despejado",
        2: "Parcialmente nublado",
        3: "Nublado",
        45: "Niebla",
        48: "Niebla con escarcha",
        51: "Llovizna ligera",
        61: "Lluvia ligera",
        63: "Lluvia moderada",
        65: "Lluvia intensa",
        71: "Nieve ligera",
        80: "Chubascos ligeros",
        95: "Tormenta",
    }
    return codigos.get(codigo, f"Código {codigo}")


# =============================================================================
# SECCIÓN 5: Consumir REST Countries
# =============================================================================

def obtener_info_pais(nombre_pais: str) -> None:
    """
    Obtiene información detallada de un país usando la API REST Countries.

    Por qué: esta API devuelve datos complejos y anidados, ideal para practicar
    el acceso a estructuras JSON profundas con .get() seguro.

    Args:
        nombre_pais: Nombre del país en inglés o español.
    """
    print(f"\n--- Información de {nombre_pais} ---")

    url = f"https://restcountries.com/v3.1/name/{nombre_pais}"
    parametros = {
        # Pedimos solo los campos que necesitamos (más eficiente)
        "fields": "name,population,capital,area,languages,currencies,flags",
    }

    try:
        respuesta = requests.get(url, params=parametros, timeout=10)
        respuesta.raise_for_status()

        # La API devuelve una lista — tomamos el primer resultado
        paises = respuesta.json()
        pais = paises[0]

        nombre_oficial = pais.get("name", {}).get("official", "N/A")
        poblacion = pais.get("population", 0)
        capital = pais.get("capital", ["N/A"])[0]
        area = pais.get("area", 0)

        # Los idiomas vienen como dict: {"spa": "Spanish", "eng": "English"}
        idiomas = list(pais.get("languages", {}).values())

        # Las monedas también son dict anidado
        monedas_dict = pais.get("currencies", {})
        monedas = [f"{v['name']} ({k})" for k, v in monedas_dict.items()]

        print(f"  Nombre oficial: {nombre_oficial}")
        print(f"  Capital: {capital}")
        print(f"  Población: {poblacion:,}")
        print(f"  Área: {area:,.0f} km²")
        print(f"  Idiomas: {', '.join(idiomas)}")
        print(f"  Monedas: {', '.join(monedas)}")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"  País '{nombre_pais}' no encontrado.")
        else:
            print(f"  Error HTTP: {e}")
    except requests.exceptions.RequestException as e:
        print(f"  Error de conexión: {e}")


# =============================================================================
# SECCIÓN 6: Streaming de respuestas grandes
# =============================================================================

def descargar_con_streaming(url: str, max_bytes: int = 1024) -> None:
    """
    Descarga una respuesta grande usando streaming para no cargar todo en RAM.

    Por qué streaming: si la respuesta pesa megabytes (archivo, imagen, datos),
    cargarla completa en memoria puede ser ineficiente. Con stream=True,
    requests no descarga el body hasta que lo iteramos.

    Args:
        url: URL del recurso a descargar.
        max_bytes: Máximo de bytes a leer (solo para demostración).
    """
    print(f"\n--- Descarga con streaming ---")
    print(f"  URL: {url}")

    try:
        # stream=True indica que NO descargue el body inmediatamente
        with requests.get(url, stream=True, timeout=10) as respuesta:
            respuesta.raise_for_status()

            # Podemos leer los headers antes de leer el body
            tipo = respuesta.headers.get("Content-Type", "desconocido")
            print(f"  Content-Type: {tipo}")

            bytes_leidos = 0
            # iter_content itera el body en chunks del tamaño especificado
            for chunk in respuesta.iter_content(chunk_size=256):
                bytes_leidos += len(chunk)
                if bytes_leidos >= max_bytes:
                    break  # Paramos pronto — solo es una demostración

            print(f"  Bytes leídos (demo): {bytes_leidos}")
            print("  (En producción leerías todo y lo guardarías a disco)")

    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("REQUESTS AVANZADO — APIs reales con Python")
    print("=" * 60)

    # 1. GET básico
    ejemplo_get_basico()

    # 2. Session con headers persistentes
    ejemplo_session()

    # 3. Clima en diferentes ciudades
    ciudades = [
        (40.4168, -3.7038, "Madrid"),
        (19.4326, -99.1332, "Ciudad de México"),
        (40.7128, -74.0060, "Nueva York"),
    ]
    for lat, lon, ciudad in ciudades:
        obtener_clima(lat, lon, ciudad)
        time.sleep(0.5)  # Pequeña pausa para no saturar la API

    # 4. Información de países
    obtener_info_pais("Spain")
    obtener_info_pais("Mexico")

    # 5. Streaming (solo demostración de bytes iniciales)
    descargar_con_streaming("https://httpbin.org/bytes/2048", max_bytes=512)

    print("\n" + "=" * 60)
    print("Fin — siguiente: 03_trabajar_con_json.py")
    print("=" * 60)
