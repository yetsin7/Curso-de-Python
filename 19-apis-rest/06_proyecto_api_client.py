"""
Cliente Completo para la Open Library API
==========================================
Cliente profesional para openlibrary.org con:
  - Búsqueda de libros por título o autor
  - Obtención de detalles de un libro
  - Descarga de portadas en JPEG
  - Caché JSON local (no re-consulta lo ya buscado)
  - CLI con argparse para uso desde terminal

API base: https://openlibrary.org
No requiere autenticación ni API key.

Uso desde terminal:
    python 06_proyecto_api_client.py buscar --query "Don Quijote"
    python 06_proyecto_api_client.py detalles --key "/works/OL27516W"
    python 06_proyecto_api_client.py portada --id 8739161 --size M

Dependencias externas:
    pip install requests
"""

import argparse
import json
import os
from pathlib import Path

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False
    print("[AVISO] Instala requests: pip install requests")

# --- Rutas de caché ---
BASE_DIR   = Path(os.path.dirname(__file__))
CACHE_FILE = BASE_DIR / "openlibrary_cache.json"
COVERS_DIR = BASE_DIR / "portadas"

API_BASE    = "https://openlibrary.org"
COVERS_BASE = "https://covers.openlibrary.org/b/id"


# ===========================================================================
# Sistema de caché local
# ===========================================================================

def cargar_cache() -> dict:
    """
    Carga el archivo de caché desde disco.
    Si no existe, retorna un diccionario vacío.

    Returns:
        Diccionario con las consultas previas guardadas.
    """
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_cache(cache: dict) -> None:
    """
    Persiste el diccionario de caché en disco como JSON.

    Args:
        cache: Diccionario actualizado con nuevas consultas.
    """
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def clave_cache(tipo: str, valor: str) -> str:
    """
    Genera una clave única para el diccionario de caché.

    Args:
        tipo : Tipo de consulta (ej. 'buscar', 'detalles').
        valor: Valor de la consulta (query o clave del libro).

    Returns:
        String con formato 'tipo::valor' en minúsculas normalizadas.
    """
    return f"{tipo}::{valor.lower().strip()}"


# ===========================================================================
# Cliente Open Library
# ===========================================================================

class OpenLibraryClient:
    """
    Cliente HTTP para la API de Open Library con soporte de caché local.

    Attributes:
        session: Sesión de requests reutilizable con headers configurados.
        cache  : Diccionario de resultados previamente obtenidos.
    """

    def __init__(self) -> None:
        """Inicializa el cliente con sesión HTTP y caché cargado."""
        if not REQUESTS_OK:
            raise RuntimeError("Instala requests: pip install requests")

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "LibroPythonClient/1.0 (ejemplo educativo)",
            "Accept": "application/json",
        })
        self.cache = cargar_cache()

    def _get(self, url: str, params: dict = None) -> dict | None:
        """
        Realiza una petición GET y retorna el JSON de respuesta.
        Maneja errores de red de forma segura.

        Args:
            url   : URL completa del endpoint.
            params: Parámetros de query string opcionales.

        Returns:
            Diccionario con la respuesta JSON, o None si hubo error.
        """
        try:
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            print(f"  [HTTP ERROR] {e}")
        except requests.exceptions.ConnectionError:
            print("  [ERROR] Sin conexión a internet.")
        except requests.exceptions.Timeout:
            print("  [ERROR] La petición tardó demasiado.")
        return None

    def buscar(self, query: str, limite: int = 5) -> list[dict]:
        """
        Busca libros por título o autor en Open Library.
        Usa caché para no repetir consultas idénticas.

        Args:
            query : Texto a buscar (título, autor, ISBN, etc.).
            limite: Número máximo de resultados a retornar.

        Returns:
            Lista de diccionarios con datos básicos de cada libro.
        """
        key = clave_cache("buscar", query)

        if key in self.cache:
            print("  [caché] Resultado desde caché local.")
            return self.cache[key]

        print(f"  [API] Buscando: '{query}'…")
        data = self._get(f"{API_BASE}/search.json", params={"q": query, "limit": limite})

        if data is None:
            return []

        resultados = []
        for doc in data.get("docs", [])[:limite]:
            resultados.append({
                "titulo"  : doc.get("title", "Sin título"),
                "autores" : doc.get("author_name", ["Desconocido"]),
                "año"     : doc.get("first_publish_year"),
                "key"     : doc.get("key", ""),
                "cover_id": doc.get("cover_i"),
            })

        self.cache[key] = resultados
        guardar_cache(self.cache)
        return resultados

    def obtener_detalles(self, work_key: str) -> dict | None:
        """
        Obtiene los detalles completos de un libro por su clave de obra.

        Args:
            work_key: Clave de la obra, ej. '/works/OL27516W'

        Returns:
            Diccionario con detalles o None si no se encontró.
        """
        key = clave_cache("detalles", work_key)

        if key in self.cache:
            print("  [caché] Detalles desde caché local.")
            return self.cache[key]

        url = f"{API_BASE}{work_key}.json"
        print(f"  [API] Obteniendo detalles: {url}")
        data = self._get(url)

        if data:
            self.cache[key] = data
            guardar_cache(self.cache)

        return data

    def descargar_portada(self, cover_id: int, size: str = "M") -> str | None:
        """
        Descarga la portada de un libro y la guarda como JPEG local.
        Tamaños disponibles: S (pequeño), M (mediano), L (grande).

        Args:
            cover_id: ID numérico de la portada (campo 'cover_i' en resultados).
            size    : Tamaño de la imagen ('S', 'M' o 'L').

        Returns:
            Ruta local del archivo descargado, o None si falló.
        """
        COVERS_DIR.mkdir(exist_ok=True)
        ruta_local = COVERS_DIR / f"cover_{cover_id}_{size}.jpg"

        if ruta_local.exists():
            print(f"  [caché] Portada ya descargada: {ruta_local.name}")
            return str(ruta_local)

        url = f"{COVERS_BASE}/{cover_id}-{size}.jpg"
        print(f"  [API] Descargando portada: {url}")

        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()

            with open(ruta_local, "wb") as f:
                f.write(resp.content)

            print(f"  [ok] Portada guardada: {ruta_local}")
            return str(ruta_local)

        except Exception as e:
            print(f"  [ERROR] No se pudo descargar la portada: {e}")
            return None


# ===========================================================================
# Comandos CLI
# ===========================================================================

def cmd_buscar(args: argparse.Namespace) -> None:
    """
    Comando CLI: buscar libros por query.

    Args:
        args: Argumentos de argparse con 'query' y 'limite'.
    """
    client = OpenLibraryClient()
    resultados = client.buscar(args.query, limite=args.limite)

    if not resultados:
        print("  No se encontraron resultados.")
        return

    print(f"\n  {len(resultados)} resultado(s) para: '{args.query}'\n")
    for i, libro in enumerate(resultados, 1):
        autores = ", ".join(libro["autores"][:2])
        print(f"  {i}. {libro['titulo']}")
        print(f"     Autor(es) : {autores}")
        print(f"     Año       : {libro['año'] or 'N/D'}")
        print(f"     Clave     : {libro['key']}")
        print(f"     Cover ID  : {libro['cover_id'] or 'No disponible'}")
        print()


def cmd_detalles(args: argparse.Namespace) -> None:
    """
    Comando CLI: obtener detalles de un libro por su clave.

    Args:
        args: Argumentos de argparse con 'key'.
    """
    client = OpenLibraryClient()
    detalles = client.obtener_detalles(args.key)

    if not detalles:
        print("  No se encontraron detalles.")
        return

    print(f"\n  Título    : {detalles.get('title', 'N/D')}")

    desc = detalles.get("description")
    if isinstance(desc, dict):
        desc = desc.get("value", "")
    print(f"  Descripción (primeros 200 chars):")
    print(f"    {str(desc or 'Sin descripción')[:200]}…")

    subjects = detalles.get("subjects", [])[:5]
    if subjects:
        print(f"  Temas     : {', '.join(subjects)}")


def cmd_portada(args: argparse.Namespace) -> None:
    """
    Comando CLI: descargar la portada de un libro.

    Args:
        args: Argumentos de argparse con 'id' y 'size'.
    """
    client = OpenLibraryClient()
    ruta = client.descargar_portada(args.id, size=args.size.upper())

    if ruta:
        print(f"\n  Portada guardada en: {ruta}")


# ===========================================================================
# Construcción del parser de argumentos
# ===========================================================================

def construir_parser() -> argparse.ArgumentParser:
    """
    Construye y retorna el parser de argumentos con subcomandos.

    Returns:
        ArgumentParser configurado con los tres subcomandos.
    """
    parser = argparse.ArgumentParser(
        prog="open_library",
        description="Cliente CLI para Open Library API"
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    # Subcomando: buscar
    p_buscar = subparsers.add_parser("buscar", help="Buscar libros por título o autor")
    p_buscar.add_argument("--query", required=True, help="Término de búsqueda")
    p_buscar.add_argument("--limite", type=int, default=5, help="Máximo de resultados")
    p_buscar.set_defaults(func=cmd_buscar)

    # Subcomando: detalles
    p_det = subparsers.add_parser("detalles", help="Ver detalles de una obra")
    p_det.add_argument("--key", required=True, help="Clave de la obra, ej. /works/OL27516W")
    p_det.set_defaults(func=cmd_detalles)

    # Subcomando: portada
    p_portada = subparsers.add_parser("portada", help="Descargar portada de un libro")
    p_portada.add_argument("--id",   type=int, required=True, help="ID numérico de la portada")
    p_portada.add_argument("--size", default="M", choices=["S", "M", "L"], help="Tamaño")
    p_portada.set_defaults(func=cmd_portada)

    return parser


# ===========================================================================
# Demostración automática (sin argumentos CLI)
# ===========================================================================

def demo() -> None:
    """
    Ejecuta una demostración completa del cliente sin argumentos CLI.
    Busca un libro, obtiene detalles y descarga su portada.
    """
    if not REQUESTS_OK:
        print("  [SKIP] requests no instalado.")
        return

    print("\n=== DEMO: Cliente Open Library ===\n")
    client = OpenLibraryClient()

    # Búsqueda
    print("-- Buscando 'Cien años de soledad' --")
    resultados = client.buscar("Cien años de soledad", limite=3)
    for libro in resultados:
        print(f"  • {libro['titulo']} ({libro['año']}) — key: {libro['key']}")

    # Detalles del primer resultado con key válida
    if resultados and resultados[0]["key"]:
        print(f"\n-- Detalles de: {resultados[0]['key']} --")
        detalles = client.obtener_detalles(resultados[0]["key"])
        if detalles:
            print(f"  Título: {detalles.get('title')}")

    # Descarga de portada si hay cover_id
    libro_con_portada = next((r for r in resultados if r.get("cover_id")), None)
    if libro_con_portada:
        print(f"\n-- Descargando portada ID={libro_con_portada['cover_id']} --")
        client.descargar_portada(libro_con_portada["cover_id"], size="S")


# ===========================================================================
# Punto de entrada
# ===========================================================================

def main() -> None:
    """
    Punto de entrada: si hay argumentos usa CLI, si no ejecuta la demo.
    """
    import sys

    if len(sys.argv) > 1:
        parser = construir_parser()
        args   = parser.parse_args()
        args.func(args)
    else:
        demo()


if __name__ == "__main__":
    main()
