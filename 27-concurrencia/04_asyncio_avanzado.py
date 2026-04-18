# =============================================================================
# CAPÍTULO 27 — Concurrencia y Asincronismo
# Archivo 4: asyncio avanzado
# =============================================================================
# Temas: asyncio.Queue, Semaphore, timeout con asyncio.wait_for,
# aiofiles (pip install aiofiles), aiohttp conceptual,
# asyncio.run_in_executor para código bloqueante.
# Ejemplo: pipeline asíncrono de procesamiento de datos.
# =============================================================================

import asyncio
import time
import random
import tempfile
import os

# Intentar importar aiofiles
try:
    import aiofiles
    AIOFILES_DISPONIBLE = True
except ImportError:
    AIOFILES_DISPONIBLE = False
    print("NOTA: aiofiles no instalado. Instala con: pip install aiofiles")
    print("      La sección de I/O de archivos asíncrono será omitida.\n")


# =============================================================================
# SECCIÓN 1: asyncio.Queue — Cola asíncrona Productor-Consumidor
# =============================================================================

print("=" * 60)
print("1. asyncio.Queue — Productor-Consumidor asíncrono")
print("=" * 60)


async def productor_async(cola, cantidad, nombre):
    """
    Productor asíncrono: genera items y los pone en la cola.
    await cola.put() espera si la cola está llena (respeta maxsize).
    """
    for i in range(cantidad):
        item = {"id": i, "valor": random.randint(10, 99), "origen": nombre}
        await cola.put(item)
        print(f"  [Productor {nombre}] Producido item #{i}")
        await asyncio.sleep(random.uniform(0.05, 0.15))

    # Sentinel para indicar fin
    await cola.put(None)
    print(f"  [Productor {nombre}] Fin de producción")


async def consumidor_async(cola, nombre):
    """
    Consumidor asíncrono: procesa items de la cola hasta el sentinel.
    await cola.get() espera si la cola está vacía — sin desperdiciar CPU.
    """
    procesados = 0
    while True:
        item = await cola.get()
        if item is None:
            await cola.put(None)  # Reencolar para otros consumidores
            cola.task_done()
            break

        # Simular procesamiento asíncrono
        await asyncio.sleep(0.1)
        resultado = item["valor"] ** 2
        procesados += 1
        print(f"  [Consumidor {nombre}] item #{item['id']}: {item['valor']}² = {resultado}")
        cola.task_done()

    print(f"  [Consumidor {nombre}] Total procesados: {procesados}")


async def demo_queue():
    """Orquesta productores y consumidores con asyncio.Queue."""
    cola = asyncio.Queue(maxsize=5)  # maxsize limita ítems en cola simultáneamente

    await asyncio.gather(
        productor_async(cola, 5, "A"),
        consumidor_async(cola, "X"),
        consumidor_async(cola, "Y"),
    )
    await cola.join()  # Espera hasta que todos los items sean procesados

asyncio.run(demo_queue())


# =============================================================================
# SECCIÓN 2: asyncio.Semaphore — Limitar concurrencia
# =============================================================================

print("\n" + "=" * 60)
print("2. asyncio.Semaphore — Limitar concurrencia máxima")
print("=" * 60)

# Problema: Lanzar 20 peticiones HTTP simultáneas puede sobrecargar el servidor
# Solución: Semaphore limita cuántas se ejecutan al mismo tiempo


async def peticion_limitada(semaforo, url_id):
    """
    Simula una petición HTTP. Usa Semaphore para respetar un límite.
    Solo 'N' peticiones pueden estar activas al mismo tiempo.
    """
    async with semaforo:  # Adquiere un slot del semáforo (bloquea si están todos ocupados)
        latencia = random.uniform(0.2, 0.8)
        print(f"  Ejecutando petición #{url_id} (latencia: {latencia:.2f}s)")
        await asyncio.sleep(latencia)
        return f"Respuesta de URL-{url_id}"


async def demo_semaphore():
    """
    Demuestra cómo controlar la concurrencia máxima con Semaphore.
    Sin semáforo: todas las peticiones correrían simultáneamente.
    Con semáforo (max=3): máximo 3 corren al mismo tiempo.
    """
    MAX_CONCURRENTES = 3
    semaforo = asyncio.Semaphore(MAX_CONCURRENTES)

    print(f"  Lanzando 10 peticiones con máximo {MAX_CONCURRENTES} simultáneas:")
    inicio = time.time()

    tareas = [peticion_limitada(semaforo, i) for i in range(10)]
    resultados = await asyncio.gather(*tareas)

    print(f"  Completadas en {time.time()-inicio:.2f}s")
    print(f"  Respuestas: {len(resultados)}")

asyncio.run(demo_semaphore())


# =============================================================================
# SECCIÓN 3: asyncio.wait_for — Timeouts en operaciones asíncronas
# =============================================================================

print("\n" + "=" * 60)
print("3. asyncio.wait_for — Timeouts")
print("=" * 60)


async def operacion_lenta(nombre, duracion):
    """Simula una operación que puede tardar demasiado."""
    print(f"  [{nombre}] Iniciando (tardará {duracion}s)...")
    await asyncio.sleep(duracion)
    return f"{nombre} completado"


async def demo_timeout():
    """
    wait_for envuelve una corrutina y lanza asyncio.TimeoutError
    si no termina dentro del tiempo máximo especificado.
    """
    # Caso 1: Operación dentro del timeout
    try:
        resultado = await asyncio.wait_for(
            operacion_lenta("Rápida", 0.3),
            timeout=1.0  # Segundos máximos de espera
        )
        print(f"  Éxito: {resultado}")
    except asyncio.TimeoutError:
        print("  Timeout!")

    # Caso 2: Operación que excede el timeout
    try:
        resultado = await asyncio.wait_for(
            operacion_lenta("Lenta", 2.0),
            timeout=0.5
        )
        print(f"  Éxito: {resultado}")
    except asyncio.TimeoutError:
        print("  Timeout: la operación lenta fue cancelada por exceder 0.5s")

    # Patrón con valor por defecto en timeout
    async def con_fallback(corrutina, timeout, valor_defecto):
        """Wrapper que retorna un valor por defecto si hay timeout."""
        try:
            return await asyncio.wait_for(corrutina, timeout=timeout)
        except asyncio.TimeoutError:
            return valor_defecto

    resultado = await con_fallback(operacion_lenta("Con fallback", 5.0), 0.3, "TIMEOUT_DEFAULT")
    print(f"  Con fallback: {resultado}")

asyncio.run(demo_timeout())


# =============================================================================
# SECCIÓN 4: aiofiles — I/O de archivos no bloqueante
# =============================================================================

print("\n" + "=" * 60)
print("4. aiofiles — Lectura/escritura asíncrona de archivos")
print("=" * 60)


async def demo_aiofiles():
    """
    aiofiles permite operaciones de archivo sin bloquear el event loop.
    Sin aiofiles, open() bloqueante detendría todas las corrutinas del programa.
    """
    if not AIOFILES_DISPONIBLE:
        print("  Omitido — aiofiles no disponible.")
        return

    # Crear archivo temporal para la demo
    tmp = tempfile.mktemp(suffix=".txt")

    # Escritura asíncrona
    async with aiofiles.open(tmp, mode="w", encoding="utf-8") as f:
        for i in range(10):
            await f.write(f"Línea {i+1}: datos generados asíncronamente\n")
    print(f"  Archivo escrito: {tmp}")

    # Lectura asíncrona
    async with aiofiles.open(tmp, mode="r", encoding="utf-8") as f:
        contenido = await f.read()
    print(f"  Primeras 2 líneas leídas:")
    for linea in contenido.split("\n")[:2]:
        print(f"    {linea}")

    # Lectura línea por línea (streaming)
    async with aiofiles.open(tmp, mode="r", encoding="utf-8") as f:
        async for linea in f:
            pass  # Procesaría cada línea sin bloquear
    print(f"  Lectura streaming: completada")

    os.unlink(tmp)

asyncio.run(demo_aiofiles())


# =============================================================================
# SECCIÓN 5: run_in_executor — Código bloqueante dentro de asyncio
# =============================================================================

print("\n" + "=" * 60)
print("5. run_in_executor — Código bloqueante en asyncio")
print("=" * 60)

# PROBLEMA: ¿Qué pasa si necesitas llamar código que NO es async?
# Por ejemplo: una librería que usa requests (síncrona), PIL para imágenes,
# o cualquier función que use time.sleep().
# run_in_executor corre esa función en un ThreadPool o ProcessPool
# y le da una interfaz async para que no bloquee el event loop.


def operacion_bloqueante(nombre, duracion):
    """
    Función síncrona que bloquea (usa time.sleep, no asyncio.sleep).
    Si la llamamos directamente con await no podemos — no es async.
    Si la llamamos sin await, BLOQUEA TODA LA APLICACIÓN.
    """
    time.sleep(duracion)  # Bloquea el thread — NO cede control al event loop
    return f"{nombre}: completado en {duracion}s"


async def demo_executor():
    """
    run_in_executor toma una función bloqueante y la ejecuta en un
    ThreadPoolExecutor, retornando un Future que podemos await.
    El event loop sigue funcionando mientras la función corre en otro thread.
    """
    loop = asyncio.get_event_loop()

    print("  Ejecutando 3 funciones bloqueantes concurrentemente:")
    inicio = time.time()

    # Envolver funciones bloqueantes para que sean awaitable
    tareas = [
        loop.run_in_executor(None, operacion_bloqueante, f"Op-{i}", random.uniform(0.3, 0.8))
        for i in range(3)
    ]

    resultados = await asyncio.gather(*tareas)
    print(f"  Tiempo: {time.time()-inicio:.2f}s")
    for r in resultados:
        print(f"    {r}")

asyncio.run(demo_executor())


# =============================================================================
# SECCIÓN 6: Pipeline asíncrono de procesamiento de datos
# =============================================================================

print("\n" + "=" * 60)
print("6. Pipeline asíncrono de procesamiento de datos")
print("=" * 60)

# ARQUITECTURA DEL PIPELINE:
# Fuente → [Cola 1] → Transformador → [Cola 2] → Escritor


async def fuente_datos(cola_entrada, cantidad):
    """
    Etapa 1: Genera registros de datos crudos y los coloca en la cola.
    Simula lectura de archivos o base de datos.
    """
    for i in range(cantidad):
        registro = {
            "id": i,
            "texto": f"registro_{i}_datos_crudos",
            "valor": random.randint(1, 100),
        }
        await cola_entrada.put(registro)
        await asyncio.sleep(0.03)

    await cola_entrada.put(None)
    print(f"  [Fuente] {cantidad} registros generados")


async def transformador(cola_entrada, cola_salida):
    """
    Etapa 2: Toma registros, los transforma y los pone en la cola de salida.
    Simula procesamiento: limpieza, enriquecimiento, validación.
    """
    procesados = 0
    while True:
        registro = await cola_entrada.get()
        if registro is None:
            await cola_salida.put(None)
            cola_entrada.task_done()
            break

        # Transformaciones
        transformado = {
            "id": registro["id"],
            "texto": registro["texto"].upper().replace("_DATOS_CRUDOS", ""),
            "valor_original": registro["valor"],
            "valor_procesado": registro["valor"] * 2,
            "valido": registro["valor"] > 20,  # Filtro de validación
        }

        await asyncio.sleep(0.02)  # Simula tiempo de transformación
        await cola_salida.put(transformado)
        procesados += 1
        cola_entrada.task_done()

    print(f"  [Transformador] {procesados} registros transformados")


async def escritor(cola_salida):
    """
    Etapa 3: Toma registros transformados y los "persiste".
    Simula escritura a BD, archivo, API, etc.
    """
    escritos = 0
    invalidos = 0
    total_valor = 0

    while True:
        registro = await cola_salida.get()
        if registro is None:
            cola_salida.task_done()
            break

        if registro["valido"]:
            total_valor += registro["valor_procesado"]
            escritos += 1
        else:
            invalidos += 1

        await asyncio.sleep(0.01)  # Simula escritura
        cola_salida.task_done()

    print(f"  [Escritor] Escritos: {escritos}, Descartados: {invalidos}")
    print(f"  [Escritor] Suma total de valores procesados: {total_valor}")


async def ejecutar_pipeline(cantidad_registros):
    """
    Orquesta el pipeline completo conectando todas las etapas con colas.
    """
    cola_1 = asyncio.Queue(maxsize=10)
    cola_2 = asyncio.Queue(maxsize=10)

    inicio = time.time()

    await asyncio.gather(
        fuente_datos(cola_1, cantidad_registros),
        transformador(cola_1, cola_2),
        escritor(cola_2),
    )

    print(f"  Pipeline completado en {time.time()-inicio:.2f}s")
    print(f"  Registros procesados: {cantidad_registros}")


asyncio.run(ejecutar_pipeline(20))

print("\nFIN: 04_asyncio_avanzado.py completado")
