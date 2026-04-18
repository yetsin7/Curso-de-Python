# =============================================================================
# CAPÍTULO 25 — Scripts, Herramientas y CLI
# Archivo: 04_scripts_utiles.py
# Tema: Colección de scripts útiles del mundo real
# =============================================================================
#
# Este archivo es una caja de herramientas con scripts que resuelven
# problemas reales que los desarrolladores enfrentan a diario.
#
# HERRAMIENTAS INCLUIDAS:
# 1. Buscador de archivos duplicados (por hash MD5)
# 2. Renombrador masivo de archivos con patrón
# 3. Organizador de descargas por extensión
# 4. Generador de contraseñas seguras
# 5. Conversor de unidades (peso, longitud, temperatura, datos)
#
# Sin dependencias externas — solo librería estándar de Python
# =============================================================================

import os
import sys
import hashlib
import secrets
import string
import shutil
from pathlib import Path
from collections import defaultdict

# =============================================================================
# MENÚ PRINCIPAL
# =============================================================================

def mostrar_menu():
    """Muestra el menú principal de herramientas disponibles."""
    print("\n" + "=" * 55)
    print(" CAJA DE HERRAMIENTAS PYTHON — Scripts del Mundo Real")
    print("=" * 55)
    print("  1. Buscador de archivos duplicados")
    print("  2. Renombrador masivo de archivos")
    print("  3. Organizador de descargas")
    print("  4. Generador de contraseñas")
    print("  5. Conversor de unidades")
    print("  0. Salir")
    print("=" * 55)


# =============================================================================
# HERRAMIENTA 1: Buscador de archivos duplicados
# =============================================================================

def calcular_hash_archivo(ruta, bloque_size=65536):
    """
    Calcula el hash MD5 de un archivo leyendo en bloques.
    Leer en bloques permite manejar archivos grandes sin cargarlos enteros en RAM.
    """
    md5 = hashlib.md5()
    try:
        with open(ruta, "rb") as f:
            while True:
                bloque = f.read(bloque_size)
                if not bloque:
                    break
                md5.update(bloque)
        return md5.hexdigest()
    except (PermissionError, OSError):
        return None


def buscar_duplicados(directorio, recursivo=True):
    """
    Encuentra archivos duplicados en un directorio comparando sus hashes MD5.

    El proceso:
    1. Agrupar archivos por tamaño (los duplicados DEBEN tener el mismo tamaño)
    2. Para grupos con el mismo tamaño, calcular el hash para confirmar
    3. Reportar los grupos de duplicados encontrados

    Parámetros:
        directorio: ruta del directorio a analizar
        recursivo: si True, analiza subdirectorios también
    """
    print(f"\nAnalizando: {directorio}")

    ruta = Path(directorio)
    if not ruta.is_dir():
        print(f"Error: '{directorio}' no es un directorio válido.")
        return {}

    # Paso 1: Agrupar por tamaño (rápido, sin calcular hashes aún)
    por_tamaño = defaultdict(list)

    patron = "**/*" if recursivo else "*"
    total_archivos = 0
    for archivo in ruta.glob(patron):
        if archivo.is_file():
            try:
                tamaño = archivo.stat().st_size
                if tamaño > 0:  # Ignorar archivos vacíos
                    por_tamaño[tamaño].append(archivo)
                    total_archivos += 1
            except OSError:
                continue

    print(f"Archivos analizados: {total_archivos}")

    # Solo comparar archivos del mismo tamaño
    candidatos = {t: archivos for t, archivos in por_tamaño.items() if len(archivos) > 1}
    n_candidatos = sum(len(v) for v in candidatos.values())
    print(f"Candidatos a duplicado (mismo tamaño): {n_candidatos}")

    # Paso 2: Calcular hashes para confirmar duplicados
    por_hash = defaultdict(list)
    calculados = 0

    for tamaño, archivos in candidatos.items():
        for archivo in archivos:
            hash_val = calcular_hash_archivo(archivo)
            if hash_val:
                por_hash[hash_val].append(archivo)
            calculados += 1
            if calculados % 100 == 0:
                print(f"  Procesados: {calculados}/{n_candidatos}", end="\r")

    # Filtrar solo los grupos con más de un archivo (duplicados reales)
    duplicados = {h: archivos for h, archivos in por_hash.items() if len(archivos) > 1}

    return duplicados


def herramienta_duplicados():
    """Interfaz para el buscador de duplicados."""
    print("\n--- BUSCADOR DE ARCHIVOS DUPLICADOS ---")
    directorio = input("Directorio a analizar (Enter = directorio actual): ").strip()
    if not directorio:
        directorio = "."

    recursivo_str = input("¿Buscar recursivamente? (s/n, Enter=s): ").strip().lower()
    recursivo = recursivo_str != "n"

    duplicados = buscar_duplicados(directorio, recursivo)

    if not duplicados:
        print("\nNo se encontraron archivos duplicados.")
        return

    # Calcular espacio desperdiciado
    espacio_total = 0
    n_grupos = len(duplicados)
    n_archivos_extra = 0

    print(f"\nGrupos de duplicados encontrados: {n_grupos}")
    print("=" * 60)

    for i, (hash_val, archivos) in enumerate(duplicados.items(), 1):
        tamaño = archivos[0].stat().st_size
        espacio_duplicado = tamaño * (len(archivos) - 1)
        espacio_total += espacio_duplicado
        n_archivos_extra += len(archivos) - 1

        print(f"\nGrupo {i} ({len(archivos)} archivos, {tamaño:,} bytes c/u):")
        for j, archivo in enumerate(archivos):
            marca = "  ✓ ORIGINAL" if j == 0 else "  ✗ DUPLICADO"
            print(f"  {marca}: {archivo}")

    # Resumen
    espacio_mb = espacio_total / (1024 * 1024)
    print("\n" + "=" * 60)
    print(f"Archivos extra (duplicados): {n_archivos_extra}")
    print(f"Espacio desperdiciado: {espacio_mb:.2f} MB")
    print("\nNota: Este script SOLO muestra los duplicados, no los elimina.")
    print("Revisa manualmente antes de borrar cualquier archivo.")


# =============================================================================
# HERRAMIENTA 2: Renombrador masivo de archivos
# =============================================================================

def herramienta_renombrador():
    """
    Renombra múltiples archivos según patrones configurables.
    Siempre muestra una vista previa antes de aplicar cambios.
    """
    print("\n--- RENOMBRADOR MASIVO DE ARCHIVOS ---")
    directorio = input("Directorio de archivos (Enter = actual): ").strip() or "."
    extension = input("Extensión a procesar (ej: .jpg, Enter = todas): ").strip()

    ruta = Path(directorio)
    if not ruta.is_dir():
        print(f"Error: '{directorio}' no es un directorio.")
        return

    # Obtener archivos
    patron = f"*{extension}" if extension else "*"
    archivos = sorted([f for f in ruta.glob(patron) if f.is_file()])

    if not archivos:
        print("No se encontraron archivos.")
        return

    print(f"\nArchivos encontrados: {len(archivos)}")
    print("\nModos de renombrado:")
    print("  1. Prefijo (añadir texto al inicio)")
    print("  2. Sufijo (añadir texto antes de la extensión)")
    print("  3. Numeración secuencial")
    print("  4. Reemplazar texto")
    modo = input("Modo (1-4): ").strip()

    # Generar nuevos nombres (vista previa primero)
    plan = []

    if modo == "1":
        prefijo = input("Prefijo a añadir: ")
        for archivo in archivos:
            nuevo = archivo.parent / f"{prefijo}{archivo.name}"
            plan.append((archivo, nuevo))

    elif modo == "2":
        sufijo = input("Sufijo a añadir (antes de la extensión): ")
        for archivo in archivos:
            stem = archivo.stem  # nombre sin extensión
            ext = archivo.suffix
            nuevo = archivo.parent / f"{stem}{sufijo}{ext}"
            plan.append((archivo, nuevo))

    elif modo == "3":
        inicio = int(input("Número inicial (Enter = 1): ").strip() or "1")
        ceros = int(input("Dígitos mínimos (Enter = 3): ").strip() or "3")
        base = input("Nombre base (Enter = 'archivo'): ").strip() or "archivo"
        for i, archivo in enumerate(archivos, inicio):
            ext = archivo.suffix
            nuevo_nombre = f"{base}_{str(i).zfill(ceros)}{ext}"
            nuevo = archivo.parent / nuevo_nombre
            plan.append((archivo, nuevo))

    elif modo == "4":
        buscar = input("Texto a buscar: ")
        reemplazar = input("Texto de reemplazo: ")
        for archivo in archivos:
            nuevo_nombre = archivo.name.replace(buscar, reemplazar)
            nuevo = archivo.parent / nuevo_nombre
            plan.append((archivo, nuevo))

    else:
        print("Modo no válido.")
        return

    # Vista previa
    print("\n" + "=" * 60)
    print("VISTA PREVIA (sin cambios aún):")
    print("=" * 60)
    cambios = [(v, n) for v, n in plan if v.name != n.name]

    if not cambios:
        print("Ningún archivo requiere cambios.")
        return

    for viejo, nuevo in cambios[:10]:  # Mostrar máximo 10
        print(f"  {viejo.name}")
        print(f"    → {nuevo.name}")

    if len(cambios) > 10:
        print(f"  ... y {len(cambios) - 10} archivos más")

    print(f"\nTotal de renombramientos: {len(cambios)}")

    confirmacion = input("\n¿Aplicar cambios? (escribe 'SI' para confirmar): ").strip()
    if confirmacion != "SI":
        print("Operación cancelada.")
        return

    # Aplicar renombramientos
    exitosos = 0
    errores = 0

    for viejo, nuevo in cambios:
        try:
            viejo.rename(nuevo)
            exitosos += 1
        except Exception as e:
            print(f"Error en {viejo.name}: {e}")
            errores += 1

    print(f"\nCompletado: {exitosos} renombrados, {errores} errores")


# =============================================================================
# HERRAMIENTA 3: Organizador de descargas
# =============================================================================

CATEGORIAS_EXTENSION = {
    "Imágenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
    "Documentos": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt"],
    "Texto": [".txt", ".md", ".rst", ".csv", ".log"],
    "Código": [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs"],
    "Comprimidos": [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2"],
    "Ejecutables": [".exe", ".msi", ".dmg", ".deb", ".rpm", ".sh"],
    "Datos": [".json", ".xml", ".yaml", ".yml", ".toml", ".sql", ".db"],
}


def herramienta_organizador():
    """
    Organiza archivos de un directorio moviéndolos a subcarpetas por tipo.
    Siempre pide confirmación antes de mover archivos.
    """
    print("\n--- ORGANIZADOR DE DESCARGAS ---")
    directorio = input("Directorio a organizar (Enter = actual): ").strip() or "."

    ruta = Path(directorio)
    if not ruta.is_dir():
        print(f"Error: '{directorio}' no es un directorio.")
        return

    # Clasificar archivos
    plan_movimiento = defaultdict(list)
    sin_categoria = []

    for archivo in ruta.iterdir():
        if not archivo.is_file():
            continue

        ext = archivo.suffix.lower()
        categorizado = False

        for categoria, extensiones in CATEGORIAS_EXTENSION.items():
            if ext in extensiones:
                plan_movimiento[categoria].append(archivo)
                categorizado = True
                break

        if not categorizado and ext:
            sin_categoria.append(archivo)

    # Vista previa
    total = sum(len(v) for v in plan_movimiento.values())
    print(f"\nPlan de organización ({total} archivos):")
    print("=" * 45)

    for categoria, archivos in sorted(plan_movimiento.items()):
        print(f"  {categoria}/")
        for archivo in archivos[:3]:
            print(f"    → {archivo.name}")
        if len(archivos) > 3:
            print(f"    ... y {len(archivos) - 3} más")

    if sin_categoria:
        print(f"\n  Otros/ (sin categoría): {len(sin_categoria)} archivos")

    if not total:
        print("Ningún archivo para organizar.")
        return

    confirmacion = input("\n¿Mover los archivos? (escribe 'SI' para confirmar): ").strip()
    if confirmacion != "SI":
        print("Operación cancelada.")
        return

    # Ejecutar movimientos
    for categoria, archivos in plan_movimiento.items():
        destino = ruta / categoria
        destino.mkdir(exist_ok=True)

        for archivo in archivos:
            destino_archivo = destino / archivo.name
            # Si ya existe, agregar sufijo numérico para no sobreescribir
            contador = 1
            while destino_archivo.exists():
                stem = archivo.stem
                ext = archivo.suffix
                destino_archivo = destino / f"{stem}_{contador}{ext}"
                contador += 1

            shutil.move(str(archivo), str(destino_archivo))

    print(f"\nOrganización completada. {total} archivos movidos.")


# =============================================================================
# HERRAMIENTA 4: Generador de contraseñas
# =============================================================================

def herramienta_contraseñas():
    """
    Genera contraseñas seguras usando el módulo `secrets`.
    `secrets` usa el generador de números aleatorios del SO (CSPRNG),
    seguro para aplicaciones criptográficas.
    """
    print("\n--- GENERADOR DE CONTRASEÑAS SEGURAS ---")
    print("Nota: Usa el módulo `secrets` (criptográficamente seguro)")

    try:
        longitud = int(input("Longitud de la contraseña (Enter = 16): ").strip() or "16")
        cantidad = int(input("Cantidad a generar (Enter = 5): ").strip() or "5")
    except ValueError:
        print("Error: ingresa números válidos.")
        return

    print("\nIncluir en la contraseña:")
    incluir_mayusculas = input("  ¿Mayúsculas? (s/n, Enter = s): ").strip().lower() != "n"
    incluir_minusculas = input("  ¿Minúsculas? (s/n, Enter = s): ").strip().lower() != "n"
    incluir_numeros = input("  ¿Números? (s/n, Enter = s): ").strip().lower() != "n"
    incluir_simbolos = input("  ¿Símbolos (!@#$...)? (s/n, Enter = s): ").strip().lower() != "n"

    # Construir conjunto de caracteres
    chars = ""
    if incluir_mayusculas:
        chars += string.ascii_uppercase
    if incluir_minusculas:
        chars += string.ascii_lowercase
    if incluir_numeros:
        chars += string.digits
    if incluir_simbolos:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if not chars:
        print("Error: debes incluir al menos un tipo de caracteres.")
        return

    print(f"\nContraseñas generadas (longitud={longitud}, "
          f"{len(chars)} caracteres posibles):")
    print("=" * 50)

    for i in range(cantidad):
        # secrets.choice es el equivalente seguro de random.choice
        pw = "".join(secrets.choice(chars) for _ in range(longitud))

        # Calcular entropía (bits de seguridad)
        import math
        entropia = math.log2(len(chars) ** longitud)

        print(f"  {i+1:2d}. {pw}  [{entropia:.0f} bits de entropía]")

    print("\nTips de seguridad:")
    print("  • Usa un gestor de contraseñas (Bitwarden, 1Password, KeePass)")
    print("  • Nunca reutilices contraseñas")
    print("  • Activa 2FA donde sea posible")


# =============================================================================
# HERRAMIENTA 5: Conversor de unidades
# =============================================================================

CONVERSIONES = {
    "longitud": {
        "metros": 1.0,
        "kilómetros": 1000.0,
        "centímetros": 0.01,
        "milímetros": 0.001,
        "pulgadas": 0.0254,
        "pies": 0.3048,
        "yardas": 0.9144,
        "millas": 1609.344,
    },
    "peso": {
        "kilogramos": 1.0,
        "gramos": 0.001,
        "miligramos": 0.000001,
        "toneladas": 1000.0,
        "libras": 0.453592,
        "onzas": 0.0283495,
    },
    "datos": {
        "bytes": 1.0,
        "kilobytes": 1024.0,
        "megabytes": 1024.0 ** 2,
        "gigabytes": 1024.0 ** 3,
        "terabytes": 1024.0 ** 4,
    }
}


def convertir_temperatura(valor, de, a):
    """
    Convierte entre Celsius, Fahrenheit y Kelvin.
    Las temperaturas no siguen la regla de la proporción simple —
    tienen fórmulas específicas de conversión.
    """
    # Primero convertir todo a Celsius como base
    if de == "fahrenheit":
        celsius = (valor - 32) * 5 / 9
    elif de == "kelvin":
        celsius = valor - 273.15
    else:
        celsius = valor

    # Luego convertir de Celsius al destino
    if a == "fahrenheit":
        return celsius * 9 / 5 + 32
    elif a == "kelvin":
        return celsius + 273.15
    else:
        return celsius


def herramienta_conversor():
    """Conversor interactivo de unidades de medida."""
    print("\n--- CONVERSOR DE UNIDADES ---")
    print("Tipos disponibles:")
    tipos = list(CONVERSIONES.keys()) + ["temperatura"]
    for i, tipo in enumerate(tipos, 1):
        print(f"  {i}. {tipo.capitalize()}")

    try:
        seleccion = int(input("\nTipo (número): ").strip()) - 1
        tipo = tipos[seleccion]
    except (ValueError, IndexError):
        print("Selección no válida.")
        return

    if tipo == "temperatura":
        unidades = ["celsius", "fahrenheit", "kelvin"]
    else:
        unidades = list(CONVERSIONES[tipo].keys())

    print(f"\nUnidades de {tipo}:")
    for i, u in enumerate(unidades, 1):
        print(f"  {i}. {u.capitalize()}")

    try:
        idx_origen = int(input("Unidad origen (número): ").strip()) - 1
        idx_destino = int(input("Unidad destino (número): ").strip()) - 1
        valor = float(input("Valor a convertir: ").strip())
    except (ValueError, IndexError):
        print("Entrada no válida.")
        return

    unidad_origen = unidades[idx_origen]
    unidad_destino = unidades[idx_destino]

    if tipo == "temperatura":
        resultado = convertir_temperatura(valor, unidad_origen, unidad_destino)
    else:
        # Convertir via la unidad base
        factor_origen = CONVERSIONES[tipo][unidad_origen]
        factor_destino = CONVERSIONES[tipo][unidad_destino]
        resultado = valor * factor_origen / factor_destino

    print(f"\n  {valor} {unidad_origen} = {resultado:.6g} {unidad_destino}")


# =============================================================================
# BUCLE PRINCIPAL DEL MENÚ
# =============================================================================

def main():
    """Punto de entrada del script. Ejecuta el menú principal en bucle."""
    print("\nBienvenido a la Caja de Herramientas Python")

    while True:
        mostrar_menu()
        opcion = input("Elige una herramienta (0-5): ").strip()

        if opcion == "0":
            print("\nHasta luego.")
            break
        elif opcion == "1":
            herramienta_duplicados()
        elif opcion == "2":
            herramienta_renombrador()
        elif opcion == "3":
            herramienta_organizador()
        elif opcion == "4":
            herramienta_contraseñas()
        elif opcion == "5":
            herramienta_conversor()
        else:
            print("Opción no válida. Elige entre 0 y 5.")

        input("\nPresiona Enter para volver al menú...")


if __name__ == "__main__":
    main()
