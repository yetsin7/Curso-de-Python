# =============================================================================
# CAPÍTULO 27 — Concurrencia y Asincronismo
# Archivo 3: asyncio — Programación asíncrona básica
# =============================================================================
# Temas: async/await, event loop, coroutines, asyncio.sleep,
# asyncio.gather, asyncio.create_task. Diferencia con threads.
# Scraper asíncrono simulado como ejemplo práctico.
# =============================================================================

import asyncio
import time
import random


# =============================================================================
# CONCEPTOS CLAVE ANTES DE EMPEZAR
# =============================================================================
# asyncio es CONCURRENTE, no PARALELO.
# Un solo thread ejecuta todo el código. La clave es que cuando una
# corrutina hace "await algo", le CEDE el control al event loop,
# que puede ejecutar otras corrutinas mientras espera.
#
# Analogía: Un mesero que atiende múltiples mesas. No clona a sí mismo
# (paralelo), pero mientras la cocina prepara el plato de la mesa 1,
# atiende a la mesa 2 (concurrente).
# =============================================================================


# =============================================================================
# SECCIÓN 1: Corrutinas básicas — async def y await
# =============================================================================

print("=" * 60)
print("1. Corrutinas básicas — async def / await")
print("=" * 60)


async def saludar(nombre, delay):
    """
    Corrutina básica: función asíncrona definida con async def.
    await asyncio.sleep() cede el control al event loop durante la espera,
    permitiendo que otras corrutinas se ejecuten en ese tiempo.
    """
    print(f"  Iniciando saludo a {nombre}")
    await asyncio.sleep(delay)  # Cede el control — NO bloquea el thread
    print(f"  Hola, {nombre}! (después de {delay}s)")
    return f"Saludo a {nombre} completado"


async def demo_basica():
    """Demostración de corrutinas ejecutadas secuencialmente."""
    # Llamar corrutinas con await las ejecuta UNA POR UNA
    print("Ejecutando secuencialmente con await:")
    inicio = time.time()
    await saludar("Alice", 0.5)
    await saludar("Bob", 0.3)
    await saludar("Carlos", 0.4)
    print(f"  Tiempo total: {time.time()-inicio:.2f}s (secuencial = suma de todos)\n")

asyncio.run(demo_basica())


# =============================================================================
# SECCIÓN 2: asyncio.gather — Ejecutar múltiples corrutinas CONCURRENTEMENTE
# =============================================================================

print("=" * 60)
print("2. asyncio.gather — Concurrencia real")
print("=" * 60)


async def demo_gather():
    """
    asyncio.gather ejecuta múltiples corrutinas concurrentemente.
    Todas se inician casi simultáneamente y el tiempo total
    es aproximadamente el de la más lenta (no la suma).
    """
    print("Ejecutando concurrentemente con asyncio.gather:")
    inicio = time.time()

    # gather lanza todas las corrutinas y espera a que TODAS terminen
    resultados = await asyncio.gather(
        saludar("Alice", 0.5),
        saludar("Bob", 0.3),
        saludar("Carlos", 0.4),
    )

    print(f"  Tiempo total: {time.time()-inicio:.2f}s (concurrente ≈ max de todos)")
    print(f"  Resultados: {resultados}")

asyncio.run(demo_gather())


# =============================================================================
# SECCIÓN 3: asyncio.create_task — Tareas con más control
# =============================================================================

print("\n" + "=" * 60)
print("3. asyncio.create_task — Tareas independientes")
print("=" * 60)


async def tarea_con_resultado(nombre, duracion, valor):
    """
    Corrutina que simula trabajo y retorna un valor.
    Con create_task podemos lanzarla y no esperar inmediatamente.
    """
    await asyncio.sleep(duracion)
    return {"tarea": nombre, "resultado": valor * 2}


async def demo_create_task():
    """
    create_task permite lanzar corrutinas y continuar haciendo otras cosas
    mientras se ejecutan. Es más flexible que gather para control granular.
    """
    print("Creando tareas independientes:")

    # Las tareas SE INICIAN INMEDIATAMENTE al crear, sin necesidad de await
    tarea1 = asyncio.create_task(tarea_con_resultado("A", 0.6, 10))
    tarea2 = asyncio.create_task(tarea_con_resultado("B", 0.2, 20))
    tarea3 = asyncio.create_task(tarea_con_resultado("C", 0.4, 30))

    print("  Tareas lanzadas — haciendo otras cosas mientras esperan...")
    await asyncio.sleep(0.1)  # Podemos hacer trabajo mientras las tareas corren
    print("  Trabajo intermedio completado")

    # Ahora esperamos los resultados
    r1 = await tarea1
    r2 = await tarea2
    r3 = await tarea3

    print(f"  Resultados: {r1}, {r2}, {r3}")

    # Cancelar una tarea (útil para timeouts manuales)
    tarea_larga = asyncio.create_task(tarea_con_resultado("Larga", 10, 99))
    await asyncio.sleep(0.1)
    tarea_larga.cancel()
    try:
        await tarea_larga
    except asyncio.CancelledError:
        print("  Tarea larga cancelada correctamente")

asyncio.run(demo_create_task())


# =============================================================================
# SECCIÓN 4: Diferencia conceptual con threads
# =============================================================================

print("\n" + "=" * 60)
print("4. Threading vs Asyncio — Comparativa visual")
print("=" * 60)


async def visualizar_concurrencia():
    """
    Muestra visualmente cómo asyncio cede el control entre corrutinas,
    simulando el comportamiento del event loop.
    """
    async def tarea_visual(nombre, pasos, delay):
        for i in range(pasos):
            print(f"  {nombre}: paso {i+1}/{pasos}")
            await asyncio.sleep(delay)  # Cede control aquí

    # Todas corren en el MISMO thread, cooperando
    import threading
    print(f"  Thread actual: {threading.current_thread().name}")
    print("  Observa cómo las tareas se intercalan (cooperativo):\n")

    await asyncio.gather(
        tarea_visual("Azul  ", 3, 0.15),
        tarea_visual("Verde ", 3, 0.15),
        tarea_visual("Rojo  ", 3, 0.15),
    )

asyncio.run(visualizar_concurrencia())

print("\nCONCLUSIÓN:")
print("  - asyncio: 1 thread, cooperativo, ideal para I/O masivo")
print("  - threading: N threads, preemptivo, GIL limita CPU-bound")
print("  - La diferencia: asyncio es como un orquestador que decide")
print("    cuándo ejecutar cada cosa. Threading usa el OS para eso.")


# =============================================================================
# SECCIÓN 5: Scraper asíncrono simulado (caso de uso real)
# =============================================================================

print("\n" + "=" * 60)
print("5. Scraper asíncrono simulado")
print("=" * 60)

# Datos simulados — en producción usarías aiohttp para peticiones HTTP reales
PAGINAS_SIMULADAS = {
    "https://ejemplo.com/productos": {"items": 150, "latencia": 0.8},
    "https://ejemplo.com/categorias": {"items": 25, "latencia": 0.4},
    "https://ejemplo.com/usuarios": {"items": 1000, "latencia": 1.2},
    "https://api.ejemplo.com/precios": {"items": 300, "latencia": 0.6},
    "https://api.ejemplo.com/inventario": {"items": 200, "latencia": 0.9},
}


async def scrape_pagina(url, datos_simulados):
    """
    Simula el scraping de una URL.
    En producción: async with aiohttp.ClientSession() as session:
                       response = await session.get(url)
                       html = await response.text()
    """
    latencia = datos_simulados["latencia"]
    print(f"  Iniciando: {url}")
    await asyncio.sleep(latencia)  # Simula petición HTTP

    resultado = {
        "url": url,
        "items_encontrados": datos_simulados["items"],
        "tiempo_respuesta": latencia,
    }
    print(f"  Completado: {url} ({datos_simulados['items']} items en {latencia}s)")
    return resultado


async def scraper_principal():
    """
    Orquesta el scraping de múltiples páginas concurrentemente.
    Compara rendimiento vs scraping secuencial.
    """
    # MODO SECUENCIAL (para comparar)
    print("--- SECUENCIAL ---")
    inicio = time.time()
    resultados_seq = []
    for url, datos in PAGINAS_SIMULADAS.items():
        r = await scrape_pagina(url, datos)
        resultados_seq.append(r)
    tiempo_seq = time.time() - inicio

    total_items = sum(r["items_encontrados"] for r in resultados_seq)
    print(f"  Secuencial: {tiempo_seq:.2f}s — {total_items} items totales\n")

    # MODO CONCURRENTE (asyncio.gather)
    print("--- CONCURRENTE (asyncio.gather) ---")
    inicio = time.time()
    tareas = [scrape_pagina(url, datos) for url, datos in PAGINAS_SIMULADAS.items()]
    resultados_async = await asyncio.gather(*tareas)
    tiempo_async = time.time() - inicio

    total_items = sum(r["items_encontrados"] for r in resultados_async)
    print(f"\n  Concurrente: {tiempo_async:.2f}s — {total_items} items totales")
    print(f"  Speedup: {tiempo_seq/tiempo_async:.1f}x más rápido")

    # Ordenar por items encontrados
    por_items = sorted(resultados_async, key=lambda x: x["items_encontrados"], reverse=True)
    print("\n  Top páginas por cantidad de items:")
    for r in por_items:
        url_corta = r["url"].replace("https://", "")
        print(f"    {url_corta}: {r['items_encontrados']:,} items")


asyncio.run(scraper_principal())

print("\nFIN: 03_asyncio_basico.py completado")
