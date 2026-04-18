# =============================================================================
# CAPÍTULO 19 — APIs REST y Requests
# Archivo 04: Construir un cliente de API orientado a objetos
# =============================================================================
# Por qué un cliente OOP: en proyectos reales no llamamos a requests.get()
# directamente en cada parte del código. Encapsulamos la lógica en una clase
# que maneja headers, errores, retry, logging y rate limiting de forma
# centralizada. Así el resto del código solo llama métodos semánticos.
#
# Instalación: pip install requests
# =============================================================================

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("ERROR: Instala requests con:  pip install requests")
    raise SystemExit(1)

import logging    # Para registrar actividad del cliente
import time       # Para rate limiting (esperar entre peticiones)
import json       # Para formatear logs de respuesta
from typing import Any


# =============================================================================
# CONFIGURACIÓN DEL LOGGING
# =============================================================================

# Configuramos el logger del módulo — buena práctica vs usar print()
# Esto permite que quien use la librería controle el nivel de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("APIClient")


# =============================================================================
# EXCEPCIÓN PERSONALIZADA
# =============================================================================

class APIClientError(Exception):
    """
    Excepción base para todos los errores del APIClient.

    Por qué una excepción personalizada: permite a quien use el cliente
    capturar solo errores de la API con `except APIClientError` sin
    mezclarlos con otros errores del programa. También podemos incluir
    información adicional como el status_code.
    """

    def __init__(self, mensaje: str, status_code: int | None = None, respuesta: Any = None):
        super().__init__(mensaje)
        self.status_code = status_code  # Código HTTP si aplica
        self.respuesta = respuesta      # Datos de respuesta si los hay


# =============================================================================
# CLASE PRINCIPAL: APIClient
# =============================================================================

class APIClient:
    """
    Cliente HTTP reutilizable orientado a objetos.

    Centraliza toda la lógica común de consumo de APIs:
    - Base URL y headers por defecto
    - Session HTTP con retry automático
    - Timeout configurable
    - Rate limiting (espera entre peticiones)
    - Logging automático de requests y responses
    - Manejo unificado de errores

    Uso típico:
        cliente = APIClient("https://api.ejemplo.com", api_key="mi_clave")
        datos = cliente.get("/usuarios/1")
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        bearer_token: str | None = None,
        timeout: int = 15,
        max_reintentos: int = 3,
        delay_entre_peticiones: float = 0.5,
    ):
        """
        Inicializa el cliente con la configuración base.

        Args:
            base_url: URL base de la API (sin slash al final).
            api_key: API Key a enviar en header X-API-Key (opcional).
            bearer_token: Token Bearer para Authorization header (opcional).
            timeout: Segundos máximos por petición antes de timeout.
            max_reintentos: Cuántas veces reintentar ante errores 5xx.
            delay_entre_peticiones: Segundos de espera entre requests (rate limit).
        """
        # Normalizamos la base_url: quitamos slash final para concatenar limpio
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.delay_entre_peticiones = delay_entre_peticiones

        # Timestamp de la última petición — para calcular la espera necesaria
        self._ultima_peticion: float = 0.0

        # Creamos la session HTTP con retry configurado
        self._session = self._crear_session(max_reintentos)

        # Configuramos headers base que se enviarán en todas las peticiones
        self._session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "LibroPython-APIClient/1.0",
        })

        # Añadimos autenticación si se proporcionó
        if api_key:
            self._session.headers["X-API-Key"] = api_key
            logger.debug("API Key configurada en headers.")

        if bearer_token:
            self._session.headers["Authorization"] = f"Bearer {bearer_token}"
            logger.debug("Bearer token configurado en headers.")

        logger.info(f"APIClient inicializado para: {self.base_url}")

    def _crear_session(self, max_reintentos: int) -> requests.Session:
        """
        Crea y configura una Session HTTP con retry automático.

        Por qué HTTPAdapter: permite configurar el pool de conexiones
        y la estrategia de retry de forma independiente para HTTP y HTTPS.

        Args:
            max_reintentos: Número máximo de reintentos.

        Returns:
            Session configurada lista para usar.
        """
        session = requests.Session()

        # Retry solo en métodos idempotentes y códigos de error del servidor
        retry = Retry(
            total=max_reintentos,
            backoff_factor=1.0,          # Espera: 1s, 2s, 4s... entre reintentos
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "PUT", "DELETE", "PATCH"],
            # No reintentamos POST por defecto — podría crear duplicados
        )

        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _aplicar_rate_limit(self) -> None:
        """
        Espera el tiempo necesario para respetar el rate limit configurado.

        Por qué: muchas APIs tienen límites de peticiones por segundo/minuto.
        Este método garantiza que nunca hagamos peticiones más rápido que
        el intervalo configurado en delay_entre_peticiones.
        """
        ahora = time.monotonic()
        tiempo_transcurrido = ahora - self._ultima_peticion
        tiempo_a_esperar = self.delay_entre_peticiones - tiempo_transcurrido

        if tiempo_a_esperar > 0:
            logger.debug(f"Rate limit: esperando {tiempo_a_esperar:.2f}s")
            time.sleep(tiempo_a_esperar)

        # Actualizamos el timestamp DESPUÉS de esperar
        self._ultima_peticion = time.monotonic()

    def _construir_url(self, endpoint: str) -> str:
        """
        Construye la URL completa uniendo base_url y endpoint.

        Si el endpoint ya es una URL completa (empieza con http),
        lo usa directamente sin concatenar con base_url.

        Args:
            endpoint: Ruta del endpoint (ej: "/usuarios/1").

        Returns:
            URL completa lista para la petición.
        """
        if endpoint.startswith(("http://", "https://")):
            return endpoint
        # Aseguramos que el endpoint empiece con /
        endpoint = "/" + endpoint.lstrip("/")
        return f"{self.base_url}{endpoint}"

    def _ejecutar_peticion(
        self,
        metodo: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """
        Ejecuta una petición HTTP y maneja errores de forma unificada.

        Este es el método central del cliente. Todos los métodos públicos
        (get, post, put, etc.) delegan aquí.

        Args:
            metodo: Método HTTP ("GET", "POST", etc.).
            endpoint: Ruta del endpoint o URL completa.
            **kwargs: Argumentos adicionales para requests (params, json, etc.).

        Returns:
            El body de la respuesta parseado como dict/lista, o None si 204.

        Raises:
            APIClientError: Si la petición falla por cualquier razón.
        """
        url = self._construir_url(endpoint)

        # Respetamos el rate limit antes de hacer la petición
        self._aplicar_rate_limit()

        # Registramos la petición
        logger.info(f"→ {metodo} {url}")
        if "params" in kwargs and kwargs["params"]:
            logger.debug(f"  Params: {kwargs['params']}")

        inicio = time.monotonic()

        try:
            respuesta = self._session.request(
                method=metodo,
                url=url,
                timeout=self.timeout,
                **kwargs,
            )

            duracion = time.monotonic() - inicio
            logger.info(f"← {respuesta.status_code} en {duracion:.3f}s")

            # Levantamos excepción para códigos 4xx y 5xx
            respuesta.raise_for_status()

            # 204 No Content — respuesta exitosa sin body
            if respuesta.status_code == 204:
                return None

            # Intentamos parsear como JSON
            if "application/json" in respuesta.headers.get("Content-Type", ""):
                return respuesta.json()

            # Si no es JSON, devolvemos el texto
            return respuesta.text

        except requests.exceptions.HTTPError as e:
            codigo = e.response.status_code if e.response is not None else None
            # Intentamos extraer el mensaje de error del body JSON
            detalle = ""
            try:
                error_json = e.response.json()
                detalle = str(error_json.get("detail") or error_json.get("message") or "")
            except Exception:
                detalle = e.response.text[:200] if e.response is not None else ""

            mensaje = f"HTTP {codigo}: {detalle or str(e)}"
            logger.error(f"Error: {mensaje}")
            raise APIClientError(mensaje, status_code=codigo) from e

        except requests.exceptions.Timeout:
            mensaje = f"Timeout después de {self.timeout}s en {url}"
            logger.error(mensaje)
            raise APIClientError(mensaje) from None

        except requests.exceptions.ConnectionError as e:
            mensaje = f"Error de conexión: {e}"
            logger.error(mensaje)
            raise APIClientError(mensaje) from e

        except requests.exceptions.RequestException as e:
            mensaje = f"Error de requests: {e}"
            logger.error(mensaje)
            raise APIClientError(mensaje) from e

    # ----------------------------------------------------------------
    # Métodos públicos de conveniencia — API semántica del cliente
    # ----------------------------------------------------------------

    def get(self, endpoint: str, params: dict | None = None) -> Any:
        """Petición GET. Retorna los datos parseados."""
        return self._ejecutar_peticion("GET", endpoint, params=params)

    def post(self, endpoint: str, datos: dict | None = None) -> Any:
        """Petición POST con body JSON. Retorna la respuesta."""
        return self._ejecutar_peticion("POST", endpoint, json=datos)

    def put(self, endpoint: str, datos: dict | None = None) -> Any:
        """Petición PUT con body JSON. Reemplaza el recurso completo."""
        return self._ejecutar_peticion("PUT", endpoint, json=datos)

    def patch(self, endpoint: str, datos: dict | None = None) -> Any:
        """Petición PATCH con body JSON. Actualización parcial."""
        return self._ejecutar_peticion("PATCH", endpoint, json=datos)

    def delete(self, endpoint: str) -> None:
        """Petición DELETE. No retorna datos (204 No Content esperado)."""
        self._ejecutar_peticion("DELETE", endpoint)

    def cerrar(self) -> None:
        """Cierra la session HTTP y libera recursos de red."""
        self._session.close()
        logger.info("Session HTTP cerrada.")

    # Soporte para context manager (with APIClient(...) as cliente:)
    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.cerrar()


# =============================================================================
# CLIENTE ESPECÍFICO: JSONPlaceholderClient
# =============================================================================

class JSONPlaceholderClient(APIClient):
    """
    Cliente especializado para la API JSONPlaceholder.

    Por qué una subclase: cuando trabajamos con una API específica,
    tiene sentido crear métodos semánticos del dominio (get_post, crear_comentario)
    en lugar de llamar a get("/posts/1") en el código del negocio.
    Esto hace el código más legible y fácil de mantener.
    """

    def __init__(self):
        # Inicializamos el cliente base con la URL de JSONPlaceholder
        super().__init__(
            base_url="https://jsonplaceholder.typicode.com",
            delay_entre_peticiones=0.3,  # 300ms entre peticiones — API pública
        )

    def obtener_posts(self, usuario_id: int | None = None) -> list[dict]:
        """
        Obtiene posts, opcionalmente filtrados por usuario.

        Args:
            usuario_id: ID del usuario para filtrar sus posts.

        Returns:
            Lista de posts en formato dict.
        """
        params = {"userId": usuario_id} if usuario_id else None
        return self.get("/posts", params=params)

    def obtener_post(self, post_id: int) -> dict:
        """
        Obtiene un post específico por su ID.

        Args:
            post_id: ID del post a obtener.

        Returns:
            Diccionario con los datos del post.
        """
        return self.get(f"/posts/{post_id}")

    def crear_post(self, titulo: str, cuerpo: str, usuario_id: int) -> dict:
        """
        Crea un nuevo post (simulado — JSONPlaceholder no persiste datos).

        Args:
            titulo: Título del post.
            cuerpo: Contenido del post.
            usuario_id: ID del autor.

        Returns:
            El post creado con su ID asignado.
        """
        return self.post("/posts", {
            "title": titulo,
            "body": cuerpo,
            "userId": usuario_id,
        })

    def obtener_comentarios_post(self, post_id: int) -> list[dict]:
        """
        Obtiene los comentarios de un post específico.

        Args:
            post_id: ID del post.

        Returns:
            Lista de comentarios.
        """
        return self.get(f"/posts/{post_id}/comments")

    def obtener_usuario(self, usuario_id: int) -> dict:
        """
        Obtiene información de un usuario por su ID.

        Args:
            usuario_id: ID del usuario.

        Returns:
            Diccionario con los datos del usuario.
        """
        return self.get(f"/users/{usuario_id}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CLIENTE DE API ORIENTADO A OBJETOS")
    print("=" * 60)

    # Usamos el context manager para garantizar que la session se cierre
    with JSONPlaceholderClient() as cliente:

        # 1. Obtener posts de un usuario
        print("\n[1] Posts del usuario #1:")
        posts = cliente.obtener_posts(usuario_id=1)
        print(f"  Total de posts: {len(posts)}")
        for post in posts[:3]:
            print(f"  [{post['id']}] {post['title'][:50]}")

        # 2. Obtener detalle de un post
        print("\n[2] Detalle del post #5:")
        post = cliente.obtener_post(5)
        print(f"  Título: {post['title']}")
        print(f"  Cuerpo: {post['body'][:80]}...")

        # 3. Obtener comentarios de un post
        print("\n[3] Comentarios del post #1:")
        comentarios = cliente.obtener_comentarios_post(1)
        print(f"  Total de comentarios: {len(comentarios)}")
        for c in comentarios[:2]:
            print(f"  • {c['name']} ({c['email']})")

        # 4. Crear un nuevo post
        print("\n[4] Crear nuevo post:")
        nuevo = cliente.crear_post(
            titulo="Aprendiendo Python con APIs",
            cuerpo="Este es un post creado desde mi cliente API personalizado.",
            usuario_id=1,
        )
        print(f"  Post creado con ID: {nuevo['id']}")
        print(f"  Título: {nuevo['title']}")

        # 5. Manejo de error controlado
        print("\n[5] Manejo de error 404:")
        try:
            cliente.obtener_post(99999)  # Post que no existe
        except APIClientError as e:
            print(f"  Error capturado: {e}")
            print(f"  Status code: {e.status_code}")

    print("\n" + "=" * 60)
    print("Fin — siguiente: 05_autenticacion.py")
    print("=" * 60)
