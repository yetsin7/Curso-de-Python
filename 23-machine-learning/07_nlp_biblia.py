"""
NLP Aplicado a la Biblia con scikit-learn
==========================================
Procesamiento de lenguaje natural sobre los versículos de la Biblia RV60:
  - Cargar versículos en DataFrame
  - TF-IDF para términos representativos por libro
  - Clustering de libros por similitud de vocabulario (KMeans)
  - Clasificador AT/NT con LogisticRegression
  - Evaluación con precision/recall/F1

Dependencias:
    pip install pandas scikit-learn

Ruta a BD: ../../datos/biblia_rv60.sqlite3
"""

import os
import re
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')

try:
    import pandas as pd
    PANDAS_OK = True
except ImportError:
    PANDAS_OK = False
    print("[AVISO] pip install pandas")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    from sklearn.pipeline import Pipeline
    import numpy as np
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False
    print("[AVISO] pip install scikit-learn")

# Stopwords mínimas para reducir ruido en TF-IDF
STOPWORDS = [
    "de", "la", "el", "en", "y", "a", "que", "los", "las", "se",
    "del", "con", "su", "por", "para", "un", "una", "le", "lo",
    "me", "te", "nos", "al", "más", "no", "ni", "es", "son", "fue",
    "ser", "mi", "tu", "sus", "esto", "esta", "este", "como", "pero",
    "si", "sobre", "todo", "yo", "él", "ella", "ellos", "les", "o",
    "era", "e", "ha", "hay", "ya", "porque", "cuando", "hasta",
    "entre", "sin", "muy", "así", "tan", "ante", "tras", "bajo",
]


def limpiar_strong(texto: str) -> str:
    """
    Elimina marcas Strong <S>NNNN</S> del texto bíblico.

    Args:
        texto: Texto crudo con marcas numéricas.

    Returns:
        Texto limpio en minúsculas.
    """
    limpio = re.sub(r'<S>\d+</S>', '', texto).strip()
    return limpio.lower()


def cargar_datos() -> tuple:
    """
    Carga books y verses de la BD en DataFrames.
    Limpia el texto y agrega columna 'testamento'.

    Returns:
        Tupla (df_books, df_verses) listos para análisis NLP.
    """
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] BD no encontrada: {DB_PATH}")
        return None, None

    conn = sqlite3.connect(DB_PATH)
    df_books  = pd.read_sql("SELECT * FROM books",  conn)
    df_verses = pd.read_sql("SELECT * FROM verses", conn)
    conn.close()

    df_verses["text_clean"] = df_verses["text"].apply(limpiar_strong)
    df_verses["testamento"] = df_verses["book_number"].apply(
        lambda n: "AT" if n <= 390 else "NT"
    )

    print(f"  Cargados {len(df_verses):,} versículos de {len(df_books)} libros.")
    return df_books, df_verses


# ===========================================================================
# Ejercicio 1: TF-IDF — términos representativos por libro
# ===========================================================================

def tfidf_por_libro(df_verses: "pd.DataFrame", df_books: "pd.DataFrame") -> None:
    """
    Calcula TF-IDF agrupando todos los versículos de cada libro
    como un 'documento' y muestra los 5 términos más representativos
    de cada libro seleccionado.

    TF-IDF mide cuán importante es una palabra para un libro
    en relación al resto de la Biblia.

    Args:
        df_verses: DataFrame de versículos con 'text_clean' y 'book_number'.
        df_books : DataFrame de libros con 'long_name'.
    """
    print("\n=== TF-IDF: Términos representativos por libro ===")

    # Agrupar versículos por libro → un documento por libro
    corpus = (
        df_verses.groupby("book_number")["text_clean"]
        .apply(lambda textos: " ".join(textos))
        .reset_index()
        .merge(df_books[["book_number", "long_name"]], on="book_number")
    )

    vectorizer = TfidfVectorizer(
        stop_words=STOPWORDS,
        max_features=5000,
        min_df=2,
        token_pattern=r'\b[a-záéíóúñü]{3,}\b'
    )

    tfidf_matrix = vectorizer.fit_transform(corpus["text_clean"])
    feature_names = vectorizer.get_feature_names_out()

    # Mostrar top 5 términos para algunos libros representativos
    libros_muestra = ["Génesis", "Salmos", "Isaías", "Marcos", "Apocalipsis"]
    for nombre in libros_muestra:
        fila = corpus[corpus["long_name"].str.contains(nombre, case=False)]
        if fila.empty:
            continue
        idx    = fila.index[0]
        scores = tfidf_matrix[idx].toarray()[0]
        top5   = scores.argsort()[-5:][::-1]
        terminos = ", ".join(feature_names[i] for i in top5)
        print(f"  {nombre:<15}: {terminos}")


# ===========================================================================
# Ejercicio 2: Clustering de libros por similitud de vocabulario
# ===========================================================================

def clustering_libros(df_verses: "pd.DataFrame", df_books: "pd.DataFrame") -> None:
    """
    Agrupa los 66 libros de la Biblia en clusters según la similitud
    de su vocabulario usando KMeans sobre vectores TF-IDF.

    Esto puede revelar agrupaciones naturales (libros proféticos,
    evangelios, epístolas, etc.).

    Args:
        df_verses: DataFrame de versículos.
        df_books : DataFrame de libros.
    """
    print("\n=== Clustering de libros por vocabulario (KMeans, k=5) ===")

    corpus = (
        df_verses.groupby("book_number")["text_clean"]
        .apply(lambda t: " ".join(t))
        .reset_index()
        .merge(df_books[["book_number", "long_name"]], on="book_number")
    )

    vectorizer = TfidfVectorizer(
        stop_words=STOPWORDS,
        max_features=2000,
        token_pattern=r'\b[a-záéíóúñü]{3,}\b'
    )
    X = vectorizer.fit_transform(corpus["text_clean"])

    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    corpus["cluster"] = kmeans.fit_predict(X)

    for cluster_id in range(5):
        libros_cluster = corpus[corpus["cluster"] == cluster_id]["long_name"].tolist()
        print(f"\n  Cluster {cluster_id + 1} ({len(libros_cluster)} libros):")
        print(f"    {', '.join(libros_cluster[:8])}{'…' if len(libros_cluster) > 8 else ''}")


# ===========================================================================
# Ejercicio 3: Clasificador AT vs NT con LogisticRegression
# ===========================================================================

def clasificador_at_nt(df_verses: "pd.DataFrame") -> None:
    """
    Entrena un clasificador de texto para predecir si un versículo
    pertenece al Antiguo (AT) o Nuevo Testamento (NT).

    Pipeline: TF-IDF → LogisticRegression
    Evalúa con precision, recall y F1-score.

    Args:
        df_verses: DataFrame de versículos con 'text_clean' y 'testamento'.
    """
    print("\n=== Clasificador AT/NT con LogisticRegression ===")

    # Muestra balanceada para entrenamiento más justo
    at = df_verses[df_verses["testamento"] == "AT"].sample(n=5000, random_state=42)
    nt = df_verses[df_verses["testamento"] == "NT"].sample(n=5000, random_state=42)
    df_sample = pd.concat([at, nt]).sample(frac=1, random_state=42)

    X = df_sample["text_clean"]
    y = df_sample["testamento"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Pipeline: TF-IDF + clasificador
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words=STOPWORDS,
            max_features=3000,
            token_pattern=r'\b[a-záéíóúñü]{3,}\b'
        )),
        ("clf", LogisticRegression(max_iter=1000, C=1.0, random_state=42)),
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    print("\n  Reporte de clasificación:")
    print(classification_report(y_test, y_pred, target_names=["AT", "NT"]))

    # Probar con versículos de ejemplo
    ejemplos = [
        "En el principio creó Dios los cielos y la tierra",          # Génesis → AT
        "Porque de tal manera amó Dios al mundo que dio a su Hijo",  # Juan 3:16 → NT
        "El Señor es mi pastor nada me faltará",                     # Salmos → AT
        "La gracia de nuestro Señor Jesucristo sea con todos vosotros", # Apocalipsis → NT
    ]

    print("\n  Predicciones de ejemplo:")
    predicciones = pipeline.predict(ejemplos)
    for texto, pred in zip(ejemplos, predicciones):
        print(f"  [{pred}] {texto[:60]}…")


# ===========================================================================
# Punto de entrada
# ===========================================================================

def main() -> None:
    """
    Ejecuta el pipeline completo de NLP sobre la Biblia.
    """
    print("=" * 60)
    print("  NLP APLICADO A LA BIBLIA — scikit-learn")
    print("=" * 60)

    if not PANDAS_OK or not SKLEARN_OK:
        print("\n  [ERROR] Dependencias faltantes:")
        print("  pip install pandas scikit-learn")
        return

    df_books, df_verses = cargar_datos()
    if df_verses is None:
        return

    tfidf_por_libro(df_verses, df_books)
    clustering_libros(df_verses, df_books)
    clasificador_at_nt(df_verses)

    print("\n✓ Análisis NLP completado.")


if __name__ == "__main__":
    main()
