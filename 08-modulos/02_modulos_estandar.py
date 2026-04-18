# =============================================================================
# ARCHIVO: 02_modulos_estandar.py
# TEMA: Módulos estándar más útiles — vienen con Python, sin instalar nada
# =============================================================================


# ================================================================
# MÓDULO: math — operaciones matemáticas avanzadas
# ================================================================
import math

print("=== math ===")
print(math.sqrt(144))        # 12.0  → raíz cuadrada
print(math.pow(2, 10))       # 1024.0 → potencia
print(math.log(100, 10))     # 2.0   → logaritmo base 10
print(math.factorial(5))     # 120   → 5! = 5×4×3×2×1
print(math.pi)               # 3.14159...
print(math.e)                # 2.71828... (número de Euler)
print(math.abs(-5))          # 5   (valor absoluto — también funciona con abs(-5))
print(math.gcd(12, 8))       # 4   → máximo común divisor


# ================================================================
# MÓDULO: random — números y selecciones aleatorias
# ================================================================
import random

print("\n=== random ===")

# Número entero aleatorio entre a y b (inclusivos)
print(random.randint(1, 100))

# Número decimal entre 0.0 y 1.0
print(random.random())

# Número decimal en un rango
print(random.uniform(1.5, 9.5))

# Elemento aleatorio de una lista
frutas = ["manzana", "banana", "naranja", "uva"]
print(random.choice(frutas))

# Muestra aleatoria de N elementos (sin repetir)
print(random.sample(frutas, 2))

# Mezclar una lista en el lugar
numeros = [1, 2, 3, 4, 5]
random.shuffle(numeros)
print(numeros)

# Fijar la semilla (para resultados reproducibles — útil en pruebas)
random.seed(42)
print(random.randint(1, 100))   # siempre dará el mismo resultado con seed=42


# ================================================================
# MÓDULO: datetime — fechas y horas
# ================================================================
from datetime import datetime, date, timedelta

print("\n=== datetime ===")

# Fecha y hora actual
ahora = datetime.now()
print(ahora)
print(ahora.year, ahora.month, ahora.day)
print(ahora.hour, ahora.minute, ahora.second)

# Solo la fecha actual
hoy = date.today()
print(f"Hoy es: {hoy}")
print(f"Año: {hoy.year}, Mes: {hoy.month}, Día: {hoy.day}")

# Crear una fecha específica
cumpleanos = date(1995, 7, 15)
print(f"Cumpleaños: {cumpleanos}")

# Diferencia entre fechas
dias_vividos = hoy - cumpleanos
print(f"Días vividos: {dias_vividos.days}")

# Sumar/restar tiempo con timedelta
manana = hoy + timedelta(days=1)
hace_una_semana = hoy - timedelta(weeks=1)
print(f"Mañana: {manana}")
print(f"Hace una semana: {hace_una_semana}")

# Formatear fecha como texto
print(ahora.strftime("%d/%m/%Y %H:%M"))     # 15/07/2024 14:30
print(ahora.strftime("%A, %d de %B de %Y")) # Monday, 15 de July de 2024


# ================================================================
# MÓDULO: os — interactuar con el sistema operativo
# ================================================================
import os

print("\n=== os ===")

# Directorio de trabajo actual
print(os.getcwd())

# Listar archivos y carpetas
# print(os.listdir("."))   # descomenta para ver

# Verificar si un archivo o carpeta existe
print(os.path.exists("README.md"))

# Combinar rutas de forma correcta (multiplataforma)
ruta = os.path.join("carpeta", "subcarpeta", "archivo.txt")
print(ruta)   # carpeta/subcarpeta/archivo.txt  (o \ en Windows)

# Separar nombre de archivo y extensión
nombre, extension = os.path.splitext("documento.pdf")
print(f"Nombre: {nombre}, Extensión: {extension}")

# Nombre del sistema operativo
print(os.name)   # 'nt' en Windows, 'posix' en Linux/Mac


# ================================================================
# MÓDULO: sys — información del intérprete Python
# ================================================================
import sys

print("\n=== sys ===")
print(sys.version)          # versión de Python
print(sys.platform)         # plataforma: 'win32', 'linux', 'darwin'

# sys.exit() terminaría el programa — no lo llamamos aquí


# ================================================================
# MÓDULO: json — leer y escribir JSON
# ================================================================
import json

print("\n=== json ===")

# Convertir diccionario Python a string JSON
datos = {"nombre": "Ana", "edad": 28, "activo": True, "notas": [8, 9, 7]}
json_string = json.dumps(datos, indent=2, ensure_ascii=False)
print(json_string)

# Convertir string JSON a diccionario Python
texto_json = '{"ciudad": "Lima", "pais": "Peru"}'
diccionario = json.loads(texto_json)
print(diccionario["ciudad"])   # Lima
