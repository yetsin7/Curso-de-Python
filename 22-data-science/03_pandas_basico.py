# =============================================================================
# CAPÍTULO 22 — Data Science con Python
# Archivo: 03_pandas_basico.py
# Tema: Pandas básico — Series, DataFrame, selección y filtros
# =============================================================================
#
# Pandas es la librería de manipulación de datos más importante de Python.
# Construida sobre NumPy, agrega la capacidad de trabajar con datos tabulares
# etiquetados: filas con índices, columnas con nombres, tipos mixtos.
#
# El DataFrame es la estructura central: piensa en él como una hoja de Excel
# pero completamente programable, con millones de filas posibles.
# =============================================================================

try:
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"Librería faltante: {e}")
    print("Instala con: pip install pandas numpy")
    exit(1)

print("=" * 60)
print("PANDAS BÁSICO — Series, DataFrame y selección de datos")
print("=" * 60)

# =============================================================================
# SECCIÓN 1: Series — El array 1D etiquetado de Pandas
# =============================================================================
print("\n--- 1. Series ---")

# Una Series es un array 1D con un índice (etiqueta para cada elemento)
# Piensa en ella como una columna de una tabla
temperaturas = pd.Series(
    data=[22.5, 25.1, 19.8, 23.4, 27.0],
    index=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"],
    name="Temperatura (°C)"
)

print(temperaturas)
print(f"\nTipo: {type(temperaturas)}")
print(f"dtype: {temperaturas.dtype}")
print(f"Nombre: {temperaturas.name}")

# Acceder a elementos por etiqueta o posición
print(f"\nTemperatura del Martes: {temperaturas['Martes']}")
print(f"Temperatura del día 0: {temperaturas.iloc[0]}")

# Operaciones estadísticas básicas
print(f"\nMedia: {temperaturas.mean():.2f}°C")
print(f"Máxima: {temperaturas.max()}°C")
print(f"Día más caluroso: {temperaturas.idxmax()}")

# =============================================================================
# SECCIÓN 2: Crear un DataFrame desde cero
# =============================================================================
print("\n--- 2. Creación de DataFrame ---")

# Creación desde diccionario: cada clave es una columna
# Este es el método más común cuando construyes datos manualmente
empleados_dict = {
    "nombre": ["Ana García", "Carlos López", "Sofía Martín", "Juan Pérez", "María Ruiz"],
    "departamento": ["Ventas", "IT", "Ventas", "IT", "RRHH"],
    "edad": [28, 35, 31, 29, 42],
    "salario": [42000, 58000, 45000, 55000, 48000],
    "años_empresa": [3, 7, 4, 2, 10]
}

df = pd.DataFrame(empleados_dict)
print(df)
print(f"\nTipo: {type(df)}")

# =============================================================================
# SECCIÓN 3: Información básica del DataFrame
# =============================================================================
print("\n--- 3. Exploración básica ---")

# shape: (filas, columnas) — lo primero que revisas en un dataset nuevo
print(f"Shape: {df.shape}")  # (5, 5)

# columns: nombres de las columnas
print(f"Columnas: {list(df.columns)}")

# dtypes: tipo de dato de cada columna
print(f"\nTipos de datos:\n{df.dtypes}")

# head/tail: primeras/últimas N filas (por defecto 5)
print(f"\nPrimeras 3 filas:\n{df.head(3)}")

# info: resumen completo: tipos, nulos, memoria
print("\nInfo:")
df.info()

# describe: estadísticas descriptivas de columnas numéricas
print(f"\nDescribe:\n{df.describe()}")

# value_counts: frecuencia de cada valor en una columna categórica
print(f"\nConteo por departamento:\n{df['departamento'].value_counts()}")

# =============================================================================
# SECCIÓN 4: Selección de datos — Columnas
# =============================================================================
print("\n--- 4. Selección de columnas ---")

# Seleccionar una columna — devuelve una Series
nombres = df["nombre"]
print(f"Columna nombre (Series):\n{nombres}")

# Seleccionar múltiples columnas — devuelve un DataFrame
subconjunto = df[["nombre", "salario"]]
print(f"\nColumnas nombre y salario:\n{subconjunto}")

# =============================================================================
# SECCIÓN 5: Selección de datos — Filas con loc e iloc
# =============================================================================
print("\n--- 5. Selección de filas: loc e iloc ---")

# iloc — selección por POSICIÓN numérica (como NumPy)
# El índice es la posición entera: 0, 1, 2...
print("iloc[0] — primera fila por posición:")
print(df.iloc[0])

print("\niloc[1:3] — filas 1 y 2 por posición:")
print(df.iloc[1:3])

# iloc[filas, columnas] — selección 2D por posición
print("\niloc[0:2, 2:4] — primeras 2 filas, columnas 2 y 3:")
print(df.iloc[0:2, 2:4])

# loc — selección por ETIQUETA del índice
# Como el índice por defecto es numérico, parece igual a iloc,
# pero son conceptualmente diferentes
print("\nloc[0] — fila con etiqueta de índice 0:")
print(df.loc[0])

# loc con nombre de columnas — más legible que iloc para columnas
print("\nloc[0:2, 'nombre':'salario'] — con etiquetas:")
print(df.loc[0:2, "nombre":"salario"])  # ¡Incluye el final! (diferencia con iloc)

# =============================================================================
# SECCIÓN 6: Filtros booleanos — Consultar datos con condiciones
# =============================================================================
print("\n--- 6. Filtros booleanos ---")

# Filtro simple: empleados del departamento IT
filtro_it = df["departamento"] == "IT"
print(f"Máscara booleana:\n{filtro_it}")
print(f"\nEmpleados de IT:\n{df[filtro_it]}")

# Atajo sin variable intermedia
print(f"\nEmpleados con salario > 50000:\n{df[df['salario'] > 50000]}")

# Múltiples condiciones con & (AND) y | (OR)
# IMPORTANTE: cada condición debe estar entre paréntesis
filtro_complejo = (df["departamento"] == "IT") & (df["salario"] > 50000)
print(f"\nEmpleados IT con salario > 50000:\n{df[filtro_complejo]}")

# isin — filtrar por lista de valores permitidos
depts_seleccionados = df[df["departamento"].isin(["Ventas", "RRHH"])]
print(f"\nVentas o RRHH:\n{depts_seleccionados}")

# between — filtrar rango de valores
rango_edad = df[df["edad"].between(28, 35)]
print(f"\nEdad entre 28 y 35:\n{rango_edad}")

# =============================================================================
# SECCIÓN 7: Agregar y modificar columnas
# =============================================================================
print("\n--- 7. Agregar y modificar columnas ---")

# Agregar nueva columna calculada
df["salario_mensual"] = df["salario"] / 12
df["salario_mensual"] = df["salario_mensual"].round(2)
print(f"Con columna salario_mensual:\n{df[['nombre', 'salario', 'salario_mensual']]}")

# Columna basada en condición
df["senior"] = df["años_empresa"] >= 5
print(f"\nColumna 'senior' (>= 5 años):\n{df[['nombre', 'años_empresa', 'senior']]}")

# Renombrar columnas
df_renombrado = df.rename(columns={"años_empresa": "antiguedad"})
print(f"\nColumnas renombradas: {list(df_renombrado.columns)}")

# =============================================================================
# SECCIÓN 8: Leer y escribir datos (CSV / JSON)
# =============================================================================
print("\n--- 8. Leer y escribir CSV/JSON ---")

# Guardar a CSV — operación muy común para guardar resultados
ruta_csv = "empleados_ejemplo.csv"
df.to_csv(ruta_csv, index=False)  # index=False para no guardar el índice numérico
print(f"DataFrame guardado en '{ruta_csv}'")

# Leer el CSV guardado
df_leido = pd.read_csv(ruta_csv)
print(f"CSV leído, shape: {df_leido.shape}")

# Guardar a JSON
ruta_json = "empleados_ejemplo.json"
df.to_json(ruta_json, orient="records", indent=2)
print(f"DataFrame guardado en '{ruta_json}'")

# Leer JSON
df_json = pd.read_json(ruta_json)
print(f"JSON leído, shape: {df_json.shape}")

# Limpiar archivos de ejemplo
import os
for f in [ruta_csv, ruta_json]:
    if os.path.exists(f):
        os.remove(f)
print("Archivos de ejemplo eliminados.")

print("\n" + "=" * 60)
print("Fin de Pandas Básico — Continúa con 04_pandas_avanzado.py")
print("=" * 60)
