# =============================================================================
# CAPÍTULO 23 — Machine Learning con Python
# Archivo: 06_sklearn_pipeline.py
# Tema: Pipeline completo de producción con sklearn
# =============================================================================
#
# Este archivo muestra cómo construir un pipeline ML de nivel producción:
# - ColumnTransformer para preprocesar columnas heterogéneas
# - Pipeline encadenado con modelo
# - GridSearchCV para optimizar hiperparámetros automáticamente
# - cross_val_score para validación cruzada robusta
# - Guardar y cargar el modelo con joblib
# =============================================================================

try:
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.model_selection import (
        train_test_split, cross_val_score,
        GridSearchCV, StratifiedKFold
    )
    from sklearn.metrics import (
        classification_report, confusion_matrix,
        roc_auc_score, accuracy_score
    )
    import joblib
except ImportError as e:
    print(f"Librería faltante: {e}")
    print("Instala con: pip install scikit-learn numpy pandas matplotlib joblib")
    exit(1)

import os
import warnings
warnings.filterwarnings("ignore")

OUTPUT_DIR = "modelo_produccion"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 65)
print("SKLEARN PIPELINE DE PRODUCCIÓN — Completo, robusto, guardable")
print("=" * 65)

# =============================================================================
# PASO 1: Generar un dataset realista con columnas mixtas
# =============================================================================
print("\n--- PASO 1: Dataset de préstamos bancarios ---")

np.random.seed(2024)
N = 1000

# Datos de clientes solicitando préstamos
ingresos = np.random.lognormal(mean=10.5, sigma=0.5, size=N).astype(int)
edad = np.random.randint(18, 70, N)
deuda_actual = np.random.uniform(0, 50000, N).astype(int)
historial = np.random.choice(["Excelente", "Bueno", "Regular", "Malo"], N,
                              p=[0.25, 0.40, 0.25, 0.10])
tipo_empleo = np.random.choice(["Asalariado", "Autónomo", "Desempleado"], N,
                                p=[0.55, 0.30, 0.15])
meses_trabajo = np.random.randint(0, 240, N)

# Target: aprobado (1) o rechazado (0) — basado en lógica de negocio + ruido
probabilidad_base = (
    0.3 * (ingresos > 40000)
    + 0.2 * (deuda_actual < 15000)
    + 0.25 * (historial == "Excelente") + 0.15 * (historial == "Bueno")
    + 0.1 * (tipo_empleo == "Asalariado")
)
probabilidad_base = np.clip(probabilidad_base, 0.05, 0.95)
aprobado = (np.random.uniform(0, 1, N) < probabilidad_base).astype(int)

# Introducir nulos realistas
idx_nulos = np.random.choice(N, int(N * 0.08), replace=False)
ingresos_f = ingresos.astype(float)
ingresos_f[idx_nulos] = np.nan

df = pd.DataFrame({
    "ingresos": ingresos_f,
    "edad": edad,
    "deuda_actual": deuda_actual,
    "meses_trabajo": meses_trabajo,
    "historial_crediticio": historial,
    "tipo_empleo": tipo_empleo,
    "aprobado": aprobado
})

print(f"Dataset: {df.shape}")
print(f"Aprobados: {aprobado.sum()} ({aprobado.mean()*100:.1f}%)")
print(f"Rechazados: {(1-aprobado).sum()} ({(1-aprobado).mean()*100:.1f}%)")
print(f"Nulos en ingresos: {df['ingresos'].isnull().sum()}")

# =============================================================================
# PASO 2: Definir el pipeline de preprocesamiento
# =============================================================================
print("\n--- PASO 2: Definición del Pipeline ---")

# Separar features y target
X = df.drop("aprobado", axis=1)
y = df["aprobado"]

# Identificar tipos de columnas
COLS_NUMERICAS = ["ingresos", "edad", "deuda_actual", "meses_trabajo"]
COLS_CATEGORICAS = ["historial_crediticio", "tipo_empleo"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Train: {X_train.shape}, Test: {X_test.shape}")

# Pipeline numérico: imputar con mediana + escalar
pipeline_numerico = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

# Pipeline categórico: imputar con moda + codificar
pipeline_categorico = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
])

# ColumnTransformer aplica cada pipeline a sus columnas correspondientes
# "remainder='drop'" elimina columnas no especificadas
preprocessor = ColumnTransformer([
    ("numericas", pipeline_numerico, COLS_NUMERICAS),
    ("categoricas", pipeline_categorico, COLS_CATEGORICAS)
], remainder="drop")

# Pipeline completo: preprocesamiento + modelo
pipeline_final = Pipeline([
    ("preprocesamiento", preprocessor),
    ("modelo", RandomForestClassifier(n_estimators=100, random_state=42))
])

print("Pipeline definido:")
print(f"  Columnas numéricas: {COLS_NUMERICAS}")
print(f"  Columnas categóricas: {COLS_CATEGORICAS}")

# =============================================================================
# PASO 3: Validación cruzada con el pipeline
# =============================================================================
print("\n--- PASO 3: Validación Cruzada ---")

# StratifiedKFold mantiene la proporción de clases en cada fold
# Esto es esencial con datasets desbalanceados
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_scores = cross_val_score(pipeline_final, X_train, y_train,
                             cv=cv, scoring="roc_auc", n_jobs=-1)
print(f"Validación cruzada (5-fold) — ROC-AUC:")
print(f"  Scores: {cv_scores.round(4)}")
print(f"  Media:  {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# =============================================================================
# PASO 4: GridSearchCV — Optimización de hiperparámetros
# =============================================================================
print("\n--- PASO 4: GridSearchCV (Optimización de Hiperparámetros) ---")

# El prefijo "modelo__" accede a los parámetros del componente "modelo" del pipeline
param_grid = {
    "modelo__n_estimators": [50, 100, 150],
    "modelo__max_depth": [None, 5, 10],
    "modelo__min_samples_split": [2, 5]
}

print(f"Combinaciones a probar: {3 * 3 * 2}")

grid_search = GridSearchCV(
    pipeline_final,
    param_grid,
    cv=3,                # Menor para velocidad; en producción usar 5
    scoring="roc_auc",
    n_jobs=-1,           # Usar todos los núcleos disponibles
    verbose=0
)

grid_search.fit(X_train, y_train)

print(f"\nMejores hiperparámetros: {grid_search.best_params_}")
print(f"Mejor ROC-AUC (CV): {grid_search.best_score_:.4f}")

# El mejor modelo encontrado
mejor_pipeline = grid_search.best_estimator_

# =============================================================================
# PASO 5: Evaluación final en el conjunto de test
# =============================================================================
print("\n--- PASO 5: Evaluación en Test ---")

y_pred = mejor_pipeline.predict(X_test)
y_prob = mejor_pipeline.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)

print(f"\nAccuracy: {acc:.4f}")
print(f"ROC-AUC:  {auc:.4f}")
print(f"\nReporte de clasificación:")
print(classification_report(y_test, y_pred, target_names=["Rechazado", "Aprobado"]))

# =============================================================================
# PASO 6: Guardar y cargar el modelo con joblib
# =============================================================================
print("\n--- PASO 6: Guardar y Cargar el Modelo ---")

# joblib.dump / joblib.load: la forma estándar de persistir modelos sklearn
# El pipeline COMPLETO se guarda: preprocesamiento + modelo
ruta_modelo = os.path.join(OUTPUT_DIR, "pipeline_prestamos.joblib")
joblib.dump(mejor_pipeline, ruta_modelo)
print(f"Modelo guardado en: {ruta_modelo}")

# Cargar el modelo guardado
pipeline_cargado = joblib.load(ruta_modelo)
print(f"Modelo cargado: {type(pipeline_cargado).__name__}")

# Verificar que produce los mismos resultados
y_pred_cargado = pipeline_cargado.predict(X_test)
assert (y_pred == y_pred_cargado).all(), "ERROR: predicciones no coinciden"
print(f"Verificación: predicciones idénticas ✓")

# =============================================================================
# PASO 7: Predicción en producción — cómo usarlo en una app real
# =============================================================================
print("\n--- PASO 7: Simulación de producción ---")

# En producción, recibirías un dict con los datos del nuevo cliente
nuevo_cliente = pd.DataFrame([{
    "ingresos": 52000,
    "edad": 35,
    "deuda_actual": 8000,
    "meses_trabajo": 60,
    "historial_crediticio": "Bueno",
    "tipo_empleo": "Asalariado"
}])

prediccion = pipeline_cargado.predict(nuevo_cliente)[0]
probabilidad = pipeline_cargado.predict_proba(nuevo_cliente)[0, 1]

print(f"\nNuevo cliente: {nuevo_cliente.iloc[0].to_dict()}")
print(f"Decisión: {'APROBADO' if prediccion == 1 else 'RECHAZADO'}")
print(f"Probabilidad de aprobación: {probabilidad:.1%}")

# =============================================================================
# PASO 8: Visualización del desempeño
# =============================================================================
print("\n--- PASO 8: Gráficos de evaluación ---")

from sklearn.metrics import roc_curve

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Pipeline de Producción — Evaluación Final", fontsize=13)

# Curva ROC
fpr, tpr, _ = roc_curve(y_test, y_prob)
axes[0].plot(fpr, tpr, color="#1565C0", linewidth=2.5, label=f"ROC (AUC={auc:.3f})")
axes[0].plot([0, 1], [0, 1], "k--", linewidth=1)
axes[0].set_title("Curva ROC — Test Set")
axes[0].set_xlabel("Tasa de Falsos Positivos")
axes[0].set_ylabel("Tasa de Verdaderos Positivos")
axes[0].legend()

# Distribución de probabilidades predichas
axes[1].hist([y_prob[y_test == 0], y_prob[y_test == 1]],
             bins=25, label=["Rechazados", "Aprobados"],
             color=["#EF5350", "#66BB6A"], alpha=0.7, edgecolor="white")
axes[1].axvline(0.5, color="black", linestyle="--", linewidth=1.5, label="Umbral=0.5")
axes[1].set_title("Distribución de Probabilidades")
axes[1].set_xlabel("P(Aprobado)")
axes[1].set_ylabel("Frecuencia")
axes[1].legend()

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "evaluacion_final.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Gráfico guardado: {ruta}")

print("\n" + "=" * 65)
print("Fin del Capítulo 23 — ¡Pasa al Capítulo 24: Deep Learning!")
print("=" * 65)
