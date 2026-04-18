# =============================================================================
# ARCHIVO: 03_diccionarios.py
# TEMA: Diccionarios — almacenar datos por clave y valor
# =============================================================================
#
# Un diccionario almacena pares clave:valor.
# Es como un diccionario real: buscas por la "palabra" (clave) y obtienes
# la "definición" (valor).
#
# Características:
#   - Las claves son únicas (no puede haber dos "nombre")
#   - Los valores pueden ser cualquier tipo
#   - Acceso muy rápido por clave (más rápido que buscar en lista)
#   - Se define con llaves {}
#
# Es la estructura perfecta para representar objetos del mundo real.
# =============================================================================


# --- CREAR DICCIONARIOS ---

persona = {
    "nombre": "Ana García",
    "edad": 28,
    "ciudad": "Buenos Aires",
    "activo": True
}

producto = {
    "id": 101,
    "nombre": "Laptop Pro",
    "precio": 999.99,
    "stock": 15
}

vacio = {}   # diccionario vacío

print(persona)
print(type(persona))    # <class 'dict'>


# --- ACCEDER A VALORES ---

print(persona["nombre"])   # Ana García
print(persona["edad"])     # 28

# Con .get() — más seguro: devuelve None (o un valor por defecto) si la clave no existe
print(persona.get("ciudad"))           # Buenos Aires
print(persona.get("telefono"))         # None  (no da error)
print(persona.get("telefono", "N/A"))  # N/A   (valor por defecto)

# ❌ Esto daría KeyError si la clave no existe:
# print(persona["telefono"])   # KeyError: 'telefono'


# --- MODIFICAR Y AGREGAR ---

# Cambiar un valor existente
persona["edad"] = 29
print(persona["edad"])   # 29

# Agregar una nueva clave
persona["email"] = "ana@ejemplo.com"
print(persona)


# --- ELIMINAR ---

del persona["activo"]        # elimina la clave "activo"
print(persona)

eliminado = persona.pop("ciudad")    # elimina y devuelve el valor
print(f"Ciudad eliminada: {eliminado}")


# --- VERIFICAR SI UNA CLAVE EXISTE ---

if "nombre" in persona:
    print(f"El nombre es: {persona['nombre']}")

if "telefono" not in persona:
    print("No tiene teléfono registrado")


# --- RECORRER UN DICCIONARIO ---

alumno = {"nombre": "Carlos", "nota": 85, "aprobado": True}

# Recorrer solo las claves
for clave in alumno:
    print(clave)

# Recorrer solo los valores
for valor in alumno.values():
    print(valor)

# Recorrer claves y valores al mismo tiempo
for clave, valor in alumno.items():
    print(f"{clave}: {valor}")


# --- MÉTODOS ÚTILES ---

config = {"debug": True, "version": "1.0", "puerto": 8080}

print(config.keys())     # dict_keys(['debug', 'version', 'puerto'])
print(config.values())   # dict_values([True, '1.0', 8080])
print(config.items())    # dict_items([('debug', True), ...])
print(len(config))       # 3


# --- DICCIONARIOS ANIDADOS ---
# El valor de una clave puede ser otro diccionario.

usuarios = {
    "ana123": {
        "nombre": "Ana García",
        "email": "ana@ejemplo.com",
        "rol": "admin"
    },
    "carlos99": {
        "nombre": "Carlos López",
        "email": "carlos@ejemplo.com",
        "rol": "usuario"
    }
}

# Acceder a datos anidados
print(usuarios["ana123"]["nombre"])     # Ana García
print(usuarios["carlos99"]["email"])    # carlos@ejemplo.com

# Recorrer usuarios
for username, datos in usuarios.items():
    print(f"\nUsuario: {username}")
    for campo, valor in datos.items():
        print(f"  {campo}: {valor}")


# --- LISTA DE DICCIONARIOS (patrón muy común) ---
# Representa una tabla de datos: cada elemento es un "registro".

inventario = [
    {"id": 1, "producto": "Laptop",  "precio": 999.99, "stock": 5},
    {"id": 2, "producto": "Mouse",   "precio": 25.00,  "stock": 50},
    {"id": 3, "producto": "Teclado", "precio": 45.00,  "stock": 30},
]

# Buscar producto por nombre
def buscar_producto(nombre):
    """Busca y devuelve un producto por su nombre."""
    for item in inventario:
        if item["producto"].lower() == nombre.lower():
            return item
    return None

encontrado = buscar_producto("mouse")
if encontrado:
    print(f"\nProducto: {encontrado['producto']}")
    print(f"Precio: ${encontrado['precio']}")
    print(f"Stock: {encontrado['stock']} unidades")
