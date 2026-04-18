"""
Análisis de la Biblia con Pandas
==================================
Análisis completo de la Biblia Reina-Valera 1960 usando Pandas:
  1. Cargar BD en DataFrames
  2. Limpiar texto (quitar marcas Strong)
  3. Top 20 palabras más usadas (sin stopwords en español)
  4. Comparativa AT vs NT
  5. Gráfico de barras: versículos por libro (PNG)
  6. Heatmap de versículos por capítulo en Salmos
  7. WordCloud (conceptual)
  8. Top 10 versículos más ricos en vocabulario

Dependencias:
    pip install pandas matplotlib seaborn
    pip install wordcloud   ← opcional para ejercicio 7

Ruta a BD: ../../datos/biblia_rv60.sqlite3
"""

import os
import re
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')

# --- Importaciones con manejo de dependencias ---
try:
    import pandas as pd
    PANDAS_OK = True
except ImportError:
    PANDAS_OK = False
    print("[AVISO] Instala pandas: pip install pandas")

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use("Agg")  # modo sin pantalla, guarda en archivo
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False
    print("[AVISO] Instala matplotlib: pip install matplotlib")

try:
    import seaborn as sns
    SEABORN_OK = True
except ImportError:
    SEABORN_OK = False
    print("[AVISO] Instala seaborn: pip install seaborn")

# Stopwords en español para eliminar palabras vacías
STOPWORDS_ES = {
    "de", "la", "el", "en", "y", "a", "que", "los", "las", "se",
    "del", "con", "su", "por", "para", "un", "una", "le", "lo",
    "me", "te", "nos", "al", "más", "no", "ni", "es", "son", "fue",
    "ser", "mi", "tu", "sus", "sus", "esto", "esta", "este", "como",
    "pero", "si", "sobre", "todo", "yo", "él", "ella", "ellos", "les",
    "o", "era", "e", "ha", "hay", "has", "han", "he", "ya", "también",
    "porque", "cuando", "hasta", "entre", "sin", "muy", "así", "tan",
    "ante", "tras", "bajo", "sobre", "contra", "hacia", "desde", "que",
}


def limpiar_strong(texto: str) -> str:
    """
    Elimina marcas Strong <S>NNNN</S> del texto del versículo.

    Args:
        texto: Texto crudo con marcas numéricas Strong.

    Returns:
        Texto limpio, en minúsculas y sin puntuación extra.
    """
    return re.sub(r'<S>\d+</S>', '', texto).strip()


def verificar_bd() -> bool:
    """
    Verifica que la base de datos exista y sea accesible.

    Returns:
        True si la BD está disponible.
    """
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] BD no encontrada: {DB_PATH}")
        return False
    return True


# ===========================================================================
# Ejercicio 1: Cargar la BD en DataFrames
# ===========================================================================

def cargar_datos() -> tuple:
    """
    Carga las tablas `books` y `verses` de la BD en DataFrames de Pandas.
    Aplica limpieza de texto en la columna 'text'.

    Returns:
        Tupla (df_books, df_verses) con los DataFrames cargados.
    """
    conn = sqlite3.connect(DB_PATH)
    df_books  = pd.read_sql("SELECT * FROM books",  conn)
    df_verses = pd.read_sql("SELECT * FROM verses", conn)
    conn.close()

    print(f"  Libros: {len(df_books)} registros")
    print(f"  Versículos: {len(df_verses):,} registros")
    return df_books, df_verses


# ===========================================================================
# Ejercicio 2: Limpiar texto
# ===========================================================================

def limpiar_dataframe(df_verses: "pd.DataFrame") -> "pd.DataFrame":
    """
    Aplica limpieza de texto a la columna 'text' del DataFrame de versículos.
    Agrega columna 'text_clean' con el texto normalizado.

    Args:
        df_verses: DataFrame con columna 'text' cruda.

    Returns:
        DataFrame con columna adicional 'text_clean'.
    """
    df_verses = df_verses.copy()
    df_verses["text_clean"] = df_verses["text"].apply(limpiar_strong)

    # Agregar columna de testamento para análisis posterior
    df_verses["testamento"] = df_verses["book_number"].apply(
        lambda n: "AT" if n <= 390 else "NT"
    )

    print(f"  Texto limpio. Ejemplo: {df_verses['text_clean'].iloc[0][:60]}…")
    return df_verses


# ===========================================================================
# Ejercicio 3: Top 20 palabras más usadas
# ===========================================================================

def top_palabras(df_verses: "pd.DataFrame", top_n: int = 20) -> "pd.Series":
    """
    Calcula las palabras más frecuentes en toda la Biblia,
    excluyendo stopwords en español y palabras menores a 3 caracteres.

    Args:
        df_verses: DataFrame con columna 'text_clean'.
        top_n    : Cuántas palabras devolver.

    Returns:
        Serie de pandas con las N palabras más frecuentes y sus conteos.
    """
    # Unir todo el texto, tokenizar y filtrar
    todo = " ".join(df_verses["text_clean"].dropna())
    palabras = re.findall(r'\b[a-záéíóúñü]{3,}\b', todo.lower())
    palabras_filtradas = [p for p in palabras if p not in STOPWORDS_ES]

    conteo = pd.Series(palabras_filtradas).value_counts().head(top_n)

    print(f"\n  Top {top_n} palabras más usadas en la Biblia:")
    for palabra, freq in conteo.items():
        print(f"    {palabra:<20} {freq:>7,}")

    return conteo


# ===========================================================================
# Ejercicio 4: Comparativa AT vs NT
# ===========================================================================

def comparativa_testamentos(df_verses: "pd.DataFrame", df_books: "pd.DataFrame") -> None:
    """
    Compara el Antiguo y Nuevo Testamento en:
    - Total de versículos
    - Longitud promedio de versículos
    - Cantidad de palabras únicas (vocabulario)

    Args:
        df_verses: DataFrame de versículos con columna 'testamento'.
        df_books : DataFrame de libros (no usado directamente, para contexto).
    """
    print("\n=== Ejercicio 4: Comparativa AT vs NT ===")

    resumen = df_verses.groupby("testamento").agg(
        total_versiculos=("text_clean", "count"),
        longitud_promedio=("text_clean", lambda x: x.str.len().mean()),
    ).round(2)

    print(resumen.to_string())

    # Vocabulario único por testamento
    for testamento in ["AT", "NT"]:
        subset = df_verses[df_verses["testamento"] == testamento]["text_clean"]
        todo = " ".join(subset)
        palabras = set(re.findall(r'\b[a-záéíóúñü]{3,}\b', todo.lower()))
        print(f"  Vocabulario único {testamento}: {len(palabras):,} palabras distintas")


# ===========================================================================
# Ejercicio 5: Gráfico de barras — versículos por libro
# ===========================================================================

def grafico_versiculos_por_libro(
    df_verses: "pd.DataFrame",
    df_books: "pd.DataFrame"
) -> None:
    """
    Genera y guarda un gráfico de barras con los 20 libros
    que tienen más versículos. Guarda como PNG en el directorio actual.

    Args:
        df_verses: DataFrame de versículos.
        df_books : DataFrame de libros con nombre largo.
    """
    if not MATPLOTLIB_OK:
        print("  [SKIP] matplotlib no disponible.")
        return

    print("\n=== Ejercicio 5: Gráfico de versículos por libro ===")

    conteo = (
        df_verses.groupby("book_number")
        .size()
        .reset_index(name="versiculos")
        .merge(df_books[["book_number", "long_name"]], on="book_number")
        .nlargest(20, "versiculos")
        .sort_values("versiculos", ascending=True)
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(conteo["long_name"], conteo["versiculos"], color="steelblue")
    ax.set_xlabel("Número de versículos")
    ax.set_title("Top 20 libros con más versículos — Biblia RV60")
    plt.tight_layout()

    ruta = os.path.join(os.path.dirname(__file__), "biblia_versiculos_por_libro.png")
    plt.savefig(ruta, dpi=100)
    plt.close()
    print(f"  Gráfico guardado: {ruta}")


# ===========================================================================
# Ejercicio 6: Heatmap de versículos en Salmos
# ===========================================================================

def heatmap_salmos(df_verses: "pd.DataFrame") -> None:
    """
    Genera un heatmap de cantidad de versículos por capítulo en el libro
    de Salmos. Cada celda muestra el conteo de versículos.

    Args:
        df_verses: DataFrame completo de versículos.
    """
    if not SEABORN_OK or not MATPLOTLIB_OK:
        print("  [SKIP] seaborn/matplotlib no disponible.")
        return

    print("\n=== Ejercicio 6: Heatmap Salmos ===")

    # Salmos = book_number 230 en RV60
    salmos = df_verses[df_verses["book_number"] == 230].copy()

    if salmos.empty:
        print("  [WARN] No se encontraron versículos de Salmos con book_number=230.")
        return

    pivot = (
        salmos.groupby(["chapter", "verse"])
        .size()
        .unstack(fill_value=0)
    )
    # Limitar a los primeros 50 capítulos para que el heatmap sea legible
    pivot = pivot.iloc[:50]

    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(
        pivot,
        cmap="YlOrRd",
        linewidths=0.1,
        ax=ax,
        cbar_kws={"label": "Versículos"}
    )
    ax.set_title("Heatmap de versículos por capítulo — Salmos 1-50")
    ax.set_xlabel("Versículo")
    ax.set_ylabel("Capítulo")
    plt.tight_layout()

    ruta = os.path.join(os.path.dirname(__file__), "biblia_heatmap_salmos.png")
    plt.savefig(ruta, dpi=100)
    plt.close()
    print(f"  Heatmap guardado: {ruta}")


# ===========================================================================
# Ejercicio 7: WordCloud (conceptual)
# ===========================================================================

def wordcloud_conceptual() -> None:
    """
    Explica cómo generar un WordCloud de la Biblia y lo intenta si
    la librería wordcloud está instalada.
    """
    print("""
=== Ejercicio 7: WordCloud de la Biblia ===

  Para generar un WordCloud necesitas:
    pip install wordcloud

  Código de ejemplo:
  ------------------
  from wordcloud import WordCloud
  import matplotlib.pyplot as plt

  # 'todo_texto' es el texto completo de la Biblia limpio
  wc = WordCloud(
      width=1200, height=600,
      background_color="white",
      stopwords=STOPWORDS_ES,
      collocations=False,
  ).generate(todo_texto)

  plt.figure(figsize=(15, 7))
  plt.imshow(wc, interpolation="bilinear")
  plt.axis("off")
  plt.title("WordCloud — Biblia Reina-Valera 1960")
  plt.savefig("biblia_wordcloud.png", dpi=150)
""")

    try:
        from wordcloud import WordCloud
        print("  [INFO] wordcloud está instalado. Puedes ejecutar el código de arriba.")
    except ImportError:
        print("  [AVISO] wordcloud no instalado: pip install wordcloud")


# ===========================================================================
# Ejercicio 8: Top 10 versículos más ricos en vocabulario
# ===========================================================================

def versiculos_ricos_vocabulario(df_verses: "pd.DataFrame", top_n: int = 10) -> None:
    """
    Encuentra los versículos con más palabras únicas (riqueza de vocabulario).
    Excluye stopwords del conteo para medir vocabulario real.

    Args:
        df_verses: DataFrame con columna 'text_clean'.
        top_n    : Cuántos versículos mostrar.
    """
    print(f"\n=== Ejercicio 8: Top {top_n} versículos más ricos en vocabulario ===")

    def contar_palabras_unicas(texto: str) -> int:
        """Cuenta palabras únicas en un texto, excluyendo stopwords."""
        palabras = re.findall(r'\b[a-záéíóúñü]{3,}\b', str(texto).lower())
        return len({p for p in palabras if p not in STOPWORDS_ES})

    df_verses = df_verses.copy()
    df_verses["palabras_unicas"] = df_verses["text_clean"].apply(contar_palabras_unicas)

    top = df_verses.nlargest(top_n, "palabras_unicas")[
        ["book_number", "chapter", "verse", "palabras_unicas", "text_clean"]
    ]

    for _, row in top.iterrows():
        ref = f"Libro {row['book_number']} {row['chapter']}:{row['verse']}"
        print(f"  [{ref}] {row['palabras_unicas']} palabras únicas")
        print(f"    {str(row['text_clean'])[:80]}…\n")


# ===========================================================================
# Punto de entrada
# ===========================================================================

def main() -> None:
    """
    Ejecuta todos los ejercicios de análisis de la Biblia con Pandas.
    """
    print("=" * 60)
    print("  ANÁLISIS DE LA BIBLIA CON PANDAS")
    print("=" * 60)

    if not PANDAS_OK:
        print("  [ERROR] Pandas no está instalado. pip install pandas")
        return

    if not verificar_bd():
        return

    # Cargar y limpiar datos
    print("\n=== Ejercicio 1: Cargar DataFrames ===")
    df_books, df_verses = cargar_datos()

    print("\n=== Ejercicio 2: Limpiar texto ===")
    df_verses = limpiar_dataframe(df_verses)

    # Análisis
    print("\n=== Ejercicio 3: Top 20 palabras más usadas ===")
    top_palabras(df_verses)

    comparativa_testamentos(df_verses, df_books)
    grafico_versiculos_por_libro(df_verses, df_books)
    heatmap_salmos(df_verses)
    wordcloud_conceptual()
    versiculos_ricos_vocabulario(df_verses)

    print("\n✓ Análisis completado.")


if __name__ == "__main__":
    main()
