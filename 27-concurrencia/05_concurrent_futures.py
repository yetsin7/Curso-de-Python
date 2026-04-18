# =============================================================================
# CAPÍTULO 27 — Concurrencia y Asincronismo
# Archivo 5: concurrent.futures — La forma más Pythónica de paralelismo
# =============================================================================
# Temas: ThreadPoolExecutor, ProcessPoolExecutor, as_completed, map, submit.
# Comparativa de rendimiento con benchmark real.
# =============================================================================

import time
import random
import math
import threading
import multiprocessing
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    as_completed,
    wait,
    FIRST_COMPLETED,
    ALL_COMPLETED,
)


# =============================================================================
# FUNCIONES PARA BENCHMARKS
# =============================================================================

def tarea_io_bound(url_id):
    """
    Simula una tarea I/O-bound (espera de red).
    Ideal para ThreadPoolExecutor.
    """
    latencia = random.uniform(0.1, 0.5)
    time.sleep(latencia)
    return {"url": url_id, "tiempo": latencia, "bytes": random.randint(100, 5000)}


def tarea_cpu_bound(n):
    """
    Tarea CPU-bound pura: calcula si n es primo.
    Ideal para ProcessPoolExecutor.
    """
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def contar_primos_en_rango(rango):
    """
    Cuenta cuántos primos hay en un rango dado.
    Diseñada para distribución con Pool (un argumento = un proceso).
    """
    inicio, fin = rango
    return sum(1 for n in range(inicio, fin) if tarea_cpu_bound(n))


# =============================================================================
# SECCIÓN 1: ThreadPoolExecutor — Básico
# =============================================================================

print("=" * 60)
print("1. ThreadPoolExecutor — Básico")
print("=" * 60)

# FORMA 1: Context manager (recomendada — garantiza cleanup automático)
with ThreadPoolExecutor(max_workers=4, thread_name_prefix="Worker") as executor:
    # submit() envía UNA tarea y retorna un Future inmediatamente
    futuro = executor.submit(tarea_io_bound, "url-1")

    # El Future representa la tarea en ejecución
    print(f"  Future creado: {futuro}")
    print(f"  ¿Terminado?: {futuro.done()}")  # Probablemente False todavía

    resultado = futuro.result()  # Bloquea hasta que termine
    print(f"  ¿Terminado?: {futuro.done()}")  # True ahora
    print(f"  Resultado: {resultado}")

# FORMA 2: executor.map() — como map() pero en paralelo
print("\n  Usando executor.map() para múltiples URLs:")
inicio = time.time()

with ThreadPoolExecutor(max_workers=5) as executor:
    resultados = list(executor.map(tarea_io_bound, range(10)))

print(f"  10 tareas I/O en {time.time()-inicio:.2f}s")
print(f"  Total bytes: {sum(r['bytes'] for r in resultados):,}")


# =============================================================================
# SECCIÓN 2: as_completed — Procesar resultados conforme van llegando
# =============================================================================

print("\n" + "=" * 60)
print("2. as_completed — Procesar en orden de finalización")
print("=" * 60)

# as_completed es mejor que map cuando:
# - Quieres procesar cada resultado tan pronto como llega
# - Las tareas tienen tiempos muy diferentes
# - Quieres mostrar progreso en tiempo real

print("  Lanzando 8 tareas, procesando en orden de llegada:")

with ThreadPoolExecutor(max_workers=4) as executor:
    # Guardar referencia a cada future para saber qué tarea es
    futuros = {
        executor.submit(tarea_io_bound, f"url-{i}"): f"url-{i}"
        for i in range(8)
    }

    completados = 0
    for futuro in as_completed(futuros):
        url = futuros[futuro]
        try:
            resultado = futuro.result()
            completados += 1
            print(f"  [{completados}/8] {url} → {resultado['bytes']} bytes "
                  f"({resultado['tiempo']:.2f}s)")
        except Exception as e:
            print(f"  ERROR en {url}: {e}")


# =============================================================================
# SECCIÓN 3: Manejo de errores en futures
# =============================================================================

print("\n" + "=" * 60)
print("3. Manejo de errores en futures")
print("=" * 60)


def tarea_que_puede_fallar(n):
    """Tarea que falla para ciertos valores — para demostrar manejo de errores."""
    if n % 3 == 0:
        raise ValueError(f"El número {n} es múltiplo de 3 — error simulado")
    time.sleep(0.1)
    return n * n


with ThreadPoolExecutor(max_workers=3) as executor:
    futuros = {executor.submit(tarea_que_puede_fallar, i): i for i in range(9)}

    for futuro in as_completed(futuros):
        n = futuros[futuro]
        try:
            resultado = futuro.result()
            print(f"  {n}² = {resultado}")
        except ValueError as e:
            print(f"  ERROR: {e}")


# =============================================================================
# SECCIÓN 4: ProcessPoolExecutor — Para tareas CPU-bound
# =============================================================================

print("\n" + "=" * 60)
print("4. ProcessPoolExecutor — Tareas CPU-bound en paralelo")
print("=" * 60)

if __name__ == "__main__":
    # Dividir el trabajo en chunks para distribuir entre procesos
    TOTAL = 200_000
    NUM_PROCESOS = multiprocessing.cpu_count()
    tamano_chunk = TOTAL // NUM_PROCESOS

    rangos = [
        (i * tamano_chunk, (i + 1) * tamano_chunk)
        for i in range(NUM_PROCESOS)
    ]

    print(f"  Contando primos hasta {TOTAL:,} con {NUM_PROCESOS} procesos:")
    print(f"  Chunks: {rangos}")

    # Secuencial para comparar
    inicio = time.time()
    total_sec = contar_primos_en_rango((2, TOTAL))
    tiempo_sec = time.time() - inicio
    print(f"\n  Secuencial: {total_sec:,} primos en {tiempo_sec:.3f}s")

    # ProcessPoolExecutor
    inicio = time.time()
    with ProcessPoolExecutor(max_workers=NUM_PROCESOS) as executor:
        resultados_chunks = list(executor.map(contar_primos_en_rango, rangos))
    total_paralelo = sum(resultados_chunks)
    tiempo_paralelo = time.time() - inicio

    print(f"  Paralelo:   {total_paralelo:,} primos en {tiempo_paralelo:.3f}s")
    print(f"  Speedup: {tiempo_sec/tiempo_paralelo:.1f}x")
    print(f"  Resultados iguales: {total_sec == total_paralelo}")


# =============================================================================
# SECCIÓN 5: wait() — Control avanzado de múltiples futures
# =============================================================================

print("\n" + "=" * 60)
print("5. wait() — Esperar por condiciones específicas")
print("=" * 60)


async_tasks = list(range(6))

with ThreadPoolExecutor(max_workers=3) as executor:
    futuros = [executor.submit(tarea_io_bound, i) for i in async_tasks]

    # Esperar hasta que AL MENOS UNO termine
    completados, pendientes = wait(futuros, return_when=FIRST_COMPLETED)
    print(f"  Primer completado: {len(completados)} listo, {len(pendientes)} pendientes")

    # Ahora esperar a que TODOS terminen
    completados, _ = wait(futuros, return_when=ALL_COMPLETED)
    print(f"  Todos completados: {len(completados)} listos")


# =============================================================================
# SECCIÓN 6: BENCHMARK COMPARATIVO COMPLETO
# =============================================================================

print("\n" + "=" * 60)
print("6. Benchmark comparativo: Secuencial vs Thread vs Process")
print("=" * 60)

if __name__ == "__main__":
    # ---- BENCHMARK I/O-BOUND ----
    print("\n  --- I/O-bound (simula 20 peticiones de red) ---")
    N_IO = 20

    # Secuencial
    inicio = time.time()
    for i in range(N_IO):
        tarea_io_bound(i)
    t_sec_io = time.time() - inicio

    # ThreadPoolExecutor
    inicio = time.time()
    with ThreadPoolExecutor(max_workers=N_IO) as ex:
        list(ex.map(tarea_io_bound, range(N_IO)))
    t_thread_io = time.time() - inicio

    # ProcessPoolExecutor (peor para I/O por overhead de procesos)
    inicio = time.time()
    with ProcessPoolExecutor(max_workers=4) as ex:
        list(ex.map(tarea_io_bound, range(N_IO)))
    t_proc_io = time.time() - inicio

    print(f"  Secuencial:    {t_sec_io:.2f}s")
    print(f"  ThreadPool:    {t_thread_io:.2f}s  ({t_sec_io/t_thread_io:.1f}x speedup) ← GANADOR para I/O")
    print(f"  ProcessPool:   {t_proc_io:.2f}s  ({t_sec_io/t_proc_io:.1f}x speedup)")

    # ---- BENCHMARK CPU-BOUND ----
    print("\n  --- CPU-bound (verificar primalidad de 200 números) ---")
    numeros = [random.randint(10**6, 10**7) for _ in range(200)]

    # Secuencial
    inicio = time.time()
    list(map(tarea_cpu_bound, numeros))
    t_sec_cpu = time.time() - inicio

    # ThreadPoolExecutor (GIL limita el beneficio)
    inicio = time.time()
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(tarea_cpu_bound, numeros))
    t_thread_cpu = time.time() - inicio

    # ProcessPoolExecutor (verdadero paralelismo)
    inicio = time.time()
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as ex:
        list(ex.map(tarea_cpu_bound, numeros))
    t_proc_cpu = time.time() - inicio

    print(f"  Secuencial:    {t_sec_cpu:.2f}s")
    print(f"  ThreadPool:    {t_thread_cpu:.2f}s  ({t_sec_cpu/t_thread_cpu:.1f}x speedup) ← GIL limita")
    print(f"  ProcessPool:   {t_proc_cpu:.2f}s  ({t_sec_cpu/t_proc_cpu:.1f}x speedup) ← GANADOR para CPU")

    print("\n  RESUMEN:")
    print("  ┌───────────────────────────────────────────────────┐")
    print("  │  I/O-bound  → ThreadPoolExecutor (o asyncio)      │")
    print("  │  CPU-bound  → ProcessPoolExecutor                 │")
    print("  └───────────────────────────────────────────────────┘")

print("\nFIN: 05_concurrent_futures.py completado")
