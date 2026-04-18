# =============================================================================
# CAPÍTULO 23 — Machine Learning con Python
# Archivo: 03_regresion.py
# Tema: Regresión — predecir valores numéricos continuos
# =============================================================================
#
# La regresión responde preguntas del tipo "¿cuánto?" o "¿qué valor?":
# - ¿Cuánto costará esta casa?
# - ¿Qué temperatura habrá mañana?
# - ¿Cuántas unidades venderemos el próximo mes?
#
# Modelos cubiertos:
# - Regresión Lineal: la más simple, relación directamente proporcional
# - Regresión Polinomial: relaciones curvilíneas
# - Ridge y Lasso: regresión con regularización para evitar overfitting
# =============================================================================

try:
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression, Ridge, Lasso
    from sklearn.preprocessing import PolynomialFeatures, StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
except ImportError as e:
    print(f"Librería faltante: {e}")
    print("Instala con: pip install scikit-learn numpy pandas matplotlib")
    exit(1)

import os
OUTPUT_DIR = "graficos_regresion"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("REGRESIÓN — Predecir valores numéricos")
print("=" * 60)

# =============================================================================
# DATASET: Precios de casas (generado con relaciones realistas)
# =============================================================================
np.random.seed(42)
n = 300

tamano_m2 = np.random.uniform(40, 350, n)
habitaciones = np.random.choice([1, 2, 3, 4, 5], n, p=[0.05, 0.20, 0.40, 0.25, 0.10])
antiguedad = np.random.uniform(0, 50, n)
distancia_centro = np.random.uniform(1, 30, n)

# Precio con relaciones múltiples + ruido (simula precios reales)
precio = (
    80000
    + tamano_m2 * 1800
    + habitaciones * 15000
    - antiguedad * 800
    - distancia_centro * 1200
    + np.random.normal(0, 20000, n)
).clip(50000, 800000)

df_casas = pd.DataFrame({
    "tamano_m2": tamano_m2,
    "habitaciones": habitaciones,
    "antiguedad": antiguedad,
    "distancia_centro": distancia_centro,
    "precio": precio
})

print(f"Dataset de casas: {df_casas.shape}")
print(f"\nEstadísticas:")
print(f"  Precio min: €{df_casas['precio'].min():,.0f}")
print(f"  Precio max: €{df_casas['precio'].max():,.0f}")
print(f"  Precio media: €{df_casas['precio'].mean():,.0f}")

# =============================================================================
# SECCIÓN 1: Métricas de regresión — qué miden y cuándo usarlas
# =============================================================================
print("\n--- 1. Métricas de Regresión ---")

def evaluar_modelo(nombre, y_real, y_pred):
    """
    Calcula y muestra las métricas principales de regresión.

    - MAE: Error Absoluto Medio — promedio de |predicción - real|
           Interpretable directamente en las unidades del target
    - MSE: Error Cuadrático Medio — penaliza más los errores grandes
    - RMSE: Raíz de MSE — mismas unidades que MAE, pero penaliza más outliers
    - R²: Coeficiente de determinación — 1.0 = perfecto, 0 = como predecir la media
           Negativo si el modelo es peor que simplemente predecir la media
    """
    mae = mean_absolute_error(y_real, y_pred)
    mse = mean_squared_error(y_real, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_real, y_pred)

    print(f"\n  {nombre}:")
    print(f"    MAE  (Error Abs. Medio):  €{mae:,.0f}")
    print(f"    RMSE (Raíz Error Cuad.):  €{rmse:,.0f}")
    print(f"    R²   (Coef. Determinac.): {r2:.4f}")
    return {"mae": mae, "rmse": rmse, "r2": r2}

# =============================================================================
# SECCIÓN 2: Regresión Lineal
# =============================================================================
print("\n--- 2. Regresión Lineal ---")

X = df_casas[["tamano_m2", "habitaciones", "antiguedad", "distancia_centro"]]
y = df_casas["precio"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# LinearRegression: encuentra la ecuación y = β0 + β1*x1 + β2*x2 + ...
# que minimiza la suma de errores cuadráticos (OLS — Ordinary Least Squares)
modelo_lineal = LinearRegression()
modelo_lineal.fit(X_train, y_train)

print(f"Coeficientes del modelo lineal:")
for feature, coef in zip(X.columns, modelo_lineal.coef_):
    print(f"  {feature:20s}: €{coef:+,.0f} por unidad")
print(f"  Intercepto (β0):      €{modelo_lineal.intercept_:,.0f}")

y_pred_lineal = modelo_lineal.predict(X_test)
metricas_lineal = evaluar_modelo("Regresión Lineal", y_test, y_pred_lineal)

# =============================================================================
# SECCIÓN 3: Regresión Polinomial — Para relaciones no lineales
# =============================================================================
print("\n--- 3. Regresión Polinomial ---")

# Solo con una variable para visualizar mejor la diferencia
X_simple = df_casas[["tamano_m2"]]
y_simple = df_casas["precio"]

X_s_train, X_s_test, y_s_train, y_s_test = train_test_split(
    X_simple, y_simple, test_size=0.2, random_state=42
)

resultados_poly = {}
for degree in [1, 2, 3, 5]:
    # PolynomialFeatures crea features x, x², x³, etc.
    pipeline_poly = Pipeline([
        ("poly", PolynomialFeatures(degree=degree, include_bias=False)),
        ("scaler", StandardScaler()),
        ("modelo", LinearRegression())
    ])
    pipeline_poly.fit(X_s_train, y_s_train)
    y_pred = pipeline_poly.predict(X_s_test)
    r2 = r2_score(y_s_test, y_pred)
    mae = mean_absolute_error(y_s_test, y_pred)
    resultados_poly[degree] = {"r2": r2, "mae": mae, "model": pipeline_poly}
    print(f"  Grado {degree}: R²={r2:.3f}, MAE=€{mae:,.0f}")

# =============================================================================
# SECCIÓN 4: Ridge y Lasso — Regularización
# =============================================================================
print("\n--- 4. Ridge y Lasso (Regularización) ---")

# Ridge (L2): agrega penalización α * Σβ² al costo
# Reduce el valor de TODOS los coeficientes pero no los lleva a cero
# Bueno cuando TODAS las features son relevantes pero quieres evitar overfitting

# Lasso (L1): agrega penalización α * Σ|β|
# Puede llevar coeficientes a exactamente 0 → selección automática de features
# Bueno cuando MUCHAS features son irrelevantes

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"\n{'Modelo':15s} | {'Alpha':>8s} | {'R² Test':>8s} | {'MAE':>12s}")
print("-" * 55)

for alpha in [0.1, 1.0, 10.0, 100.0]:
    ridge = Ridge(alpha=alpha)
    lasso = Lasso(alpha=alpha, max_iter=10000)

    ridge.fit(X_train_scaled, y_train)
    lasso.fit(X_train_scaled, y_train)

    r2_ridge = r2_score(y_test, ridge.predict(X_test_scaled))
    r2_lasso = r2_score(y_test, lasso.predict(X_test_scaled))

    mae_ridge = mean_absolute_error(y_test, ridge.predict(X_test_scaled))
    mae_lasso = mean_absolute_error(y_test, lasso.predict(X_test_scaled))

    coef_lasso_cero = (np.abs(lasso.coef_) < 0.001).sum()

    print(f"{'Ridge':15s} | {alpha:8.1f} | {r2_ridge:8.3f} | €{mae_ridge:>10,.0f}")
    print(f"{'Lasso':15s} | {alpha:8.1f} | {r2_lasso:8.3f} | €{mae_lasso:>10,.0f}"
          f"  (coef=0: {coef_lasso_cero})")

# =============================================================================
# SECCIÓN 5: Visualización — Predicciones vs Valores Reales
# =============================================================================
print("\n--- 5. Visualización de resultados ---")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Regresión — Evaluación Visual", fontsize=13, fontweight="bold")

# Gráfico 1: Predicciones vs Valores Reales
# La línea diagonal perfecta significa predicción = realidad
axes[0].scatter(y_test, y_pred_lineal, alpha=0.5, s=30, color="steelblue")
min_val = min(y_test.min(), y_pred_lineal.min())
max_val = max(y_test.max(), y_pred_lineal.max())
axes[0].plot([min_val, max_val], [min_val, max_val], "r--", linewidth=2, label="Perfecta")
axes[0].set_title(f"Predicción vs Real\nR²={metricas_lineal['r2']:.3f}")
axes[0].set_xlabel("Precio Real (€)")
axes[0].set_ylabel("Precio Predicho (€)")
axes[0].legend()

# Gráfico 2: Residuos — distribución del error
residuos = y_test.values - y_pred_lineal
axes[1].scatter(y_pred_lineal, residuos, alpha=0.5, s=30, color="coral")
axes[1].axhline(0, color="red", linewidth=2, linestyle="--")
axes[1].set_title("Gráfico de Residuos\n(debe ser aleatorio alrededor de 0)")
axes[1].set_xlabel("Precio Predicho (€)")
axes[1].set_ylabel("Residuo (Real - Predicho)")

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "regresion_evaluacion.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Gráfico guardado: {ruta}")

# Validación cruzada — estimación más confiable del rendimiento real
cv_scores = cross_val_score(
    LinearRegression(), X, y,
    cv=5, scoring="r2"
)
print(f"\nValidación cruzada (5-fold) — R²:")
print(f"  Scores: {cv_scores.round(3)}")
print(f"  Media: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

print("\n" + "=" * 60)
print("Fin de Regresión — Continúa con 04_clasificacion.py")
print("=" * 60)
