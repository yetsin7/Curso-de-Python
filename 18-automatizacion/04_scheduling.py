# =============================================================================
# 04_scheduling.py — Tareas periódicas y programadas con Python
# =============================================================================
# El scheduling permite ejecutar código automáticamente en horarios fijos
# o en intervalos regulares: backups diarios, reportes semanales,
# limpieza de archivos, notificaciones, etc.
#
# Instalación:
#   pip install schedule
#
# Librerías cubiertas:
#   schedule  — simple, para scripts y tareas básicas (pip install schedule)
#   threading — incluido con Python, para ejecutar tareas en segundo plano
#   APScheduler — mencionado conceptualmente, para aplicaciones web/complejas
#
# Contenido:
#   - Tareas con schedule: cada N segundos, minutos, horas, días
#   - Background scheduling con threading
#   - Cancelar y pausar tareas
#   - Manejo de errores en tareas periódicas
#   - Ejemplo práctico: limpieza de carpeta, reporte diario
# =============================================================================

import time
import threading
import logging
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False


# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================

# Configurar logging para ver qué hacen las tareas programadas
# El scheduling en producción siempre debe tener logging para auditoría
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


# =============================================================================
# VERIFICACIÓN DE INSTALACIÓN
# =============================================================================

def check_schedule():
    """
    Verifica que schedule esté instalado.

    Retorna:
        bool: True si está disponible
    """
    if not SCHEDULE_AVAILABLE:
        print("La librería 'schedule' no está instalada.")
        print("Instala con: pip install schedule")
        return False
    return True


# =============================================================================
# TAREAS DE EJEMPLO
# =============================================================================

class TaskCounter:
    """
    Contador compartido entre hilos para llevar seguimiento de ejecuciones.
    Usa threading.Lock() para evitar condiciones de carrera al acceder
    el contador desde múltiples hilos simultáneamente.
    """

    def __init__(self):
        """Inicializa el contador y el lock de sincronización."""
        self._count = 0
        self._lock  = threading.Lock()

    def increment(self):
        """Incrementa el contador de forma thread-safe."""
        with self._lock:
            self._count += 1
            return self._count

    @property
    def value(self):
        """Devuelve el valor actual del contador."""
        with self._lock:
            return self._count


# Instancia global del contador para los ejemplos
task_counter = TaskCounter()


def task_send_heartbeat():
    """
    Tarea de heartbeat: confirma que el sistema está funcionando.

    En sistemas de monitoreo, un heartbeat es una señal periódica que indica
    'sigo vivo y funcionando'. Si el heartbeat deja de llegar, algo falló.
    """
    count = task_counter.increment()
    timestamp = datetime.now().strftime("%H:%M:%S")
    logger.info(f"[Heartbeat #{count}] Sistema activo — {timestamp}")


def task_clean_temp_folder(folder_path, max_age_minutes=60):
    """
    Tarea de limpieza: elimina archivos viejos de una carpeta.

    Parámetros:
        folder_path (Path): carpeta a limpiar
        max_age_minutes (int): eliminar archivos más viejos que esto

    Esta tarea simula lo que haría un sistema real:
    limpiar logs viejos, archivos temporales, caché expirada, etc.
    """
    if not folder_path.exists():
        logger.warning(f"Carpeta no encontrada: {folder_path}")
        return

    now = datetime.now()
    deleted = 0
    errors  = 0

    for file_path in folder_path.iterdir():
        if not file_path.is_file():
            continue

        # Calcular antigüedad del archivo
        mtime    = datetime.fromtimestamp(file_path.stat().st_mtime)
        age_mins = (now - mtime).total_seconds() / 60

        if age_mins > max_age_minutes:
            try:
                file_path.unlink()
                deleted += 1
            except OSError as e:
                logger.error(f"No se pudo eliminar {file_path.name}: {e}")
                errors += 1

    logger.info(f"[Limpieza] Eliminados: {deleted} archivos | Errores: {errors}")


def task_generate_report():
    """
    Tarea de reporte: genera un archivo de reporte con estadísticas.

    En producción, esta tarea podría:
    - Consultar una base de datos
    - Procesar logs del día
    - Calcular métricas de negocio
    - Enviar el reporte por email
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"reporte_{timestamp}.txt"

    # Simular generación de reporte
    report_content = (
        f"=== Reporte Automático ===\n"
        f"Generado: {datetime.now().isoformat()}\n"
        f"Ejecuciones del heartbeat: {task_counter.value}\n"
        f"Estado del sistema: OK\n"
        f"Uso de memoria: simulado\n"
    )

    logger.info(f"[Reporte] Generado: {report_name} ({len(report_content)} bytes)")
    return report_content


def task_safe_wrapper(task_func, *args, **kwargs):
    """
    Envuelve una tarea con manejo de errores para que un fallo no detenga el scheduler.

    Si una tarea falla y no se maneja el error, schedule puede dejar de ejecutar
    esa tarea (dependiendo de la versión) o crashear el proceso.
    Esta función envuelve cualquier tarea para atrapar todos los errores.

    Parámetros:
        task_func: función a ejecutar
        *args, **kwargs: argumentos para la función
    """
    try:
        task_func(*args, **kwargs)
    except Exception as error:
        logger.error(
            f"Error en tarea {task_func.__name__}: {type(error).__name__}: {error}",
            exc_info=True  # incluye el traceback completo en el log
        )


# =============================================================================
# SCHEDULING BÁSICO
# =============================================================================

def demo_schedule_sintaxis():
    """
    Demuestra la sintaxis de schedule sin ejecutar ninguna tarea larga.

    Muestra todos los tipos de planificación disponibles.
    """
    print("\n--- Sintaxis de schedule ---")

    print("""
  Ejemplos de planificación con schedule:

  # Cada 10 segundos
  schedule.every(10).seconds.do(mi_tarea)

  # Cada 5 minutos
  schedule.every(5).minutes.do(mi_tarea)

  # Cada hora
  schedule.every().hour.do(mi_tarea)

  # Todos los días a las 8:00 AM
  schedule.every().day.at("08:00").do(mi_tarea)

  # Todos los lunes a las 9:30 AM
  schedule.every().monday.at("09:30").do(mi_tarea)

  # Con argumentos
  schedule.every(30).minutes.do(limpiar_carpeta, carpeta="/tmp", max_age=60)

  # Tarea que se ejecuta solo una vez (se cancela sola)
  def tarea_unica():
      print("Solo una vez")
      return schedule.CancelJob   # valor especial para auto-cancelar

  schedule.every(5).seconds.do(tarea_unica)

  # Ver tareas programadas
  print(schedule.jobs)

  # Cancelar una tarea específica
  job = schedule.every().hour.do(mi_tarea)
  schedule.cancel_job(job)

  # Cancelar todas las tareas
  schedule.clear()

  # Bucle principal (bloquea el hilo actual)
  while True:
      schedule.run_pending()
      time.sleep(1)
    """)


# =============================================================================
# BACKGROUND SCHEDULING CON THREADING
# =============================================================================

class BackgroundScheduler:
    """
    Ejecuta el scheduler de schedule en un hilo de fondo.

    Permite que el programa principal continúe ejecutándose mientras
    las tareas corren automáticamente en segundo plano.

    Ejemplo de uso:
        scheduler = BackgroundScheduler()
        scheduler.start()
        # ... código principal ...
        scheduler.stop()
    """

    def __init__(self, interval_seconds=1):
        """
        Inicializa el scheduler en background.

        Parámetros:
            interval_seconds (float): con qué frecuencia revisar las tareas pendientes
        """
        self._interval = interval_seconds
        self._thread   = None
        self._running  = False

    def _run_loop(self):
        """
        Bucle interno que ejecuta las tareas pendientes de schedule.
        Corre en un hilo separado. daemon=True asegura que el hilo
        muere automáticamente cuando el programa principal termina.
        """
        logger.info("BackgroundScheduler iniciado.")

        while self._running:
            # run_pending() ejecuta todas las tareas cuyo tiempo ha llegado
            schedule.run_pending()
            time.sleep(self._interval)

        logger.info("BackgroundScheduler detenido.")

    def start(self):
        """Inicia el hilo del scheduler en segundo plano."""
        if self._thread and self._thread.is_alive():
            logger.warning("El scheduler ya está corriendo.")
            return

        self._running = True
        # daemon=True: el hilo muere cuando el proceso principal termina
        self._thread  = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Detiene el scheduler de forma ordenada."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)  # esperar máximo 5 segundos
        schedule.clear()
        logger.info("Todas las tareas canceladas.")


# =============================================================================
# DEMOSTRACIÓN EN VIVO
# =============================================================================

def demo_live_scheduling(duration_seconds=8):
    """
    Ejecuta una demostración real del scheduler durante N segundos.

    Parámetros:
        duration_seconds (int): cuántos segundos correr la demo
    """
    if not SCHEDULE_AVAILABLE:
        return

    print(f"\n--- Demo en vivo: scheduler corriendo {duration_seconds} segundos ---")
    print(f"  (Las tareas se ejecutan en background mientras este código corre)")

    # Limpiar cualquier tarea previa
    schedule.clear()
    task_counter._count = 0

    # Programar las tareas
    # Heartbeat cada 2 segundos
    schedule.every(2).seconds.do(
        task_safe_wrapper, task_send_heartbeat
    )

    # Reporte cada 5 segundos
    schedule.every(5).seconds.do(
        task_safe_wrapper, task_generate_report
    )

    # Iniciar el scheduler en background
    bg_scheduler = BackgroundScheduler(interval_seconds=0.5)
    bg_scheduler.start()

    # Simular trabajo en el hilo principal mientras el scheduler corre
    print(f"\n  Programa principal activo...")
    end_time = time.time() + duration_seconds

    while time.time() < end_time:
        remaining = int(end_time - time.time())
        print(f"\r  Tiempo restante: {remaining}s | Heartbeats: {task_counter.value}  ", end="")
        time.sleep(0.5)

    print()  # nueva línea después del carriage return

    # Detener el scheduler
    bg_scheduler.stop()
    print(f"\n  Demo completada. Total de heartbeats ejecutados: {task_counter.value}")


# =============================================================================
# EJEMPLO PRÁCTICO: MONITOR DE ARCHIVOS
# =============================================================================

def demo_file_monitor():
    """
    Demuestra un monitor de archivos que reporta cambios periódicamente.

    Simula un caso de uso real: monitorear una carpeta de uploads
    y reportar cuántos archivos nuevos llegaron cada N segundos.
    """
    if not SCHEDULE_AVAILABLE:
        return

    print("\n--- Caso real: Monitor de carpeta de uploads ---")

    # Crear carpeta temporal de uploads para la demo
    upload_dir = Path(tempfile.mkdtemp(prefix="uploads_demo_"))
    print(f"  Carpeta monitoreada: {upload_dir}")

    # Estado previo del monitor
    last_count = [0]  # lista para poder modificar desde la closure

    def check_uploads():
        """Verifica archivos nuevos en la carpeta de uploads."""
        current_files = list(upload_dir.iterdir())
        current_count = len(current_files)
        diff = current_count - last_count[0]

        if diff > 0:
            logger.info(f"[Monitor] {diff} archivo(s) nuevo(s) en uploads. Total: {current_count}")
        else:
            logger.info(f"[Monitor] Sin cambios. Total archivos: {current_count}")

        last_count[0] = current_count

    # Programar chequeo cada 2 segundos
    schedule.clear()
    schedule.every(2).seconds.do(check_uploads)

    bg = BackgroundScheduler(interval_seconds=0.5)
    bg.start()

    # Simular llegada de archivos
    print("\n  Simulando llegada de archivos:")
    for i in range(1, 5):
        time.sleep(2.5)
        # Crear un archivo de prueba
        fake_file = upload_dir / f"upload_{i:03d}.dat"
        fake_file.write_text(f"contenido del archivo {i}")
        print(f"  -> Archivo creado: {fake_file.name}")

    time.sleep(3)  # esperar última verificación
    bg.stop()

    # Limpiar
    shutil.rmtree(upload_dir, ignore_errors=True)
    print(f"  Carpeta temporal eliminada.")


# =============================================================================
# CONCEPTOS DE APScheduler
# =============================================================================

def explain_apscheduler():
    """
    Explica APScheduler conceptualmente para aplicaciones más complejas.
    """
    print("""
--- APScheduler: Para aplicaciones más complejas ---

APScheduler es más potente que schedule:
  - Soporta triggers cron (expresiones como cron de Unix)
  - Persistencia de trabajos (sobrevive reinicios)
  - Integración con Flask, Django, FastAPI
  - Gestión de zonas horarias

Instalación:
  pip install apscheduler

Ejemplo básico con APScheduler:

    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BackgroundScheduler()

    # Todos los días a las 8:00 AM
    scheduler.add_job(
        func=generar_reporte,
        trigger=CronTrigger(hour=8, minute=0),
        id="reporte_diario",
        name="Reporte diario de ventas",
        replace_existing=True
    )

    # Cada 30 minutos
    scheduler.add_job(
        func=limpiar_cache,
        trigger="interval",
        minutes=30
    )

    scheduler.start()

Cuándo usar cada librería:
  schedule    → scripts simples, tareas locales, proyectos pequeños
  APScheduler → aplicaciones web, múltiples zonas horarias, persistencia
    """)


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal que demuestra el scheduling de tareas."""

    print("=" * 60)
    print("  DEMO: Scheduling — Tareas Periódicas con Python")
    print("=" * 60)

    if not check_schedule():
        print("\nMostrando solo la sintaxis conceptual...")
        demo_schedule_sintaxis()
        explain_apscheduler()
        return

    demo_schedule_sintaxis()
    demo_live_scheduling(duration_seconds=8)
    demo_file_monitor()
    explain_apscheduler()

    print("\n" + "=" * 60)
    print("  Demo completado.")
    print("=" * 60)


if __name__ == "__main__":
    main()
