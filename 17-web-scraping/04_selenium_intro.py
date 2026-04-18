# =============================================================================
# 04_selenium_intro.py — Automatización de navegador con Selenium
# =============================================================================
# Selenium controla un navegador web real (Chrome, Firefox) desde Python.
# Es imprescindible cuando el contenido se genera con JavaScript dinámicamente,
# como en SPAs (React, Angular, Vue) o páginas que requieren login.
#
# Instalación:
#   pip install selenium
#
# Requisitos adicionales:
#   - Chrome instalado en tu sistema
#   - ChromeDriver compatible con tu versión de Chrome
#
# Formas de obtener ChromeDriver:
#   Opción A (recomendada): pip install webdriver-manager
#       from webdriver_manager.chrome import ChromeDriverManager
#       from selenium.webdriver.chrome.service import Service
#       driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
#
#   Opción B: Descargar manualmente
#       https://chromedriver.chromium.org/downloads
#       Versión debe coincidir con tu Chrome (ver chrome://version/)
#
#   Opción C: Selenium 4.6+ incluye Selenium Manager (descarga automática)
#       Solo funciona con selenium >= 4.6
#
# Este archivo ejecuta una simulación si Selenium no está instalado.
# =============================================================================

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import (
        TimeoutException,
        NoSuchElementException,
        WebDriverException,
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

import time
import sys


# =============================================================================
# CONCEPTOS FUNDAMENTALES DE SELENIUM (educativos)
# =============================================================================

def explain_selenium_concepts():
    """
    Explica los conceptos principales de Selenium antes del código.
    """
    print("""
CONCEPTOS CLAVE DE SELENIUM:
─────────────────────────────────────────────────────────────

1. WebDriver
   El objeto principal. Representa y controla el navegador.
   driver = webdriver.Chrome()   → abre Chrome
   driver.get("https://url.com") → navega a la URL
   driver.quit()                 → cierra el navegador

2. Localizadores (By)
   Formas de encontrar elementos en la página:
   By.ID          → driver.find_element(By.ID, "mi-id")
   By.CLASS_NAME  → driver.find_element(By.CLASS_NAME, "mi-clase")
   By.CSS_SELECTOR → driver.find_element(By.CSS_SELECTOR, "div.clase")
   By.XPATH       → driver.find_element(By.XPATH, "//div[@id='x']")
   By.TAG_NAME    → driver.find_element(By.TAG_NAME, "h1")
   By.LINK_TEXT   → driver.find_element(By.LINK_TEXT, "Texto del link")

3. Esperas (Waits) — CRÍTICO para páginas con JavaScript
   El navegador puede mostrar el DOM antes de que el JS lo modifique.
   Si buscas un elemento antes de que exista → NoSuchElementException.

   a) Espera implícita (global, para todos los elementos):
      driver.implicitly_wait(10)  → espera hasta 10s por cualquier elemento

   b) Espera explícita (recomendada, para condiciones específicas):
      wait = WebDriverWait(driver, timeout=10)
      element = wait.until(EC.presence_of_element_located((By.ID, "mi-id")))
      element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn")))
      element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "modal")))

4. Interacciones con elementos
   element.click()                    → hacer clic
   element.send_keys("texto")         → escribir texto
   element.send_keys(Keys.ENTER)      → presionar Enter
   element.send_keys(Keys.CONTROL, "a") → Ctrl+A
   element.clear()                    → limpiar campo
   element.text                       → obtener texto visible
   element.get_attribute("href")      → obtener atributo

5. Ejecutar JavaScript
   driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
   result = driver.execute_script("return document.title")

6. Headless Mode (sin ventana gráfica)
   Ideal para servidores o CI/CD donde no hay pantalla.
   options = Options()
   options.add_argument("--headless")
   driver = webdriver.Chrome(options=options)
─────────────────────────────────────────────────────────────
""")


# =============================================================================
# SIMULACIÓN SIN SELENIUM
# =============================================================================

def run_simulation():
    """
    Simula el comportamiento de Selenium cuando no está instalado.

    Esta función imprime exactamente lo que haría el código de Selenium
    real, para que el usuario entienda el flujo sin necesidad de instalarlo.
    """
    print("\n" + "=" * 60)
    print("  SIMULACIÓN: Cómo funcionaría Selenium")
    print("  (Selenium no está instalado — esto es una demo)")
    print("=" * 60)

    steps = [
        ("SETUP",      "Configurando Chrome en modo headless..."),
        ("SETUP",      "Iniciando ChromeDriver..."),
        ("NAVIGATE",   "driver.get('https://quotes.toscrape.com/login')"),
        ("WAIT",       "Esperando que cargue el formulario de login..."),
        ("FIND",       "driver.find_element(By.ID, 'username')"),
        ("INTERACT",   "username_field.send_keys('user@example.com')"),
        ("FIND",       "driver.find_element(By.ID, 'password')"),
        ("INTERACT",   "password_field.send_keys('mypassword')"),
        ("INTERACT",   "password_field.send_keys(Keys.ENTER)"),
        ("WAIT",       "WebDriverWait: esperando redirección post-login..."),
        ("NAVIGATE",   "driver.get('https://quotes.toscrape.com/')"),
        ("FIND",       "driver.find_elements(By.CSS_SELECTOR, 'div.quote')"),
        ("EXTRACT",    "Extrayendo 10 frases de la página..."),
        ("SCROLL",     "execute_script: scroll al final de página"),
        ("WAIT",       "Esperando contenido dinámico (lazy loading)..."),
        ("SCREENSHOT", "driver.save_screenshot('resultado.png')"),
        ("CLEANUP",    "driver.quit()  — cerrando navegador"),
    ]

    for step_type, description in steps:
        # Simular tiempo de ejecución
        time.sleep(0.15)
        print(f"  [{step_type:10}] {description}")

    print("\n  Simulación completada.")
    print("  Para ejecutar código real, instala: pip install selenium webdriver-manager")


# =============================================================================
# CÓDIGO SELENIUM REAL
# =============================================================================

def create_driver(headless=True):
    """
    Crea y configura el WebDriver de Chrome.

    Parámetros:
        headless (bool): True = sin ventana gráfica (ideal para automatización)

    Retorna:
        WebDriver: objeto driver configurado

    El modo headless es preferido para:
    - Servidores sin interfaz gráfica
    - Integración continua (CI/CD)
    - Mayor velocidad de ejecución
    """
    options = Options()

    if headless:
        # Modo sin ventana visible — el navegador corre en segundo plano
        options.add_argument("--headless=new")  # nueva API de headless en Chrome 112+

    # Opciones recomendadas para estabilidad
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )

    # Suprimir logs innecesarios de Chrome
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=options)

    # Espera implícita: si un elemento no existe aún, espera hasta N segundos
    driver.implicitly_wait(5)

    return driver


def demo_navegacion_basica(driver):
    """
    Demuestra navegación básica con Selenium.

    Parámetros:
        driver: WebDriver activo
    """
    print("\n[1] Navegación básica:")

    driver.get("https://quotes.toscrape.com/")
    print(f"  URL actual: {driver.current_url}")
    print(f"  Título:     {driver.title}")

    # Obtener el encabezado principal
    h1 = driver.find_element(By.TAG_NAME, "h1")
    print(f"  H1:         {h1.text}")


def demo_esperas_explicitas(driver):
    """
    Demuestra las esperas explícitas — la forma correcta de manejar JS.

    Parámetros:
        driver: WebDriver activo

    Las esperas explícitas esperan hasta que una CONDICIÓN se cumpla.
    Son más precisas y confiables que time.sleep() fijo.
    """
    print("\n[2] Esperas explícitas (WebDriverWait):")

    # Crear objeto Wait con timeout de 10 segundos
    wait = WebDriverWait(driver, timeout=10)

    try:
        # Esperar hasta que las tarjetas de frases estén presentes en el DOM
        quotes = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.quote"))
        )
        print(f"  Frases cargadas: {len(quotes)}")

        # Extraer texto de las primeras 3 frases
        for i, quote in enumerate(quotes[:3], 1):
            text_elem = quote.find_element(By.CSS_SELECTOR, "span.text")
            author_elem = quote.find_element(By.CSS_SELECTOR, "small.author")
            text = text_elem.text[:60]
            author = author_elem.text
            print(f"  Frase {i}: \"{text}...\" — {author}")

    except TimeoutException:
        print("  Timeout: los elementos no cargaron en 10 segundos")


def demo_interacciones(driver):
    """
    Demuestra cómo interactuar con elementos de la página.

    Parámetros:
        driver: WebDriver activo
    """
    print("\n[3] Interacciones con elementos:")

    wait = WebDriverWait(driver, timeout=10)

    # Navegar a la página de login
    driver.get("https://quotes.toscrape.com/login")

    try:
        # Esperar y encontrar el formulario
        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = driver.find_element(By.ID, "password")
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")

        print(f"  Formulario encontrado. Campos: username, password")
        print(f"  Botón de submit: '{submit_button.get_attribute('value')}'")

        # Escribir en los campos (simulamos credenciales)
        username_field.clear()
        username_field.send_keys("usuario_demo")

        password_field.clear()
        password_field.send_keys("password_demo")

        print("  Datos del formulario completados (no enviamos para no hacer login real)")

        # Obtener los valores escritos para verificar
        print(f"  Valor en username: '{username_field.get_attribute('value')}'")

    except (TimeoutException, NoSuchElementException) as e:
        print(f"  Error encontrando elementos: {e}")


def demo_scroll_y_javascript(driver):
    """
    Demuestra el scroll y la ejecución de JavaScript.

    Parámetros:
        driver: WebDriver activo

    execute_script() permite ejecutar código JavaScript directamente
    en el contexto de la página, muy útil para:
    - Hacer scroll
    - Modificar elementos
    - Obtener datos que no están en el DOM directamente
    """
    print("\n[4] Scroll y JavaScript:")

    driver.get("https://quotes.toscrape.com/")

    # Obtener altura inicial del viewport
    initial_height = driver.execute_script("return window.pageYOffset")
    print(f"  Posición de scroll inicial: {initial_height}px")

    # Scroll al final de la página usando JavaScript
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(0.5)

    # Verificar nueva posición
    new_height = driver.execute_script("return window.pageYOffset")
    print(f"  Posición tras scroll al final: {new_height}px")

    # Obtener el título de la página vía JavaScript
    page_title = driver.execute_script("return document.title")
    print(f"  Título (via JS): {page_title}")

    # Scroll de vuelta al inicio
    driver.execute_script("window.scrollTo(0, 0)")
    print("  Scroll de vuelta al inicio.")


def demo_multiples_paginas(driver):
    """
    Demuestra cómo navegar entre páginas usando Selenium.

    Parámetros:
        driver: WebDriver activo
    """
    print("\n[5] Navegar entre páginas:")

    driver.get("https://quotes.toscrape.com/")

    wait = WebDriverWait(driver, timeout=10)
    page = 1

    while page <= 3:
        quotes = driver.find_elements(By.CSS_SELECTOR, "div.quote")
        print(f"  Página {page}: {len(quotes)} frases | URL: {driver.current_url}")

        # Buscar el botón "Next"
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "li.next a")
            next_btn.click()

            # Esperar a que la nueva página cargue
            wait.until(EC.staleness_of(quotes[0]))  # el elemento viejo desaparece
            time.sleep(0.5)
            page += 1

        except NoSuchElementException:
            print("  No hay más páginas.")
            break


def run_selenium_demo():
    """
    Ejecuta la demostración real de Selenium.
    Se activa solo si Selenium está instalado y Chrome disponible.
    """
    print("\n" + "=" * 60)
    print("  DEMO REAL: Selenium WebDriver en acción")
    print("=" * 60)

    driver = None
    try:
        print("\nIniciando Chrome en modo headless...")
        driver = create_driver(headless=True)
        print("Chrome iniciado correctamente.")

        demo_navegacion_basica(driver)
        demo_esperas_explicitas(driver)
        demo_interacciones(driver)
        demo_scroll_y_javascript(driver)
        demo_multiples_paginas(driver)

        print("\n[OK] Demo de Selenium completado exitosamente.")

    except WebDriverException as e:
        print(f"\nError al iniciar Chrome: {e}")
        print("\nPosibles causas:")
        print("  1. Chrome no está instalado")
        print("  2. ChromeDriver no coincide con la versión de Chrome")
        print("  3. Instala: pip install webdriver-manager")
        print("     Y modifica create_driver() para usar ChromeDriverManager")
        print("\nEjemplo con webdriver-manager:")
        print("  from webdriver_manager.chrome import ChromeDriverManager")
        print("  from selenium.webdriver.chrome.service import Service")
        print("  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))")

    finally:
        # Siempre cerrar el driver para liberar recursos
        if driver:
            driver.quit()
            print("ChromeDriver cerrado.")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal del archivo de Selenium."""

    print("=" * 60)
    print("  DEMO: Selenium — Automatización de Navegador")
    print("=" * 60)

    # Mostrar conceptos teóricos siempre
    explain_selenium_concepts()

    if not SELENIUM_AVAILABLE:
        print("Selenium NO está instalado.")
        print("\nPara instalarlo:")
        print("  pip install selenium")
        print("  pip install webdriver-manager  (recomendado para ChromeDriver)")
        print()

        # Ejecutar simulación para mostrar el flujo conceptualmente
        run_simulation()
    else:
        print("Selenium está instalado.")
        print("Versión: selenium " + __import__("selenium").__version__)
        run_selenium_demo()


if __name__ == "__main__":
    main()
