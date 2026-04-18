# =============================================================================
# ARCHIVO: 02_tuplas.py
# TEMA: Tuplas — colecciones ordenadas e inmutables
# =============================================================================
#
# Una tupla es como una lista, PERO NO SE PUEDE MODIFICAR después de creada.
# Se define con paréntesis () en lugar de corchetes [].
#
# ¿Por qué usar tuplas si ya tenemos listas?
#   - Comunicar intención: "estos datos no deben cambiar"
#   - Son más eficientes en memoria que las listas
#   - Se pueden usar como claves en diccionarios (las listas no)
#   - Múltiples retornos de funciones son tuplas por defecto
# =============================================================================


# --- CREAR TUPLAS ---

coordenadas = (10.5, -3.2)           # coordenada GPS
color_rojo = (255, 0, 0)              # color RGB
dias_semana = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")
mixta = (42, "hola", True)
vacia = ()

# También se puede sin paréntesis (el separador es la coma)
punto = 3, 5
print(punto)          # (3, 5)
print(type(punto))    # <class 'tuple'>

# Tupla de un solo elemento (la coma es OBLIGATORIA)
un_elemento = (42,)   # ← la coma lo hace tupla
no_es_tupla = (42)    # ← sin coma, es solo el número 42 entre paréntesis
print(type(un_elemento))   # <class 'tuple'>
print(type(no_es_tupla))   # <class 'int'>


# --- ACCEDER A ELEMENTOS ---
# Igual que en las listas, con índices.

print(color_rojo[0])     # 255
print(color_rojo[-1])    # 0
print(dias_semana[2])    # Mié

# Slicing también funciona
print(dias_semana[:5])   # ('Lun', 'Mar', 'Mié', 'Jue', 'Vie')


# --- LAS TUPLAS SON INMUTABLES ---
# No puedes agregar, eliminar ni modificar elementos.

# ❌ Esto daría error (descomenta para ver el error):
# color_rojo[0] = 100    # TypeError: 'tuple' object does not support item assignment


# --- DESEMPAQUETADO DE TUPLAS ---
# Una de las características más útiles de las tuplas.

x, y = coordenadas
print(f"X: {x}, Y: {y}")

r, g, b = color_rojo
print(f"Rojo: {r}, Verde: {g}, Azul: {b}")

# Intercambiar variables (truco de Python usando tuplas)
a = 10
b = 20
a, b = b, a    # swap en una línea — internamente Python usa una tupla
print(f"a={a}, b={b}")    # a=20, b=10


# --- TUPLAS COMO RETORNO DE FUNCIONES ---

def obtener_dimensiones(rectangulo):
    """Devuelve el ancho y alto de un rectángulo como tupla."""
    return rectangulo["ancho"], rectangulo["alto"]   # retorna tupla

rect = {"ancho": 100, "alto": 50}
ancho, alto = obtener_dimensiones(rect)   # desempaqueta la tupla
print(f"Ancho: {ancho}, Alto: {alto}")


# --- MÉTODOS DE TUPLAS ---
# Las tuplas solo tienen 2 métodos (porque son inmutables)

nums = (3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5)

print(nums.count(5))    # 3  → cuántas veces aparece el 5
print(nums.index(9))    # 5  → en qué índice está el 9


# --- CONVERTIR ENTRE LISTA Y TUPLA ---

lista = [1, 2, 3, 4, 5]
tupla = tuple(lista)
print(type(tupla))    # <class 'tuple'>

de_vuelta = list(tupla)
print(type(de_vuelta))   # <class 'list'>


# --- EJEMPLO PRÁCTICO: datos que no deben cambiar ---

# Configuración de la aplicación — no debe modificarse en tiempo de ejecución
COLORES_PERMITIDOS = ("rojo", "azul", "verde", "negro", "blanco")
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")

def nombre_mes(numero):
    """Devuelve el nombre del mes dado su número (1-12)."""
    if 1 <= numero <= 12:
        return MESES[numero - 1]
    return "Mes inválido"

print(nombre_mes(3))    # marzo
print(nombre_mes(12))   # diciembre
