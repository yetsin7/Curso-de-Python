# =============================================================================
# CAPÍTULO 23 — Machine Learning con Python
# Archivo: 02_preprocesamiento.py
# Tema: Preprocesamiento de datos para ML
# =============================================================================
#
# "Garbage in, garbage out" — si los datos de entrada son malos, el modelo
# producirá predicciones malas. El preprocesamiento convierte datos crudos
# del mundo real en un formato que los algoritmos de ML pueden procesar.
#
# Problemas comunes en datos reales:
# - Escala muy diferente entre features (salario en miles, edad en decenas)
# - Variables categóricas (ML trabaja solo con números)
# - Valores faltantes (NaN)
# - Outliers extremos
# =============================================================================

try:
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import (
        StandardScaler, MinMaxScaler, RobustScaler,
        LabelEncoder, OneHotEncoder, OrdinalEncoder
    )
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score
except ImportError as e:
    print(f"Librería faltante: {e}")
    print("Instala con: pip install scikit-learn numpy pandas")
    exit(1)

print("=" * 60)
print("PREPROCESAMIENTO — Transformar datos para ML")
print("=" * 60)

# =============================================================================
# DATASET: Empleados con problemas típicos de datos reales
# =============================================================================
np.random.seed(42)
n = 100

df = pd.DataFrame({
    "edad": np.random.randint(22, 60, n).astype(float),
    "salario": np.random.randint(25000, 120000, n).astype(float),
    "años_exp": np.random.randint(0, 30, n).astype(float),
    "departamento": np.random.choice(["IT", "Ventas", "Marketing", "RRHH"], n),
    "nivel": np.random.choice(["Junior", "Mid", "Senior", "Lead"], n),
    "promovido": np.random.choice([0, 1], n, p=[0.6, 0.4])
})

# Introducir valores nulos artificialmente (simular datos reales)
idx_nulos_edad = np.random.choice(n, 8, replace=False)
idx_nulos_salario = np.random.choice(n, 5, replace=False)
idx_nulos_depto = np.random.choice(n, 6, replace=False)
df.loc[idx_nulos_edad, "edad"] = np.nan
df.loc[idx_nulos_salario, "salario"] = np.nan
df.loc[idx_nulos_depto, "departamento"] = np.nan

print(f"Dataset creado: {df.shape}")
print(f"\nNulos por columna:\n{df.isnull().sum()}")
print(f"\nPrimeras filas:\n{df.head()}")

# =============================================================================
# SECCIÓN 1: Escalado de features numéricas
# =============================================================================
print("\n--- 1. Escalado de Features ---")

# Problema: salario (25k-120k) vs edad (22-60) vs años_exp (0-30)
# Algoritmos como KNN, SVM, redes neuronales son sensibles a la escala
# Scikit-learn usa distancias, y 1 año = 1 año ≠ 1000 en salario

X_num = df[["edad", "salario", "años_exp"]].dropna()
print(f"\nAntes de escalar:")
print(f"  edad:     [{X_num['edad'].min():.0f}, {X_num['edad'].max():.0f}]")
print(f"  salario:  [{X_num['salario'].min():.0f}, {X_num['salario'].max():.0f}]")
print(f"  años_exp: [{X_num['años_exp'].min():.0f}, {X_num['años_exp'].max():.0f}]")

# StandardScaler: media=0, std=1 — el más común, bueno para distribuciones normales
std_scaler = StandardScaler()
X_std = std_scaler.fit_transform(X_num)
print(f"\nStandardScaler (media=0, std=1):")
print(f"  edad media: {X_std[:, 0].mean():.3f}, std: {X_std[:, 0].std():.3f}")

# MinMaxScaler: rango [0, 1] — útil cuando el rango específico importa
minmax = MinMaxScaler()
X_minmax = minmax.fit_transform(X_num)
print(f"\nMinMaxScaler (rango [0,1]):")
print(f"  salario min: {X_minmax[:, 1].min():.3f}, max: {X_minmax[:, 1].max():.3f}")

# RobustScaler: usa mediana e IQR — robusto frente a outliers extremos
robust = RobustScaler()
X_robust = robust.fit_transform(X_num)
print(f"\nRobustScaler (usa mediana, resistente a outliers)")
print(f"  Útil cuando hay valores extremos que no puedes eliminar")

# =============================================================================
# SECCIÓN 2: Imputación de valores nulos
# =============================================================================
print("\n--- 2. Imputación de Valores Nulos ---")

# SimpleImputer: rellena nulos con media, mediana, moda o valor constante
# strategy="mean" — para numéricos con distribución normal
# strategy="median" — mejor cuando hay outliers (mediana es más robusta)
# strategy="most_frequent" — para categóricas o cuando la moda tiene sentido

# Imputar columnas numéricas con la mediana
imputer_num = SimpleImputer(strategy="median")
X_numericas = df[["edad", "salario", "años_exp"]]
X_imputed = imputer_num.fit_transform(X_numericas)

print(f"Nulos en numéricas antes: {X_numericas.isnull().sum().sum()}")
print(f"Nulos en numéricas después: {np.isnan(X_imputed).sum()}")
print(f"Valores de imputación usados: {imputer_num.statistics_.round(1)}")

# Imputar columnas categóricas con la moda (most_frequent)
imputer_cat = SimpleImputer(strategy="most_frequent")
X_categoricas = df[["departamento"]]
X_cat_imputed = imputer_cat.fit_transform(X_categoricas)

print(f"\nNulos en departamento antes: {df['departamento'].isnull().sum()}")
print(f"Nulos en departamento después: {pd.isna(X_cat_imputed).sum()}")

# =============================================================================
# SECCIÓN 3: Codificación de variables categóricas
# =============================================================================
print("\n--- 3. Codificación de Categorías ---")

# Los algoritmos de ML necesitan NÚMEROS, no strings
# Existen varias estrategias:

# LabelEncoder: convierte categorías en 0, 1, 2, 3...
# SOLO para la variable objetivo (y), NO para features independientes
# porque introduce una relación de orden falsa (IT > RRHH > Marketing?)
le = LabelEncoder()
departamentos = ["IT", "Ventas", "Marketing", "RRHH"]
encoded = le.fit_transform(departamentos)
print(f"LabelEncoder:")
print(f"  Antes: {departamentos}")
print(f"  Después: {encoded}")
print(f"  Clases: {le.classes_}")
print(f"  Problema: implica IT < Marketing < RRHH < Ventas (¡falso!)")

# OneHotEncoder: crea una columna binaria por cada categoría (dummies)
# Elimina el problema del orden falso — es el método correcto para ML
ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
X_dept = np.array(departamentos).reshape(-1, 1)
X_ohe = ohe.fit_transform(X_dept)
print(f"\nOneHotEncoder:")
print(f"  Categorías: {ohe.categories_}")
print(f"  Resultado (cada columna = una categoría):\n{X_ohe}")
print(f"  Shape: {X_ohe.shape} — {len(departamentos)} filas × {len(departamentos)} cols")

# OrdinalEncoder: para categorías CON orden real
# Ejemplo: Junior < Mid < Senior < Lead (aquí sí tiene sentido el orden)
oe = OrdinalEncoder(categories=[["Junior", "Mid", "Senior", "Lead"]])
niveles = [["Junior"], ["Lead"], ["Mid"], ["Senior"]]
encoded_ord = oe.fit_transform(niveles)
print(f"\nOrdinalEncoder (con orden):")
for nivel, cod in zip(niveles, encoded_ord):
    print(f"  {nivel[0]:8s} → {cod[0]:.0f}")

# =============================================================================
# SECCIÓN 4: Pipeline de preprocesamiento completo
# =============================================================================
print("\n--- 4. Pipeline de Preprocesamiento ---")

# ColumnTransformer aplica transformaciones DIFERENTES a columnas DIFERENTES
# Muy útil cuando tienes columnas numéricas y categóricas en el mismo dataset

# Definir qué columnas son de cada tipo
columnas_numericas = ["edad", "salario", "años_exp"]
columnas_categoricas = ["departamento"]

# Pipeline para columnas numéricas: primero imputa, luego escala
pipeline_numerico = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

# Pipeline para columnas categóricas: primero imputa, luego OHE
pipeline_categorico = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
])

# ColumnTransformer combina ambos pipelines
preprocessor = ColumnTransformer([
    ("numericas", pipeline_numerico, columnas_numericas),
    ("categoricas", pipeline_categorico, columnas_categoricas)
])

# Preparar datos para entrenamiento
X = df[columnas_numericas + columnas_categoricas]
y = df["promovido"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Pipeline completo: preprocesamiento + modelo
pipeline_completo = Pipeline([
    ("preprocesamiento", preprocessor),
    ("modelo", LogisticRegression(random_state=42, max_iter=1000))
])

# fit() aplica TODA la cadena de transformaciones + entrenamiento
pipeline_completo.fit(X_train, y_train)

# predict() aplica las MISMAS transformaciones a los datos de test
y_pred = pipeline_completo.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Pipeline completo entrenado correctamente")
print(f"Shape de entrada:  {X_train.shape}")

# Obtener shape de salida del preprocesamiento
X_transformado = preprocessor.fit_transform(X_train)
print(f"Shape tras preprocesamiento: {X_transformado.shape}")
print(f"  (3 numéricas escaladas + 4 columnas OHE de departamento)")
print(f"\nAccuracy en test: {accuracy:.3f}")

# =============================================================================
# SECCIÓN 5: Por qué el pipeline es mejor que transformar manualmente
# =============================================================================
print("\n--- 5. Por qué usar Pipeline ---")

print("""
Sin Pipeline (código peligroso, no hagas esto):
    scaler.fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)  # Correcto: usa stats de train
    # Pero si te olvidas de este orden, contaminas el test con estadísticas
    # del train, lo cual da métricas falsamente optimistas.

Con Pipeline:
    pipeline.fit(X_train, y_train)        # Aprende stats de train
    pipeline.predict(X_test)              # Aplica stats de train al test
    # El orden es AUTOMÁTICO. No puedes equivocarte.
    # También funciona perfecto con cross-validation.
""")

print("\n" + "=" * 60)
print("Fin de Preprocesamiento — Continúa con 03_regresion.py")
print("=" * 60)
