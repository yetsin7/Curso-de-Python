"""
Proyecto Integrador de Automatización
=======================================
Organizador automático de descargas que:
  - Monitorea una carpeta y mueve archivos según su extensión
  - Genera un reporte diario en texto de qué se organizó
  - Registra todas las operaciones con logging completo
  - Maneja errores y archivos en uso de forma segura
  - Soporta modo "dry-run" para simular sin mover nada real

Uso:
    python 06_proyecto_automatizacion.py [--dry-run] [--carpeta RUTA]

Dependencias: solo librería estándar de Python.
"""

import argparse
import logging
import os
import shutil
import time
from datetime import date
from pathlib import Path

# ===========================================================================
# Configuración de categorías por extensión
# ===========================================================================

CATEGORIAS: dict[str, list[str]] = {
    "Imagenes":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"],
    "Videos":      [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".m4v"],
    "Audios":      [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "Documentos":  [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".odt"],
    "Codigo":      [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".sh"],
    "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Ejecutables": [".exe", ".msi", ".apk", ".dmg", ".deb", ".rpm"],
    "Otros":       [],  # carpeta para extensiones no clasificadas
}


def obtener_categoria(extension: str) -> str:
    """
    Determina la carpeta de destino de un archivo según su extensión.

    Args:
        extension: Extensión del archivo en minúsculas, con punto (ej. '.jpg').

    Returns:
        Nombre de la carpeta de destino (ej. 'Imagenes', 'Otros').
    """
    ext_lower = extension.lower()
    for categoria, extensiones in CATEGORIAS.items():
        if ext_lower in extensiones:
            return categoria
    return "Otros"


# ===========================================================================
# Configuración del logger
# ===========================================================================

def configurar_logger(carpeta_log: Path) -> logging.Logger:
    """
    Configura y retorna el logger principal del organizador.
    Escribe simultáneamente en consola y en archivo de log diario.

    Args:
        carpeta_log: Directorio donde guardar los archivos .log

    Returns:
        Logger configurado con dos handlers (consola + archivo).
    """
    carpeta_log.mkdir(parents=True, exist_ok=True)
    archivo_log = carpeta_log / f"organizador_{date.today().isoformat()}.log"

    logger = logging.getLogger("organizador")
    logger.setLevel(logging.DEBUG)

    formato = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )

    # Handler de consola
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.INFO)
    handler_consola.setFormatter(formato)

    # Handler de archivo (guarda DEBUG también)
    handler_archivo = logging.FileHandler(archivo_log, encoding="utf-8")
    handler_archivo.setLevel(logging.DEBUG)
    handler_archivo.setFormatter(formato)

    if not logger.handlers:  # evitar duplicar handlers en re-ejecuciones
        logger.addHandler(handler_consola)
        logger.addHandler(handler_archivo)

    return logger


# ===========================================================================
# Verificación de archivos en uso
# ===========================================================================

def archivo_en_uso(ruta: Path) -> bool:
    """
    Intenta abrir el archivo en modo exclusivo para verificar si está en uso.
    Método portable que funciona en Windows y Linux.

    Args:
        ruta: Path del archivo a verificar.

    Returns:
        True si el archivo está siendo usado por otro proceso.
    """
    try:
        with open(ruta, "r+b"):
            pass
        return False
    except (IOError, PermissionError, OSError):
        return True


# ===========================================================================
# Motor principal del organizador
# ===========================================================================

class OrganizadorDescargas:
    """
    Organiza los archivos de una carpeta moviéndolos a subcarpetas
    según su tipo. Soporta modo dry-run para simular operaciones.

    Attributes:
        carpeta     : Carpeta de descargas a organizar.
        dry_run     : Si True, simula las operaciones sin moverlas.
        logger      : Logger para registrar eventos.
        estadisticas: Resumen de archivos movidos, omitidos y con error.
    """

    def __init__(self, carpeta: Path, dry_run: bool = False) -> None:
        """
        Inicializa el organizador.

        Args:
            carpeta : Carpeta raíz a monitorear y organizar.
            dry_run : Si True, no mueve archivos reales.
        """
        self.carpeta = carpeta
        self.dry_run = dry_run
        self.logger  = configurar_logger(carpeta / "logs")
        self.estadisticas: dict[str, int] = {
            "movidos":  0,
            "omitidos": 0,
            "errores":  0,
        }

    def _mover_archivo(self, origen: Path, destino: Path) -> bool:
        """
        Mueve un archivo al destino, creando la carpeta si no existe.
        En dry-run solo registra la operación sin mover.

        Args:
            origen : Ruta actual del archivo.
            destino: Ruta destino del archivo.

        Returns:
            True si la operación fue exitosa (o simulada).
        """
        if self.dry_run:
            self.logger.info(f"[DRY-RUN] {origen.name} → {destino.parent.name}/")
            return True

        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
            # Evitar sobreescribir: renombrar si ya existe
            if destino.exists():
                stem, suffix = destino.stem, destino.suffix
                contador = 1
                while destino.exists():
                    destino = destino.parent / f"{stem}_{contador}{suffix}"
                    contador += 1

            shutil.move(str(origen), str(destino))
            self.logger.info(f"Movido: {origen.name} → {destino.parent.name}/")
            return True

        except PermissionError:
            self.logger.warning(f"Sin permisos para mover: {origen.name}")
            return False
        except OSError as e:
            self.logger.error(f"Error al mover {origen.name}: {e}")
            return False

    def organizar(self) -> None:
        """
        Recorre todos los archivos directos (no recursivo) de la carpeta
        y los mueve a la subcarpeta correspondiente según su extensión.
        Omite subcarpetas, archivos ocultos y archivos en uso.
        """
        if not self.carpeta.exists():
            self.logger.error(f"La carpeta no existe: {self.carpeta}")
            return

        modo = "DRY-RUN" if self.dry_run else "REAL"
        self.logger.info(f"Iniciando organización [{modo}]: {self.carpeta}")

        archivos = [f for f in self.carpeta.iterdir()
                    if f.is_file() and not f.name.startswith(".")]

        if not archivos:
            self.logger.info("No se encontraron archivos para organizar.")
            return

        for archivo in archivos:
            # Omitir el propio script si está en la misma carpeta
            if archivo.suffix == ".py":
                self.logger.debug(f"Omitido (script Python): {archivo.name}")
                self.estadisticas["omitidos"] += 1
                continue

            # Verificar si el archivo está en uso
            if archivo_en_uso(archivo):
                self.logger.warning(f"Archivo en uso, omitido: {archivo.name}")
                self.estadisticas["omitidos"] += 1
                continue

            categoria = obtener_categoria(archivo.suffix)
            destino   = self.carpeta / categoria / archivo.name

            if self._mover_archivo(archivo, destino):
                self.estadisticas["movidos"] += 1
            else:
                self.estadisticas["errores"] += 1

        self.logger.info(
            f"Finalizado — Movidos: {self.estadisticas['movidos']} | "
            f"Omitidos: {self.estadisticas['omitidos']} | "
            f"Errores: {self.estadisticas['errores']}"
        )

    def generar_reporte(self) -> str:
        """
        Genera un reporte de texto con el resumen de la organización.
        Guarda el reporte en un archivo dentro de la carpeta.

        Returns:
            Ruta del archivo de reporte generado.
        """
        hoy = date.today().isoformat()
        ruta_reporte = self.carpeta / f"reporte_{hoy}.txt"

        lineas = [
            f"REPORTE DE ORGANIZACIÓN — {hoy}",
            "=" * 40,
            f"Carpeta procesada : {self.carpeta}",
            f"Modo              : {'DRY-RUN (simulación)' if self.dry_run else 'REAL'}",
            "",
            "RESUMEN:",
            f"  Archivos movidos  : {self.estadisticas['movidos']}",
            f"  Archivos omitidos : {self.estadisticas['omitidos']}",
            f"  Errores           : {self.estadisticas['errores']}",
            "",
            "CATEGORÍAS DISPONIBLES:",
        ]

        for cat in CATEGORIAS:
            subcarpeta = self.carpeta / cat
            count = len(list(subcarpeta.iterdir())) if subcarpeta.exists() else 0
            lineas.append(f"  {cat:<15} → {count} archivo(s)")

        lineas.append("")
        lineas.append("Reporte generado automáticamente por el Organizador de Descargas.")

        contenido = "\n".join(lineas)

        if not self.dry_run:
            with open(ruta_reporte, "w", encoding="utf-8") as f:
                f.write(contenido)
            self.logger.info(f"Reporte guardado: {ruta_reporte}")
        else:
            self.logger.info(f"[DRY-RUN] Reporte no guardado (simulación activa).")

        return contenido


# ===========================================================================
# Punto de entrada con CLI
# ===========================================================================

def main() -> None:
    """
    Punto de entrada con argumentos de línea de comandos.
    Permite especificar carpeta y activar el modo dry-run.
    """
    parser = argparse.ArgumentParser(
        description="Organizador automático de descargas por tipo de archivo"
    )
    parser.add_argument(
        "--carpeta",
        type=str,
        default=str(Path.home() / "Downloads"),
        help="Carpeta a organizar (por defecto: ~/Downloads)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simular sin mover archivos reales"
    )

    args = parser.parse_args()
    carpeta = Path(args.carpeta)

    print("=" * 60)
    print("  ORGANIZADOR DE DESCARGAS")
    print("=" * 60)
    print(f"  Carpeta : {carpeta}")
    print(f"  Modo    : {'DRY-RUN (simulación)' if args.dry_run else 'REAL — se moverán archivos'}")
    print()

    organizador = OrganizadorDescargas(carpeta=carpeta, dry_run=args.dry_run)
    organizador.organizar()

    reporte = organizador.generar_reporte()
    print("\n--- REPORTE ---")
    print(reporte)


if __name__ == "__main__":
    main()
