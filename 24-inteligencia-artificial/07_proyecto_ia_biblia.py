"""
Proyecto de IA con la Biblia: Búsqueda Semántica y RAG
========================================================
Sistema de IA aplicado a la Biblia Reina-Valera 1960:
  - Búsqueda semántica con TF-IDF + cosine similarity (sin GPU)
  - función versiculos_similares(query, n=5)
  - Generador de "devocional" con versículo aleatorio + análisis
  - Concepto de RAG (Retrieval Augmented Generation)
  - Código de integración con OpenAI y Anthropic (conceptual)

Dependencias:
    pip install pandas scikit-learn

Ruta a BD: ../../datos/biblia_rv60.sqlite3
"""

import os
import random
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
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False
    print("[AVISO] pip install scikit-learn")


# ===========================================================================
# Limpieza de texto
# ===========================================================================

def limpiar_strong(texto: str) -> str:
    """
    Elimina marcas Strong <S>NNNN</S> del texto del versículo.

    Args:
        texto: Texto crudo con marcas numéricas.

    Returns:
        Texto limpio.
    """
    return re.sub(r'<S>\d+</S>', '', texto).strip()


# ===========================================================================
# Motor de Búsqueda Semántica
# ===========================================================================

class BuscadorBiblico:
    """
    Motor de búsqueda semántica para versículos de la Biblia.
    Usa TF-IDF como embedding simple y cosine similarity para ranking.

    Este enfoque no requiere GPU ni modelos de lenguaje grandes.
    Es un excelente primer paso antes de embeddings neuronales.

    Attributes:
        df_verses  : DataFrame con todos los versículos.
        df_books   : DataFrame con nombres de libros.
        vectorizer : TfidfVectorizer ajustado al corpus bíblico.
        tfidf_matrix: Matriz TF-IDF de todos los versículos.
    """

    def __init__(self) -> None:
        """
        Inicializa el buscador cargando la BD y construyendo el índice TF-IDF.
        Este proceso tarda algunos segundos la primera vez.
        """
        self.df_verses   = None
        self.df_books    = None
        self.vectorizer  = None
        self.tfidf_matrix = None
        self._inicializado = False

    def inicializar(self) -> bool:
        """
        Carga los datos y construye el índice de búsqueda.
        Retorna True si se inicializó correctamente.

        Returns:
            True si el índice está listo para buscar.
        """
        if self._inicializado:
            return True

        if not os.path.exists(DB_PATH):
            print(f"[ERROR] BD no encontrada: {DB_PATH}")
            return False

        print("  Cargando Biblia…")
        conn = sqlite3.connect(DB_PATH)
        self.df_verses = pd.read_sql("SELECT * FROM verses", conn)
        self.df_books  = pd.read_sql("SELECT * FROM books",  conn)
        conn.close()

        self.df_verses["text_clean"] = self.df_verses["text"].apply(limpiar_strong)

        print("  Construyendo índice TF-IDF (puede tardar unos segundos)…")
        self.vectorizer = TfidfVectorizer(
            max_features=8000,
            token_pattern=r'\b[a-záéíóúñü]{3,}\b',
            sublinear_tf=True,   # log(TF) para suavizar frecuencias altas
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.df_verses["text_clean"].fillna("")
        )

        self._inicializado = True
        print(f"  Índice listo: {self.tfidf_matrix.shape[0]:,} versículos indexados.")
        return True

    def versiculos_similares(self, query: str, n: int = 5) -> list[dict]:
        """
        Encuentra los N versículos más similares semánticamente a la consulta.
        Usa cosine similarity entre el vector TF-IDF de la query
        y todos los vectores del corpus.

        Args:
            query: Texto de búsqueda en lenguaje natural.
            n    : Número de versículos a retornar.

        Returns:
            Lista de diccionarios con referencia, texto y puntuación.
        """
        if not self._inicializado:
            raise RuntimeError("Llama a inicializar() primero.")

        # Convertir query al espacio TF-IDF del corpus
        query_vec = self.vectorizer.transform([query.lower()])

        # Calcular similitud coseno con todos los versículos
        similitudes = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        # Obtener los índices de los N más similares
        top_indices = similitudes.argsort()[-n:][::-1]

        resultados = []
        for idx in top_indices:
            row = self.df_verses.iloc[idx]

            # Obtener nombre del libro
            libro_info = self.df_books[
                self.df_books["book_number"] == row["book_number"]
            ]
            nombre_libro = libro_info["long_name"].values[0] if not libro_info.empty else "?"

            resultados.append({
                "referencia" : f"{nombre_libro} {row['chapter']}:{row['verse']}",
                "texto"      : row["text_clean"],
                "similitud"  : float(similitudes[idx]),
            })

        return resultados

    def versículo_aleatorio(self) -> dict:
        """
        Retorna un versículo aleatorio con su referencia completa.

        Returns:
            Diccionario con referencia y texto del versículo.
        """
        if not self._inicializado:
            raise RuntimeError("Llama a inicializar() primero.")

        row = self.df_verses.sample(1).iloc[0]
        libro_info = self.df_books[self.df_books["book_number"] == row["book_number"]]
        nombre_libro = libro_info["long_name"].values[0] if not libro_info.empty else "?"

        return {
            "referencia": f"{nombre_libro} {row['chapter']}:{row['verse']}",
            "texto"     : row["text_clean"],
        }


# ===========================================================================
# Generador de devocional
# ===========================================================================

def generar_devocional(buscador: "BuscadorBiblico") -> None:
    """
    Genera un mini-devocional:
    1. Selecciona un versículo aleatorio
    2. Extrae palabras clave del versículo
    3. Busca 3 versículos relacionados temáticamente
    4. Presenta todo como un devocional cohesionado

    Args:
        buscador: Instancia inicializada de BuscadorBiblico.
    """
    print("\n=== DEVOCIONAL DEL DÍA ===\n")

    verso = buscador.versículo_aleatorio()
    print(f"  Versículo principal: {verso['referencia']}")
    print(f"  \"{verso['texto']}\"\n")

    # Encontrar versículos temáticamente relacionados
    print("  Versículos relacionados:")
    relacionados = buscador.versiculos_similares(verso["texto"], n=4)

    # Excluir el versículo principal de los resultados
    relacionados = [r for r in relacionados
                    if r["referencia"] != verso["referencia"]][:3]

    for r in relacionados:
        print(f"  • {r['referencia']} (similitud: {r['similitud']:.3f})")
        print(f"    {r['texto'][:80]}…\n")


# ===========================================================================
# Concepto de RAG aplicado a la Biblia
# ===========================================================================

def explicar_rag() -> None:
    """
    Explica el concepto de RAG (Retrieval Augmented Generation)
    y cómo aplicarlo a la Biblia con OpenAI o Anthropic.
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║   RAG (RETRIEVAL AUGMENTED GENERATION) — CONCEPTO               ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  RAG = Recuperación + Generación                                 ║
║                                                                  ║
║  1. RECUPERACIÓN: dado un query del usuario, buscar los          ║
║     fragmentos más relevantes del corpus (en nuestro caso,       ║
║     versículos de la Biblia) usando TF-IDF, embeddings, etc.    ║
║                                                                  ║
║  2. GENERACIÓN: enviar esos fragmentos como contexto a un LLM    ║
║     (GPT-4, Claude, Llama) para que genere una respuesta         ║
║     fundamentada en el texto bíblico real.                       ║
║                                                                  ║
║  Ventajas:                                                       ║
║  • El LLM no "alucina" datos bíblicos                            ║
║  • Se pueden citar fuentes exactas                               ║
║  • No se necesita re-entrenar el modelo                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


def codigo_rag_openai() -> None:
    """
    Muestra el código de ejemplo para integrar el buscador bíblico
    con la API de OpenAI usando RAG.
    """
    print("""
--- INTEGRACIÓN CON OPENAI (código conceptual) ---

import openai

def responder_con_biblia_openai(pregunta: str, buscador: BuscadorBiblico) -> str:
    \"\"\"
    Responde una pregunta usando versículos bíblicos como contexto (RAG).

    Args:
        pregunta: Pregunta del usuario sobre la Biblia.
        buscador: Instancia del buscador bíblico inicializado.

    Returns:
        Respuesta generada por el LLM con citas bíblicas.
    \"\"\"
    # Paso 1: Recuperar versículos relevantes
    versiculos = buscador.versiculos_similares(pregunta, n=5)
    contexto = "\\n".join([
        f"{v['referencia']}: {v['texto']}"
        for v in versiculos
    ])

    # Paso 2: Generar respuesta con el LLM
    client = openai.OpenAI(api_key="TU_API_KEY")
    respuesta = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un asistente bíblico. Responde SOLO basándote "
                    "en los versículos proporcionados. Cita siempre la referencia."
                )
            },
            {
                "role": "user",
                "content": f"Pregunta: {pregunta}\\n\\nVersículos relevantes:\\n{contexto}"
            }
        ]
    )
    return respuesta.choices[0].message.content
""")


def codigo_rag_anthropic() -> None:
    """
    Muestra el código de ejemplo para integrar con la API de Anthropic (Claude).
    """
    print("""
--- INTEGRACIÓN CON ANTHROPIC/CLAUDE (código conceptual) ---

import anthropic

def responder_con_biblia_claude(pregunta: str, buscador: BuscadorBiblico) -> str:
    \"\"\"
    Responde usando Claude de Anthropic con RAG sobre la Biblia.

    Args:
        pregunta: Pregunta del usuario.
        buscador: Instancia del buscador bíblico inicializado.

    Returns:
        Respuesta de Claude fundamentada en la Biblia.
    \"\"\"
    versiculos = buscador.versiculos_similares(pregunta, n=5)
    contexto = "\\n".join([
        f"{v['referencia']}: {v['texto']}"
        for v in versiculos
    ])

    client  = anthropic.Anthropic(api_key="TU_API_KEY")
    mensaje = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=(
            "Eres un asistente bíblico. Responde basándote ÚNICAMENTE "
            "en los versículos del contexto proporcionado."
        ),
        messages=[{
            "role": "user",
            "content": f"Pregunta: {pregunta}\\n\\nContexto bíblico:\\n{contexto}"
        }]
    )
    return mensaje.content[0].text
""")


# ===========================================================================
# Punto de entrada
# ===========================================================================

def main() -> None:
    """
    Demuestra el sistema completo: búsqueda semántica, devocional y RAG.
    """
    print("=" * 60)
    print("  PROYECTO IA — BÚSQUEDA SEMÁNTICA BÍBLICA")
    print("=" * 60)

    if not PANDAS_OK or not SKLEARN_OK:
        print("\n  [ERROR] pip install pandas scikit-learn")
        return

    # Inicializar motor de búsqueda
    buscador = BuscadorBiblico()
    if not buscador.inicializar():
        return

    # Demo: búsqueda semántica
    queries = [
        "el amor de Dios hacia los hombres",
        "la fe que mueve montañas",
        "sabiduría y entendimiento",
    ]

    for query in queries:
        print(f"\n--- Búsqueda: '{query}' ---")
        resultados = buscador.versiculos_similares(query, n=3)
        for r in resultados:
            print(f"  [{r['similitud']:.3f}] {r['referencia']}: {r['texto'][:70]}…")

    # Devocional generado
    generar_devocional(buscador)

    # Explicación de RAG e integración con LLMs
    explicar_rag()
    codigo_rag_openai()
    codigo_rag_anthropic()

    print("\n✓ Proyecto de IA con la Biblia completado.")


if __name__ == "__main__":
    main()
