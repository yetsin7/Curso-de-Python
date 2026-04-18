# =============================================================================
# CAPÍTULO 22 — Data Science con Python
# Archivo: 01_numpy_basico.py
# Tema: NumPy — La base del cálculo numérico en Python
# =============================================================================
#
# NumPy (Numerical Python) es la librería fundamental para computación
# científica en Python. Introduce el tipo ndarray: un array N-dimensional
# que almacena elementos del MISMO tipo en memoria contigua.
#
# ¿Por qué NumPy en vez de listas Python?
#   - Las listas Python son lentas para matemáticas: cada elemento es un
#     objeto Python con overhead de memoria
#   - NumPy almacena datos en C por debajo: sin overhead, memoria contigua
#   - Las operaciones vectorizadas corren en C, no en el intérprete Python
#   - Resultado: 10x - 100x más rápido para cálculos numéricos
# =============================================================================

# Intentamos importar NumPy; si falla, explicamos cómo instalarlo
try:
    import numpy as np
except ImportError:
    print("NumPy no está instalado.")
    print("Instálalo con: pip install numpy")
    exit(1)

print("=" * 60)
print("NUMPY BÁSICO — Arrays, operaciones y álgebra lineal")
print("=" * 60)

# =============================================================================
# SECCIÓN 1: Arrays vs Listas Python
# =============================================================================
print("\n--- 1. Arrays vs Listas Python ---")

# Lista Python normal — puede mezclar tipos, pero es lenta para matemáticas
lista_python = [1, 2, 3, 4, 5]

# Array NumPy — homogéneo, almacenado en C, ultra-rápido
array_numpy = np.array([1, 2, 3, 4, 5])

print(f"Lista Python: {lista_python}")
print(f"Array NumPy:  {array_numpy}")

# Demostración de velocidad conceptual: multiplicar cada elemento por 2
# Con lista: necesitas un bucle o comprensión
resultado_lista = [x * 2 for x in lista_python]

# Con NumPy: operación vectorizada — multiplica TODO el array de una vez
# internamente usa código C optimizado, sin bucle en Python
resultado_array = array_numpy * 2

print(f"Lista x2 (comprensión): {resultado_lista}")
print(f"Array x2 (vectorizado): {resultado_array}")

# =============================================================================
# SECCIÓN 2: Tipos de datos (dtype) — Por qué importan
# =============================================================================
print("\n--- 2. Tipos de datos (dtype) ---")

# NumPy elige el dtype automáticamente según los datos
arr_enteros = np.array([1, 2, 3])
arr_flotantes = np.array([1.0, 2.5, 3.7])
arr_bool = np.array([True, False, True])

print(f"Enteros - dtype: {arr_enteros.dtype}")    # int64 en la mayoría de sistemas
print(f"Flotantes - dtype: {arr_flotantes.dtype}") # float64
print(f"Booleanos - dtype: {arr_bool.dtype}")      # bool

# También puedes especificar el dtype manualmente
# Útil para ahorrar memoria (ej: int8 en vez de int64 para números pequeños)
arr_float32 = np.array([1, 2, 3], dtype=np.float32)
print(f"Float32 explícito: {arr_float32}, dtype: {arr_float32.dtype}")

# =============================================================================
# SECCIÓN 3: Shape y Reshape — Dimensiones del array
# =============================================================================
print("\n--- 3. Shape y Reshape ---")

# Shape indica las dimensiones: (filas, columnas) para 2D
arr_1d = np.array([1, 2, 3, 4, 5, 6])
print(f"Array 1D: {arr_1d}")
print(f"Shape: {arr_1d.shape}")  # (6,) — un eje de longitud 6

# Reshape: reorganizar los datos en otra forma
# El total de elementos debe mantenerse igual (6 = 2*3 = 3*2)
arr_2d = arr_1d.reshape(2, 3)  # 2 filas, 3 columnas
print(f"\nArray 2D (2x3):\n{arr_2d}")
print(f"Shape: {arr_2d.shape}")  # (2, 3)

arr_3d = arr_1d.reshape(2, 3, 1)  # 3 dimensiones
print(f"\nArray 3D (2x3x1) shape: {arr_3d.shape}")

# -1 como comodín: NumPy calcula esa dimensión automáticamente
arr_auto = arr_1d.reshape(3, -1)  # 3 filas, NumPy calcula que son 2 columnas
print(f"\nReshape con -1 (3, -1):\n{arr_auto}")

# =============================================================================
# SECCIÓN 4: Creación de arrays especiales
# =============================================================================
print("\n--- 4. Arrays especiales ---")

# np.zeros — array lleno de ceros (útil para inicializar)
ceros = np.zeros((3, 4))
print(f"Zeros (3x4):\n{ceros}")

# np.ones — array lleno de unos
unos = np.ones((2, 3))
print(f"\nOnes (2x3):\n{unos}")

# np.arange — como range() pero devuelve un array (inicio, fin, paso)
rango = np.arange(0, 10, 2)
print(f"\nArange (0 a 10, paso 2): {rango}")

# np.linspace — N puntos equidistantes entre inicio y fin (incluye el fin)
# Muy útil para graficar funciones continuas
linspace = np.linspace(0, 1, 5)
print(f"Linspace (0 a 1, 5 puntos): {linspace}")

# np.eye — matriz identidad (diagonal de 1s)
identidad = np.eye(3)
print(f"\nMatriz identidad 3x3:\n{identidad}")

# =============================================================================
# SECCIÓN 5: Indexing y Slicing — Acceder a elementos
# =============================================================================
print("\n--- 5. Indexing y Slicing ---")

arr = np.array([10, 20, 30, 40, 50])

# Indexing: igual que listas Python, con índice negativo desde el final
print(f"Array: {arr}")
print(f"Primer elemento [0]: {arr[0]}")
print(f"Último elemento [-1]: {arr[-1]}")

# Slicing: [inicio:fin:paso] — igual que listas Python
print(f"Primeros 3 [0:3]: {arr[0:3]}")
print(f"Desde índice 2 [2:]: {arr[2:]}")
print(f"Invertido [::-1]: {arr[::-1]}")

# Arrays 2D: [fila, columna]
matriz = np.array([[1, 2, 3],
                   [4, 5, 6],
                   [7, 8, 9]])

print(f"\nMatriz 3x3:\n{matriz}")
print(f"Elemento [1,2] (fila 1, col 2): {matriz[1, 2]}")  # 6
print(f"Fila 0: {matriz[0, :]}")  # [1, 2, 3]
print(f"Columna 1: {matriz[:, 1]}")  # [2, 5, 8]
print(f"Submatriz [0:2, 1:3]:\n{matriz[0:2, 1:3]}")

# Indexing booleano — filtrar elementos según condición
arr_num = np.array([5, 12, 3, 18, 7, 25, 2])
mayores_10 = arr_num[arr_num > 10]  # devuelve solo los elementos donde condición es True
print(f"\nArray: {arr_num}")
print(f"Elementos > 10: {mayores_10}")

# =============================================================================
# SECCIÓN 6: Operaciones vectorizadas
# =============================================================================
print("\n--- 6. Operaciones vectorizadas ---")

a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])

# Las operaciones aplican elemento a elemento, sin bucles explícitos
print(f"a + b = {a + b}")      # Suma elemento a elemento
print(f"a * b = {a * b}")      # Multiplicación elemento a elemento
print(f"a ** 2 = {a ** 2}")    # Potencia elemento a elemento
print(f"b / a = {b / a}")      # División elemento a elemento

# Funciones matemáticas universales (ufuncs)
angulos = np.array([0, np.pi/6, np.pi/4, np.pi/2])
print(f"\nSeno de [0, π/6, π/4, π/2]: {np.sin(angulos).round(3)}")
print(f"Raíz cuadrada de [1,4,9,16]: {np.sqrt(np.array([1, 4, 9, 16]))}")
print(f"Exponencial de [0,1,2]: {np.exp(np.array([0, 1, 2])).round(3)}")

# =============================================================================
# SECCIÓN 7: Broadcasting — Operar arrays de distinta forma
# =============================================================================
print("\n--- 7. Broadcasting ---")

# Broadcasting: NumPy "expande" el array más pequeño para que coincida
# con la forma del más grande, sin copiar datos en memoria

matriz_2d = np.array([[1, 2, 3],
                       [4, 5, 6],
                       [7, 8, 9]])

# Sumar un escalar a toda la matriz
print(f"Matriz + 10:\n{matriz_2d + 10}")

# Sumar un vector fila a cada fila de la matriz
# El vector [1,0,-1] se "expande" para cada fila
vector_fila = np.array([1, 0, -1])
print(f"\nMatriz + [1,0,-1]:\n{matriz_2d + vector_fila}")

# =============================================================================
# SECCIÓN 8: Álgebra lineal básica
# =============================================================================
print("\n--- 8. Álgebra lineal básica ---")

A = np.array([[1, 2],
              [3, 4]])

B = np.array([[5, 6],
              [7, 8]])

# Multiplicación matricial (producto punto) — NO es elemento a elemento
# Usar @ (operador de Python 3.5+) o np.dot
producto = A @ B
print(f"Multiplicación matricial A @ B:\n{producto}")

# Transpuesta: filas y columnas intercambiadas
print(f"\nTranspuesta de A:\n{A.T}")

# Determinante
det = np.linalg.det(A)
print(f"\nDeterminante de A: {det:.2f}")  # 1*4 - 2*3 = -2

# Inversa de una matriz cuadrada
inversa = np.linalg.inv(A)
print(f"\nInversa de A:\n{inversa}")

# Verificación: A @ A^(-1) debe ser la identidad
verificacion = A @ inversa
print(f"\nA @ A^(-1) (debe ser identidad):\n{verificacion.round(10)}")

print("\n" + "=" * 60)
print("Fin de NumPy básico — Continúa con 02_numpy_avanzado.py")
print("=" * 60)
