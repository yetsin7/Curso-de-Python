# =============================================================================
# 01_sistema_archivos.py — Automatización del sistema de archivos
# =============================================================================
# Python incluye de serie todas las herramientas necesarias para el sistema
# de archivos. No requiere instalación de librerías externas.
#
# Módulos usados (todos incluidos con Python):
#   - os         : operaciones del sistema operativo
#   - os.path    : manipulación de rutas (API clásica)
#   - shutil     : copiar, mover, eliminar archivos y carpetas
#   - pathlib    : API moderna orientada a objetos para rutas (Python 3.4+)
#   - glob       : búsqueda de archivos por patrón
#   - tempfile   : archivos y carpetas temporales para las pruebas
#
# IMPORTANTE: Este archivo crea archivos y carpetas de prueba en una
# carpeta temporal y los elimina al final. No modifica nada fuera de esa carpeta.
# =============================================================================

import os
import shutil
import glob
import tempfile
from pathlib import Path
from datetime import datetime


# =============================================================================
# PREPARAR ENTORNO DE PRUEBA
# =============================================================================

def create_test_environment(base_dir):
    """
    Crea una estructura de carpetas y archivos de prueba para los ejemplos.

    Parámetros:
        base_dir (Path): carpeta raíz donde crear el entorno de prueba

    Retorna:
        dict: diccionario con las rutas creadas para referencia
    """
    print(f"  Creando entorno de prueba en: {base_dir}")

    # Crear estructura de carpetas
    folders = {
        "docs":     base_dir / "documentos",
        "imgs":     base_dir / "imagenes",
        "reports":  base_dir / "reportes",
        "archive":  base_dir / "archivo",
        "backup":   base_dir / "backup",
    }

    for name, path in folders.items():
        path.mkdir(parents=True, exist_ok=True)

    # Crear archivos de prueba con contenido
    test_files = [
        (folders["docs"] / "informe_enero.txt",  "Contenido del informe de enero 2024"),
        (folders["docs"] / "informe_febrero.txt", "Contenido del informe de febrero 2024"),
        (folders["docs"] / "notas.txt",           "Notas personales importantes"),
        (folders["docs"] / "presupuesto.csv",     "mes,ingresos,gastos\nenero,5000,3200"),
        (folders["imgs"] / "foto_01.jpg",         "datos_binarios_simulados_jpg"),
        (folders["imgs"] / "foto_02.jpg",         "datos_binarios_simulados_jpg"),
        (folders["imgs"] / "logo.png",            "datos_binarios_simulados_png"),
        (folders["reports"] / "reporte_q1.pdf",   "contenido_del_reporte_pdf"),
        (folders["reports"] / "reporte_q2.pdf",   "contenido_del_reporte_pdf"),
    ]

    for file_path, content in test_files:
        file_path.write_text(content, encoding="utf-8")

    print(f"  Creadas {len(folders)} carpetas y {len(test_files)} archivos.")
    return folders


# =============================================================================
# EXPLORACIÓN CON os Y os.path
# =============================================================================

def demo_os_basico(base_dir):
    """
    Demuestra las operaciones básicas del módulo os y os.path.

    os.path es la API clásica para trabajar con rutas.
    pathlib (más abajo) es la alternativa moderna y preferida.
    """
    print("\n--- os y os.path: API clásica ---")

    # Convertir a string para usar con os.path
    base = str(base_dir)

    # os.path.exists() — verificar si existe
    print(f"  ¿Existe la carpeta?: {os.path.exists(base)}")
    print(f"  ¿Es directorio?:     {os.path.isdir(base)}")

    # os.path.join() — construir rutas de forma multiplataforma
    # Usa / en Linux/Mac y \ en Windows automáticamente
    docs_path = os.path.join(base, "documentos")
    nota_path = os.path.join(docs_path, "notas.txt")
    print(f"  Ruta construida:     {nota_path}")
    print(f"  ¿Es archivo?:        {os.path.isfile(nota_path)}")

    # os.path.split() — separar directorio y nombre
    folder, filename = os.path.split(nota_path)
    print(f"  Carpeta padre:       {folder}")
    print(f"  Nombre del archivo:  {filename}")

    # os.path.splitext() — separar nombre y extensión
    name, ext = os.path.splitext(filename)
    print(f"  Nombre sin ext:      {name}")
    print(f"  Extensión:           {ext}")

    # os.path.getsize() — tamaño en bytes
    size = os.path.getsize(nota_path)
    print(f"  Tamaño del archivo:  {size} bytes")

    # os.listdir() — listar contenido de una carpeta
    contents = os.listdir(docs_path)
    print(f"\n  Contenido de 'documentos' ({len(contents)} items):")
    for item in sorted(contents):
        full = os.path.join(docs_path, item)
        tipo = "DIR " if os.path.isdir(full) else "FILE"
        print(f"    [{tipo}] {item}")


# =============================================================================
# PATHLIB — LA API MODERNA (RECOMENDADA)
# =============================================================================

def demo_pathlib(base_dir):
    """
    Demuestra pathlib — la forma moderna y recomendada de trabajar con rutas.

    pathlib.Path trata las rutas como objetos con métodos y propiedades.
    Es más legible y menos propenso a errores que os.path.

    Parámetros:
        base_dir (Path): carpeta base del entorno de prueba
    """
    print("\n--- pathlib: API moderna orientada a objetos ---")

    docs = base_dir / "documentos"   # el operador / construye rutas

    # Propiedades del objeto Path
    nota = docs / "notas.txt"
    print(f"  Path completo:  {nota}")
    print(f"  Solo nombre:    {nota.name}")
    print(f"  Sin extensión:  {nota.stem}")
    print(f"  Extensión:      {nota.suffix}")
    print(f"  Carpeta padre:  {nota.parent}")
    print(f"  ¿Existe?:       {nota.exists()}")
    print(f"  ¿Es archivo?:   {nota.is_file()}")
    print(f"  Tamaño:         {nota.stat().st_size} bytes")

    # Leer y escribir archivos con Path (muy conveniente)
    contenido = nota.read_text(encoding="utf-8")
    print(f"  Contenido:      '{contenido}'")

    # Escribir en un nuevo archivo
    nueva_nota = docs / "nueva_nota.txt"
    nueva_nota.write_text("Esta nota fue creada con pathlib", encoding="utf-8")
    print(f"\n  Archivo creado: {nueva_nota.name}")

    # iterdir() — iterar sobre contenido de una carpeta
    print(f"\n  Archivos .txt en 'documentos':")
    for txt_file in sorted(docs.glob("*.txt")):
        size = txt_file.stat().st_size
        print(f"    {txt_file.name:<30} {size} bytes")

    # Path.home() y Path.cwd() — rutas especiales del sistema
    print(f"\n  Carpeta home del usuario: {Path.home()}")
    print(f"  Directorio de trabajo:    {Path.cwd()}")


# =============================================================================
# RECORRER DIRECTORIOS RECURSIVAMENTE
# =============================================================================

def demo_recorrer_recursivo(base_dir):
    """
    Demuestra cómo recorrer carpetas y subcarpetas recursivamente.

    os.walk() y Path.rglob() son las dos formas principales.
    Se usan para indexar archivos, buscar duplicados, analizar proyectos, etc.

    Parámetros:
        base_dir (Path): carpeta raíz a recorrer
    """
    print("\n--- Recorrido recursivo de directorios ---")

    # Método 1: os.walk() — recorre todo el árbol de directorios
    # Devuelve tuplas: (ruta_carpeta, [subcarpetas], [archivos])
    print("  Con os.walk():")
    total_files = 0

    for dirpath, dirnames, filenames in os.walk(base_dir):
        # Calcular nivel de profundidad para indentación visual
        depth = len(Path(dirpath).relative_to(base_dir).parts)
        indent = "  " * (depth + 1)
        folder_name = os.path.basename(dirpath) or base_dir.name

        print(f"  {indent}📁 {folder_name}/")
        for filename in sorted(filenames):
            print(f"  {indent}  📄 {filename}")
            total_files += 1

    print(f"\n  Total de archivos encontrados: {total_files}")

    # Método 2: Path.rglob() — más Pythónico y flexible
    print("\n  Con Path.rglob() — solo archivos .txt:")
    txt_files = sorted(base_dir.rglob("*.txt"))
    for f in txt_files:
        # relative_to() devuelve la ruta relativa a la base
        rel_path = f.relative_to(base_dir)
        print(f"    {rel_path}")


# =============================================================================
# BUSCAR ARCHIVOS CON GLOB
# =============================================================================

def demo_glob(base_dir):
    """
    Demuestra búsqueda de archivos por patrón con glob.

    glob entiende estos comodines:
        *     → cualquier cantidad de caracteres (en el mismo directorio)
        ?     → un solo carácter
        **    → cualquier directorio (recursivo, con recursive=True)
        [abc] → uno de esos caracteres

    Parámetros:
        base_dir (Path): carpeta raíz
    """
    print("\n--- Búsqueda de archivos con glob ---")

    base = str(base_dir)

    # Todos los .txt en una carpeta específica
    txt_pattern = os.path.join(base, "documentos", "*.txt")
    txt_files = glob.glob(txt_pattern)
    print(f"  *.txt en documentos: {[os.path.basename(f) for f in txt_files]}")

    # Archivos que empiezan con "informe"
    informe_pattern = os.path.join(base, "documentos", "informe_*.txt")
    informes = glob.glob(informe_pattern)
    print(f"  informe_*.txt: {[os.path.basename(f) for f in informes]}")

    # Búsqueda recursiva — todos los PDF en cualquier subcarpeta
    pdf_pattern = os.path.join(base, "**", "*.pdf")
    all_pdfs = glob.glob(pdf_pattern, recursive=True)
    print(f"  **/*.pdf (recursivo): {[os.path.basename(f) for f in all_pdfs]}")

    # Con pathlib — equivalente más moderno
    all_imgs = list(base_dir.rglob("*.jpg")) + list(base_dir.rglob("*.png"))
    print(f"  Todas las imágenes: {[f.name for f in all_imgs]}")


# =============================================================================
# COPIAR, MOVER Y RENOMBRAR
# =============================================================================

def demo_shutil(base_dir, folders):
    """
    Demuestra operaciones de copia, movimiento y renombrado con shutil.

    shutil (shell utilities) proporciona operaciones de alto nivel
    que no están en os: copiar árboles completos, mover con reemplazos, etc.

    Parámetros:
        base_dir (Path): carpeta raíz del entorno de prueba
        folders (dict): rutas de las carpetas creadas en el setup
    """
    print("\n--- shutil: Copiar, mover, renombrar ---")

    # Copiar un archivo
    origen = folders["docs"] / "notas.txt"
    destino = folders["backup"] / "notas_backup.txt"
    shutil.copy2(origen, destino)
    # copy2 copia el archivo Y preserva metadatos (fecha, permisos)
    print(f"  Copiado: {origen.name} → backup/{destino.name}")

    # Copiar una carpeta completa con todo su contenido
    src_tree = folders["docs"]
    dst_tree = folders["backup"] / "docs_backup"
    shutil.copytree(src_tree, dst_tree)
    files_copied = len(list(dst_tree.iterdir()))
    print(f"  Árbol copiado: documentos/ → backup/docs_backup/ ({files_copied} items)")

    # Mover un archivo
    reporte_src = folders["reports"] / "reporte_q1.pdf"
    reporte_dst = folders["archive"] / "reporte_q1_2024.pdf"
    shutil.move(str(reporte_src), str(reporte_dst))
    print(f"  Movido: reportes/reporte_q1.pdf → archivo/reporte_q1_2024.pdf")
    print(f"  ¿Existe en origen?: {reporte_src.exists()} | ¿En destino?: {reporte_dst.exists()}")

    # Renombrar con pathlib (más claro que os.rename)
    old_name = folders["docs"] / "nueva_nota.txt"
    new_name = folders["docs"] / "nota_renombrada.txt"
    if old_name.exists():
        old_name.rename(new_name)
        print(f"  Renombrado: nueva_nota.txt → nota_renombrada.txt")


# =============================================================================
# ELIMINAR ARCHIVOS Y CARPETAS
# =============================================================================

def demo_delete(base_dir, folders):
    """
    Demuestra cómo eliminar archivos y carpetas.

    ADVERTENCIA: La eliminación en Python es PERMANENTE (no va a la Papelera).
    Siempre verifica las rutas antes de eliminar.

    Parámetros:
        base_dir (Path): carpeta raíz
        folders (dict): rutas del entorno de prueba
    """
    print("\n--- Eliminar archivos y carpetas ---")

    # Eliminar un archivo con Path.unlink()
    presupuesto = folders["docs"] / "presupuesto.csv"
    if presupuesto.exists():
        presupuesto.unlink()
        print(f"  Eliminado: presupuesto.csv | ¿Existe aún?: {presupuesto.exists()}")

    # Eliminar archivo con os.remove() (API clásica)
    nota_renombrada = folders["docs"] / "nota_renombrada.txt"
    if nota_renombrada.exists():
        os.remove(nota_renombrada)
        print(f"  Eliminado (os.remove): nota_renombrada.txt")

    # Eliminar carpeta vacía
    empty_dir = base_dir / "carpeta_vacia_test"
    empty_dir.mkdir()
    empty_dir.rmdir()
    print(f"  Carpeta vacía creada y eliminada con rmdir()")

    # Eliminar carpeta con contenido
    backup_docs = folders["backup"] / "docs_backup"
    if backup_docs.exists():
        shutil.rmtree(backup_docs)
        print(f"  Árbol eliminado: backup/docs_backup/ con shutil.rmtree()")


# =============================================================================
# CASO DE USO REAL: ORGANIZADOR DE ARCHIVOS
# =============================================================================

def organize_files_by_extension(source_dir):
    """
    Organiza los archivos de una carpeta en subcarpetas según su extensión.

    Este es un ejemplo de automatización práctica y real:
    organizar descargas, ordernar proyectos, etc.

    Parámetros:
        source_dir (Path): carpeta que contiene los archivos a organizar

    Retorna:
        dict: resumen de archivos movidos por extensión
    """
    print("\n--- Caso real: Organizador de archivos por extensión ---")

    # Mapa de extensiones a nombres de carpeta destino
    extension_map = {
        ".txt":  "textos",
        ".csv":  "datos",
        ".pdf":  "pdfs",
        ".jpg":  "imagenes",
        ".jpeg": "imagenes",
        ".png":  "imagenes",
        ".xlsx": "excel",
        ".docx": "word",
    }

    summary = {}

    # Recorrer todos los archivos (no carpetas) en la raíz del directorio
    for file_path in source_dir.iterdir():
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()
        folder_name = extension_map.get(ext, "otros")

        # Crear la subcarpeta destino si no existe
        dest_folder = source_dir / folder_name
        dest_folder.mkdir(exist_ok=True)

        # Mover el archivo a la subcarpeta correspondiente
        dest_path = dest_folder / file_path.name
        shutil.move(str(file_path), str(dest_path))

        # Registrar en el resumen
        summary[folder_name] = summary.get(folder_name, 0) + 1

    print("  Archivos organizados:")
    for folder_name, count in sorted(summary.items()):
        print(f"    {folder_name}/: {count} archivo(s)")

    return summary


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal que demuestra todas las operaciones del sistema de archivos."""

    print("=" * 60)
    print("  DEMO: Sistema de Archivos con os, pathlib y shutil")
    print("=" * 60)

    # Crear una carpeta temporal para todas las pruebas
    # tempfile.mkdtemp() crea una carpeta temporal única en el sistema
    # Garantiza que no pisamos archivos del usuario
    temp_dir = Path(tempfile.mkdtemp(prefix="python_demo_"))
    print(f"\nCarpeta temporal de prueba: {temp_dir}")

    try:
        # Setup del entorno de prueba
        print("\n[1] Preparando entorno de prueba...")
        folders = create_test_environment(temp_dir)

        print("\n[2] Explorando con os y os.path...")
        demo_os_basico(temp_dir)

        print("\n[3] Explorando con pathlib (API moderna)...")
        demo_pathlib(temp_dir)

        print("\n[4] Recorrido recursivo de directorios...")
        demo_recorrer_recursivo(temp_dir)

        print("\n[5] Búsqueda con glob...")
        demo_glob(temp_dir)

        print("\n[6] Copiar, mover y renombrar con shutil...")
        demo_shutil(temp_dir, folders)

        print("\n[7] Eliminar archivos y carpetas...")
        demo_delete(temp_dir, folders)

        # Crear una carpeta nueva con archivos mezclados para organizar
        to_organize = temp_dir / "desordenado"
        to_organize.mkdir()
        (to_organize / "reporte.pdf").write_text("pdf")
        (to_organize / "datos.csv").write_text("csv")
        (to_organize / "foto.jpg").write_text("jpg")
        (to_organize / "notas.txt").write_text("txt")
        (to_organize / "logo.png").write_text("png")

        print("\n[8] Organizador automático de archivos...")
        organize_files_by_extension(to_organize)

    finally:
        # Limpiar SIEMPRE, incluso si hay un error en algún paso
        print(f"\nLimpiando carpeta temporal: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("Limpieza completada.")

    print("\n" + "=" * 60)
    print("  Demo completado.")
    print("=" * 60)


if __name__ == "__main__":
    main()
