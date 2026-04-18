# =============================================================================
# ARCHIVO: 01_leer_escribir.py
# TEMA: Leer y escribir archivos de texto
# =============================================================================
#
# REGLA DE ORO: siempre usa encoding="utf-8" para manejar correctamente
# tildes, ñ y caracteres especiales del español.
# =============================================================================

import os

# Ruta donde guardaremos los archivos de prueba (misma carpeta)
CARPETA = os.path.dirname(os.path.abspath(__file__))

def ruta(nombre_archivo):
    """Construye la ruta completa al archivo dentro de la carpeta actual."""
    return os.path.join(CARPETA, nombre_archivo)


# ============================================================
# ESCRIBIR UN ARCHIVO (modo "w" — sobreescribe si ya existe)
# ============================================================

with open(ruta("notas.txt"), "w", encoding="utf-8") as archivo:
    archivo.write("Primera línea del archivo\n")
    archivo.write("Segunda línea con acentos: café, niño\n")
    archivo.write("Tercera línea\n")

print("Archivo 'notas.txt' creado.")


# ============================================================
# LEER UN ARCHIVO COMPLETO
# ============================================================

# read() → devuelve todo el contenido como un solo string
with open(ruta("notas.txt"), "r", encoding="utf-8") as archivo:
    contenido = archivo.read()

print("=== Contenido completo ===")
print(contenido)


# ============================================================
# LEER LÍNEA POR LÍNEA
# ============================================================

# readline() → lee una línea a la vez
with open(ruta("notas.txt"), "r", encoding="utf-8") as archivo:
    linea1 = archivo.readline()
    linea2 = archivo.readline()
    print(f"Primera línea: {linea1.strip()}")
    print(f"Segunda línea: {linea2.strip()}")

# readlines() → devuelve una lista con todas las líneas
with open(ruta("notas.txt"), "r", encoding="utf-8") as archivo:
    lineas = archivo.readlines()

print(f"\nTotal de líneas: {len(lineas)}")
for i, linea in enumerate(lineas, 1):
    print(f"  {i}: {linea.strip()}")

# Forma más eficiente: iterar directamente sobre el archivo
with open(ruta("notas.txt"), "r", encoding="utf-8") as archivo:
    for linea in archivo:
        print(linea.strip())   # strip() elimina el \n al final


# ============================================================
# AGREGAR AL FINAL (modo "a" — append)
# ============================================================

with open(ruta("notas.txt"), "a", encoding="utf-8") as archivo:
    archivo.write("Línea agregada al final\n")
    archivo.write("Otra línea más\n")

print("\nSe agregaron líneas al final.")


# ============================================================
# VERIFICAR SI UN ARCHIVO EXISTE
# ============================================================

if os.path.exists(ruta("notas.txt")):
    print("El archivo existe")
    print(f"Tamaño: {os.path.getsize(ruta('notas.txt'))} bytes")


# ============================================================
# MANEJO DE ERRORES AL LEER ARCHIVOS
# ============================================================

def leer_archivo_seguro(nombre):
    """Lee un archivo de texto de forma segura."""
    try:
        with open(nombre, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: el archivo '{nombre}' no existe")
        return None
    except PermissionError:
        print(f"Error: sin permisos para leer '{nombre}'")
        return None

contenido = leer_archivo_seguro(ruta("notas.txt"))
contenido_nulo = leer_archivo_seguro(ruta("no_existe.txt"))


# ============================================================
# ESCRIBIR MÚLTIPLES LÍNEAS CON writelines()
# ============================================================

lista_de_compras = [
    "Leche\n",
    "Pan\n",
    "Huevos\n",
    "Café\n",
    "Azúcar\n"
]

with open(ruta("compras.txt"), "w", encoding="utf-8") as f:
    f.writelines(lista_de_compras)

print("\nArchivo 'compras.txt' creado con la lista de compras.")

# Leer y mostrar
with open(ruta("compras.txt"), "r", encoding="utf-8") as f:
    print(f.read())


# ============================================================
# LIMPIEZA — eliminar los archivos de prueba
# ============================================================

for nombre in ["notas.txt", "compras.txt"]:
    ruta_completa = ruta(nombre)
    if os.path.exists(ruta_completa):
        os.remove(ruta_completa)
        print(f"Archivo '{nombre}' eliminado.")
