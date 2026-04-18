# =============================================================================
# ARCHIVO: 03_retorno.py
# TEMA: return — devolver resultados desde una función
# =============================================================================
#
# La mayoría de las funciones no solo "hacen cosas", sino que CALCULAN algo
# y lo devuelven al código que las llamó.
#
# Para devolver un valor se usa 'return'.
# El valor devuelto puede guardarse en una variable o usarse directamente.
#
# Si una función no tiene return (o tiene solo 'return' sin valor),
# devuelve None automáticamente.
# =============================================================================


# --- FUNCIÓN CON RETURN ---

def cuadrado(numero):
    """Devuelve el cuadrado de un número."""
    resultado = numero ** 2
    return resultado   # envía el resultado al código que llamó esta función

# Guardar el resultado en una variable:
area = cuadrado(5)
print(area)         # 25

# Usar el resultado directamente:
print(cuadrado(4))  # 16

# Usar el resultado en una expresión:
total = cuadrado(3) + cuadrado(4)
print(total)        # 9 + 16 = 25


# --- RETURN SALE DE LA FUNCIÓN INMEDIATAMENTE ---
# Todo código después del return NO se ejecuta.

def es_positivo(numero):
    """Indica si un número es positivo."""
    if numero > 0:
        return True    # sale aquí si es positivo
    return False       # llega aquí solo si no era positivo

print(es_positivo(5))    # True
print(es_positivo(-3))   # False
print(es_positivo(0))    # False


# --- RETORNAR MÚLTIPLES VALORES ---
# Python permite devolver varios valores separados por coma.
# Técnicamente devuelve una tupla.

def minmax(lista):
    """Devuelve el mínimo y el máximo de una lista."""
    return min(lista), max(lista)

numeros = [3, 1, 7, 2, 9, 4]
minimo, maximo = minmax(numeros)    # desempaquetado de tupla
print(f"Mínimo: {minimo}, Máximo: {maximo}")


# --- FUNCIÓN SIN RETURN → devuelve None ---

def imprimir_saludo(nombre):
    """Imprime un saludo. No devuelve nada."""
    print(f"Hola, {nombre}!")

resultado = imprimir_saludo("Ana")   # ejecuta la función
print(resultado)                     # None — no hay return


# --- EJEMPLO PRÁCTICO: funciones que se llaman entre sí ---

def calcular_iva(precio, tasa=0.19):
    """Calcula el monto del IVA de un precio."""
    return precio * tasa

def calcular_total(precio):
    """Calcula el precio total con IVA incluido."""
    iva = calcular_iva(precio)   # llama a otra función y usa su resultado
    return precio + iva

def mostrar_factura(nombre_producto, precio_base):
    """Muestra una factura simple con precio base, IVA y total."""
    iva = calcular_iva(precio_base)
    total = calcular_total(precio_base)

    print(f"\nProducto:    {nombre_producto}")
    print(f"Precio base: ${precio_base:.2f}")
    print(f"IVA (19%):   ${iva:.2f}")
    print(f"Total:       ${total:.2f}")

mostrar_factura("Laptop", 800.00)
mostrar_factura("Mouse inalámbrico", 25.99)


# --- FUNCIÓN QUE VALIDA Y DEVUELVE None COMO SEÑAL ---

def dividir(a, b):
    """
    Divide a entre b.
    Devuelve None si b es 0 (división imposible).
    """
    if b == 0:
        print("Error: no se puede dividir entre cero")
        return None    # señal de que algo salió mal
    return a / b

resultado = dividir(10, 2)
if resultado is not None:
    print(f"Resultado: {resultado}")

resultado = dividir(5, 0)
if resultado is None:
    print("La división falló")
