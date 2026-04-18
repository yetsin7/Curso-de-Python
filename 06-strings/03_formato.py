# =============================================================================
# ARCHIVO: 03_formato.py
# TEMA: Formato de strings — f-strings, format() y concatenación
# =============================================================================
#
# Existen varias formas de insertar valores dentro de strings.
# La más moderna y recomendada es el f-string (desde Python 3.6).
# =============================================================================

nombre = "Ana"
edad = 28
precio = 1234.5678

# --- FORMA 1: Concatenación con + ---
# Funciona pero es verbose y poco legible. Requiere convertir a str.

print("Hola, " + nombre + ". Tienes " + str(edad) + " años.")

# ❌ No recomendado para strings complejos


# --- FORMA 2: .format() ---
# Más flexible que la concatenación. Usa {} como marcadores de posición.

print("Hola, {}. Tienes {} años.".format(nombre, edad))

# Con índices (para reusar o cambiar orden)
print("Hola, {0}. {0} tiene {1} años.".format(nombre, edad))

# Con nombres
print("Hola, {nombre}. Tienes {edad} años.".format(nombre=nombre, edad=edad))

# Todavía se ve en código antiguo, pero f-strings es mejor.


# --- FORMA 3: f-strings (RECOMENDADA) ---
# Pones una f antes de las comillas y usas {} directamente en el string.
# Es la forma más moderna, legible y eficiente.

print(f"Hola, {nombre}. Tienes {edad} años.")

# Puedes poner expresiones y operaciones dentro de {}
print(f"En 10 años tendrás {edad + 10} años.")
print(f"Tu nombre en mayúsculas: {nombre.upper()}")
print(f"2 + 2 = {2 + 2}")

# Acceso a elementos de listas y diccionarios
frutas = ["manzana", "banana"]
persona = {"nombre": "Carlos", "ciudad": "Lima"}

print(f"Primera fruta: {frutas[0]}")
print(f"Ciudad: {persona['ciudad']}")   # usa comillas simples dentro del {}


# --- FORMATO NUMÉRICO CON f-strings ---

# Decimales: :.2f = 2 decimales
print(f"Precio: ${precio:.2f}")         # $1234.57

# Separador de miles: :,.2f
print(f"Precio: ${precio:,.2f}")        # $1,234.57

# Porcentaje: :.1% — multiplica por 100 y agrega %
tasa = 0.1875
print(f"Tasa: {tasa:.1%}")              # 18.8%

# Sin decimales: :.0f
print(f"Precio redondeado: ${precio:.0f}")   # $1235

# Notación científica: :.2e
grande = 12345678.9
print(f"Notación científica: {grande:.2e}")   # 1.23e+07

# Anchura mínima: :10 = al menos 10 caracteres
print(f"|{'hola':10}|")    # |hola      |
print(f"|{'hola':>10}|")   # |      hola|  (alineado a la derecha)
print(f"|{'hola':^10}|")   # |   hola   |  (centrado)
print(f"|{'hola':-^10}|")  # |---hola---|  (centrado con relleno -)


# --- EJEMPLO PRÁCTICO: tabla de productos ---

productos = [
    ("Laptop",   999.99,  5),
    ("Mouse",     25.00, 50),
    ("Teclado",   45.50, 30),
    ("Monitor",  350.00, 10),
]

print("\n" + "=" * 45)
print(f"{'PRODUCTO':<12} {'PRECIO':>10} {'STOCK':>8} {'TOTAL':>10}")
print("=" * 45)

for nombre_p, precio_p, stock_p in productos:
    total = precio_p * stock_p
    print(f"{nombre_p:<12} ${precio_p:>9,.2f} {stock_p:>8} ${total:>9,.2f}")

print("=" * 45)


# --- RAW STRINGS (r"...") ---
# A veces no quieres que Python interprete los caracteres especiales.
# Útil para rutas de Windows y expresiones regulares.

ruta_normal = "C:\\Users\\Ana\\Documentos"       # necesita doble \\
ruta_raw    = r"C:\Users\Ana\Documentos"          # r"" lo trata literalmente
print(ruta_normal)
print(ruta_raw)
# Ambas imprimen: C:\Users\Ana\Documentos
