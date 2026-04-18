# =============================================================================
# CAPÍTULO 23 — Machine Learning con Python
# Archivo: 05_clustering.py
# Tema: Clustering — Aprendizaje No Supervisado
# =============================================================================
#
# El clustering agrupa datos similares SIN etiquetas previas.
# A diferencia de la clasificación, no sabemos de antemano cuántos grupos
# hay ni cómo se llamarán — el algoritmo los descubre.
#
# Casos de uso reales:
# - Segmentación de clientes (¿qué tipos de clientes tengo?)
# - Detección de anomalías (punto que no pertenece a ningún grupo)
# - Compresión de imágenes
# - Organización automática de documentos
# =============================================================================

try:
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.datasets import make_blobs
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    from scipy.cluster.hierarchy import dendrogram, linkage
except ImportError as e:
    print(f"Librería faltante: {e}")
    print("Instala con: pip install scikit-learn numpy pandas matplotlib seaborn scipy")
    exit(1)

import os
import warnings
warnings.filterwarnings("ignore")

OUTPUT_DIR = "graficos_clustering"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("CLUSTERING — Segmentación no supervisada de datos")
print("=" * 60)

# =============================================================================
# DATASET: Clientes de una tienda (datos de comportamiento de compra)
# =============================================================================
np.random.seed(42)
n = 300

# Simulamos clientes con diferentes patrones de compra
# Grupo 1: clientes frecuentes, ticket bajo (jóvenes)
# Grupo 2: clientes infrecuentes, ticket muy alto (premium)
# Grupo 3: clientes medianos, ticket medio (familia)
# Grupo 4: clientes frecuentes, ticket medio-alto

frecuencia_compra = np.concatenate([
    np.random.normal(20, 2, 80),   # Grupo 1: muy frecuentes
    np.random.normal(3, 1, 60),    # Grupo 2: infrecuentes
    np.random.normal(10, 2, 90),   # Grupo 3: moderados
    np.random.normal(15, 3, 70),   # Grupo 4: frecuentes-moderados
])

ticket_promedio = np.concatenate([
    np.random.normal(30, 5, 80),    # Grupo 1: ticket bajo
    np.random.normal(250, 40, 60),  # Grupo 2: ticket muy alto
    np.random.normal(80, 15, 90),   # Grupo 3: ticket medio
    np.random.normal(120, 20, 70),  # Grupo 4: ticket medio-alto
])

# Etiquetas reales (solo para comparación — el clustering no las usa)
etiquetas_reales = np.concatenate([
    np.zeros(80), np.ones(60), np.full(90, 2), np.full(70, 3)
])

X = np.column_stack([frecuencia_compra, ticket_promedio])

# Escalar los datos — K-Means es sensible a la escala
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"Clientes en el dataset: {len(X)}")
print(f"Features: frecuencia de compra (días/mes), ticket promedio (€)")

# =============================================================================
# SECCIÓN 1: K-Means — El algoritmo de clustering más común
# =============================================================================
print("\n--- 1. K-Means ---")

# K-Means divide los datos en K grupos minimizando la varianza dentro de cada grupo
# Algoritmo:
# 1. Inicializar K centroides aleatoriamente
# 2. Asignar cada punto al centroide más cercano
# 3. Recalcular centroides como la media de los puntos asignados
# 4. Repetir 2-3 hasta convergencia

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
etiquetas_kmeans = kmeans.fit_predict(X_scaled)

centroides_escalados = kmeans.cluster_centers_
centroides = scaler.inverse_transform(centroides_escalados)

print(f"\nCentroides encontrados (en escala original):")
print(f"  {'Cluster':8s} | {'Frec/mes':>10s} | {'Ticket €':>10s} | {'Tamaño':>8s}")
print("  " + "-" * 48)
for i, centroide in enumerate(centroides):
    n_cluster = (etiquetas_kmeans == i).sum()
    print(f"  Cluster {i} | {centroide[0]:>10.1f} | {centroide[1]:>10.1f} | {n_cluster:>8d}")

# Inercia: suma de distancias cuadradas al centroide más cercano
# Menor inercia = clusters más compactos (mejor, hasta cierto punto)
print(f"\nInercia: {kmeans.inertia_:.2f}")

# =============================================================================
# SECCIÓN 2: Elbow Method — Encontrar el K óptimo
# =============================================================================
print("\n--- 2. Elbow Method (Codo) ---")

# ¿Cómo elegimos K? La inercia siempre baja al aumentar K.
# El "codo" es donde la ganancia se vuelve marginal — ese es el K óptimo.

inercias = []
silhouettes = []
rango_k = range(2, 9)

for k in rango_k:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inercias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, labels))

print(f"\n{'K':>3} | {'Inercia':>12} | {'Silhouette':>12}")
print("-" * 33)
for k, inercia, sil in zip(rango_k, inercias, silhouettes):
    print(f"{k:>3} | {inercia:>12.1f} | {sil:>12.4f}")

k_optimo = list(rango_k)[silhouettes.index(max(silhouettes))]
print(f"\nK óptimo por Silhouette: {k_optimo}")

# =============================================================================
# SECCIÓN 3: Silhouette Score — Evaluar la calidad del clustering
# =============================================================================
print("\n--- 3. Silhouette Score ---")

# El Silhouette Score mide qué tan bien separados están los clusters.
# Rango: [-1, 1]
# - Cercano a 1: cada punto está bien asignado a su cluster
# - Cercano a 0: el punto está en el borde entre dos clusters
# - Negativo: el punto probablemente está en el cluster equivocado

sil_kmeans = silhouette_score(X_scaled, etiquetas_kmeans)
print(f"Silhouette Score (K=4): {sil_kmeans:.4f}")
print(f"  (0.5-0.7 es aceptable, >0.7 es excelente)")

# =============================================================================
# SECCIÓN 4: DBSCAN — Clustering basado en densidad
# =============================================================================
print("\n--- 4. DBSCAN ---")

# DBSCAN (Density-Based Spatial Clustering of Applications with Noise)
# Ventajas sobre K-Means:
# - No necesita especificar K de antemano
# - Puede encontrar clusters de forma arbitraria (no solo esféricos)
# - Marca los puntos aislados como RUIDO (-1) → útil para anomalías
#
# Parámetros:
# - eps: radio del vecindario de un punto
# - min_samples: mínimo de puntos en el vecindario para ser "core point"

dbscan = DBSCAN(eps=0.3, min_samples=5)
etiquetas_dbscan = dbscan.fit_predict(X_scaled)

n_clusters_db = len(set(etiquetas_dbscan)) - (1 if -1 in etiquetas_dbscan else 0)
n_ruido = (etiquetas_dbscan == -1).sum()

print(f"Clusters encontrados: {n_clusters_db}")
print(f"Puntos de ruido (anomalías): {n_ruido}")
print(f"Distribución: {np.unique(etiquetas_dbscan, return_counts=True)}")

if len(set(etiquetas_dbscan)) > 1 and n_clusters_db > 1:
    sil_db = silhouette_score(X_scaled, etiquetas_dbscan)
    print(f"Silhouette Score: {sil_db:.4f}")

# =============================================================================
# SECCIÓN 5: Clustering Jerárquico
# =============================================================================
print("\n--- 5. Clustering Jerárquico ---")

# AgglomerativeClustering: empieza con cada punto como su propio cluster
# y va fusionando los más cercanos hasta llegar a K clusters
# Ventaja: no necesitas especificar K si usas un dendrograma

hier = AgglomerativeClustering(n_clusters=4, linkage="ward")
etiquetas_hier = hier.fit_predict(X_scaled)

n_por_cluster = {i: (etiquetas_hier == i).sum() for i in range(4)}
print(f"Distribución de clusters: {n_por_cluster}")
sil_hier = silhouette_score(X_scaled, etiquetas_hier)
print(f"Silhouette Score: {sil_hier:.4f}")

# =============================================================================
# SECCIÓN 6: Visualización comparativa
# =============================================================================
print("\n--- 6. Visualización ---")

fig, axes = plt.subplots(2, 2, figsize=(14, 11))
fig.suptitle("Comparación de Algoritmos de Clustering", fontsize=14, fontweight="bold")

colores = ["#E53935", "#1E88E5", "#43A047", "#FB8C00", "#8E24AA"]
cmap = plt.cm.get_cmap("Set1", 5)

# Gráfico 1: K-Means
scatter1 = axes[0, 0].scatter(X[:, 0], X[:, 1], c=etiquetas_kmeans,
                               cmap="Set1", alpha=0.6, s=30)
axes[0, 0].scatter(centroides[:, 0], centroides[:, 1],
                   c="black", marker="X", s=200, zorder=5, label="Centroides")
axes[0, 0].set_title(f"K-Means (K=4)\nSilhouette={sil_kmeans:.3f}")
axes[0, 0].set_xlabel("Frecuencia de Compra")
axes[0, 0].set_ylabel("Ticket Promedio (€)")
axes[0, 0].legend()

# Gráfico 2: DBSCAN
colores_db = ["gray" if l == -1 else cmap(l) for l in etiquetas_dbscan]
axes[0, 1].scatter(X[:, 0], X[:, 1], c=colores_db, alpha=0.6, s=30)
axes[0, 1].set_title(f"DBSCAN (eps=0.3)\n{n_clusters_db} clusters, {n_ruido} ruido")
axes[0, 1].set_xlabel("Frecuencia de Compra")
axes[0, 1].set_ylabel("Ticket Promedio (€)")

# Gráfico 3: Elbow Method
axes[1, 0].plot(list(rango_k), inercias, "bo-", linewidth=2, markersize=8)
axes[1, 0].axvline(k_optimo, color="red", linestyle="--", alpha=0.7)
axes[1, 0].set_title("Elbow Method — Inercia vs K")
axes[1, 0].set_xlabel("Número de Clusters (K)")
axes[1, 0].set_ylabel("Inercia")

# Gráfico 4: Silhouette vs K
axes[1, 1].plot(list(rango_k), silhouettes, "go-", linewidth=2, markersize=8)
axes[1, 1].axvline(k_optimo, color="red", linestyle="--",
                   alpha=0.7, label=f"K óptimo={k_optimo}")
axes[1, 1].set_title("Silhouette Score vs K")
axes[1, 1].set_xlabel("Número de Clusters (K)")
axes[1, 1].set_ylabel("Silhouette Score")
axes[1, 1].legend()

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "clustering_comparacion.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Gráfico guardado: {ruta}")

# =============================================================================
# SECCIÓN 7: Interpretar y nombrar los clusters (paso de negocio)
# =============================================================================
print("\n--- 7. Interpretación de Clusters ---")

df_clientes = pd.DataFrame(X, columns=["frecuencia", "ticket"])
df_clientes["cluster"] = etiquetas_kmeans

resumen_clusters = df_clientes.groupby("cluster").agg({
    "frecuencia": ["mean", "std"],
    "ticket": ["mean", "std", "count"]
}).round(1)
print("\nResumen por cluster:")
print(resumen_clusters)

nombres_clusters = {
    0: "Compradores Frecuentes Económicos",
    1: "Clientes Premium Selectivos",
    2: "Compradores Moderados",
    3: "Clientes Frecuentes Medios"
}
print(f"\nNombres asignados (requiere interpretación humana):")
for idx, nombre in nombres_clusters.items():
    n_clientes = (etiquetas_kmeans == idx).sum()
    print(f"  Cluster {idx}: {nombre} ({n_clientes} clientes)")

print("\n" + "=" * 60)
print("Fin de Clustering — Continúa con 06_sklearn_pipeline.py")
print("=" * 60)
