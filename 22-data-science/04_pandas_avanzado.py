# =============================================================================
# CAPÍTULO 22 — Data Science con Python
# Archivo: 04_pandas_avanzado.py
# Tema: Pandas avanzado — GroupBy, merge, pivot, fechas, nulos
# =============================================================================
#
# Una vez que dominas el acceso y filtro básico de DataFrames, las herramientas
# avanzadas de Pandas te permiten responder preguntas de negocio reales:
# ¿Cuánto vendió cada región? ¿Cómo se relacionan dos tablas? ¿Qué pasa
# con los datos faltantes? ¿Cómo analizo series de tiempo?
# =============================================================================

try:
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"Librería faltante: {e}")
    print("Instala con: pip install pandas numpy")
    exit(1)

print("=" * 60)
print("PANDAS AVANZADO — GroupBy, merge, pivot y más")
print("=" * 60)

# Dataset de ventas para los ejemplos
np.random.seed(42)
n = 60
regiones = np.random.choice(["Norte", "Sur", "Este", "Oeste"], n)
productos = np.random.choice(["Laptop", "Tablet", "Monitor", "Teclado"], n)
meses = np.random.choice(range(1, 7), n)
ventas = np.random.randint(1000, 10000, n)
unidades = np.random.randint(1, 20, n)

df_ventas = pd.DataFrame({
    "region": regiones,
    "producto": productos,
    "mes": meses,
    "ventas": ventas,
    "unidades": unidades
})

print(f"Dataset de ventas creado: {df_ventas.shape}")

# =============================================================================
# SECCIÓN 1: GroupBy — Agrupar y agregar datos
# =============================================================================
print("\n--- 1. GroupBy ---")

# GroupBy divide el DataFrame en grupos y aplica una función de agregación
# Pregunta: ¿Cuánto vendió cada región en total?
ventas_por_region = df_ventas.groupby("region")["ventas"].sum().sort_values(ascending=False)
print(f"Ventas totales por región:\n{ventas_por_region}")

# Múltiples funciones de agregación a la vez con agg()
resumen = df_ventas.groupby("region")["ventas"].agg(["sum", "mean", "max", "count"])
resumen.columns = ["total", "promedio", "maximo", "transacciones"]
print(f"\nResumen por región:\n{resumen.round(1)}")

# Agrupar por múltiples columnas
ventas_region_producto = (df_ventas
    .groupby(["region", "producto"])["ventas"]
    .sum()
    .reset_index()  # Convierte el MultiIndex en columnas normales
    .sort_values("ventas", ascending=False)
)
print(f"\nVentas por región y producto (top 6):\n{ventas_region_producto.head(6)}")

# =============================================================================
# SECCIÓN 2: Pivot Table — Tablas de resumen bidimensionales
# =============================================================================
print("\n--- 2. Pivot Table ---")

# pivot_table es como una tabla dinámica de Excel
# Filas: regiones, Columnas: productos, Valores: suma de ventas
tabla_pivot = pd.pivot_table(
    df_ventas,
    values="ventas",
    index="region",    # Filas
    columns="producto", # Columnas
    aggfunc="sum",
    fill_value=0       # Reemplaza NaN con 0 donde no hay datos
)
print(f"Pivot table ventas por región y producto:\n{tabla_pivot}")

# melt — operación inversa a pivot (formato ancho → formato largo)
# Útil cuando los datos vienen en formato "ancho" y necesitas formato "largo"
df_ancho = pd.DataFrame({
    "ciudad": ["Madrid", "Barcelona", "Sevilla"],
    "enero": [100, 150, 80],
    "febrero": [120, 160, 90],
    "marzo": [130, 145, 95]
})
print(f"\nDataFrame ancho:\n{df_ancho}")

df_largo = df_ancho.melt(
    id_vars="ciudad",      # Columna que se mantiene como identificador
    value_vars=["enero", "febrero", "marzo"],  # Columnas que se "funden"
    var_name="mes",        # Nombre para la nueva columna de variables
    value_name="ventas"    # Nombre para la nueva columna de valores
)
print(f"\nDataFrame largo (melt):\n{df_largo}")

# =============================================================================
# SECCIÓN 3: Merge y Join — Combinar DataFrames
# =============================================================================
print("\n--- 3. Merge y Join ---")

# Simulamos dos tablas: clientes y pedidos
clientes = pd.DataFrame({
    "cliente_id": [1, 2, 3, 4, 5],
    "nombre": ["Ana", "Bruno", "Carmen", "Diego", "Elena"],
    "ciudad": ["Madrid", "Barcelona", "Madrid", "Sevilla", "Valencia"]
})

pedidos = pd.DataFrame({
    "pedido_id": [101, 102, 103, 104, 105, 106],
    "cliente_id": [1, 2, 2, 3, 1, 6],  # Cliente 6 no existe en clientes
    "monto": [250, 180, 320, 90, 410, 150]
})

print(f"Clientes:\n{clientes}")
print(f"\nPedidos:\n{pedidos}")

# INNER JOIN — solo clientes que tienen pedidos (y pedidos con cliente existente)
inner = pd.merge(pedidos, clientes, on="cliente_id", how="inner")
print(f"\nINNER JOIN:\n{inner}")

# LEFT JOIN — todos los pedidos, aunque el cliente no exista
left = pd.merge(pedidos, clientes, on="cliente_id", how="left")
print(f"\nLEFT JOIN (todos los pedidos):\n{left}")

# RIGHT JOIN — todos los clientes, aunque no tengan pedidos
right = pd.merge(pedidos, clientes, on="cliente_id", how="right")
print(f"\nRIGHT JOIN (todos los clientes):\n{right}")

# =============================================================================
# SECCIÓN 4: Valores nulos — El problema más común en datos reales
# =============================================================================
print("\n--- 4. Manejo de valores nulos ---")

# Crear DataFrame con nulos intencionales
df_nulos = pd.DataFrame({
    "nombre": ["Ana", "Bruno", None, "Diego", "Elena"],
    "edad": [25, None, 32, 28, None],
    "salario": [50000, 60000, None, 55000, 48000],
    "ciudad": ["Madrid", "Barcelona", "Madrid", None, "Valencia"]
})

print(f"DataFrame con nulos:\n{df_nulos}")

# Detectar nulos
print(f"\nMáscara de nulos:\n{df_nulos.isnull()}")
print(f"\nConteo de nulos por columna:\n{df_nulos.isnull().sum()}")
print(f"Total nulos: {df_nulos.isnull().sum().sum()}")
print(f"% de nulos por columna:\n{(df_nulos.isnull().sum() / len(df_nulos) * 100).round(1)}")

# Eliminar filas con nulos — solo si los nulos son pocos y aleatorios
df_sin_nulos = df_nulos.dropna()
print(f"\nTras dropna (eliminar filas con cualquier nulo):\n{df_sin_nulos}")

# Rellenar nulos — estrategia más común, preserva todas las filas
df_rellenado = df_nulos.copy()
df_rellenado["edad"] = df_rellenado["edad"].fillna(df_rellenado["edad"].mean())
df_rellenado["salario"] = df_rellenado["salario"].fillna(df_rellenado["salario"].median())
df_rellenado["nombre"] = df_rellenado["nombre"].fillna("Desconocido")
df_rellenado["ciudad"] = df_rellenado["ciudad"].fillna("No especificada")
print(f"\nTras fillna (rellenar con media/mediana):\n{df_rellenado}")

# =============================================================================
# SECCIÓN 5: apply y map — Transformar datos fila a fila / celda a celda
# =============================================================================
print("\n--- 5. apply y map ---")

df_emp = pd.DataFrame({
    "nombre": ["ana garcia", "CARLOS LOPEZ", "Sofia Martin"],
    "salario": [42000, 58000, 45000],
    "departamento": ["ventas", "IT", "VENTAS"]
})

# map — aplica una función o diccionario a cada elemento de una Series
# Útil para transformar valores individuales
df_emp["nombre_limpio"] = df_emp["nombre"].map(str.title)
print(f"Nombre normalizado:\n{df_emp[['nombre', 'nombre_limpio']]}")

# Mapeo con diccionario: reemplazar valores según tabla
dept_map = {"ventas": "Ventas", "IT": "Tecnología", "VENTAS": "Ventas"}
df_emp["dept_normalizado"] = df_emp["departamento"].map(dept_map)
print(f"\nDepartamento normalizado:\n{df_emp[['departamento', 'dept_normalizado']]}")

# apply — aplica una función a cada fila o columna completa
# Con axis=1: la función recibe cada FILA como una Series
def calcular_bono(fila):
    """Calcula bono del 10% si es Ventas, 15% si es Tecnología."""
    if fila["dept_normalizado"] == "Ventas":
        return fila["salario"] * 0.10
    elif fila["dept_normalizado"] == "Tecnología":
        return fila["salario"] * 0.15
    return 0

df_emp["bono"] = df_emp.apply(calcular_bono, axis=1)
print(f"\nCon bono calculado:\n{df_emp[['nombre_limpio', 'dept_normalizado', 'salario', 'bono']]}")

# =============================================================================
# SECCIÓN 6: Fechas y series temporales
# =============================================================================
print("\n--- 6. Fechas y series temporales ---")

# Crear un rango de fechas — pd.date_range
fechas = pd.date_range(start="2024-01-01", periods=12, freq="MS")  # "MS" = inicio de mes
print(f"Rango de 12 meses:\n{fechas}")

# DataFrame de serie temporal
np.random.seed(10)
ventas_mensuales = pd.DataFrame({
    "fecha": fechas,
    "ventas": np.random.randint(50000, 150000, 12),
    "costos": np.random.randint(30000, 80000, 12)
})
ventas_mensuales["ganancia"] = ventas_mensuales["ventas"] - ventas_mensuales["costos"]

# Convertir columna a datetime si viene como string
ventas_mensuales["fecha"] = pd.to_datetime(ventas_mensuales["fecha"])

# Establecer fecha como índice — necesario para operaciones temporales
ventas_mensuales = ventas_mensuales.set_index("fecha")
print(f"\nVentas mensuales con índice de fecha:\n{ventas_mensuales}")

# Extraer componentes de la fecha
ventas_mensuales["mes"] = ventas_mensuales.index.month
ventas_mensuales["trimestre"] = ventas_mensuales.index.quarter
print(f"\nCon mes y trimestre:\n{ventas_mensuales[['ventas', 'mes', 'trimestre']].head(6)}")

# Resample — agrupar por período de tiempo
# "Q" = quarterly (trimestral)
ventas_trimestrales = ventas_mensuales["ventas"].resample("QE").sum()
print(f"\nVentas por trimestre:\n{ventas_trimestrales}")

# Media móvil — suaviza fluctuaciones, revela tendencias
ventas_mensuales["media_movil_3m"] = ventas_mensuales["ventas"].rolling(window=3).mean().round(0)
print(f"\nMedia móvil de 3 meses:\n{ventas_mensuales[['ventas', 'media_movil_3m']]}")

print("\n" + "=" * 60)
print("Fin de Pandas Avanzado — Continúa con 05_matplotlib_basico.py")
print("=" * 60)
