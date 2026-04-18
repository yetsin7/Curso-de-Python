# =============================================================================
# ARCHIVO: 02_csv_json.py
# TEMA: Trabajar con archivos CSV y JSON
# =============================================================================
#
# CSV (Comma Separated Values) — formato tabular simple, como Excel en texto
# JSON (JavaScript Object Notation) — formato de datos estructurado, muy usado en APIs
#
# Python incluye módulos para ambos: csv y json
# =============================================================================

import csv
import json
import os

CARPETA = os.path.dirname(os.path.abspath(__file__))

def ruta(nombre):
    """Construye la ruta completa al archivo."""
    return os.path.join(CARPETA, nombre)


# ============================================================
# CSV — ESCRIBIR
# ============================================================

print("=== ARCHIVOS CSV ===\n")

# Datos de productos a guardar
productos = [
    {"id": 1, "nombre": "Laptop",  "precio": 999.99, "stock": 5},
    {"id": 2, "nombre": "Mouse",   "precio": 25.00,  "stock": 50},
    {"id": 3, "nombre": "Teclado", "precio": 45.00,  "stock": 30},
    {"id": 4, "nombre": "Monitor", "precio": 350.00, "stock": 8},
]

# Escribir con DictWriter (cada fila es un diccionario)
with open(ruta("productos.csv"), "w", newline="", encoding="utf-8") as f:
    campos = ["id", "nombre", "precio", "stock"]
    escritor = csv.DictWriter(f, fieldnames=campos)

    escritor.writeheader()    # escribe la fila de encabezados
    escritor.writerows(productos)   # escribe todas las filas

print("Archivo 'productos.csv' creado.")


# ============================================================
# CSV — LEER
# ============================================================

# Leer con DictReader — cada fila se convierte en un diccionario
with open(ruta("productos.csv"), "r", encoding="utf-8") as f:
    lector = csv.DictReader(f)
    productos_leidos = list(lector)

print(f"\nProductos leídos del CSV ({len(productos_leidos)} registros):")
for p in productos_leidos:
    # OJO: los valores del CSV son siempre strings — hay que convertir
    print(f"  {p['nombre']}: ${float(p['precio']):.2f} (stock: {p['stock']})")

# Calcular total del inventario
total_inventario = sum(
    float(p["precio"]) * int(p["stock"])
    for p in productos_leidos
)
print(f"\nValor total del inventario: ${total_inventario:,.2f}")


# ============================================================
# JSON — ESCRIBIR
# ============================================================

print("\n=== ARCHIVOS JSON ===\n")

# Estructura de datos de un usuario
usuario = {
    "id": 1,
    "nombre": "Ana García",
    "email": "ana@ejemplo.com",
    "edad": 28,
    "activo": True,
    "intereses": ["python", "diseño", "música"],
    "direccion": {
        "ciudad": "Buenos Aires",
        "pais": "Argentina"
    }
}

# json.dump() escribe al archivo (con indent para formato legible)
with open(ruta("usuario.json"), "w", encoding="utf-8") as f:
    json.dump(usuario, f, indent=2, ensure_ascii=False)

print("Archivo 'usuario.json' creado.")


# ============================================================
# JSON — LEER
# ============================================================

# json.load() lee del archivo y devuelve el objeto Python
with open(ruta("usuario.json"), "r", encoding="utf-8") as f:
    usuario_leido = json.load(f)

# Ya es un diccionario de Python, con los tipos correctos
print(f"\nNombre: {usuario_leido['nombre']}")
print(f"Edad: {usuario_leido['edad']} (tipo: {type(usuario_leido['edad']).__name__})")
print(f"Activo: {usuario_leido['activo']} (tipo: {type(usuario_leido['activo']).__name__})")
print(f"Ciudad: {usuario_leido['direccion']['ciudad']}")
print(f"Intereses: {', '.join(usuario_leido['intereses'])}")


# ============================================================
# JSON — LISTA DE OBJETOS (patrón tipo base de datos simple)
# ============================================================

def cargar_usuarios(archivo):
    """Carga la lista de usuarios desde un archivo JSON."""
    if not os.path.exists(archivo):
        return []
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_usuarios(archivo, usuarios):
    """Guarda la lista de usuarios en un archivo JSON."""
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=2, ensure_ascii=False)

def agregar_usuario(archivo, nuevo_usuario):
    """Agrega un usuario a la base de datos JSON."""
    usuarios = cargar_usuarios(archivo)
    nuevo_usuario["id"] = len(usuarios) + 1
    usuarios.append(nuevo_usuario)
    guardar_usuarios(archivo, usuarios)
    print(f"Usuario '{nuevo_usuario['nombre']}' agregado (ID: {nuevo_usuario['id']})")

archivo_usuarios = ruta("usuarios.json")

agregar_usuario(archivo_usuarios, {"nombre": "Carlos", "email": "carlos@ej.com"})
agregar_usuario(archivo_usuarios, {"nombre": "María",  "email": "maria@ej.com"})
agregar_usuario(archivo_usuarios, {"nombre": "Pedro",  "email": "pedro@ej.com"})

todos = cargar_usuarios(archivo_usuarios)
print(f"\nTotal de usuarios: {len(todos)}")
for u in todos:
    print(f"  [{u['id']}] {u['nombre']} — {u['email']}")


# ============================================================
# LIMPIEZA
# ============================================================

for nombre in ["productos.csv", "usuario.json", "usuarios.json"]:
    ruta_completa = ruta(nombre)
    if os.path.exists(ruta_completa):
        os.remove(ruta_completa)
        print(f"Archivo '{nombre}' eliminado.")
