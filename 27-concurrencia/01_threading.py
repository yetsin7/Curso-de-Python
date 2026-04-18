# =============================================================================
# CAPÍTULO 27 — Concurrencia y Asincronismo
# Archivo 1: threading — Hilos de ejecución
# =============================================================================
# Temas: Thread, start/join, daemon threads, Lock (race condition + solución),
# Event, Queue para productor-consumidor. Descargador paralelo simulado.
# =============================================================================

import threading
import time
import random
import queue


# =============================================================================
# SECCIÓN 1: Thread básico — start() y join()
# =============================================================================

print("=" * 60)
print("1. threading.Thread básico")
print("=" * 60)


def tarea_basica(nombre, duracion):
    """Simula una tarea que tarda cierto tiempo."""
    print(f"  [{nombre}] Iniciando (durará {duracion}s)")
    time.sleep(duracion)
    print(f"  [{nombre}] Completado")


# Crear y lanzar threads
print("Ejecutando 3 tareas en paralelo:")
inicio = time.time()

threads = []
for i in range(3):
    t = threading.Thread(
        target=tarea_basica,
        args=(f"Tarea-{i+1}", random.uniform(0.5, 1.5)),
        name=f"Worker-{i+1}"   # Nombre opcional para debugging
    )
    threads.append(t)
    t.start()  # Lanza el thread — NO bloquea el hilo principal

# join() bloquea hasta que cada thread termine
for t in threads:
    t.join()

print(f"Todas las tareas completadas en {time.time()-inicio:.2f}s")


# =============================================================================
# SECCIÓN 2: Daemon threads — Threads que mueren con el proceso principal
# =============================================================================

print("\n" + "=" * 60)
print("2. Daemon threads")
print("=" * 60)


def monitor_background():
    """
    Simula un monitor de sistema en background.
    Al ser daemon=True, se detendrá automáticamente cuando
    el programa principal termine, sin necesidad de join().
    """
    contador = 0
    while True:
        contador += 1
        print(f"  [Monitor] Pulso #{contador}")
        time.sleep(0.4)


# daemon=True: el thread NO impide que el programa termine
monitor = threading.Thread(target=monitor_background, daemon=True)
monitor.start()

# El programa principal continúa y eventualmente termina
time.sleep(1.2)
print("Programa principal terminando — el monitor se detiene solo")
# No necesitamos monitor.join() — al ser daemon, muere con nosotros


# =============================================================================
# SECCIÓN 3: Race Condition — El problema y la solución con Lock
# =============================================================================

print("\n" + "=" * 60)
print("3. Race Condition y threading.Lock")
print("=" * 60)

# PROBLEMA: Contador sin protección (race condition)
contador_inseguro = 0


def incrementar_inseguro():
    """
    Incrementa el contador de forma insegura.
    Varios threads pueden leer-modificar-escribir el mismo valor
    simultáneamente, causando pérdida de incrementos.
    """
    global contador_inseguro
    for _ in range(10000):
        # Esta operación NO es atómica: read → add 1 → write
        # Otro thread puede interferir entre el read y el write
        contador_inseguro += 1


threads_malos = [threading.Thread(target=incrementar_inseguro) for _ in range(5)]
for t in threads_malos:
    t.start()
for t in threads_malos:
    t.join()

esperado = 5 * 10000
print(f"Sin Lock — Esperado: {esperado}, Obtenido: {contador_inseguro}")
print(f"  Diferencia: {esperado - contador_inseguro} (incrementos perdidos por race condition)")

# SOLUCIÓN: Lock garantiza acceso exclusivo a la sección crítica
contador_seguro = 0
lock = threading.Lock()


def incrementar_seguro():
    """
    Incrementa el contador de forma segura con un Lock.
    Solo un thread puede estar en la sección protegida a la vez.
    """
    global contador_seguro
    for _ in range(10000):
        with lock:  # acquire() + release() automático — siempre usar with
            contador_seguro += 1


threads_buenos = [threading.Thread(target=incrementar_seguro) for _ in range(5)]
for t in threads_buenos:
    t.start()
for t in threads_buenos:
    t.join()

print(f"Con Lock  — Esperado: {esperado}, Obtenido: {contador_seguro}")
print(f"  Diferencia: {esperado - contador_seguro} (perfecto)")


# =============================================================================
# SECCIÓN 4: threading.Event — Señalizar entre threads
# =============================================================================

print("\n" + "=" * 60)
print("4. threading.Event — Coordinación entre threads")
print("=" * 60)

evento_listo = threading.Event()
evento_parar = threading.Event()


def trabajador_con_evento(nombre):
    """
    Trabajador que espera una señal de inicio antes de trabajar.
    También respeta una señal de parada.
    """
    print(f"  [{nombre}] Esperando señal de inicio...")
    evento_listo.wait()  # Bloquea hasta que se llame evento.set()
    print(f"  [{nombre}] Señal recibida — trabajando")
    while not evento_parar.is_set():
        time.sleep(0.2)
    print(f"  [{nombre}] Señal de parada recibida — terminando")


# Lanzar trabajadores que esperan
workers = [threading.Thread(target=trabajador_con_evento, args=(f"W{i}",))
           for i in range(3)]
for w in workers:
    w.start()

time.sleep(0.5)
print("  [Principal] Enviando señal de inicio...")
evento_listo.set()   # Despierta a TODOS los threads que hacen .wait()

time.sleep(0.7)
print("  [Principal] Enviando señal de parada...")
evento_parar.set()   # Todos los while not evento_parar.is_set() terminan

for w in workers:
    w.join()
print("  Todos los workers terminaron")


# =============================================================================
# SECCIÓN 5: Queue — Patrón Productor-Consumidor thread-safe
# =============================================================================

print("\n" + "=" * 60)
print("5. threading.Queue — Productor-Consumidor")
print("=" * 60)

# queue.Queue es thread-safe por diseño
cola_trabajos = queue.Queue(maxsize=10)
resultados = []
lock_resultados = threading.Lock()


def productor(cantidad):
    """
    Produce 'cantidad' trabajos y los pone en la cola.
    Cuando termina, pone un sentinel None para indicar fin.
    """
    for i in range(cantidad):
        trabajo = {"id": i, "dato": random.randint(1, 100)}
        cola_trabajos.put(trabajo)  # Bloquea si la cola está llena (maxsize)
        print(f"  [Productor] Producido trabajo #{i}")
        time.sleep(0.05)

    # Sentinel: señal de que no hay más trabajos
    cola_trabajos.put(None)
    print("  [Productor] Fin de producción")


def consumidor(nombre):
    """
    Consume trabajos de la cola hasta recibir el sentinel None.
    Procesa cada trabajo y guarda el resultado.
    """
    while True:
        trabajo = cola_trabajos.get()  # Bloquea si la cola está vacía
        if trabajo is None:
            # Reencolar el sentinel para que otros consumidores también terminen
            cola_trabajos.put(None)
            print(f"  [{nombre}] Recibió sentinel — terminando")
            cola_trabajos.task_done()
            break

        # Simular procesamiento
        resultado = trabajo["dato"] ** 2
        with lock_resultados:
            resultados.append(resultado)

        print(f"  [{nombre}] Procesado trabajo #{trabajo['id']}: {trabajo['dato']}² = {resultado}")
        cola_trabajos.task_done()
        time.sleep(random.uniform(0.05, 0.15))


# Lanzar 1 productor y 2 consumidores
t_prod = threading.Thread(target=productor, args=(6,))
t_cons1 = threading.Thread(target=consumidor, args=("Consumidor-A",))
t_cons2 = threading.Thread(target=consumidor, args=("Consumidor-B",))

t_prod.start()
t_cons1.start()
t_cons2.start()

t_prod.join()
t_cons1.join()
t_cons2.join()

print(f"\n  Resultados procesados ({len(resultados)} total): {sorted(resultados)}")


# =============================================================================
# SECCIÓN 6: Descargador paralelo simulado (caso de uso real I/O-bound)
# =============================================================================

print("\n" + "=" * 60)
print("6. Descargador paralelo simulado")
print("=" * 60)

URLS_SIMULADAS = [
    ("https://api.ejemplo.com/datos/1", 0.8),    # (url, latencia simulada)
    ("https://api.ejemplo.com/datos/2", 1.2),
    ("https://api.ejemplo.com/datos/3", 0.5),
    ("https://cdn.ejemplo.com/imagen1.png", 1.0),
    ("https://cdn.ejemplo.com/imagen2.png", 0.7),
]

descargados = []
lock_desc = threading.Lock()


def descargar_url(url, latencia):
    """
    Simula la descarga de una URL con una latencia de red dada.
    En producción usarías requests.get(url) aquí.
    """
    print(f"  Descargando: {url}")
    time.sleep(latencia)  # Simula latencia de red
    contenido = f"<html>Contenido de {url.split('/')[-1]}</html>"
    with lock_desc:
        descargados.append({"url": url, "contenido": contenido, "tamano": len(contenido)})
    print(f"  Completado:  {url} ({latencia:.1f}s)")


# Comparar secuencial vs paralelo
print("\n  --- MODO SECUENCIAL ---")
inicio = time.time()
for url, latencia in URLS_SIMULADAS:
    descargar_url(url, latencia)
tiempo_secuencial = time.time() - inicio
print(f"  Tiempo secuencial: {tiempo_secuencial:.2f}s\n")

descargados.clear()

print("  --- MODO PARALELO (threading) ---")
inicio = time.time()
threads_descarga = [
    threading.Thread(target=descargar_url, args=(url, lat))
    for url, lat in URLS_SIMULADAS
]
for t in threads_descarga:
    t.start()
for t in threads_descarga:
    t.join()

tiempo_paralelo = time.time() - inicio
print(f"  Tiempo paralelo: {tiempo_paralelo:.2f}s")
print(f"  Speedup: {tiempo_secuencial / tiempo_paralelo:.1f}x más rápido")
print(f"  Archivos descargados: {len(descargados)}")

print("\nFIN: 01_threading.py completado")
