# =============================================================================
# CAPÍTULO 27 — Concurrencia y Asincronismo
# Archivo 2: multiprocessing — Procesos paralelos (CPU-bound)
# =============================================================================
# Temas: Process, Pool (map/starmap), Queue, Pipe, Manager.
# Demostración de speedup real en tarea CPU-bound vs threading.
# ProcessPoolExecutor de concurrent.futures.
# =============================================================================

import multiprocessing
import time
import os
import random
from concurrent.futures import ProcessPoolExecutor


# =============================================================================
# FUNCIÓN: Tarea CPU-bound para benchmarks
# =============================================================================

def calcular_primos_hasta(n):
    """
    Calcula todos los números primos hasta n usando la Criba de Eratóstenes.
    Esta es una tarea CPU-bound pura — solo calcula, no espera I/O.

    Args:
        n: Límite superior para buscar primos
    Returns:
        Cantidad de primos encontrados
    """
    if n < 2:
        return 0
    criba = [True] * (n + 1)
    criba[0] = criba[1] = False
    for i in range(2, int(n**0.5) + 1):
        if criba[i]:
            for j in range(i*i, n+1, i):
                criba[j] = False
    return sum(criba)


def tarea_cpu_intensiva(limite):
    """
    Envuelve el cálculo de primos para uso en Pool.
    Retorna (pid, límite, resultado) para poder verificar qué proceso lo ejecutó.
    """
    pid = os.getpid()
    resultado = calcular_primos_hasta(limite)
    return pid, limite, resultado


# =============================================================================
# SECCIÓN 1: Process básico — el equivalente a Thread pero para procesos
# =============================================================================

print("=" * 60)
print("1. multiprocessing.Process básico")
print("=" * 60)


def tarea_proceso(nombre, limite):
    """
    Función que corre en un proceso separado.
    Cada proceso tiene su propio espacio de memoria y PID.
    """
    pid = os.getpid()
    resultado = calcular_primos_hasta(limite)
    print(f"  [{nombre}] PID={pid}, primos hasta {limite}: {resultado}")


if __name__ == "__main__":
    # IMPORTANTE: En Windows, el código que crea procesos DEBE estar dentro de
    # if __name__ == "__main__" para evitar recursión infinita al importar el módulo
    print(f"Proceso principal PID: {os.getpid()}")

    procesos = [
        multiprocessing.Process(target=tarea_proceso, args=(f"P{i}", 100_000 * i))
        for i in range(1, 4)
    ]

    for p in procesos:
        p.start()

    for p in procesos:
        p.join()

    print("Todos los procesos completados")


# =============================================================================
# SECCIÓN 2: Pool — Administrar un pool de procesos trabajadores
# =============================================================================

print("\n" + "=" * 60)
print("2. multiprocessing.Pool — map y starmap")
print("=" * 60)

if __name__ == "__main__":
    limites = [200_000, 300_000, 250_000, 400_000, 150_000, 350_000]
    num_cpus = multiprocessing.cpu_count()
    print(f"CPUs disponibles: {num_cpus}")

    # Pool.map — equivalente a map() pero en múltiples procesos
    print("\nUsando Pool.map:")
    with multiprocessing.Pool(processes=num_cpus) as pool:
        inicio = time.time()
        resultados = pool.map(calcular_primos_hasta, limites)
        tiempo = time.time() - inicio

    for limite, res in zip(limites, resultados):
        print(f"  Primos hasta {limite:,}: {res:,}")
    print(f"  Tiempo con Pool.map: {tiempo:.3f}s")

    # Pool.starmap — como map pero cuando la función recibe múltiples argumentos
    print("\nUsando Pool.starmap (múltiples argumentos):")
    trabajos = [(f"Job-{i}", 100_000 * i) for i in range(1, 5)]

    with multiprocessing.Pool(processes=num_cpus) as pool:
        resultados_star = pool.starmap(tarea_cpu_intensiva, trabajos)

    for pid, limite, res in resultados_star:
        print(f"  PID={pid}, límite={limite:,}, primos={res:,}")


# =============================================================================
# SECCIÓN 3: Benchmark CPU-bound — Threading vs Multiprocessing
# =============================================================================

print("\n" + "=" * 60)
print("3. Benchmark: Threading vs Multiprocessing (CPU-bound)")
print("=" * 60)

if __name__ == "__main__":
    import threading

    LIMITES_BENCHMARK = [500_000] * multiprocessing.cpu_count()
    print(f"Tarea: calcular primos hasta 500,000 × {len(LIMITES_BENCHMARK)} veces")

    # --- SECUENCIAL ---
    inicio = time.time()
    for lim in LIMITES_BENCHMARK:
        calcular_primos_hasta(lim)
    tiempo_sec = time.time() - inicio
    print(f"\n  Secuencial:      {tiempo_sec:.3f}s")

    # --- THREADING (no mejora CPU-bound por el GIL) ---
    inicio = time.time()
    threads = [threading.Thread(target=calcular_primos_hasta, args=(lim,))
               for lim in LIMITES_BENCHMARK]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    tiempo_thread = time.time() - inicio
    print(f"  Threading:       {tiempo_thread:.3f}s (GIL limita el beneficio)")

    # --- MULTIPROCESSING (verdadero paralelismo) ---
    inicio = time.time()
    with multiprocessing.Pool(processes=len(LIMITES_BENCHMARK)) as pool:
        pool.map(calcular_primos_hasta, LIMITES_BENCHMARK)
    tiempo_mp = time.time() - inicio
    print(f"  Multiprocessing: {tiempo_mp:.3f}s")

    print(f"\n  Speedup vs secuencial: {tiempo_sec/tiempo_mp:.1f}x")
    print(f"  (Esperado ≈ {multiprocessing.cpu_count()}x con {multiprocessing.cpu_count()} CPUs)")


# =============================================================================
# SECCIÓN 4: Queue entre procesos — comunicación segura
# =============================================================================

print("\n" + "=" * 60)
print("4. multiprocessing.Queue — comunicación entre procesos")
print("=" * 60)


def productor_procesos(cola, cantidad):
    """
    Produce números en una Queue compartida entre procesos.
    Distinto a threading.Queue — esta cruza límites de proceso.
    """
    for i in range(cantidad):
        cola.put(i * i)
        time.sleep(0.01)
    cola.put(None)  # Sentinel
    print(f"  [Productor PID={os.getpid()}] Producción terminada")


def consumidor_procesos(cola, nombre):
    """
    Consume valores de la Queue hasta recibir el sentinel None.
    """
    total = 0
    while True:
        valor = cola.get()
        if valor is None:
            cola.put(None)  # Reencolar para otros consumidores
            break
        total += valor
    print(f"  [{nombre} PID={os.getpid()}] Suma total consumida: {total}")


if __name__ == "__main__":
    cola_mp = multiprocessing.Queue()

    p_prod = multiprocessing.Process(target=productor_procesos, args=(cola_mp, 8))
    p_cons = multiprocessing.Process(target=consumidor_procesos, args=(cola_mp, "Consumidor"))

    p_prod.start()
    p_cons.start()
    p_prod.join()
    p_cons.join()


# =============================================================================
# SECCIÓN 5: Pipe — Canal de comunicación bidireccional entre procesos
# =============================================================================

print("\n" + "=" * 60)
print("5. multiprocessing.Pipe — Comunicación bidireccional")
print("=" * 60)


def proceso_hijo(conn):
    """
    Proceso hijo que recibe un mensaje y envía una respuesta.
    conn es uno de los dos extremos del Pipe.
    """
    mensaje = conn.recv()
    print(f"  [Hijo PID={os.getpid()}] Recibido: '{mensaje}'")
    respuesta = f"Procesé '{mensaje}' correctamente"
    conn.send(respuesta)
    conn.close()


if __name__ == "__main__":
    # Pipe() retorna dos Connection objects: (extremo_padre, extremo_hijo)
    conn_padre, conn_hijo = multiprocessing.Pipe()

    p = multiprocessing.Process(target=proceso_hijo, args=(conn_hijo,))
    p.start()

    conn_padre.send("Hola desde el proceso principal")
    respuesta = conn_padre.recv()
    print(f"  [Principal PID={os.getpid()}] Respuesta: '{respuesta}'")

    p.join()
    conn_padre.close()


# =============================================================================
# SECCIÓN 6: Manager — Objetos compartidos entre procesos
# =============================================================================

print("\n" + "=" * 60)
print("6. multiprocessing.Manager — Estado compartido entre procesos")
print("=" * 60)


def trabajador_manager(diccionario_compartido, clave, valor):
    """
    Escribe en un diccionario compartido administrado por Manager.
    A diferencia de un dict normal, este es accesible desde múltiples procesos.
    """
    diccionario_compartido[clave] = valor
    print(f"  [PID={os.getpid()}] Escribí: {clave} = {valor}")


if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        dict_compartido = manager.dict()  # Diccionario accesible entre procesos
        lista_compartida = manager.list()  # Lista accesible entre procesos

        trabajos = [
            multiprocessing.Process(
                target=trabajador_manager,
                args=(dict_compartido, f"clave_{i}", i * 10)
            )
            for i in range(4)
        ]

        for p in trabajos:
            p.start()
        for p in trabajos:
            p.join()

        print(f"  Diccionario final: {dict(dict_compartido)}")


# =============================================================================
# SECCIÓN 7: ProcessPoolExecutor (concurrent.futures) — API moderna
# =============================================================================

print("\n" + "=" * 60)
print("7. ProcessPoolExecutor — API moderna y Pythónica")
print("=" * 60)

if __name__ == "__main__":
    limites_test = [100_000, 200_000, 150_000, 300_000]

    # submit + as_completed — procesa resultados a medida que terminan
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futuros = {executor.submit(calcular_primos_hasta, lim): lim
                   for lim in limites_test}

        from concurrent.futures import as_completed
        for futuro in as_completed(futuros):
            limite = futuros[futuro]
            resultado = futuro.result()
            print(f"  Primos hasta {limite:,}: {resultado:,}")

    print("\nFIN: 02_multiprocessing.py completado")
