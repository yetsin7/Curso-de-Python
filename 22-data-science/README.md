# Capítulo 22 — Data Science con Python

## ¿Qué es Data Science?

Data Science (Ciencia de Datos) es la disciplina que combina estadística, programación y conocimiento del negocio para **extraer valor de los datos**. Un Data Scientist recopila, limpia, analiza y visualiza datos para responder preguntas importantes y apoyar la toma de decisiones.

Python se convirtió en el lenguaje dominante de Data Science por tres razones:
1. Su sintaxis clara permite enfocarse en los datos, no en el código
2. Tiene el ecosistema de librerías más rico del mundo para análisis numérico
3. La comunidad científica y académica lo adoptó masivamente

---

## El Stack de Python para Data Science

```
NumPy       → Matemáticas numéricas rápidas (arrays, álgebra lineal)
Pandas      → Manipulación y análisis de datos tabulares (DataFrames)
Matplotlib  → Visualización base, control total sobre los gráficos
Seaborn     → Visualización estadística de alto nivel sobre Matplotlib
Scikit-learn → Machine Learning (ver Capítulo 23)
```

Instalación del stack completo:

```bash
pip install numpy pandas matplotlib seaborn
```

O con un entorno dedicado (recomendado):

```bash
python -m venv ds_env
source ds_env/bin/activate  # Linux/Mac
ds_env\Scripts\activate     # Windows
pip install numpy pandas matplotlib seaborn jupyter
```

---

## El Flujo de un Proyecto de Data Science

```
1. PROBLEMA       → Definir la pregunta de negocio
2. DATOS          → Recopilar y almacenar datos relevantes
3. LIMPIEZA       → Manejar valores nulos, duplicados, tipos incorrectos
4. EDA            → Análisis Exploratorio de Datos (distribuciones, correlaciones)
5. MODELADO       → Aplicar estadística o Machine Learning
6. EVALUACIÓN     → Validar resultados
7. COMUNICACIÓN   → Visualizaciones y reportes para stakeholders
8. DEPLOY         → Poner el modelo o análisis en producción
```

Los archivos de este capítulo cubren los pasos 2-4 (el núcleo del análisis).

---

## Jupyter Notebooks

Jupyter Notebook es el entorno interactivo estándar para Data Science. Combina:
- Celdas de código Python ejecutables
- Celdas de texto con formato Markdown
- Visualización inline de gráficos
- Narrativa + código en un solo documento

**Instalación y uso:**
```bash
pip install jupyter
jupyter notebook          # Abre en el navegador
# O la versión moderna:
pip install jupyterlab
jupyter lab
```

Los archivos `.py` de este capítulo son equivalentes a notebooks pero en formato de script puro, ejecutables desde la terminal con `python nombre_archivo.py`.

---

## Archivos del Capítulo

| Archivo | Tema |
|---------|------|
| `01_numpy_basico.py` | Arrays NumPy, operaciones vectorizadas, indexing |
| `02_numpy_avanzado.py` | Random, estadísticas, sorting, concatenación |
| `03_pandas_basico.py` | Series, DataFrame, lectura, filtros, selección |
| `04_pandas_avanzado.py` | GroupBy, merge, pivot, fechas, valores nulos |
| `05_matplotlib_basico.py` | Gráficos: línea, barras, histograma, scatter, pie |
| `06_seaborn_y_visualizacion.py` | Visualización estadística avanzada |
| `07_analisis_exploratorio.py` | EDA completo con dataset de ventas ficticias |

---

## Conceptos Clave

**Array vs Lista Python:**
- Una lista puede contener tipos mixtos: `[1, "dos", 3.0]`
- Un array NumPy es homogéneo: todos los elementos del mismo tipo
- Esto permite operaciones vectorizadas ultra-rápidas en C por debajo

**DataFrame:**
- Una tabla bidimensional con etiquetas en filas y columnas
- Como una hoja de Excel, pero programable y sin límite de filas

**EDA (Exploratory Data Analysis):**
- Proceso de "conocer" los datos antes de modelarlos
- ¿Cuántas filas/columnas? ¿Hay nulos? ¿Qué distribuciones tienen? ¿Hay outliers? ¿Correlaciones?

---

## Prerequisitos

- Capítulo 1-5 (Python básico)
- Capítulo 11 (comprensiones de listas — útiles con Pandas)
- Opcional: Matemáticas de bachillerato (media, desviación estándar)
