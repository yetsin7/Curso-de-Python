"""
Ejercicios Prácticos de Web Scraping
======================================
Proyectos reales que cubren scraping de precios, exportación a CSV/JSON,
detección de bloqueos, rate limiting, manejo de JavaScript y checkpoints
para no re-scrapear páginas ya visitadas.

Sitio de práctica: books.toscrape.com (hecho para scraping, sin restricciones)

Dependencias externas:
    pip install requests beautifulsoup4
"""

import csv
import json
import os
import random
import time

# --- Importación con manejo de dependencias opcionales ---
try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False
    print("[AVISO] Instala las dependencias: pip install requests beautifulsoup4")

BASE_DIR   = os.path.dirname(__file__)
CHECKPOINT = os.path.join(BASE_DIR, "scraping_checkpoint.json")
OUTPUT_CSV = os.path.join(BASE_DIR, "libros_scraped.csv")
OUTPUT_JSON = os.path.join(BASE_DIR, "libros_scraped.json")

BASE_URL = "http://books.toscrape.com/catalogue/"


# ===========================================================================
# Utilidades generales
# ===========================================================================

def delay_aleatorio(min_seg: float = 0.8, max_seg: float = 2.0) -> None:
    """
    Pausa la ejecución un tiempo aleatorio entre min_seg y max_seg segundos.
    Simula comportamiento humano y evita sobrecargar el servidor.

    Args:
        min_seg: Mínimo de segundos a esperar.
        max_seg: Máximo de segundos a esperar.
    """
    tiempo = random.uniform(min_seg, max_seg)
    print(f"  [rate-limit] Esperando {tiempo:.2f}s…")
    time.sleep(tiempo)


def obtener_headers() -> dict:
    """
    Retorna headers HTTP que imitan a un navegador real.
    Muchos sitios bloquean peticiones sin User-Agent válido.

    Returns:
        Diccionario de headers para usar en requests.get().
    """
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }


def detectar_bloqueo(response: "requests.Response") -> bool:
    """
    Detecta si el servidor está bloqueando el scraper.
    Señales comunes: código 403/429, CAPTCHA en el cuerpo, etc.

    Args:
        response: Objeto Response de requests.

    Returns:
        True si se detecta un posible bloqueo.
    """
    if response.status_code in (403, 429):
        print(f"  [BLOQUEO] Código {response.status_code} — el sitio rechazó la petición.")
        return True

    indicadores = ["captcha", "access denied", "blocked", "robot"]
    cuerpo = response.text.lower()
    for ind in indicadores:
        if ind in cuerpo:
            print(f"  [BLOQUEO] Detectado indicador en HTML: '{ind}'")
            return True

    return False


# ===========================================================================
# Sistema de checkpoint
# ===========================================================================

def cargar_checkpoint() -> dict:
    """
    Carga el archivo de checkpoint si existe.
    Permite reanudar un scraping sin repetir páginas ya visitadas.

    Returns:
        Diccionario con URLs visitadas y datos parciales guardados.
    """
    if os.path.exists(CHECKPOINT):
        with open(CHECKPOINT, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"visitadas": [], "libros": []}


def guardar_checkpoint(estado: dict) -> None:
    """
    Persiste el estado actual al archivo de checkpoint en disco.

    Args:
        estado: Diccionario con URLs visitadas y libros recolectados.
    """
    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def limpiar_checkpoint() -> None:
    """Elimina el archivo de checkpoint al finalizar con éxito."""
    if os.path.exists(CHECKPOINT):
        os.remove(CHECKPOINT)
        print("  [checkpoint] Archivo de progreso eliminado.")


# ===========================================================================
# Ejercicio 1 y 2: Scraper de precios + exportar a CSV y JSON
# ===========================================================================

def scrape_pagina(url: str, estado: dict) -> list[dict]:
    """
    Extrae todos los libros (título, precio, rating) de una página del catálogo.
    Omite la página si ya fue visitada (checkpoint).

    Args:
        url   : URL completa de la página a scrapear.
        estado: Diccionario de checkpoint compartido.

    Returns:
        Lista de diccionarios con datos de cada libro encontrado.
    """
    if url in estado["visitadas"]:
        print(f"  [checkpoint] Omitiendo (ya visitada): {url}")
        return []

    response = requests.get(url, headers=obtener_headers(), timeout=10)

    if detectar_bloqueo(response):
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    libros = []

    for articulo in soup.select("article.product_pod"):
        titulo = articulo.select_one("h3 a")["title"]
        precio = articulo.select_one("p.price_color").text.strip()
        rating_clase = articulo.select_one("p.star-rating")["class"][1]

        libros.append({
            "titulo": titulo,
            "precio": precio,
            "rating": rating_clase,
        })

    estado["visitadas"].append(url)
    estado["libros"].extend(libros)
    guardar_checkpoint(estado)

    print(f"  [ok] {len(libros)} libros de: {url}")
    return libros


def exportar_csv(libros: list[dict], ruta: str) -> None:
    """
    Exporta la lista de libros a un archivo CSV.

    Args:
        libros: Lista de dicts con claves titulo, precio, rating.
        ruta  : Ruta completa donde guardar el CSV.
    """
    if not libros:
        print("  [warn] No hay libros para exportar.")
        return

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["titulo", "precio", "rating"])
        writer.writeheader()
        writer.writerows(libros)

    print(f"  [CSV] Guardado en: {ruta}")


def exportar_json(libros: list[dict], ruta: str) -> None:
    """
    Exporta la lista de libros a un archivo JSON con formato legible.

    Args:
        libros: Lista de dicts con los datos de libros.
        ruta  : Ruta completa donde guardar el JSON.
    """
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(libros, f, ensure_ascii=False, indent=2)

    print(f"  [JSON] Guardado en: {ruta}")


def ejercicio_scraper_precios(paginas: int = 3) -> None:
    """
    Ejercicio 1+2: Scrapea N páginas de books.toscrape.com,
    aplica rate limiting y checkpoint, y exporta resultados a CSV y JSON.

    Args:
        paginas: Número de páginas del catálogo a procesar.
    """
    if not REQUESTS_OK:
        print("  [SKIP] requests/bs4 no disponibles.")
        return

    print(f"\n=== Ejercicio 1+2: Scraper de precios ({paginas} páginas) ===")
    estado = cargar_checkpoint()

    urls = [
        f"{BASE_URL}page-{i}.html" if i > 1 else "http://books.toscrape.com/catalogue/page-1.html"
        for i in range(1, paginas + 1)
    ]

    for url in urls:
        scrape_pagina(url, estado)
        delay_aleatorio()  # rate limiting entre páginas

    libros_totales = estado["libros"]
    print(f"\n  Total libros recolectados: {len(libros_totales)}")
    exportar_csv(libros_totales, OUTPUT_CSV)
    exportar_json(libros_totales, OUTPUT_JSON)
    limpiar_checkpoint()


# ===========================================================================
# Ejercicio 3: Detectar bloqueos de bots
# ===========================================================================

def ejercicio_detectar_bloqueo() -> None:
    """
    Ejercicio 3: Muestra cómo detectar cuando un sitio bloquea bots.
    Hace una petición con y sin User-Agent para comparar respuestas.
    """
    if not REQUESTS_OK:
        print("  [SKIP] requests no disponible.")
        return

    print("\n=== Ejercicio 3: Detección de bloqueo ===")

    url_prueba = "http://books.toscrape.com/"

    # Petición sin User-Agent (como lo haría un script básico)
    resp_basico = requests.get(url_prueba, timeout=10)
    print(f"  Sin User-Agent → código: {resp_basico.status_code}")

    # Petición con User-Agent de navegador
    resp_con_ua = requests.get(url_prueba, headers=obtener_headers(), timeout=10)
    print(f"  Con User-Agent → código: {resp_con_ua.status_code}")

    bloqueado = detectar_bloqueo(resp_basico)
    print(f"  ¿Bloqueado con petición básica? {'Sí' if bloqueado else 'No'}")

    print("""
  TÉCNICAS ANTI-BLOQUEO:
    1. User-Agent de navegador real
    2. Delays aleatorios entre peticiones
    3. Rotar User-Agents (lista de UAs distintos)
    4. Usar proxies rotativos
    5. Respetar robots.txt
    6. Sessions de requests para mantener cookies
    7. Referer header que apunta a la página anterior
""")


# ===========================================================================
# Ejercicio 5: Páginas con JavaScript — explicación conceptual
# ===========================================================================

def ejercicio_javascript_conceptual() -> None:
    """
    Ejercicio 5: Explica cómo manejar sitios que requieren JavaScript
    y muestra alternativas sin necesidad de Selenium en todos los casos.
    """
    print("""
=== Ejercicio 5: Páginas que requieren JavaScript ===

PROBLEMA:
  requests + BeautifulSoup solo obtienen el HTML estático.
  Si el contenido se carga con JavaScript (React, Vue, Ajax),
  el HTML inicial estará vacío o incompleto.

SOLUCIONES:

1. Buscar la API interna (la más eficiente)
   - Abrir DevTools → pestaña Network → filtrar XHR/Fetch
   - El navegador muestra las llamadas a la API real
   - Hacer la petición directamente a esa API con requests
   - Ejemplo:
       resp = requests.get("https://sitio.com/api/products.json")
       datos = resp.json()

2. Selenium (automatizar el navegador real)
   pip install selenium
   from selenium import webdriver
   driver = webdriver.Chrome()
   driver.get("https://sitio.com")
   html = driver.page_source          # HTML DESPUÉS de ejecutar JS
   soup = BeautifulSoup(html, "html.parser")
   driver.quit()

3. Playwright (más moderno que Selenium)
   pip install playwright
   playwright install chromium
   from playwright.sync_api import sync_playwright
   with sync_playwright() as p:
       browser = p.chromium.launch()
       page = browser.new_page()
       page.goto("https://sitio.com")
       page.wait_for_selector(".products")
       html = page.content()

4. Scrapy-Splash (para scrapers grandes con JS)
   - Splash es un navegador lightweight para Scrapy
   - Ejecuta JS sin una interfaz gráfica completa

REGLA GENERAL:
  Si el sitio tiene API → úsala directamente
  Si no hay API → Playwright (más confiable que Selenium)
  Si es un scraper masivo → Scrapy + Splash
""")


# ===========================================================================
# Punto de entrada
# ===========================================================================

def main() -> None:
    """
    Ejecuta todos los ejercicios de scraping en secuencia.
    """
    print("=" * 60)
    print("  EJERCICIOS PRÁCTICOS DE WEB SCRAPING")
    print("=" * 60)

    ejercicio_scraper_precios(paginas=2)
    ejercicio_detectar_bloqueo()
    ejercicio_javascript_conceptual()

    print("\n✓ Todos los ejercicios completados.")


if __name__ == "__main__":
    main()
