# Capítulo 23 — Machine Learning con Python

## ¿Qué es Machine Learning?

Machine Learning (Aprendizaje Automático) es una rama de la Inteligencia Artificial donde los sistemas **aprenden patrones de los datos** sin ser programados explícitamente para cada caso.

En lugar de escribir reglas manualmente ("si el email contiene 'GRATIS' y viene de un remitente desconocido, es spam"), entrenamos un modelo con miles de ejemplos de spam y no-spam, y el modelo aprende las reglas por sí solo.

---

## Tipos de Machine Learning

### 1. Aprendizaje Supervisado
Los datos de entrenamiento tienen **etiquetas** (la respuesta correcta).

- **Regresión**: predecir un número continuo → precio de casa, temperatura mañana
- **Clasificación**: predecir una categoría → spam/no-spam, diagnóstico médico

### 2. Aprendizaje No Supervisado
Los datos **NO tienen etiquetas**. El modelo descubre estructura por sí solo.

- **Clustering**: agrupar datos similares → segmentación de clientes
- **Reducción de dimensionalidad**: comprimir datos → PCA, t-SNE
- **Detección de anomalías**: identificar datos inusuales → fraude bancario

### 3. Aprendizaje por Refuerzo
Un agente aprende por **prueba y error** con recompensas y penalizaciones.
- Videojuegos (AlphaGo, OpenAI Five)
- Robots
- Trading algorítmico

---

## El Flujo de un Proyecto ML

```
1. DEFINIR EL PROBLEMA
   ¿Es clasificación o regresión? ¿Qué métrica importa?

2. RECOPILAR DATOS
   Más datos generalmente = mejor modelo

3. EDA (Análisis Exploratorio)
   Ver Capítulo 22 — limpiar, entender, visualizar

4. PREPROCESAMIENTO
   Escalar features, codificar categorías, manejar nulos

5. DIVIDIR: Train / Validation / Test
   Nunca evaluar con los mismos datos con que se entrenó

6. SELECCIONAR Y ENTRENAR MODELO
   Empezar simple (regresión lineal), subir complejidad si se necesita

7. EVALUAR
   Métricas correctas según el problema

8. OPTIMIZAR (Hyperparameter tuning)
   GridSearchCV, RandomSearchCV

9. MODELO FINAL + DEPLOY
   Guardar modelo, servir predicciones
```

---

## Scikit-learn — El Estándar para ML Clásico

Scikit-learn es la librería de Machine Learning más usada de Python porque:
- API uniforme: todos los modelos tienen `.fit()`, `.predict()`, `.score()`
- Más de 50 algoritmos listos para usar
- Herramientas de preprocesamiento, validación y selección de modelos
- Documentación ejemplar

```bash
pip install scikit-learn
```

---

## Cuándo Usar Qué

| Situación | Herramienta |
|-----------|-------------|
| Datos tabulares estructurados | Scikit-learn (ML clásico) |
| Imágenes / audio / secuencias complejas | Deep Learning (Capítulo 24) |
| < 1000 filas con relaciones claras | Estadística clásica |
| Muchas features, pocas filas | Regularización (Ridge, Lasso) |
| Producción a escala masiva | Scikit-learn + MLflow/Airflow |

---

## Instalación

```bash
pip install scikit-learn numpy pandas matplotlib seaborn joblib
```

---

## Archivos del Capítulo

| Archivo | Tema |
|---------|------|
| `01_ml_conceptos.py` | Features, labels, split, overfitting, datasets |
| `02_preprocesamiento.py` | Scalers, encoders, imputers, pipelines |
| `03_regresion.py` | Linear, Ridge, Lasso, métricas de regresión |
| `04_clasificacion.py` | Logistic, Decision Tree, Random Forest, SVM, KNN |
| `05_clustering.py` | K-Means, DBSCAN, silhouette score |
| `06_sklearn_pipeline.py` | Pipeline completo de producción |
