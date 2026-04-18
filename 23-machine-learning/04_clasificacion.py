# =============================================================================
# CAPÍTULO 23 — Machine Learning con Python
# Archivo: 04_clasificacion.py
# Tema: Clasificación — predecir categorías
# =============================================================================
#
# La clasificación responde preguntas del tipo "¿a qué categoría pertenece?":
# - ¿Es spam o no es spam?
# - ¿Tiene cáncer o no tiene cáncer?
# - ¿Qué dígito es? (0-9)
#
# Modelos cubiertos:
# - Logistic Regression: a pesar del nombre, es un clasificador
# - Decision Tree: árbol de decisiones interpretable
# - Random Forest: conjunto de árboles, más robusto
# - SVM: máquina de vectores de soporte
# - KNN: K vecinos más cercanos
# =============================================================================

try:
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        confusion_matrix, classification_report, roc_auc_score, roc_curve
    )
except ImportError as e:
    print(f"Librería faltante: {e}")
    print("Instala con: pip install scikit-learn numpy pandas matplotlib seaborn")
    exit(1)

import os
OUTPUT_DIR = "graficos_clasificacion"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("CLASIFICACIÓN — Predecir categorías con ML")
print("=" * 60)

# =============================================================================
# DATASET: Diagnóstico médico simplificado (tumor benigno vs maligno)
# =============================================================================
np.random.seed(42)

# Dataset sintético de clasificación binaria
X, y = make_classification(
    n_samples=800,
    n_features=8,
    n_informative=5,
    n_redundant=2,
    n_classes=2,
    class_sep=1.2,
    random_state=42
)

feature_names = [f"marcador_{i+1}" for i in range(X.shape[1])]
clase_nombres = ["Benigno", "Maligno"]

print(f"Dataset médico sintético: {X.shape[0]} pacientes, {X.shape[1]} marcadores")
print(f"Clases: {np.unique(y, return_counts=True)}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Escalar features — necesario para Logistic Regression, SVM y KNN
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# =============================================================================
# SECCIÓN 1: Métricas de clasificación — Qué miden
# =============================================================================
print("\n--- 1. Métricas de Clasificación ---")
print("""
ACCURACY — Porcentaje de predicciones correctas
  Problema: con datos desbalanceados (95% clase A), predecir siempre A da 95% accuracy

PRECISION — De todos los que predije como Positivos, ¿cuántos eran realmente Positivos?
  Importante cuando: el costo de un Falso Positivo es alto
  Ejemplo: filtro de spam — no quiero marcar emails legítimos como spam

RECALL (Sensitividad) — De todos los Positivos reales, ¿cuántos detecté?
  Importante cuando: el costo de un Falso Negativo es alto
  Ejemplo: diagnóstico de cáncer — no quiero perderme ningún caso real

F1-SCORE — Media armónica de Precision y Recall (equilibra ambos)
  Útil cuando hay desbalance de clases

ROC-AUC — Área bajo la curva ROC
  Mide la capacidad del modelo de distinguir entre clases
  0.5 = aleatorio, 1.0 = perfecto
""")

def evaluar_clasificador(nombre, y_real, y_pred, y_prob=None):
    """Evalúa un clasificador y muestra todas las métricas relevantes."""
    acc = accuracy_score(y_real, y_pred)
    prec = precision_score(y_real, y_pred)
    rec = recall_score(y_real, y_pred)
    f1 = f1_score(y_real, y_pred)
    auc = roc_auc_score(y_real, y_prob) if y_prob is not None else None

    print(f"\n  {nombre}:")
    print(f"    Accuracy:  {acc:.3f}")
    print(f"    Precision: {prec:.3f}")
    print(f"    Recall:    {rec:.3f}")
    print(f"    F1-Score:  {f1:.3f}")
    if auc:
        print(f"    ROC-AUC:   {auc:.3f}")
    return {"acc": acc, "prec": prec, "rec": rec, "f1": f1, "auc": auc}

# =============================================================================
# SECCIÓN 2: Entrenar y comparar múltiples modelos
# =============================================================================
print("\n--- 2. Comparación de Modelos ---")

modelos = {
    "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "SVM": SVC(kernel="rbf", probability=True, random_state=42),
    "KNN (k=5)": KNeighborsClassifier(n_neighbors=5)
}

resultados = {}
roc_data = {}

for nombre, modelo in modelos.items():
    # Los modelos de árbol no necesitan escalar, pero no daña hacerlo
    modelo.fit(X_train_s, y_train)
    y_pred = modelo.predict(X_test_s)
    y_prob = modelo.predict_proba(X_test_s)[:, 1]

    metricas = evaluar_clasificador(nombre, y_test, y_pred, y_prob)
    resultados[nombre] = metricas

    # Guardar datos ROC para visualización
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_data[nombre] = (fpr, tpr, metricas["auc"])

# =============================================================================
# SECCIÓN 3: Confusion Matrix — Visualizar errores del modelo
# =============================================================================
print("\n--- 3. Confusion Matrix ---")

# El mejor modelo (Random Forest) para la confusion matrix
mejor_modelo = RandomForestClassifier(n_estimators=100, random_state=42)
mejor_modelo.fit(X_train_s, y_train)
y_pred_mejor = mejor_modelo.predict(X_test_s)

cm = confusion_matrix(y_test, y_pred_mejor)
print(f"\nConfusion Matrix (Random Forest):")
print(cm)
print(f"\nInterpretación:")
print(f"  Verdaderos Negativos (TN): {cm[0,0]} — predijo Benigno, era Benigno ✓")
print(f"  Falsos Positivos (FP):     {cm[0,1]} — predijo Maligno, era Benigno ✗")
print(f"  Falsos Negativos (FN):     {cm[1,0]} — predijo Benigno, era Maligno ✗ (peligroso)")
print(f"  Verdaderos Positivos (TP): {cm[1,1]} — predijo Maligno, era Maligno ✓")

print(f"\nReporte completo (Random Forest):")
print(classification_report(y_test, y_pred_mejor, target_names=clase_nombres))

# Importancia de features (solo para Random Forest)
importancias = mejor_modelo.feature_importances_
feat_imp = pd.DataFrame({
    "feature": feature_names,
    "importancia": importancias
}).sort_values("importancia", ascending=False)
print(f"Importancia de features:")
print(feat_imp.to_string(index=False))

# =============================================================================
# SECCIÓN 4: Visualizaciones
# =============================================================================
print("\n--- 4. Visualizaciones ---")

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Evaluación de Clasificadores", fontsize=13, fontweight="bold")

# Gráfico 1: Confusion Matrix
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=clase_nombres, yticklabels=clase_nombres, ax=axes[0])
axes[0].set_title("Confusion Matrix\n(Random Forest)")
axes[0].set_ylabel("Real")
axes[0].set_xlabel("Predicho")

# Gráfico 2: Curvas ROC de todos los modelos
for nombre, (fpr, tpr, auc) in roc_data.items():
    axes[1].plot(fpr, tpr, linewidth=1.5, label=f"{nombre} (AUC={auc:.2f})")
axes[1].plot([0, 1], [0, 1], "k--", linewidth=1, label="Aleatorio")
axes[1].set_title("Curvas ROC — Comparación")
axes[1].set_xlabel("Tasa de Falsos Positivos")
axes[1].set_ylabel("Tasa de Verdaderos Positivos")
axes[1].legend(fontsize=7, loc="lower right")

# Gráfico 3: Comparación de métricas
nombres_modelos = list(resultados.keys())
f1_scores = [resultados[n]["f1"] for n in nombres_modelos]
aucs = [resultados[n]["auc"] for n in nombres_modelos]

x = np.arange(len(nombres_modelos))
width = 0.35
axes[2].bar(x - width/2, f1_scores, width, label="F1", color="#1565C0", alpha=0.8)
axes[2].bar(x + width/2, aucs, width, label="AUC", color="#FF6F00", alpha=0.8)
axes[2].set_title("Comparación: F1 vs AUC")
axes[2].set_xticks(x)
axes[2].set_xticklabels([n.replace(" ", "\n") for n in nombres_modelos], fontsize=7)
axes[2].set_ylim(0, 1.1)
axes[2].legend()
axes[2].axhline(0.9, color="red", linestyle="--", alpha=0.5, linewidth=1)

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "clasificacion_evaluacion.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Gráfico guardado: {ruta}")

print("\n" + "=" * 60)
print("Fin de Clasificación — Continúa con 05_clustering.py")
print("=" * 60)
