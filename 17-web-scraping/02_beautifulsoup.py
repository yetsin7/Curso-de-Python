# =============================================================================
# 02_beautifulsoup.py — Parsear HTML con BeautifulSoup4
# =============================================================================
# BeautifulSoup convierte HTML crudo en una estructura de objetos navegable.
# Es la librería más popular para extraer datos de páginas web.
#
# Instalación:
#   pip install beautifulsoup4
#   pip install requests          (para el ejemplo con internet)
#
# Contenido:
#   - Parsear HTML hardcodeado (sin conexión a internet)
#   - find() y find_all() para buscar elementos
#   - Selectores CSS con select() y select_one()
#   - Extraer texto, atributos y estructuras anidadas
#   - Ejemplo real con requests a un sitio público
# =============================================================================

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# =============================================================================
# HTML DE EJEMPLO — Simula una página web real
# =============================================================================

# Este HTML está hardcodeado para que los ejemplos funcionen sin internet.
# Simula la estructura típica de una tienda en línea.
SAMPLE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <title>TechStore — Productos de Tecnología</title>
    <meta name="description" content="La mejor tienda de tecnología">
</head>
<body>
    <header>
        <nav id="main-nav">
            <a href="/">Inicio</a>
            <a href="/productos">Productos</a>
            <a href="/contacto">Contacto</a>
        </nav>
    </header>

    <main>
        <h1 class="page-title">Catálogo de Productos</h1>
        <p class="subtitle">Descubre nuestra selección de tecnología</p>

        <section id="products-grid">

            <article class="product-card" data-id="1" data-category="laptop">
                <h2 class="product-title">Laptop Pro 15</h2>
                <p class="product-description">Procesador Intel i7, 16GB RAM, SSD 512GB</p>
                <span class="price">$1,299.99</span>
                <span class="badge badge-sale">OFERTA</span>
                <a href="/producto/laptop-pro-15" class="btn-detail">Ver detalle</a>
                <div class="rating" data-score="4.8">★★★★★ (4.8/5)</div>
            </article>

            <article class="product-card" data-id="2" data-category="mouse">
                <h2 class="product-title">Mouse Inalámbrico Ergonómico</h2>
                <p class="product-description">DPI ajustable, batería de 12 meses</p>
                <span class="price">$29.99</span>
                <a href="/producto/mouse-ergonomico" class="btn-detail">Ver detalle</a>
                <div class="rating" data-score="4.5">★★★★☆ (4.5/5)</div>
            </article>

            <article class="product-card" data-id="3" data-category="keyboard">
                <h2 class="product-title">Teclado Mecánico RGB</h2>
                <p class="product-description">Switches Cherry MX, retroiluminación RGB</p>
                <span class="price">$89.99</span>
                <span class="badge badge-new">NUEVO</span>
                <a href="/producto/teclado-mecanico-rgb" class="btn-detail">Ver detalle</a>
                <div class="rating" data-score="4.7">★★★★★ (4.7/5)</div>
            </article>

            <article class="product-card" data-id="4" data-category="monitor">
                <h2 class="product-title">Monitor 4K 27"</h2>
                <p class="product-description">Resolución 4K UHD, 144Hz, IPS</p>
                <span class="price">$399.99</span>
                <a href="/producto/monitor-4k-27" class="btn-detail">Ver detalle</a>
                <div class="rating" data-score="4.9">★★★★★ (4.9/5)</div>
            </article>

        </section>

        <aside id="sidebar">
            <h3>Categorías</h3>
            <ul class="categories-list">
                <li><a href="/cat/laptops">Laptops (12)</a></li>
                <li><a href="/cat/perifericos">Periféricos (34)</a></li>
                <li><a href="/cat/monitores">Monitores (8)</a></li>
            </ul>

            <h3>Rango de precio</h3>
            <form id="price-filter">
                <input type="number" name="min_price" placeholder="Mínimo">
                <input type="number" name="max_price" placeholder="Máximo">
                <button type="submit">Filtrar</button>
            </form>
        </aside>
    </main>

    <footer>
        <p>© 2024 TechStore. Todos los derechos reservados.</p>
        <a href="/privacidad">Política de privacidad</a>
        <a href="/terminos">Términos de uso</a>
    </footer>
</body>
</html>
"""


# =============================================================================
# PARSEO BÁSICO
# =============================================================================

def demo_parseo_basico(soup):
    """
    Demuestra las operaciones más básicas de BeautifulSoup.

    Parámetros:
        soup: objeto BeautifulSoup ya parseado

    BeautifulSoup crea un árbol de objetos a partir del HTML.
    Cada nodo HTML se convierte en un objeto Tag con atributos y métodos.
    """
    print("\n--- Parseo Básico ---")

    # Acceder a elementos directamente por nombre de tag
    # soup.title devuelve el primer <title> encontrado
    title = soup.title
    print(f"  Título de la página: {title.string}")

    # .string devuelve el texto del elemento si solo tiene texto
    # .text o .get_text() funciona aunque haya elementos anidados
    h1 = soup.find("h1")
    print(f"  Encabezado H1: {h1.text.strip()}")

    # Acceder a atributos como diccionario
    nav = soup.find("nav")
    nav_id = nav.get("id", "sin-id")
    print(f"  ID del nav principal: {nav_id}")

    # soup.head / soup.body acceden directamente a esas secciones
    meta = soup.find("meta", {"name": "description"})
    if meta:
        print(f"  Meta description: {meta.get('content', 'N/A')}")


# =============================================================================
# find() Y find_all()
# =============================================================================

def demo_find_methods(soup):
    """
    Demuestra find() y find_all() — los métodos más usados de BeautifulSoup.

    find(): devuelve el PRIMER elemento que coincide (o None si no encuentra)
    find_all(): devuelve una LISTA de todos los elementos que coinciden
    """
    print("\n--- find() y find_all() ---")

    # find_all() por nombre de tag — todos los <article>
    articles = soup.find_all("article")
    print(f"  Artículos encontrados: {len(articles)}")

    # find_all() por clase CSS — busca elementos con class="product-card"
    # Nota: 'class_' con guion bajo porque 'class' es keyword de Python
    product_cards = soup.find_all("article", class_="product-card")
    print(f"  Tarjetas de producto: {len(product_cards)}")

    # find() por ID — busca el elemento con id="products-grid"
    grid = soup.find("div", id="products-grid") or soup.find("section", id="products-grid")
    print(f"  Grid de productos encontrado: {grid is not None}")

    # find_all() por atributo personalizado (data attributes)
    laptops = soup.find_all("article", {"data-category": "laptop"})
    print(f"  Productos de categoría 'laptop': {len(laptops)}")

    # Extraer información de cada tarjeta de producto
    print("\n  Lista de productos:")
    for card in product_cards:
        # Buscar elementos dentro del card (búsqueda contextual)
        title_tag = card.find("h2", class_="product-title")
        price_tag = card.find("span", class_="price")
        rating_div = card.find("div", class_="rating")
        badge = card.find("span", class_="badge")

        title_text = title_tag.text.strip() if title_tag else "N/A"
        price_text = price_tag.text.strip() if price_tag else "N/A"
        # data-score es un atributo personalizado del HTML
        score = rating_div.get("data-score", "N/A") if rating_div else "N/A"
        badge_text = badge.text.strip() if badge else ""

        badge_str = f" [{badge_text}]" if badge_text else ""
        print(f"    {title_text:<35} {price_text:<12} ★{score}{badge_str}")


# =============================================================================
# SELECTORES CSS
# =============================================================================

def demo_css_selectors(soup):
    """
    Demuestra el uso de selectores CSS para buscar elementos.

    select() equivale a find_all() pero usa sintaxis CSS.
    select_one() equivale a find() con selectores CSS.

    Sintaxis CSS:
        'h1'              → por tag
        '.clase'          → por clase
        '#id'             → por id
        'div.clase'       → tag con clase específica
        'div > p'         → p hijo directo de div
        'div p'           → p descendiente de div (cualquier nivel)
        '[atributo]'      → elemento con ese atributo
        '[attr="valor"]'  → elemento con attr=valor exacto
    """
    print("\n--- Selectores CSS con select() ---")

    # Selector de clase — todos los .price
    prices = soup.select(".price")
    price_values = [p.text.strip() for p in prices]
    print(f"  Precios (.price): {price_values}")

    # Selector combinado — título dentro de product-card
    product_titles = soup.select(".product-card .product-title")
    print(f"\n  Títulos en product-card: {len(product_titles)}")
    for t in product_titles:
        print(f"    {t.text.strip()}")

    # Selector por atributo — links con clase btn-detail
    detail_links = soup.select("a.btn-detail")
    print(f"\n  Links de detalle:")
    for link in detail_links:
        # El atributo href es la URL del enlace
        href = link.get("href", "N/A")
        text = link.text.strip()
        print(f"    {text} → {href}")

    # select_one() — primer elemento que coincide
    first_badge = soup.select_one(".badge")
    if first_badge:
        print(f"\n  Primera insignia encontrada: '{first_badge.text.strip()}'")

    # Selector descendiente — links dentro del sidebar
    sidebar_links = soup.select("#sidebar a")
    print(f"\n  Links del sidebar ({len(sidebar_links)}):")
    for link in sidebar_links:
        print(f"    {link.text.strip()} → {link.get('href', 'N/A')}")


# =============================================================================
# EXTRAER TODOS LOS LINKS
# =============================================================================

def demo_extraer_links(soup):
    """
    Demuestra cómo extraer todos los enlaces de una página.

    Extraer links es una de las operaciones más comunes en scraping,
    especialmente para encontrar páginas a rastrear (crawling).
    """
    print("\n--- Extraer Todos los Links ---")

    # find_all("a") encuentra todos los elementos <a>
    all_links = soup.find_all("a")

    print(f"  Total de links en la página: {len(all_links)}")
    print("\n  Links encontrados:")

    for link in all_links:
        href = link.get("href", "")     # atributo href (URL del link)
        text = link.get_text().strip()  # texto visible del link
        css_class = link.get("class", [])

        # Filtrar links vacíos
        if href and text:
            class_str = f" [clase: {' '.join(css_class)}]" if css_class else ""
            print(f"    {text:<30} → {href}{class_str}")


# =============================================================================
# NAVEGAR LA ESTRUCTURA DEL ÁRBOL
# =============================================================================

def demo_navegar_arbol(soup):
    """
    Demuestra cómo navegar por la estructura padre-hijo del HTML.

    BeautifulSoup permite navegar en todas las direcciones del árbol:
    - .parent: el elemento padre
    - .children: los hijos directos (generador)
    - .descendants: todos los descendientes
    - .next_sibling / .previous_sibling: elementos al mismo nivel
    """
    print("\n--- Navegación del Árbol HTML ---")

    # Obtener el primer product-card
    first_card = soup.find("article", class_="product-card")

    if first_card:
        print(f"  Primer producto: {first_card.find('h2').text.strip()}")

        # Acceder al padre del article
        parent = first_card.parent
        print(f"  Padre del article: <{parent.name} id='{parent.get('id', '')}'>")

        # Iterar sobre los hijos directos del article
        print("  Hijos directos del article:")
        for child in first_card.children:
            # NavigableString son los textos entre tags (espacios, saltos de línea)
            from bs4 import NavigableString
            if not isinstance(child, NavigableString):
                text = child.get_text().strip()
                if text:
                    print(f"    <{child.name}> → '{text[:40]}'")

        # Siguiente hermano (siguiente article en el mismo contenedor)
        next_card = first_card.find_next_sibling("article")
        if next_card:
            print(f"  Siguiente tarjeta: {next_card.find('h2').text.strip()}")

    # get_text() extrae todo el texto de un contenedor
    footer = soup.find("footer")
    if footer:
        footer_text = footer.get_text(separator=" | ", strip=True)
        print(f"\n  Texto del footer: {footer_text}")


# =============================================================================
# EJEMPLO REAL CON REQUESTS (requiere internet)
# =============================================================================

def demo_con_requests():
    """
    Demuestra el uso conjunto de requests y BeautifulSoup con un sitio real.

    Usamos books.toscrape.com — un sitio diseñado específicamente
    para practicar web scraping de forma legal y ética.
    """
    print("\n--- Ejemplo Real: books.toscrape.com ---")

    if not REQUESTS_AVAILABLE:
        print("  requests no está instalado. Ejecuta: pip install requests")
        return

    url = "http://books.toscrape.com/"

    try:
        # Añadir User-Agent para identificarse correctamente
        headers = {"User-Agent": "Python-Education-Scraper/1.0"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Parsear el HTML de la respuesta
        # 'html.parser' es el parser incluido con Python, no requiere instalación
        soup = BeautifulSoup(response.text, "html.parser")

        # Extraer el título de la página
        print(f"  Página: {soup.title.string.strip()}")

        # Extraer los libros de la primera página
        books = soup.select("article.product_pod")
        print(f"  Libros en primera página: {len(books)}")

        # Mostrar los 5 primeros con título y precio
        print("\n  Primeros 5 libros:")
        for book in books[:5]:
            # El título está en el atributo 'title' del tag <a>, no en el texto visible
            title_tag = book.select_one("h3 a")
            price_tag = book.select_one(".price_color")

            if title_tag and price_tag:
                full_title = title_tag.get("title", title_tag.text).strip()
                price = price_tag.text.strip()
                print(f"    {full_title[:45]:<45} {price}")

    except requests.exceptions.ConnectionError:
        print("  Sin conexión a internet — omitiendo ejemplo real.")
    except requests.exceptions.Timeout:
        print("  Timeout — el servidor tardó demasiado.")
    except Exception as e:
        print(f"  Error inesperado: {e}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal que ejecuta todas las demostraciones de BeautifulSoup."""

    if not BS4_AVAILABLE:
        print("BeautifulSoup4 no está instalado.")
        print("Ejecuta: pip install beautifulsoup4")
        return

    print("=" * 60)
    print("  DEMO: BeautifulSoup4 — Parsear HTML con Python")
    print("=" * 60)

    # Parsear el HTML de ejemplo (sin necesidad de internet)
    # 'html.parser' es el parser de Python estándar
    # 'lxml' es más rápido pero requiere: pip install lxml
    soup = BeautifulSoup(SAMPLE_HTML, "html.parser")

    print("\nUsando HTML hardcodeado (no requiere internet).")

    demo_parseo_basico(soup)
    demo_find_methods(soup)
    demo_css_selectors(soup)
    demo_extraer_links(soup)
    demo_navegar_arbol(soup)

    # El ejemplo real requiere internet
    print("\n" + "-" * 60)
    print("(El siguiente ejemplo requiere conexión a internet)")
    demo_con_requests()

    print("\n" + "=" * 60)
    print("  Demo completado.")
    print("=" * 60)


if __name__ == "__main__":
    main()
