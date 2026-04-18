# Capítulo 27 — Concurrencia y Asincronismo

## El problema: hacer múltiples cosas "al mismo tiempo"

Por defecto, Python ejecuta código de forma **secuencial**: una instrucción, luego otra, luego otra. Si necesitas descargar 100 archivos, los descarga uno por uno. Si necesitas procesar 1,000,000 de números, los procesa uno a uno.

La concurrencia y el paralelismo son las respuestas a este problema, pero en Python tienen particularidades únicas que debes entender antes de usarlos.

---

## El GIL — Global Interpreter Lock

El GIL es quizás la característica más malentendida de Python. Es un **mutex** (cerrojo) dentro del intérprete CPython que solo permite que **un thread ejecute código Python a la vez**.

### ¿Por qué existe?

El GIL simplifica la gestión de memoria de CPython. El contador de referencias (cómo Python sabe cuándo liberar memoria) no es thread-safe sin el GIL. Fue una decisión de diseño de los años 90 que aún persiste.

### ¿Qué implica?

```
Thread 1: [===ejecuta===]    [====ejecuta====]
Thread 2:                [===ejecuta===]
           tiempo →
```

Aunque tengas 8 núcleos de CPU, Python solo usa uno para ejecutar código Python. Los threads se turnan, no se ejecutan verdaderamente en paralelo.

### ¿Cuándo el GIL NO es problema?

Cuando el trabajo es **I/O-bound** (esperando disco, red, base de datos). Mientras un thread espera que lleguen bytes de internet, **libera el GIL** y permite que otro thread ejecute.

### ¿Cuándo el GIL SÍ es problema?

Cuando el trabajo es **CPU-bound** (cálculos matemáticos, procesamiento de imágenes, ML). El thread nunca está esperando — siempre está calculando — entonces el GIL nunca se libera de forma útil.

---

## CPU-bound vs I/O-bound — La diferencia clave

Esta distinción es fundamental para elegir la herramienta correcta:

### I/O-bound (limitado por entrada/salida)
El programa pasa la mayor parte del tiempo **esperando**:
- Descargando archivos de internet
- Consultando una base de datos
- Leyendo/escribiendo archivos en disco
- Llamando a APIs externas
- Esperando respuestas de usuario

**Ejemplo:** Descargar 100 páginas web. Cada descarga tarda 0.5s esperando la red.
- Secuencial: 100 × 0.5s = **50 segundos**
- Concurrente (threads/async): ≈ 0.5s (todas esperan simultáneamente)

### CPU-bound (limitado por procesador)
El programa pasa la mayor parte del tiempo **calculando**:
- Compresión/descompresión de datos
- Criptografía
- Renderizado de imágenes
- Machine learning
- Simulaciones numéricas

**Ejemplo:** Calcular el número primo siguiente para 100 números grandes.
- Secuencial: 100 × 0.1s = **10 segundos**
- Multiprocessing: 10s / núcleos_CPU ≈ **1.25s** (con 8 núcleos)
- Threading: ≈ **10 segundos** (el GIL anula el beneficio)

---

## Threading vs Multiprocessing vs Asyncio

### Diagrama mental de decisión

```
¿Cuál es el cuello de botella?
│
├── I/O-bound (esperas de red, disco, BD)
│   │
│   ├── ¿Muchas conexiones simultáneas? (100+)
│   │   └── → asyncio (más eficiente, menos overhead)
│   │
│   └── ¿Pocas conexiones o código existente blocking?
│       └── → threading (más simple, compatible con librerías síncronas)
│
└── CPU-bound (cálculos intensivos)
    └── → multiprocessing (procesos separados, evita el GIL)
```

### Comparativa

| Característica | threading | multiprocessing | asyncio |
|---|---|---|---|
| **Paralelismo real** | No (GIL) | Sí | No (cooperativo) |
| **Ideal para** | I/O-bound | CPU-bound | I/O-bound |
| **Overhead** | Bajo | Alto | Muy bajo |
| **Complejidad** | Media | Media | Alta |
| **Memoria compartida** | Sí (con cuidado) | No (por defecto) | Sí |
| **Número recomendado** | Docenas | = núcleos CPU | Miles |

---

## Sincrónico → Threads → Procesos → Async

```
SINCRÓNICO (baseline)
┌─────────────────────────────────────┐
│ tarea1 → tarea2 → tarea3 → tarea4  │
│ tiempo total = suma de todos        │
└─────────────────────────────────────┘

THREADING (concurrencia I/O-bound)
┌─────────────────────────────────────┐
│ tarea1 ──→                          │
│ tarea2   ──→                        │ GIL: solo
│ tarea3     ──→                      │ uno ejecuta
│ tarea4       ──→                    │ a la vez
│ tiempo total ≈ max(tareas)          │
└─────────────────────────────────────┘

MULTIPROCESSING (paralelismo CPU-bound)
┌─────────────────────────────────────┐
│ Proceso 1: tarea1 + tarea3          │
│ Proceso 2: tarea2 + tarea4          │ Verdadero
│ Proceso 3: ...                      │ paralelismo
│ tiempo total ≈ total / núcleos      │
└─────────────────────────────────────┘

ASYNCIO (concurrencia cooperativa)
┌─────────────────────────────────────┐
│ await tarea1 → switch → await tarea2│
│ Un solo thread, pero coopera        │
│ Ideal: miles de conexiones I/O      │
│ tiempo total ≈ max(tareas)          │
└─────────────────────────────────────┘
```

---

## Archivos de este capítulo

1. **`01_threading.py`** — `threading.Thread`, Lock, Event, Queue. Descargador paralelo simulado
2. **`02_multiprocessing.py`** — `multiprocessing.Process`, Pool, Queue, Pipe. Benchmark CPU-bound
3. **`03_asyncio_basico.py`** — `async/await`, event loop, coroutines, `asyncio.gather`
4. **`04_asyncio_avanzado.py`** — Queue, Semaphore, timeouts, aiofiles, pipeline asíncrono
5. **`05_concurrent_futures.py`** — `ThreadPoolExecutor`, `ProcessPoolExecutor`, comparativa

---

## Recursos adicionales

- [threading — documentación oficial](https://docs.python.org/3/library/threading.html)
- [multiprocessing — documentación oficial](https://docs.python.org/3/library/multiprocessing.html)
- [asyncio — documentación oficial](https://docs.python.org/3/library/asyncio.html)
- [concurrent.futures — documentación oficial](https://docs.python.org/3/library/concurrent.futures.html)
- [Real Python: Speed Up Your Python Program With Concurrency](https://realpython.com/python-concurrency/)
