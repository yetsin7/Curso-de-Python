# =============================================================================
# CAPÍTULO 23 — Machine Learning con Python
# Archivo: 01_ml_conceptos.py
# Tema: Conceptos fundamentales de ML con código
# =============================================================================
#
# Antes de usar modelos de ML, es esencial entender los conceptos básicos:
# ¿Qué son features y labels? ¿Por qué dividir en train/test? ¿Qué es
# overfitting y por qué destruye los modelos en producción?
# =============================================================================

try:
    import numpy as np
    import pandas as pd
    from sklearn import datasets
    from sklearn.model_selection import train_test_split, learning_curve
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.metrics import accuracy_score, mean_squared_error
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Librería faltante: {e}")
    print("Instala con: pip install scikit-learn numpy pandas matplotlib")
    exit(1)

import os
OUTPUT_DIR = "graficos_ml_conceptos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("ML CONCEPTOS — Features, Labels, Split y Overfitting")
print("=" * 60)

# =============================================================================
# SECCIÓN 1: Features vs Labels
# =============================================================================
print("\n--- 1. Features vs Labels ---")

# Dataset Iris: el "Hola Mundo" de ML — clasificar flores por medidas
iris = datasets.load_iris()

# X = Features (características de entrada) — lo que el modelo RECIBE
# Cada columna es una característica: largo sépalo, ancho sépalo, etc.
X = iris.data
print(f"Features (X) — shape: {X.shape}")
print(f"Nombres de features: {iris.feature_names}")
print(f"Primeras 3 filas de X:\n{X[:3]}")

# y = Labels (etiquetas de salida) — lo que el modelo PREDICE
# En clasificación: la clase a la que pertenece cada ejemplo
y = iris.target
print(f"\nLabels (y) — shape: {y.shape}")
print(f"Clases: {iris.target_names}")
print(f"Primeras 10 etiquetas: {y[:10]}")

# Distribución de clases — importante verificar que no esté desbalanceada
clases, conteos = np.unique(y, return_counts=True)
print(f"\nDistribución de clases:")
for clase, conteo in zip(iris.target_names, conteos):
    print(f"  {clase}: {conteo} ejemplos")

# =============================================================================
# SECCIÓN 2: Train / Test Split — La regla de oro del ML
# =============================================================================
print("\n--- 2. Train/Test Split ---")

# NUNCA evalúes el modelo con los mismos datos con que lo entrenaste.
# Si lo haces, mides cuánto MEMORIZÓ, no cuánto APRENDIÓ.
#
# Dividimos los datos en:
# - Entrenamiento (train): el modelo aprende de estos
# - Prueba (test): el modelo NUNCA los ve durante el entrenamiento
#   Los usamos solo al final para la evaluación final honesta

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,     # 20% para test, 80% para entrenamiento
    random_state=42,   # Semilla para reproducibilidad
    stratify=y         # Mantener la proporción de clases en ambos sets
)

print(f"Total de ejemplos: {len(X)}")
print(f"Entrenamiento:  X_train {X_train.shape}, y_train {y_train.shape}")
print(f"Prueba:         X_test  {X_test.shape},  y_test  {y_test.shape}")

# Verificar que la proporción de clases se mantiene (stratify=y lo garantiza)
print(f"\nClases en train: {np.unique(y_train, return_counts=True)[1]}")
print(f"Clases en test:  {np.unique(y_test,  return_counts=True)[1]}")

# =============================================================================
# SECCIÓN 3: Overfitting vs Underfitting
# =============================================================================
print("\n--- 3. Overfitting vs Underfitting ---")

# Overfitting (sobreajuste): el modelo memoriza el entrenamiento pero
# falla con datos nuevos. Causa: modelo demasiado complejo para los datos.
#
# Underfitting (subajuste): el modelo es demasiado simple y no captura
# los patrones, falla tanto en train como en test.
#
# El objetivo: bias-variance tradeoff — encontrar el punto de complejidad
# óptimo donde el modelo generaliza bien a datos nuevos.

# Demostración con un Decision Tree de distinta profundidad
print("\nDemostración de overfitting con árboles de distinta profundidad:")
print(f"{'Profundidad':>12} | {'Train Accuracy':>14} | {'Test Accuracy':>13} | Estado")
print("-" * 65)

for max_depth in [1, 2, 3, 4, 5, 8, 12, None]:
    modelo = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    modelo.fit(X_train, y_train)

    acc_train = accuracy_score(y_train, modelo.predict(X_train))
    acc_test = accuracy_score(y_test, modelo.predict(X_test))
    gap = acc_train - acc_test

    # Diagnosticar el estado del modelo
    if acc_train < 0.85 and acc_test < 0.85:
        estado = "Underfitting"
    elif gap > 0.05:
        estado = "Overfitting"
    else:
        estado = "Bien ajustado"

    profundidad_str = str(max_depth) if max_depth else "Ninguna"
    print(f"{profundidad_str:>12} | {acc_train:>13.3f} | {acc_test:>12.3f} | {estado}")

# =============================================================================
# SECCIÓN 4: Datasets de sklearn — Herramientas de práctica
# =============================================================================
print("\n--- 4. Datasets incluidos en sklearn ---")

# sklearn trae datasets listos para practicar, sin necesidad de descargar nada

# make_classification: genera un dataset sintético de clasificación
X_clf, y_clf = datasets.make_classification(
    n_samples=500,
    n_features=10,
    n_informative=5,   # 5 features realmente útiles
    n_redundant=2,     # 2 features redundantes (combinación de otros)
    n_classes=2,       # Clasificación binaria
    random_state=42
)
print(f"\nmake_classification: X={X_clf.shape}, y={y_clf.shape}")
print(f"  Clases: {np.unique(y_clf, return_counts=True)}")

# make_regression: dataset sintético de regresión
X_reg, y_reg = datasets.make_regression(
    n_samples=300,
    n_features=5,
    n_informative=3,
    noise=15.0,
    random_state=42
)
print(f"\nmake_regression: X={X_reg.shape}, y={y_reg.shape}")
print(f"  y range: [{y_reg.min():.1f}, {y_reg.max():.1f}]")

# make_blobs: clusters para clustering (Capítulo 23-05)
X_blob, y_blob = datasets.make_blobs(
    n_samples=300, centers=4, cluster_std=0.8, random_state=42
)
print(f"\nmake_blobs: X={X_blob.shape}, y (clusters)={y_blob.shape}")

# =============================================================================
# SECCIÓN 5: Visualización — Datos de ejemplo
# =============================================================================
print("\n--- 5. Visualización de conceptos ---")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Conceptos Fundamentales de ML", fontsize=13, fontweight="bold")

# Gráfico 1: Dataset clasificación (primeras 2 features)
scatter = axes[0].scatter(X_clf[:, 0], X_clf[:, 1], c=y_clf, cmap="bwr", alpha=0.6, s=20)
axes[0].set_title("Dataset de Clasificación\n(2 primeras features)")
axes[0].set_xlabel("Feature 1")
axes[0].set_ylabel("Feature 2")

# Gráfico 2: Curva de aprendizaje — muestra overfitting visualmente
# train_sizes: porcentajes del dataset de entrenamiento a usar
profundidades = [1, 2, 3, 4, 5, 6, 8, None]
train_scores = []
test_scores = []

for d in profundidades:
    m = DecisionTreeClassifier(max_depth=d, random_state=42)
    m.fit(X_train, y_train)
    train_scores.append(accuracy_score(y_train, m.predict(X_train)))
    test_scores.append(accuracy_score(y_test, m.predict(X_test)))

etiquetas_x = [str(d) if d else "∞" for d in profundidades]
axes[1].plot(etiquetas_x, train_scores, "o-", color="blue", label="Train", linewidth=2)
axes[1].plot(etiquetas_x, test_scores, "s-", color="red", label="Test", linewidth=2)
axes[1].fill_between(etiquetas_x, train_scores, test_scores, alpha=0.1, color="orange")
axes[1].set_title("Overfitting — Train vs Test\nsegun profundidad del árbol")
axes[1].set_xlabel("Profundidad Máxima")
axes[1].set_ylabel("Accuracy")
axes[1].legend()
axes[1].set_ylim(0.5, 1.05)

# Gráfico 3: Dataset de regresión
axes[2].scatter(X_reg[:, 0], y_reg, alpha=0.4, s=20, color="teal")
axes[2].set_title("Dataset de Regresión\n(Feature 1 vs Target)")
axes[2].set_xlabel("Feature 1")
axes[2].set_ylabel("Target (y)")

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "conceptos_ml.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Gráfico guardado: {ruta}")

print("\n" + "=" * 60)
print("Fin de Conceptos ML — Continúa con 02_preprocesamiento.py")
print("=" * 60)
