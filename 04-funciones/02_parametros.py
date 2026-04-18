# =============================================================================
# ARCHIVO: 02_parametros.py
# TEMA: Parámetros y argumentos — pasar datos a las funciones
# =============================================================================
#
# PARÁMETRO → la variable en la definición de la función (el "molde")
# ARGUMENTO → el valor real que pasas al llamar la función
#
# def saludar(nombre):    ← 'nombre' es el PARÁMETRO
#     print(nombre)
#
# saludar("Ana")          ← "Ana" es el ARGUMENTO
# =============================================================================


# --- MÚLTIPLES PARÁMETROS ---

def presentar(nombre, edad, ciudad):
    """Presenta a una persona con sus datos básicos."""
    print(f"Me llamo {nombre}, tengo {edad} años y vivo en {ciudad}.")

presentar("Ana", 25, "Buenos Aires")
presentar("Carlos", 30, "Madrid")


# --- ARGUMENTOS POR POSICIÓN vs. POR NOMBRE ---

# Por posición: el orden importa
presentar("Lucía", 22, "Lima")         # nombre=Lucía, edad=22, ciudad=Lima

# Por nombre (keyword arguments): el orden NO importa
presentar(ciudad="México", nombre="Pedro", edad=28)


# --- PARÁMETROS CON VALORES POR DEFECTO ---
# Si no pasas un argumento, se usa el valor por defecto.

def saludar(nombre, saludo="Hola"):
    """Saluda a una persona. El saludo por defecto es 'Hola'."""
    print(f"{saludo}, {nombre}!")

saludar("Ana")                    # Hola, Ana!   (usa el valor por defecto)
saludar("Carlos", "Buenos días")  # Buenos días, Carlos!  (usa el argumento)
saludar("María", saludo="Hey")    # Hey, María!


# --- PARÁMETROS OPCIONALES AL FINAL ---
# Los parámetros con valor por defecto siempre van al final de la lista.

def crear_usuario(nombre, rol="usuario", activo=True):
    """Crea un usuario con valores por defecto para rol y estado."""
    print(f"Usuario: {nombre} | Rol: {rol} | Activo: {activo}")

crear_usuario("Ana")
crear_usuario("Carlos", "admin")
crear_usuario("María", "moderador", False)
crear_usuario("Pedro", activo=False)    # omite rol, cambia activo


# --- *args: número variable de argumentos ---
# Cuando no sabes cuántos argumentos recibirás, usa *args.
# Python los empaqueta como una tupla.

def sumar(*numeros):
    """Suma todos los números que se pasen como argumentos."""
    total = 0
    for numero in numeros:
        total += numero
    return total

print(sumar(1, 2))             # 3
print(sumar(1, 2, 3, 4, 5))   # 15
print(sumar(10))               # 10


# --- **kwargs: argumentos con nombre variables ---
# Para recibir un número variable de argumentos con nombre.
# Python los empaqueta como un diccionario.

def mostrar_info(**datos):
    """Muestra cualquier cantidad de datos con su nombre."""
    for clave, valor in datos.items():
        print(f"  {clave}: {valor}")

mostrar_info(nombre="Ana", edad=25, ciudad="Lima")
mostrar_info(producto="Laptop", precio=999.99, stock=5, disponible=True)


# --- EJEMPLO PRÁCTICO ---

def calcular_precio(precio_base, descuento=0, impuesto=0.19):
    """
    Calcula el precio final aplicando descuento e impuesto.

    precio_base: precio original del producto
    descuento: fracción de descuento (0.10 = 10%)
    impuesto: fracción de impuesto (por defecto 19% IVA)
    """
    precio_con_descuento = precio_base * (1 - descuento)
    precio_final = precio_con_descuento * (1 + impuesto)
    return precio_final

print(calcular_precio(100))               # sin descuento, con IVA
print(calcular_precio(100, 0.10))         # con 10% descuento, con IVA
print(calcular_precio(100, 0.10, 0))      # con descuento, sin IVA
