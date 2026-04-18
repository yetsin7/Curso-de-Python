# =============================================================================
# CAPÍTULO 22 — Data Science con Python
# Archivo: 07_analisis_exploratorio.py
# Tema: EDA completo — Análisis Exploratorio de Datos
# =============================================================================
#
# El Análisis Exploratorio de Datos (EDA) es el proceso de "conocer" un
# dataset antes de modelarlo. Es la fase más importante y subestimada del
# Data Science. Un buen EDA:
#   - Revela la calidad real de los datos (nulos, outliers, errores)
#   - Muestra distribuciones y tendencias
#   - Descubre correlaciones y patrones inesperados
#   - Genera hipótesis para el modelado
#
# Este script simula un dataset de ventas de una tienda de electrónica
# y realiza un EDA completo y profesional.
# =============================================================================

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"Librería faltante: {e}")
    print("Instala con: pip install pandas numpy matplotlib seaborn")
    exit(1)

import os
import warnings
warnings.filterwarnings("ignore")

OUTPUT_DIR = "graficos_eda"
os.makedirs(OUTPUT_DIR, exist_ok=True)
sns.set_theme(style="whitegrid", palette="husl")

print("=" * 65)
print("EDA COMPLETO — Dataset de Ventas de Tienda de Electrónica")
print("=" * 65)

# =============================================================================
# PASO 1: Generación del dataset
# =============================================================================
print("\n--- PASO 1: Cargando / generando datos ---")

np.random.seed(2024)
N = 500  # 500 transacciones de venta

# Variables del dataset
fechas = pd.date_range("2023-01-01", "2023-12-31", periods=N)
fechas = np.sort(np.random.choice(fechas, N, replace=False))

categorias = np.random.choice(
    ["Laptops", "Smartphones", "Tablets", "Accesorios", "Monitores"],
    N, p=[0.20, 0.30, 0.15, 0.25, 0.10]
)

# Precios realistas por categoría
precios_base = {"Laptops": 900, "Smartphones": 650, "Tablets": 400,
                "Accesorios": 50, "Monitores": 350}
precios = np.array([
    precios_base[cat] * np.random.uniform(0.7, 1.5)
    for cat in categorias
]).round(2)

unidades = np.random.choice([1, 2, 3], N, p=[0.70, 0.20, 0.10])
total_venta = (precios * unidades).round(2)

regiones = np.random.choice(["Norte", "Sur", "Este", "Oeste", "Centro"], N)

# Método de pago
metodo_pago = np.random.choice(
    ["Tarjeta", "Efectivo", "Transferencia", "PayPal"],
    N, p=[0.45, 0.25, 0.20, 0.10]
)

# Puntuación del cliente (1-5)
satisfaccion = np.random.choice([1, 2, 3, 4, 5], N,
                                 p=[0.03, 0.07, 0.15, 0.45, 0.30])

# Introducir problemas realistas (datos faltantes, outliers)
# Algunos registros sin satisfacción (cliente no respondió la encuesta)
idx_sin_satisfaccion = np.random.choice(N, int(N * 0.15), replace=False)
satisfaccion = satisfaccion.astype(float)
satisfaccion[idx_sin_satisfaccion] = np.nan

# Outliers en precio (errores de entrada de datos)
idx_outliers = np.random.choice(N, 5, replace=False)
precios[idx_outliers] = precios[idx_outliers] * 10  # Error: precio x10

df = pd.DataFrame({
    "fecha": pd.to_datetime(fechas),
    "categoria": categorias,
    "precio_unitario": precios,
    "unidades": unidades,
    "total_venta": total_venta,
    "region": regiones,
    "metodo_pago": metodo_pago,
    "satisfaccion": satisfaccion
})

print(f"Dataset creado: {df.shape[0]} filas × {df.shape[1]} columnas")

# =============================================================================
# PASO 2: Inspección inicial
# =============================================================================
print("\n--- PASO 2: Inspección inicial ---")

print("\n>> df.head():")
print(df.head())

print("\n>> df.dtypes:")
print(df.dtypes)

print("\n>> df.describe():")
print(df.describe().round(2))

print("\n>> Distribución de categorías:")
print(df["categoria"].value_counts())

# =============================================================================
# PASO 3: Calidad de datos — Nulos y duplicados
# =============================================================================
print("\n--- PASO 3: Calidad de datos ---")

# Análisis de valores nulos
nulos = df.isnull().sum()
pct_nulos = (nulos / len(df) * 100).round(1)
print("\nNulos por columna:")
for col in df.columns:
    if nulos[col] > 0:
        print(f"  {col}: {nulos[col]} ({pct_nulos[col]}%)")
    else:
        print(f"  {col}: 0 (0%)")

# Duplicados
n_duplicados = df.duplicated().sum()
print(f"\nFilas duplicadas: {n_duplicados}")

# =============================================================================
# PASO 4: Detección y manejo de outliers
# =============================================================================
print("\n--- PASO 4: Detección de outliers ---")

# Método IQR (Rango Intercuartílico) — el más robusto para outliers
Q1 = df["precio_unitario"].quantile(0.25)
Q3 = df["precio_unitario"].quantile(0.75)
IQR = Q3 - Q1
limite_inf = Q1 - 1.5 * IQR
limite_sup = Q3 + 1.5 * IQR

outliers = df[(df["precio_unitario"] < limite_inf) | (df["precio_unitario"] > limite_sup)]
print(f"Outliers en precio_unitario: {len(outliers)} registros")
print(f"  Límite inferior: {limite_inf:.2f}")
print(f"  Límite superior: {limite_sup:.2f}")
print(f"  Valores extremos encontrados:\n{outliers[['categoria', 'precio_unitario']].head()}")

# Eliminar outliers y recalcular total_venta
df_limpio = df[
    (df["precio_unitario"] >= limite_inf) &
    (df["precio_unitario"] <= limite_sup)
].copy()
df_limpio["total_venta"] = (df_limpio["precio_unitario"] * df_limpio["unidades"]).round(2)
print(f"\nDataset tras eliminar outliers: {df_limpio.shape[0]} filas")

# Rellenar satisfacción faltante con la mediana
mediana_sat = df_limpio["satisfaccion"].median()
df_limpio["satisfaccion"] = df_limpio["satisfaccion"].fillna(mediana_sat)
print(f"Satisfacción nula rellenada con mediana: {mediana_sat}")

# =============================================================================
# PASO 5: Análisis de distribuciones
# =============================================================================
print("\n--- PASO 5: Distribuciones ---")

fig, axes = plt.subplots(2, 2, figsize=(13, 10))
fig.suptitle("EDA — Distribuciones de Variables Clave", fontsize=14, fontweight="bold")

# Distribución de precios por categoría
sns.boxplot(data=df_limpio, x="categoria", y="precio_unitario",
            palette="Set2", ax=axes[0, 0])
axes[0, 0].set_title("Precios por Categoría")
axes[0, 0].tick_params(axis="x", rotation=20)

# Distribución de ventas totales
sns.histplot(data=df_limpio, x="total_venta", bins=30, kde=True,
             color="#1565C0", ax=axes[0, 1])
axes[0, 1].set_title("Distribución de Total por Venta")
axes[0, 1].set_xlabel("Total Venta (€)")

# Satisfacción del cliente
satisfaccion_counts = df_limpio["satisfaccion"].value_counts().sort_index()
axes[1, 0].bar(satisfaccion_counts.index.astype(str), satisfaccion_counts.values,
               color=sns.color_palette("RdYlGn", 5))
axes[1, 0].set_title("Satisfacción del Cliente (1-5)")
axes[1, 0].set_xlabel("Puntuación")
axes[1, 0].set_ylabel("Número de clientes")

# Ventas por método de pago
pago_data = df_limpio["metodo_pago"].value_counts()
axes[1, 1].pie(pago_data.values, labels=pago_data.index,
               autopct="%1.1f%%", startangle=90,
               colors=sns.color_palette("pastel"))
axes[1, 1].set_title("Métodos de Pago")

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "01_distribuciones.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Gráfico guardado: {ruta}")

# =============================================================================
# PASO 6: Análisis temporal
# =============================================================================
print("\n--- PASO 6: Tendencias temporales ---")

df_limpio["mes"] = df_limpio["fecha"].dt.month
df_limpio["mes_nombre"] = df_limpio["fecha"].dt.strftime("%b")
df_limpio["dia_semana"] = df_limpio["fecha"].dt.day_name()
df_limpio["trimestre"] = df_limpio["fecha"].dt.quarter

# Ventas mensuales
ventas_mes = df_limpio.groupby("mes")["total_venta"].sum().reset_index()
ventas_mes_nombre = df_limpio.groupby("mes_nombre")["total_venta"].sum()

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Ventas por mes
meses_orden = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ventas_mens_ord = df_limpio.groupby("mes")["total_venta"].sum()
axes[0].plot(range(1, 13), [ventas_mens_ord.get(m, 0) for m in range(1, 13)],
             marker="o", color="#1565C0", linewidth=2.5, markersize=8)
axes[0].fill_between(range(1, 13), [ventas_mens_ord.get(m, 0) for m in range(1, 13)],
                     alpha=0.15, color="#1565C0")
axes[0].set_title("Ventas Totales por Mes (2023)")
axes[0].set_xlabel("Mes")
axes[0].set_ylabel("Total Ventas (€)")
axes[0].set_xticks(range(1, 13))

# Ventas por trimestre y categoría
ventas_trim_cat = df_limpio.groupby(["trimestre", "categoria"])["total_venta"].sum().reset_index()
pivot = ventas_trim_cat.pivot(index="trimestre", columns="categoria", values="total_venta")
pivot.plot(kind="bar", ax=axes[1], colormap="tab10", edgecolor="white")
axes[1].set_title("Ventas por Trimestre y Categoría")
axes[1].set_xlabel("Trimestre")
axes[1].set_ylabel("Total Ventas (€)")
axes[1].legend(title="Categoría", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
axes[1].tick_params(axis="x", rotation=0)

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "02_tendencias_tiempo.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Gráfico guardado: {ruta}")

# =============================================================================
# PASO 7: Correlaciones
# =============================================================================
print("\n--- PASO 7: Correlaciones ---")

# Codificar variables categóricas para incluirlas en la correlación
df_corr = df_limpio[["precio_unitario", "unidades", "total_venta", "satisfaccion"]].copy()
correlacion = df_corr.corr()
print(f"\nMatriz de correlación:\n{correlacion.round(3)}")

fig, ax = plt.subplots(figsize=(7, 6))
mask = np.triu(np.ones_like(correlacion, dtype=bool), k=1)  # Ocultar triángulo superior
sns.heatmap(correlacion, annot=True, fmt=".2f", cmap="RdYlGn",
            vmin=-1, vmax=1, center=0, square=True,
            linewidths=0.5, ax=ax)
ax.set_title("Mapa de Correlaciones")
plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "03_correlaciones.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Gráfico guardado: {ruta}")

# =============================================================================
# PASO 8: Resumen ejecutivo — Hallazgos del EDA
# =============================================================================
print("\n--- PASO 8: Resumen ejecutivo ---")

total_ventas = df_limpio["total_venta"].sum()
ticket_promedio = df_limpio["total_venta"].mean()
categoria_top = df_limpio.groupby("categoria")["total_venta"].sum().idxmax()
region_top = df_limpio.groupby("region")["total_venta"].sum().idxmax()
mes_top = df_limpio.groupby("mes")["total_venta"].sum().idxmax()
sat_promedio = df_limpio["satisfaccion"].mean()

print("\n" + "=" * 65)
print("RESUMEN EJECUTIVO — Dataset de Ventas 2023")
print("=" * 65)
print(f"Transacciones analizadas:  {len(df_limpio):,}")
print(f"Ventas totales:            €{total_ventas:,.2f}")
print(f"Ticket promedio:           €{ticket_promedio:,.2f}")
print(f"Categoría más vendida:     {categoria_top}")
print(f"Región con más ventas:     {region_top}")
print(f"Mes más rentable:          Mes {mes_top}")
print(f"Satisfacción promedio:     {sat_promedio:.2f} / 5.0")
print(f"Outliers eliminados:       {len(outliers)}")
print(f"Nulos en satisfacción:     {len(idx_sin_satisfaccion)} (rellenados con mediana)")
print("=" * 65)

print(f"\nTodos los gráficos guardados en: {OUTPUT_DIR}/")
print("\n" + "=" * 65)
print("Fin del Capítulo 22 — ¡Pasa al Capítulo 23: Machine Learning!")
print("=" * 65)
