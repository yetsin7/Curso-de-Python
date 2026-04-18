# Capítulo 17 — Web Scraping con Python

## ¿Qué es el Web Scraping?

**Web scraping** es la técnica de extraer datos automáticamente de páginas web. Un programa descarga el HTML de una página y extrae la información que nos interesa.

### ¿Para qué sirve?
- **Investigación**: recopilar datos de precios, noticias, reseñas.
- **Ciencia de datos**: crear datasets de entrenamiento.
- **Monitoreo**: vigilar cambios en páginas web.
- **Automatización**: extraer datos de sitios que no tienen API.
- **Agregación**: combinar datos de múltiples fuentes.

---

## Aspectos éticos y legales

Antes de hacer scraping, **siempre verifica**:

### 1. robots.txt
Cada sitio web puede tener un archivo `robots.txt` que indica qué partes pueden ser rastreadas por bots.

```
https://ejemplo.com/robots.txt
```

```
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /public/
```

**Respetar `robots.txt` es una práctica ética fundamental.**

### 2. Términos de servicio (ToS)
Muchos sitios prohíben explícitamente el scraping automatizado en sus términos de uso. Leerlos es obligatorio.

### 3. Buenas prácticas
- Añade **delays** entre peticiones (no sobrecargues el servidor).
- Identifica tu bot con un **User-Agent** descriptivo.
- Usa **caché**: no descargues la misma página dos veces.
- No extraigas datos personales sin consentimiento (GDPR, LOPD).
- Si el sitio tiene API, **úsala en lugar de scraping**.

### Legalidad
El scraping de **datos públicos** generalmente está permitido para uso personal e investigación, pero siempre puede variar según la jurisdicción. Para uso comercial, consulta con un abogado.

---

## Herramientas principales

### requests — Hacer peticiones HTTP
La librería más popular para hacer peticiones HTTP en Python.

```bash
pip install requests
```

- Hace GET, POST, PUT, DELETE, etc.
- Maneja headers, cookies, autenticación, sesiones.
- Devuelve el HTML crudo de la página.

### BeautifulSoup4 — Parsear HTML
Convierte el HTML crudo en una estructura de objetos navegable.

```bash
pip install beautifulsoup4
```

- Busca elementos por tag, id, clase CSS, atributo.
- Extrae texto, atributos y estructura del HTML.
- Soporta varios parsers: `html.parser` (incluido), `lxml` (más rápido).

### Cuándo usar requests + BeautifulSoup
- Páginas **estáticas**: el contenido está en el HTML original.
- Sitios simples sin JavaScript dinámico.
- La opción más ligera y fácil de aprender.

### Scrapy — Framework completo de scraping
Framework profesional para scraping a gran escala.

```bash
pip install scrapy
```

- Maneja concurrencia, reintentos, pipelines de datos.
- Ideal para proyectos grandes que rastrean miles de páginas.
- Curva de aprendizaje más alta.
- Tiene su propio sistema de comandos CLI.

### Selenium — Automatización de navegador real
Controla un navegador web real (Chrome, Firefox) desde Python.

```bash
pip install selenium
```

- Puede ejecutar JavaScript (lo que requests no puede).
- Simula interacciones reales: clics, formularios, scrolling.
- Imprescindible para sitios con **contenido dinámico** (SPAs, React, Angular).
- Más lento que requests porque carga el navegador completo.

---

## ¿Cuándo usar cada herramienta?

| Herramienta | Cuándo usarla |
|-------------|---------------|
| `requests` | Solo necesitas hacer peticiones HTTP, consumir APIs |
| `requests` + `BeautifulSoup` | Scraping de páginas HTML estáticas |
| `Scrapy` | Proyectos grandes, múltiples páginas, pipelines de datos |
| `Selenium` | Páginas con JavaScript, formularios de login, contenido dinámico |
| `Playwright` | Alternativa moderna a Selenium, más rápida y confiable |

---

## Flujo típico de scraping

```
1. requests.get(url)        → Descargar HTML
2. BeautifulSoup(html)      → Parsear HTML
3. soup.find/find_all()     → Extraer datos
4. Guardar en CSV/JSON/DB   → Almacenar resultados
5. Siguiente página         → Repetir hasta terminar
```

---

## Archivos del capítulo

| Archivo | Contenido |
|---------|-----------|
| `01_requests_basico.py` | GET, POST, headers, sesiones, manejo de errores HTTP |
| `02_beautifulsoup.py` | Parsear HTML, selectores CSS, extraer texto y atributos |
| `03_scraping_practico.py` | Proyecto completo: scraping con paginación, CSV y JSON |
| `04_selenium_intro.py` | Selenium conceptual, WebDriver, esperas explícitas |

---

## Conceptos clave

- **HTML**: lenguaje de marcado de las páginas web. El scraping analiza su estructura.
- **CSS Selector**: forma de seleccionar elementos HTML por clase, id, tipo (`div.precio`, `#titulo`).
- **XPath**: otra forma de seleccionar elementos, más potente pero más compleja.
- **Status code HTTP**: 200 OK, 404 Not Found, 403 Forbidden, 429 Too Many Requests.
- **User-Agent**: cabecera HTTP que identifica al cliente (navegador, bot).
- **Rate limiting**: límite de peticiones por segundo que impone el servidor.
- **Headless browser**: navegador sin interfaz gráfica, ideal para servidores.
