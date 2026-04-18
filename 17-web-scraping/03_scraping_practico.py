# =============================================================================
# 03_scraping_practico.py — Proyecto completo de Web Scraping
# =============================================================================
# Scraper completo que extrae frases de quotes.toscrape.com
#
# quotes.toscrape.com es un sitio creado ESPECÍFICAMENTE para aprender
# web scraping de forma legal y ética. No tiene robots.txt restrictivo
# y está diseñado para ser rastreado por estudiantes.
#
# Instalación:
#   pip install requests beautifulsoup4
#
# El scraper:
#   1. Extrae frases, autores y tags de múltiples páginas
#   2. Maneja la paginación automáticamente
#   3. Aplica rate limiting (pausa entre peticiones)
#   4. Guarda los datos en CSV y JSON
#   5. Maneja errores de red correctamente
# =============================================================================

try:
    import requests
    from bs4 import BeautifulSoup
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False

import csv
import json
import time
import os
from datetime import datetime


# =============================================================================
# CONFIGURACIÓN DEL SCRAPER
# =============================================================================

# URL base del sitio a scrapear
BASE_URL = "https://quotes.toscrape.com"

# Pausa entre peticiones en segundos (buena práctica para no sobrecargar el servidor)
REQUEST_DELAY = 1.5

# Número máximo de páginas a rastrear (None = todas)
MAX_PAGES = 5

# Archivos de salida
OUTPUT_CSV  = "quotes.csv"
OUTPUT_JSON = "quotes.json"

# Headers que simulan un navegador para peticiones más respetuosas
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; PythonEducationBot/1.0; "
        "+https://github.com/educacion-python)"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


# =============================================================================
# FUNCIONES DE SCRAPING
# =============================================================================

def fetch_page(url, session, retries=3):
    """
    Descarga una página web con manejo de errores y reintentos.

    Los reintentos son importantes en scraping real: a veces el servidor
    falla temporalmente y un segundo intento tiene éxito.

    Parámetros:
        url (str): URL a descargar
        session: objeto requests.Session activo
        retries (int): número de intentos antes de rendirse

    Retorna:
        str | None: HTML de la página o None si todos los intentos fallaron
    """
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            return response.text

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "N/A"

            # 429 = Too Many Requests — el servidor dice "espera más"
            if status == 429:
                wait_time = 30 * attempt
                print(f"  Rate limit (429). Esperando {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"  HTTP {status} en intento {attempt}/{retries}: {url}")
                if attempt == retries:
                    return None

        except requests.exceptions.ConnectionError:
            print(f"  Sin conexión en intento {attempt}/{retries}")
            if attempt < retries:
                time.sleep(5)
            else:
                return None

        except requests.exceptions.Timeout:
            print(f"  Timeout en intento {attempt}/{retries}")
            if attempt < retries:
                time.sleep(3)
            else:
                return None

    return None


def parse_quotes_page(html):
    """
    Extrae todas las frases de una página HTML de quotes.toscrape.com.

    Parámetros:
        html (str): contenido HTML de la página

    Retorna:
        list[dict]: lista de frases con texto, autor, tags y URL del autor
    """
    soup = BeautifulSoup(html, "html.parser")
    quotes = []

    # Cada frase está en un <div class="quote">
    for quote_div in soup.select("div.quote"):

        # Extraer el texto de la frase (está en <span class="text">)
        text_tag = quote_div.select_one("span.text")
        text = text_tag.get_text(strip=True) if text_tag else ""

        # Limpiar las comillas tipográficas que usa el sitio (\u201c y \u201d)
        text = text.strip('"').strip('\u201c').strip('\u201d')

        # Extraer el nombre del autor
        author_tag = quote_div.select_one("small.author")
        author = author_tag.get_text(strip=True) if author_tag else "Desconocido"

        # Extraer el link a la página del autor
        author_link_tag = quote_div.select_one("a[href*='/author/']")
        author_url = ""
        if author_link_tag:
            author_url = BASE_URL + author_link_tag.get("href", "")

        # Extraer los tags — cada tag está en <a class="tag">
        tag_elements = quote_div.select("a.tag")
        tags = [tag.get_text(strip=True) for tag in tag_elements]

        # Solo agregar si tiene texto válido
        if text:
            quotes.append({
                "text":       text,
                "author":     author,
                "author_url": author_url,
                "tags":       tags,
            })

    return quotes


def get_next_page_url(html):
    """
    Encuentra la URL de la siguiente página de paginación.

    Parámetros:
        html (str): HTML de la página actual

    Retorna:
        str | None: URL de la siguiente página, o None si es la última
    """
    soup = BeautifulSoup(html, "html.parser")

    # El botón "Next" está en <li class="next"><a href="...">
    next_button = soup.select_one("li.next a")

    if next_button:
        # La URL es relativa (/page/2/), hay que añadir la base
        relative_url = next_button.get("href", "")
        return BASE_URL + relative_url

    # Si no hay botón Next, es la última página
    return None


def scrape_quotes(max_pages=MAX_PAGES):
    """
    Función principal del scraper. Extrae frases de múltiples páginas.

    Parámetros:
        max_pages (int | None): límite de páginas. None = todas las páginas.

    Retorna:
        list[dict]: todas las frases extraídas de todas las páginas
    """
    all_quotes = []
    current_url = BASE_URL + "/page/1/"
    page_number = 1

    print(f"Iniciando scraping de {BASE_URL}")
    print(f"Límite: {max_pages} páginas | Delay: {REQUEST_DELAY}s entre páginas\n")

    # Usar Session para reutilizar la conexión TCP entre páginas
    with requests.Session() as session:
        session.headers.update(HEADERS)

        while current_url:
            # Verificar si alcanzamos el límite de páginas
            if max_pages and page_number > max_pages:
                print(f"Límite de {max_pages} páginas alcanzado.")
                break

            print(f"Página {page_number}: {current_url}")

            # Descargar la página
            html = fetch_page(current_url, session)

            if html is None:
                print(f"  No se pudo descargar la página {page_number}. Deteniendo.")
                break

            # Extraer frases de esta página
            page_quotes = parse_quotes_page(html)
            all_quotes.extend(page_quotes)
            print(f"  Extraídas {len(page_quotes)} frases. Total acumulado: {len(all_quotes)}")

            # Encontrar la URL de la siguiente página
            current_url = get_next_page_url(html)
            page_number += 1

            # Rate limiting: pausar entre peticiones para no sobrecargar el servidor
            if current_url:
                print(f"  Esperando {REQUEST_DELAY}s...")
                time.sleep(REQUEST_DELAY)

    print(f"\nScraping completado. Total de frases: {len(all_quotes)}")
    return all_quotes


# =============================================================================
# FUNCIONES DE ALMACENAMIENTO
# =============================================================================

def save_to_csv(quotes, filename=OUTPUT_CSV):
    """
    Guarda las frases en un archivo CSV.

    CSV (Comma-Separated Values) es ideal para datos tabulares
    que se van a abrir en Excel o procesar con pandas.

    Parámetros:
        quotes (list[dict]): lista de frases a guardar
        filename (str): nombre del archivo CSV de salida
    """
    if not quotes:
        print("No hay datos para guardar en CSV.")
        return

    # Definir las columnas del CSV
    fieldnames = ["text", "author", "author_url", "tags"]

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Escribir encabezados
        writer.writeheader()

        for quote in quotes:
            # Convertir la lista de tags a string separado por comas
            row = {
                "text":       quote["text"],
                "author":     quote["author"],
                "author_url": quote["author_url"],
                # Los tags como lista se guardan como string "tag1,tag2,tag3"
                "tags":       ",".join(quote["tags"]),
            }
            writer.writerow(row)

    print(f"CSV guardado: {filename} ({len(quotes)} frases)")


def save_to_json(quotes, filename=OUTPUT_JSON):
    """
    Guarda las frases en un archivo JSON.

    JSON es ideal cuando necesitas preservar la estructura anidada
    (los tags como lista, por ejemplo) o consumir los datos con JavaScript.

    Parámetros:
        quotes (list[dict]): lista de frases a guardar
        filename (str): nombre del archivo JSON de salida
    """
    if not quotes:
        print("No hay datos para guardar en JSON.")
        return

    output_data = {
        "metadata": {
            "source":      BASE_URL,
            "total":       len(quotes),
            "scraped_at":  datetime.now().isoformat(),
            "pages":       MAX_PAGES,
        },
        "quotes": quotes
    }

    with open(filename, "w", encoding="utf-8") as jsonfile:
        # indent=2 hace el JSON legible para humanos
        # ensure_ascii=False preserva caracteres UTF-8 correctamente
        json.dump(output_data, jsonfile, indent=2, ensure_ascii=False)

    print(f"JSON guardado: {filename} ({len(quotes)} frases)")


# =============================================================================
# ANÁLISIS DE LOS DATOS
# =============================================================================

def analyze_quotes(quotes):
    """
    Realiza un análisis básico de las frases extraídas.

    Parámetros:
        quotes (list[dict]): lista de frases con autor y tags
    """
    if not quotes:
        return

    print("\n" + "=" * 50)
    print("  ANÁLISIS DE LOS DATOS EXTRAÍDOS")
    print("=" * 50)

    # Autores más frecuentes
    from collections import Counter

    authors = [q["author"] for q in quotes]
    author_counter = Counter(authors)
    top_authors = author_counter.most_common(5)

    print("\nTop 5 autores con más frases:")
    for author, count in top_authors:
        print(f"  {author:<30} {count} frases")

    # Tags más usados
    all_tags = []
    for q in quotes:
        all_tags.extend(q["tags"])

    tag_counter = Counter(all_tags)
    top_tags = tag_counter.most_common(8)

    print("\nTop 8 tags más frecuentes:")
    for tag, count in top_tags:
        print(f"  #{tag:<25} {count} veces")

    # Estadísticas básicas
    text_lengths = [len(q["text"]) for q in quotes]
    avg_length = sum(text_lengths) / len(text_lengths)
    longest = max(quotes, key=lambda q: len(q["text"]))

    print(f"\nEstadísticas:")
    print(f"  Total de frases:        {len(quotes)}")
    print(f"  Autores únicos:         {len(set(authors))}")
    print(f"  Tags únicos:            {len(set(all_tags))}")
    print(f"  Longitud promedio:      {avg_length:.0f} caracteres")
    print(f"  Frase más larga:        {len(longest['text'])} chars ({longest['author']})")


# =============================================================================
# MODO DEMO (sin internet)
# =============================================================================

def demo_sin_internet():
    """
    Demuestra el flujo del scraper usando datos hardcodeados.
    Se activa automáticamente si no hay conexión a internet.
    """
    print("\n(Modo demo — usando datos de ejemplo sin internet)\n")

    # HTML de ejemplo que simula quotes.toscrape.com
    sample_html = """
    <html><body>
    <div class="quote">
        <span class="text">\u201cEl mundo es un libro y los que no viajan leen solo una p\u00e1gina.\u201d</span>
        <small class="author">San Agust\u00edn</small>
        <a href="/author/San-Agustin">sobre el autor</a>
        <div class="tags"><a class="tag" href="/tag/viaje">viaje</a>
        <a class="tag" href="/tag/libros">libros</a></div>
    </div>
    <div class="quote">
        <span class="text">\u201cLa vida es lo que pasa mientras est\u00e1s ocupado haciendo otros planes.\u201d</span>
        <small class="author">John Lennon</small>
        <a href="/author/John-Lennon">sobre el autor</a>
        <div class="tags"><a class="tag" href="/tag/vida">vida</a>
        <a class="tag" href="/tag/inspiracion">inspiracion</a></div>
    </div>
    </body></html>
    """

    quotes = parse_quotes_page(sample_html)
    print("Frases extraídas del HTML de demo:")
    for q in quotes:
        print(f"  \"{q['text'][:60]}...\"")
        print(f"  — {q['author']} | Tags: {q['tags']}\n")

    return quotes


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal del scraper."""

    if not LIBS_AVAILABLE:
        print("Faltan librerías. Instala con:")
        print("  pip install requests beautifulsoup4")
        return

    print("=" * 60)
    print("  PROYECTO: Scraper de quotes.toscrape.com")
    print("=" * 60)
    print("\nquotes.toscrape.com es un sitio diseñado para aprender scraping.")
    print("Respetamos sus términos y aplicamos rate limiting ético.\n")

    quotes = []

    # Intentar scraping real con conexión a internet
    try:
        test = requests.get(BASE_URL, timeout=8)
        test.raise_for_status()
        # Si llegamos aquí, hay conexión
        quotes = scrape_quotes(max_pages=MAX_PAGES)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("Sin conexión a internet.")
        quotes = demo_sin_internet()

    except Exception as e:
        print(f"Error al conectar: {e}")
        quotes = demo_sin_internet()

    # Guardar resultados si tenemos datos
    if quotes:
        print("\n--- Guardando resultados ---")
        save_to_csv(quotes, OUTPUT_CSV)
        save_to_json(quotes, OUTPUT_JSON)

        # Mostrar muestra de los datos
        print("\n--- Muestra de frases extraídas ---")
        for quote in quotes[:3]:
            print(f"\n  \"{quote['text'][:80]}...\"")
            print(f"  — {quote['author']}")
            print(f"  Tags: {', '.join(quote['tags'][:4])}")

        # Análisis
        analyze_quotes(quotes)

        # Limpiar archivos generados (demo)
        for f in [OUTPUT_CSV, OUTPUT_JSON]:
            if os.path.exists(f):
                os.remove(f)
                print(f"\nArchivo '{f}' eliminado (limpieza de demo).")

    print("\nScraper finalizado.")


if __name__ == "__main__":
    main()
