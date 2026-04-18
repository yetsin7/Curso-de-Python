# =============================================================================
# CAPÍTULO 22 — Data Science con Python
# Archivo: 06_seaborn_y_visualizacion.py
# Tema: Seaborn — Visualización estadística de alto nivel
# =============================================================================
#
# Seaborn está construido sobre Matplotlib pero ofrece una API de alto nivel
# orientada a la visualización estadística. Sus ventajas sobre Matplotlib puro:
# - Gráficos estadísticos complejos con una sola línea de código
# - Manejo nativo de DataFrames de Pandas
# - Estilos más atractivos por defecto
# - Visualización de distribuciones, correlaciones y categorías
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
    print("Instala con: pip install seaborn matplotlib pandas numpy")
    exit(1)

import os

OUTPUT_DIR = "graficos_seaborn"
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Gráficos se guardarán en: {OUTPUT_DIR}/")

# Configuración global de Seaborn
sns.set_theme(style="whitegrid", palette="husl", font_scale=1.1)

# =============================================================================
# DATASET: Generamos un dataset realista de empleados
# =============================================================================
np.random.seed(42)
n = 200

departamentos = np.random.choice(["Ventas", "IT", "Marketing", "RRHH", "Finanzas"], n,
                                  p=[0.30, 0.25, 0.20, 0.10, 0.15])
experiencia = np.random.randint(1, 20, n)

# Salario correlacionado con experiencia y departamento
salario_base = {"Ventas": 38000, "IT": 52000, "Marketing": 40000,
                "RRHH": 36000, "Finanzas": 48000}
salarios = [salario_base[d] + experiencia[i] * 1800 + np.random.normal(0, 5000)
            for i, d in enumerate(departamentos)]

satisfaccion = np.random.choice([1, 2, 3, 4, 5], n, p=[0.05, 0.10, 0.20, 0.40, 0.25])
genero = np.random.choice(["Hombre", "Mujer"], n)

df = pd.DataFrame({
    "departamento": departamentos,
    "experiencia": experiencia,
    "salario": np.array(salarios).round(0).astype(int),
    "satisfaccion": satisfaccion,
    "genero": genero
})

print(f"Dataset creado: {df.shape}")
print(df.head())

# =============================================================================
# SECCIÓN 1: histplot — Distribuciones de una variable
# =============================================================================
print("\n--- 1. histplot y kde ---")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Histograma con curva KDE (estimación de densidad del núcleo)
# KDE suaviza el histograma para mostrar la distribución continua
sns.histplot(data=df, x="salario", kde=True, bins=20,
             color="#1565C0", ax=axes[0])
axes[0].set_title("Distribución de Salarios")
axes[0].set_xlabel("Salario (€)")

# Histograma separado por una variable categórica (hue)
sns.histplot(data=df, x="salario", hue="genero", kde=True,
             bins=20, alpha=0.6, ax=axes[1])
axes[1].set_title("Distribución de Salarios por Género")
axes[1].set_xlabel("Salario (€)")

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "01_histplot.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Guardado: {ruta}")

# =============================================================================
# SECCIÓN 2: boxplot y violinplot — Comparar distribuciones por grupo
# =============================================================================
print("\n--- 2. boxplot y violinplot ---")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Boxplot: muestra mediana, cuartiles y outliers (puntos fuera de los bigotes)
# Muy útil para comparar distribuciones entre grupos y detectar outliers
sns.boxplot(data=df, x="departamento", y="salario", palette="Set2", ax=axes[0])
axes[0].set_title("Boxplot: Salario por Departamento")
axes[0].set_xlabel("Departamento")
axes[0].set_ylabel("Salario (€)")
axes[0].tick_params(axis="x", rotation=20)

# Violinplot: como boxplot pero muestra la forma completa de la distribución
# La "anchura" del violín en cada punto indica la densidad de datos ahí
sns.violinplot(data=df, x="departamento", y="salario",
               hue="genero", split=True, palette="pastel", ax=axes[1])
axes[1].set_title("Violinplot: Salario por Depto y Género")
axes[1].set_xlabel("Departamento")
axes[1].set_ylabel("Salario (€)")
axes[1].tick_params(axis="x", rotation=20)

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "02_boxplot_violin.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Guardado: {ruta}")

# =============================================================================
# SECCIÓN 3: heatmap — Matrices de correlación
# =============================================================================
print("\n--- 3. heatmap (correlaciones) ---")

# Calcular la matriz de correlación — valores entre -1 y 1
# 1 = correlación perfecta positiva
# 0 = sin correlación
# -1 = correlación perfecta negativa
df_numerico = df[["experiencia", "salario", "satisfaccion"]]
correlacion = df_numerico.corr()
print(f"\nMatriz de correlación:\n{correlacion.round(3)}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Heatmap de correlación
sns.heatmap(correlacion, annot=True, fmt=".2f", cmap="RdYlGn",
            vmin=-1, vmax=1, center=0,
            square=True, linewidths=0.5, ax=axes[0])
axes[0].set_title("Mapa de Calor — Correlaciones")

# Heatmap de tabla pivot: salario promedio por depto y satisfacción
tabla = df.pivot_table(values="salario", index="departamento",
                       columns="satisfaccion", aggfunc="mean").round(0)
sns.heatmap(tabla, annot=True, fmt=".0f", cmap="YlOrRd",
            linewidths=0.5, ax=axes[1])
axes[1].set_title("Salario Promedio por Depto y Satisfacción")
axes[1].set_xlabel("Nivel de Satisfacción (1-5)")

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "03_heatmap.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Guardado: {ruta}")

# =============================================================================
# SECCIÓN 4: scatterplot y regplot — Relaciones entre variables
# =============================================================================
print("\n--- 4. scatterplot y regplot ---")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# scatterplot con colores y tamaños para más dimensiones
sns.scatterplot(data=df, x="experiencia", y="salario",
                hue="departamento", alpha=0.7, s=60, ax=axes[0])
axes[0].set_title("Experiencia vs Salario por Departamento")
axes[0].set_xlabel("Años de Experiencia")
axes[0].set_ylabel("Salario (€)")

# regplot — scatter + línea de regresión + intervalo de confianza
# Muy útil para visualizar relaciones lineales y su confianza estadística
sns.regplot(data=df, x="experiencia", y="salario",
            scatter_kws={"alpha": 0.3, "color": "#1565C0"},
            line_kws={"color": "red", "linewidth": 2},
            ax=axes[1])
axes[1].set_title("Regresión: Experiencia → Salario")
axes[1].set_xlabel("Años de Experiencia")
axes[1].set_ylabel("Salario (€)")

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "04_scatter_reg.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Guardado: {ruta}")

# =============================================================================
# SECCIÓN 5: pairplot — Explorar todas las relaciones a la vez
# =============================================================================
print("\n--- 5. pairplot ---")

# pairplot crea una matriz de gráficos: cada par de variables numéricas
# entre sí. La diagonal muestra la distribución de cada variable sola.
# Es una de las herramientas más útiles en EDA.
g = sns.pairplot(df[["experiencia", "salario", "satisfaccion", "departamento"]],
                 hue="departamento", plot_kws={"alpha": 0.5},
                 diag_kind="kde", corner=True)
g.fig.suptitle("Pairplot — Relaciones entre variables numéricas", y=1.02, fontsize=13)

ruta = os.path.join(OUTPUT_DIR, "05_pairplot.png")
g.savefig(ruta, dpi=120, bbox_inches="tight")
plt.close()
print(f"Guardado: {ruta}")

# =============================================================================
# SECCIÓN 6: Gráficos categóricos — countplot y barplot
# =============================================================================
print("\n--- 6. Gráficos categóricos ---")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# countplot — cuenta ocurrencias de cada categoría
sns.countplot(data=df, x="departamento", hue="genero",
              palette="Set1", ax=axes[0])
axes[0].set_title("Conteo de Empleados por Depto y Género")
axes[0].set_xlabel("Departamento")
axes[0].set_ylabel("Número de Empleados")
axes[0].tick_params(axis="x", rotation=15)

# barplot — muestra el promedio (u otra métrica) con intervalo de confianza
sns.barplot(data=df, x="departamento", y="salario",
            hue="genero", palette="Set1",
            estimator="mean", errorbar="ci", ax=axes[1])
axes[1].set_title("Salario Promedio por Depto y Género")
axes[1].set_xlabel("Departamento")
axes[1].set_ylabel("Salario Promedio (€)")
axes[1].tick_params(axis="x", rotation=15)

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "06_categoricos.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Guardado: {ruta}")

# =============================================================================
# NOTA SOBRE PLOTLY — Visualización interactiva
# =============================================================================
print("\n--- Nota sobre Plotly ---")
print("""
Plotly es una librería de visualización interactiva para Python.
Sus gráficos son HTML interactivo: zoom, hover, filtros, etc.
Es ideal para dashboards y reportes web.

Instalación: pip install plotly

Ejemplo básico:
    import plotly.express as px
    df = px.data.iris()
    fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
    fig.show()  # Abre en el navegador

Plotly Express tiene funciones de alto nivel equivalentes a Seaborn.
Plotly Graph Objects da control total como Matplotlib.
Para dashboards: pip install dash
""")

print(f"\nTodos los gráficos guardados en '{OUTPUT_DIR}/'")
print("\n" + "=" * 60)
print("Fin de Seaborn — Continúa con 07_analisis_exploratorio.py")
print("=" * 60)
