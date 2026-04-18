# =============================================================================
# CAPÍTULO 22 — Data Science con Python
# Archivo: 02_numpy_avanzado.py
# Tema: NumPy Avanzado — Random, estadísticas, sorting y más
# =============================================================================
#
# Este archivo cubre las herramientas NumPy que se usan constantemente en
# Data Science real: generación de datos aleatorios (para simulaciones y
# pruebas), estadísticas descriptivas, y manipulación avanzada de arrays.
# =============================================================================

try:
    import numpy as np
except ImportError:
    print("NumPy no está instalado. Ejecuta: pip install numpy")
    exit(1)

print("=" * 60)
print("NUMPY AVANZADO — Random, estadísticas y manipulación")
print("=" * 60)

# =============================================================================
# SECCIÓN 1: np.random — Generación de números aleatorios
# =============================================================================
print("\n--- 1. Generación de números aleatorios ---")

# Semilla aleatoria: garantiza reproducibilidad
# SIEMPRE fijar la semilla en experimentos científicos para que otros
# puedan reproducir exactamente los mismos resultados
np.random.seed(42)

# Enteros aleatorios entre low (incluido) y high (excluido)
enteros = np.random.randint(low=1, high=101, size=10)
print(f"10 enteros aleatorios [1-100]: {enteros}")

# Flotantes uniformes entre 0 y 1
uniformes = np.random.random(size=5)
print(f"5 flotantes uniformes [0,1): {uniformes.round(3)}")

# Distribución normal (gaussiana): media=0, std=1 por defecto
# Es la distribución más importante en estadística
normales = np.random.normal(loc=0, scale=1, size=8)
print(f"8 valores distribución normal: {normales.round(3)}")

# Distribución normal con parámetros personalizados
# Ejemplo: simular alturas de personas (media=170cm, std=10cm)
alturas = np.random.normal(loc=170, scale=10, size=1000)
print(f"\nSimulación de 1000 alturas:")
print(f"  Media: {alturas.mean():.1f} cm")
print(f"  Std:   {alturas.std():.1f} cm")
print(f"  Min:   {alturas.min():.1f} cm")
print(f"  Max:   {alturas.max():.1f} cm")

# np.random.choice — selección aleatoria de un array
opciones = np.array(["rojo", "verde", "azul", "amarillo"])
seleccion = np.random.choice(opciones, size=5, replace=True)
print(f"\nSelección aleatoria con reemplazo: {seleccion}")

# Mezclar un array (shuffle in-place)
nums = np.arange(1, 11)
np.random.shuffle(nums)
print(f"Array mezclado: {nums}")

# =============================================================================
# SECCIÓN 2: Estadísticas descriptivas
# =============================================================================
print("\n--- 2. Estadísticas descriptivas ---")

# Dataset de ejemplo: calificaciones de 20 estudiantes
np.random.seed(123)
calificaciones = np.random.normal(loc=72, scale=12, size=20).clip(0, 100)
calificaciones = calificaciones.round(1)
print(f"Calificaciones: {calificaciones}")

# Medidas de tendencia central
print(f"\nMedia (promedio):   {np.mean(calificaciones):.2f}")
print(f"Mediana (valor central): {np.median(calificaciones):.2f}")

# Medidas de dispersión
print(f"\nDesviación estándar: {np.std(calificaciones):.2f}")
print(f"Varianza:            {np.var(calificaciones):.2f}")
print(f"Rango [min, max]:    [{np.min(calificaciones):.1f}, {np.max(calificaciones):.1f}]")

# Percentiles — qué valor está por debajo del N% de los datos
# El percentil 50 es la mediana
p25 = np.percentile(calificaciones, 25)  # Primer cuartil
p50 = np.percentile(calificaciones, 50)  # Mediana
p75 = np.percentile(calificaciones, 75)  # Tercer cuartil
print(f"\nPercentiles:")
print(f"  P25 (Q1): {p25:.1f}")
print(f"  P50 (Q2, mediana): {p50:.1f}")
print(f"  P75 (Q3): {p75:.1f}")
print(f"  IQR (rango intercuartílico): {p75 - p25:.1f}")

# Suma y producto acumulado
pequeño = np.array([1, 2, 3, 4, 5])
print(f"\nArray: {pequeño}")
print(f"Suma total: {np.sum(pequeño)}")
print(f"Suma acumulada: {np.cumsum(pequeño)}")  # [1, 3, 6, 10, 15]
print(f"Producto acumulado: {np.cumprod(pequeño)}")  # [1, 2, 6, 24, 120]

# =============================================================================
# SECCIÓN 3: Sorting y búsqueda
# =============================================================================
print("\n--- 3. Sorting y búsqueda ---")

datos = np.array([64, 34, 25, 12, 22, 11, 90])
print(f"Array original: {datos}")

# np.sort — devuelve una copia ordenada (no modifica el original)
ordenado = np.sort(datos)
print(f"Ordenado ascendente: {ordenado}")
print(f"Ordenado descendente: {np.sort(datos)[::-1]}")

# np.argsort — devuelve los ÍNDICES que ordenarían el array
# Muy útil cuando necesitas saber QUÉ elemento ocupa qué posición
indices_orden = np.argsort(datos)
print(f"Índices de orden: {indices_orden}")
print(f"Verificación: {datos[indices_orden]}")  # Igual que ordenado

# np.unique — valores únicos y sus conteos
colores_enc = np.array([1, 2, 1, 3, 2, 1, 4, 3, 1])
unicos, conteos = np.unique(colores_enc, return_counts=True)
print(f"\nValores únicos: {unicos}")
print(f"Conteos: {conteos}")

# np.where — equivalente vectorizado del if-else
# Sintaxis: np.where(condición, valor_si_verdadero, valor_si_falso)
notas = np.array([45, 72, 88, 33, 91, 67])
aprobados = np.where(notas >= 60, "Aprobado", "Reprobado")
print(f"\nNotas: {notas}")
print(f"Estado: {aprobados}")

# np.where con solo condición: devuelve índices donde es True
indices_aprobados = np.where(notas >= 60)[0]
print(f"Índices de aprobados: {indices_aprobados}")

# =============================================================================
# SECCIÓN 4: Concatenación y apilamiento
# =============================================================================
print("\n--- 4. Concatenación y apilamiento ---")

arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])
arr3 = np.array([7, 8, 9])

# np.concatenate — unir arrays a lo largo de un eje
concat_1d = np.concatenate([arr1, arr2, arr3])
print(f"Concatenación 1D: {concat_1d}")

# Para 2D: eje 0 = vertical (apilar filas), eje 1 = horizontal (apilar columnas)
mat1 = np.array([[1, 2], [3, 4]])
mat2 = np.array([[5, 6], [7, 8]])

vertical = np.concatenate([mat1, mat2], axis=0)  # Apilar filas
horizontal = np.concatenate([mat1, mat2], axis=1)  # Apilar columnas

print(f"\nApilar verticalmente (axis=0):\n{vertical}")
print(f"\nApilar horizontalmente (axis=1):\n{horizontal}")

# np.vstack y np.hstack — atajos más legibles
print(f"\nvstack:\n{np.vstack([mat1, mat2])}")
print(f"\nhstack:\n{np.hstack([mat1, mat2])}")

# np.split — dividir un array en partes iguales
array_grande = np.arange(12)
partes = np.split(array_grande, 3)  # Dividir en 3 partes iguales
print(f"\nSplit en 3 partes: {partes}")

# =============================================================================
# SECCIÓN 5: Funciones de agregación con ejes
# =============================================================================
print("\n--- 5. Agregaciones por eje ---")

# En matrices 2D:
# axis=0 → opera a lo largo de las FILAS (resultado por columna)
# axis=1 → opera a lo largo de las COLUMNAS (resultado por fila)
ventas = np.array([[100, 200, 150],   # Tienda 1: ene, feb, mar
                   [80,  250, 120],   # Tienda 2
                   [130, 180, 200]])  # Tienda 3

print(f"Ventas por tienda (filas) y mes (columnas):\n{ventas}")
print(f"\nTotal por tienda (suma de cada fila): {ventas.sum(axis=1)}")
print(f"Total por mes (suma de cada columna): {ventas.sum(axis=0)}")
print(f"Promedio por tienda: {ventas.mean(axis=1).round(1)}")
print(f"Mejor mes de cada tienda: {ventas.max(axis=1)}")
print(f"Mes con más ventas totales: {np.argmax(ventas.sum(axis=0)) + 1}")  # +1 para mes real

# =============================================================================
# SECCIÓN 6: Generación de datos para ejemplos — patrón común en DS
# =============================================================================
print("\n--- 6. Generación de datasets sintéticos ---")

np.random.seed(0)

# Generar un dataset de precios de casas (simplificado)
n_casas = 100
tamano_m2 = np.random.uniform(50, 300, n_casas).round(1)  # Entre 50 y 300 m²

# Precio con relación lineal al tamaño + ruido (simula datos reales)
# Precio base: 50,000 + 1,500 por m² + ruido aleatorio
ruido = np.random.normal(0, 15000, n_casas)
precios = (50000 + 1500 * tamano_m2 + ruido).round(-3)  # Redondear a miles

print(f"Dataset generado: {n_casas} casas")
print(f"Tamaño m² — Media: {tamano_m2.mean():.1f}, Std: {tamano_m2.std():.1f}")
print(f"Precio     — Media: ${precios.mean():,.0f}, Std: ${precios.std():,.0f}")

# Correlación entre tamaño y precio
correlacion = np.corrcoef(tamano_m2, precios)[0, 1]
print(f"Correlación tamaño-precio: {correlacion:.3f}")  # Debe ser cercana a 1.0

print("\n" + "=" * 60)
print("Fin de NumPy Avanzado — Continúa con 03_pandas_basico.py")
print("=" * 60)
