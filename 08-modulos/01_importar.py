# =============================================================================
# ARCHIVO: 01_importar.py
# TEMA: Formas de importar módulos en Python
# =============================================================================


# --- FORMA 1: import módulo ---
# Importa el módulo completo. Para usar algo, debes escribir modulo.función().

import math

print(math.pi)             # 3.141592653589793
print(math.sqrt(25))       # 5.0
print(math.floor(3.7))     # 3  (redondea hacia abajo)
print(math.ceil(3.2))      # 4  (redondea hacia arriba)


# --- FORMA 2: from módulo import algo ---
# Importa solo lo que necesitas. Puedes usarlo directamente sin el prefijo.

from math import sqrt, pi

print(sqrt(16))    # 4.0  (sin escribir math.sqrt)
print(pi)          # 3.14...

# Esto es más cómodo pero puede causar conflictos de nombres si
# dos módulos tienen funciones con el mismo nombre.


# --- FORMA 3: import módulo as alias ---
# Útil cuando el nombre del módulo es largo o existe convención de uso.

import datetime as dt
import random as rnd

hoy = dt.date.today()
print(hoy)

numero = rnd.randint(1, 10)
print(numero)

# Convenciones populares:
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt


# --- FORMA 4: from módulo import * ---
# Importa TODO el módulo directamente al espacio de nombres.
# ❌ No recomendado: puede sobreescribir funciones existentes y
#    hace difícil saber de dónde viene cada función.

# from math import *   # evita esto
# print(sqrt(9))       # funciona pero no está claro de dónde viene


# --- IMPORTAR MÓDULOS PROPIOS ---
# Si tienes un archivo Python en la misma carpeta, puedes importarlo.
# Ver archivo 03_modulo_propio.py para el ejemplo completo.

# from mis_utilidades import saludar, calcular_iva


# --- VERIFICAR QUÉ CONTIENE UN MÓDULO ---
# dir(módulo) lista todas las funciones y variables disponibles.

import random
print(dir(random))     # lista larga con todo lo que ofrece el módulo

# help(módulo) muestra la documentación completa
# help(random)   # descomenta para ver (es bastante largo)
# help(random.randint)  # documentación de una función específica
