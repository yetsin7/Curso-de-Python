"""
Capítulo 14 — Python Avanzado
Archivo: 02_context_managers.py

Context Managers (gestores de contexto) — la sentencia with.

Un context manager garantiza que ciertos recursos se inicialicen
y liberen correctamente, incluso si ocurre una excepción.

El patrón "adquirir recurso → usar recurso → liberar recurso"
es tan común que Python lo elevó a sintaxis de primera clase: with.

Sin context manager:
    f = open("archivo.txt")
    try:
        datos = f.read()
    finally:
        f.close()  # Hay que recordarlo SIEMPRE, incluso con errores

Con context manager:
    with open("archivo.txt") as f:
        datos = f.read()  # f.close() se llama automáticamente

Ejecución:
    python 02_context_managers.py
"""

import time         # Para el context manager de timer
import tempfile     # Para archivos temporales
import os           # Para operaciones de sistema de archivos
from contextlib import contextmanager, suppress  # Utilidades de context managers
from typing import Generator, Optional


# ==============================================================
# SECCIÓN 1: Cómo funciona with — el protocolo __enter__/__exit__
# ==============================================================

class GestorSimple:
    """
    Implementación mínima de un context manager mediante clase.
    Para ser un context manager, una clase necesita exactamente
    dos métodos especiales: __enter__ y __exit__.
    """

    def __init__(self, nombre: str) -> None:
        """El constructor inicializa, pero NO adquiere el recurso todavía."""
        self.nombre = nombre
        print(f"[{self.nombre}] Constructor llamado")

    def __enter__(self):
        """
        Se llama AL ENTRAR al bloque with.
        Aquí se adquiere o inicializa el recurso.
        El valor que retorna es el que recibe 'as variable'.
        Si no devuelves nada útil, devuelve self.
        """
        print(f"[{self.nombre}] __enter__ → adquiriendo recurso")
        return self  # 'with GestorSimple() as g:' — g será este objeto

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Se llama AL SALIR del bloque with, SIEMPRE.
        Esto incluye: salida normal, return, break, excepción.

        Parámetros:
            exc_type: tipo de excepción (None si no hubo error)
            exc_val:  valor/mensaje de la excepción
            exc_tb:   traceback de la excepción

        Retorno:
            True  → suprimir la excepción (no se propaga)
            False → dejar que la excepción se propague (comportamiento normal)
            None  → equivalente a False
        """
        if exc_type is None:
            print(f"[{self.nombre}] __exit__ → salida normal, liberando recurso")
        else:
            print(f"[{self.nombre}] __exit__ → hubo excepción: {exc_type.__name__}: {exc_val}")
            print(f"[{self.nombre}] Liberando recurso de todas formas")

        # Retornamos False para NO suprimir la excepción
        return False


# ==============================================================
# SECCIÓN 2: Context manager de archivo con cierre garantizado
# ==============================================================

class GestorArchivo:
    """
    Context manager que envuelve operaciones de archivo.
    Garantiza que el archivo se cierra aunque ocurra una excepción.
    (open() ya es un context manager, esto es solo para aprender)
    """

    def __init__(self, ruta: str, modo: str = "r") -> None:
        self.ruta = ruta
        self.modo = modo
        self._archivo = None

    def __enter__(self):
        """Abre el archivo y lo devuelve para usar con 'as'."""
        print(f"  Abriendo archivo: {self.ruta}")
        self._archivo = open(self.ruta, self.modo, encoding="utf-8")
        return self._archivo

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra el archivo siempre, haya o no excepción."""
        if self._archivo and not self._archivo.closed:
            self._archivo.close()
            print(f"  Archivo cerrado: {self.ruta}")
        return False  # No suprimimos excepciones


# ==============================================================
# SECCIÓN 3: Timer como context manager
# ==============================================================

class Timer:
    """
    Mide el tiempo de ejecución de un bloque de código.
    Ejemplo de uso real en profiling y benchmarking.
    """

    def __init__(self, descripcion: str = "Operación") -> None:
        self.descripcion = descripcion
        self.inicio: float = 0.0
        self.fin: float = 0.0
        self.duracion: float = 0.0  # Accesible después del bloque with

    def __enter__(self) -> "Timer":
        """Registra el tiempo de inicio."""
        self.inicio = time.perf_counter()
        return self  # Devuelve self para acceder a self.duracion después

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Calcula la duración al salir del bloque."""
        self.fin = time.perf_counter()
        self.duracion = self.fin - self.inicio
        print(f"  [{self.descripcion}] Tiempo: {self.duracion:.4f}s")
        return False


# ==============================================================
# SECCIÓN 4: Context manager con contextlib.contextmanager
# ==============================================================

@contextmanager
def directorio_temporal() -> Generator[str, None, None]:
    """
    Context manager creado con el decorador @contextmanager.
    Es más conciso que crear una clase con __enter__/__exit__.

    @contextmanager convierte una función generadora en un
    context manager. La función debe:
      1. Ejecutar el código de inicialización (antes del yield)
      2. Hacer yield con el valor que recibirá 'as variable'
      3. Ejecutar el código de limpieza (después del yield)

    El try/finally garantiza que la limpieza ocurra siempre.
    """
    # Código que se ejecuta en __enter__
    tmp_dir = tempfile.mkdtemp(prefix="python_demo_")
    print(f"  Directorio temporal creado: {tmp_dir}")

    try:
        yield tmp_dir  # El valor que recibe 'as directorio'
    finally:
        # Código que se ejecuta en __exit__ (siempre)
        # Limpiamos el directorio temporal
        import shutil
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
            print(f"  Directorio temporal eliminado: {tmp_dir}")


@contextmanager
def indentacion(nivel: int = 1) -> Generator[None, None, None]:
    """
    Context manager de ejemplo para formateo de output.
    Demuestra que un context manager puede no tener recurso real.
    """
    prefijo = "  " * nivel
    print(f"{prefijo}┌── Inicio de sección")
    try:
        yield
    finally:
        print(f"{prefijo}└── Fin de sección")


# ==============================================================
# SECCIÓN 5: contextlib.suppress — suprimir excepciones específicas
# ==============================================================

def demo_suppress():
    """
    contextlib.suppress() es un context manager que suprime
    excepciones de tipos específicos. Equivale a try/except: pass.

    Útil cuando quieres ignorar un error esperado sin escribir
    un bloque try/except completo.
    """
    print("--- contextlib.suppress ---")

    # Sin suppress:
    try:
        os.remove("archivo_que_no_existe.txt")
    except FileNotFoundError:
        pass  # Ignoramos si el archivo no existe

    # Con suppress: más legible y expresivo
    with suppress(FileNotFoundError):
        os.remove("archivo_que_no_existe.txt")
        # Si el archivo no existe, FileNotFoundError es suprimida
        # Si ocurre otro error (PermissionError), sí se propaga

    print("  (suppress ejecutado sin errores visibles)")


# ==============================================================
# SECCIÓN 6: Múltiples context managers en un solo with
# ==============================================================

def demo_multiple_context_managers():
    """
    Python permite combinar múltiples context managers en un
    solo with. Son equivalentes a anidar varios with.
    """
    print("--- Múltiples context managers ---")

    # Crear dos archivos temporales para el ejemplo
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as origen, tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as destino:
        # Ambos archivos están abiertos al mismo tiempo
        origen.write("Datos de origen\nLínea 2\nLínea 3")
        destino.write("Datos de destino")
        print(f"  Archivo origen: {origen.name}")
        print(f"  Archivo destino: {destino.name}")

    # Aquí ambos archivos están cerrados (sus __exit__ fueron llamados)
    # Limpiamos
    with suppress(OSError):
        os.unlink(origen.name)
        os.unlink(destino.name)
    print("  Ambos archivos cerrados y eliminados")


# ==============================================================
# SECCIÓN 7: Context manager que suprime y registra excepciones
# ==============================================================

class ManejadorSeguro:
    """
    Context manager que captura excepciones, las registra,
    y opcionalmente las suprime. Útil en procesos por lotes
    donde un error en un ítem no debe detener todo el proceso.
    """

    def __init__(self, suprimir: bool = False) -> None:
        self.suprimir = suprimir
        self.excepcion: Optional[Exception] = None

    def __enter__(self) -> "ManejadorSeguro":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            self.excepcion = exc_val
            print(f"  [ManejadorSeguro] Excepción capturada: {exc_type.__name__}: {exc_val}")
            # Retornamos True para suprimir la excepción si se configura así
            return self.suprimir
        return False

    @property
    def hubo_error(self) -> bool:
        """Indica si ocurrió una excepción en el bloque."""
        return self.excepcion is not None


# ==============================================================
# DEMOSTRACIÓN COMPLETA
# ==============================================================

def demo():
    """Ejecuta todos los ejemplos de context managers."""
    sep = "─" * 50

    print("=== CONTEXT MANAGERS ===\n")

    # Sección 1: protocolo básico
    print(f"{sep}\n1. PROTOCOLO __enter__ / __exit__\n")
    with GestorSimple("Ejemplo") as g:
        print(f"   Dentro del bloque, g = {g}")
    print("   Fuera del bloque\n")

    # __exit__ se llama aunque haya excepción
    print("   Con excepción:")
    try:
        with GestorSimple("ConError"):
            raise ValueError("Error de prueba")
    except ValueError:
        print("   (excepción propagada correctamente)\n")

    # Sección 3: Timer
    print(f"{sep}\n3. TIMER\n")
    with Timer("Suma de 1M números") as t:
        resultado = sum(range(1_000_000))
    print(f"  Resultado: {resultado}, duración guardada: {t.duracion:.4f}s\n")

    # Sección 4: contextmanager decorator
    print(f"{sep}\n4. @contextmanager\n")
    with directorio_temporal() as tmp:
        # Creamos un archivo dentro del directorio temporal
        ruta_archivo = os.path.join(tmp, "prueba.txt")
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write("Contenido de prueba")
        print(f"  Archivo creado: {ruta_archivo}")
        print(f"  Existe: {os.path.exists(ruta_archivo)}")
    print(f"  Después del with, ¿existe el dir? {os.path.exists(tmp)}\n")

    # Decorador de indentación
    with indentacion(1):
        print("    Contenido de la sección")
        with indentacion(2):
            print("      Contenido anidado")

    # Sección 5: suppress
    print(f"\n{sep}\n5. contextlib.suppress\n")
    demo_suppress()

    # Sección 6: múltiples context managers
    print(f"\n{sep}\n6. MÚLTIPLES CONTEXT MANAGERS\n")
    demo_multiple_context_managers()

    # Sección 7: ManejadorSeguro
    print(f"\n{sep}\n7. MANEJADOR SEGURO\n")
    with ManejadorSeguro(suprimir=True) as m:
        raise RuntimeError("Error que será suprimido")
    print(f"  ¿Hubo error? {m.hubo_error}")
    print(f"  Excepción: {m.excepcion}")
    print("  (el programa continuó normalmente)\n")


if __name__ == "__main__":
    demo()
