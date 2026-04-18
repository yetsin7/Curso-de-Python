# =============================================================================
# CAPÍTULO 24 — Inteligencia Artificial y Deep Learning
# Archivo: 04_nlp_basico.py
# Tema: NLP — Procesamiento de Lenguaje Natural
# =============================================================================
#
# NLP (Natural Language Processing) es la rama de la IA que trabaja con
# texto y lenguaje humano. Antes del deep learning, las técnicas clásicas
# (TF-IDF, Bag of Words) dominaban. Hoy los transformers son el estándar,
# pero las técnicas clásicas siguen siendo útiles para tareas simples.
#
# Este archivo cubre:
# 1. Tokenización y limpieza de texto
# 2. Stopwords y stemming (con NLTK)
# 3. Bag of Words y TF-IDF (con sklearn)
# 4. Clasificación de texto (spam detector)
# 5. Introducción a HuggingFace Transformers
# =============================================================================

import os
import re
import numpy as np

# Importar sklearn (siempre disponible si instalaste el stack de ML)
try:
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False
    print("sklearn no disponible. pip install scikit-learn")

# NLTK es una librería especializada en NLP: tokenización, stemming, etc.
try:
    import nltk
    # Descargar recursos necesarios si no están ya descargados
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, SnowballStemmer
    NLTK_OK = True
except ImportError:
    NLTK_OK = False
    print("NLTK no disponible. pip install nltk")

print("=" * 65)
print("NLP BÁSICO — Procesamiento de Lenguaje Natural")
print("=" * 65)

# =============================================================================
# SECCIÓN 1: Tokenización — Dividir texto en unidades básicas
# =============================================================================
print("\n--- 1. Tokenización ---")

texto_ejemplo = """Python es un lenguaje de programación poderoso y versátil.
Es usado en Data Science, Machine Learning e Inteligencia Artificial.
¡Su sintaxis es clara y fácil de aprender!"""

print(f"Texto original:\n{texto_ejemplo}\n")

if NLTK_OK:
    # Tokenizar por oraciones
    oraciones = sent_tokenize(texto_ejemplo)
    print(f"Tokenización por oraciones ({len(oraciones)}):")
    for i, s in enumerate(oraciones):
        print(f"  [{i}] {s}")

    # Tokenizar por palabras
    tokens = word_tokenize(texto_ejemplo.lower())
    print(f"\nTokens de palabras ({len(tokens)}): {tokens[:15]}...")
else:
    # Tokenización manual sin NLTK
    tokens = re.findall(r"\b\w+\b", texto_ejemplo.lower())
    print(f"Tokens (tokenización simple regex): {tokens[:15]}...")

# =============================================================================
# SECCIÓN 2: Stopwords y limpieza
# =============================================================================
print("\n--- 2. Stopwords y Limpieza ---")

# Stopwords: palabras muy frecuentes que no aportan significado semántico
# Ejemplos: "el", "la", "de", "en", "y", "the", "is", "a", "an"
# Eliminarlas reduce el ruido y mejora la precisión de los modelos

def limpiar_texto(texto, idioma="english"):
    """
    Limpia un texto para análisis NLP:
    1. Convierte a minúsculas
    2. Elimina puntuación y caracteres especiales
    3. Elimina stopwords
    4. Elimina tokens de una sola letra
    """
    # Minúsculas
    texto = texto.lower()

    # Eliminar URLs
    texto = re.sub(r"http\S+|www\S+", "", texto)

    # Eliminar caracteres especiales (mantener letras, números y espacios)
    texto = re.sub(r"[^a-zA-ZáéíóúñüÁÉÍÓÚÑ\s]", "", texto)

    # Tokenizar
    palabras = texto.split()

    # Eliminar stopwords
    if NLTK_OK:
        stop = set(stopwords.words(idioma))
    else:
        # Stopwords básicas en inglés como fallback
        stop = {"the", "is", "in", "a", "an", "and", "or", "to", "for",
                "of", "with", "that", "this", "it", "be", "are", "was"}

    palabras_limpias = [p for p in palabras if p not in stop and len(p) > 1]

    return palabras_limpias

texto_spam = "CONGRATULATIONS! You've WON a FREE iPhone! Click here now to claim your PRIZE!"
texto_normal = "Hello, can we schedule a meeting for tomorrow at 3pm to discuss the project?"

print(f"Spam:   {limpiar_texto(texto_spam)}")
print(f"Normal: {limpiar_texto(texto_normal)}")

# Stemming: reducir palabras a su raíz (running → run, better → better)
if NLTK_OK:
    stemmer = PorterStemmer()
    palabras_test = ["running", "runs", "ran", "running", "better", "programming"]
    print(f"\nStemming (Porter):")
    for p in palabras_test:
        print(f"  {p:15s} → {stemmer.stem(p)}")

# =============================================================================
# SECCIÓN 3: Bag of Words — Representación numérica de texto
# =============================================================================
print("\n--- 3. Bag of Words (BoW) ---")

# Bag of Words convierte texto en un vector numérico:
# Para cada documento, cuenta cuántas veces aparece cada palabra del vocabulario.
# Problema: ignora el orden y la frecuencia relativa.

if SKLEARN_OK:
    corpus_ejemplo = [
        "python es genial para data science",
        "machine learning es parte de inteligencia artificial",
        "python es popular en machine learning",
        "inteligencia artificial transforma el mundo"
    ]

    # CountVectorizer implementa Bag of Words
    vectorizer_bow = CountVectorizer()
    X_bow = vectorizer_bow.fit_transform(corpus_ejemplo)

    print(f"Vocabulario ({len(vectorizer_bow.vocabulary_)} palabras):")
    vocab_sorted = sorted(vectorizer_bow.vocabulary_.items(), key=lambda x: x[1])
    print(f"  {[w for w, _ in vocab_sorted]}")

    print(f"\nMatriz BoW (docs × palabras):")
    import pandas as pd
    df_bow = pd.DataFrame(
        X_bow.toarray(),
        columns=vectorizer_bow.get_feature_names_out()
    )
    print(df_bow)

# =============================================================================
# SECCIÓN 4: TF-IDF — Ponderación inteligente de palabras
# =============================================================================
print("\n--- 4. TF-IDF ---")
print("""
TF-IDF (Term Frequency — Inverse Document Frequency):
- TF: cuántas veces aparece una palabra en un documento específico
- IDF: penaliza palabras que aparecen en MUCHOS documentos (son poco informativas)
- TF-IDF = TF × IDF → palabras frecuentes en un doc pero raras en el corpus = importantes

Ejemplo: "Python" aparece en 3 de 4 documentos → IDF bajo → poco discriminativo
         "data science" aparece en 1 de 4 → IDF alto → muy discriminativo para ese doc
""")

if SKLEARN_OK:
    tfidf = TfidfVectorizer()
    X_tfidf = tfidf.fit_transform(corpus_ejemplo)

    print("Matriz TF-IDF:")
    df_tfidf = pd.DataFrame(
        X_tfidf.toarray().round(3),
        columns=tfidf.get_feature_names_out()
    )
    print(df_tfidf)

# =============================================================================
# SECCIÓN 5: Clasificador de Spam con TF-IDF
# =============================================================================
print("\n--- 5. Clasificador de Spam ---")

if SKLEARN_OK:
    # Dataset de emails sintético
    emails = [
        ("FREE MONEY WIN PRIZE CLICK NOW LIMITED OFFER", 1),
        ("Meeting scheduled for tomorrow at 3pm", 0),
        ("CONGRATULATIONS you won a free car register now", 1),
        ("Project deadline is next Friday, please review", 0),
        ("Claim your free gift card worth $500 today only", 1),
        ("Can you send me the quarterly report please", 0),
        ("URGENT: Your account will be suspended act NOW", 1),
        ("Hi, I wanted to discuss the marketing strategy", 0),
        ("You have been selected for exclusive cash reward", 1),
        ("The team meeting notes are attached", 0),
        ("Win big prizes FREE no purchase necessary call now", 1),
        ("Please review the attached proposal and feedback", 0),
        ("Hot singles in your area click here for free", 1),
        ("Reminder: annual performance review next week", 0),
        ("GUARANTEED income work from home make thousands", 1),
        ("Could you update the project timeline document", 0),
        ("Buy cheap medication online no prescription needed", 1),
        ("Looking forward to your presentation on Thursday", 0),
        ("You are a WINNER claim your FREE laptop today", 1),
        ("Lunch meeting confirmed for noon on Wednesday", 0),
    ]

    textos = [e[0] for e in emails]
    etiquetas = [e[1] for e in emails]

    # Pipeline: TF-IDF + Logistic Regression
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
        textos, etiquetas, test_size=0.3, random_state=42, stratify=etiquetas
    )

    tfidf_spam = TfidfVectorizer(ngram_range=(1, 2), max_features=500)
    X_train_vec = tfidf_spam.fit_transform(X_train_s)
    X_test_vec = tfidf_spam.transform(X_test_s)

    clf_spam = LogisticRegression(random_state=42)
    clf_spam.fit(X_train_vec, y_train_s)

    y_pred_s = clf_spam.predict(X_test_vec)
    print(f"Accuracy del detector de spam: {accuracy_score(y_test_s, y_pred_s):.3f}")
    print(f"\nReporte:\n{classification_report(y_test_s, y_pred_s, target_names=['Normal','Spam'])}")

    # Probar con nuevos emails
    nuevos = [
        "FREE PRIZE you are a winner click now",
        "Can we schedule a call this afternoon"
    ]
    nuevos_vec = tfidf_spam.transform(nuevos)
    preds = clf_spam.predict(nuevos_vec)
    probs = clf_spam.predict_proba(nuevos_vec)
    for email, pred, prob in zip(nuevos, preds, probs):
        print(f"  '{email[:45]}...' → {'SPAM' if pred == 1 else 'Normal'} ({prob[pred]:.1%})")

# =============================================================================
# SECCIÓN 6: HuggingFace Transformers — El estándar moderno de NLP
# =============================================================================
print("\n--- 6. HuggingFace Transformers ---")
print("""
El estado del arte en NLP usa modelos Transformer pre-entrenados.
HuggingFace es la plataforma que centraliza miles de modelos listos para usar.

Instalación: pip install transformers torch  (o tensorflow)

Ejemplo: Análisis de sentimiento con un modelo pre-entrenado

    from transformers import pipeline

    # Cargar pipeline de análisis de sentimiento (descarga el modelo la primera vez)
    sentiment = pipeline("sentiment-analysis")

    resultados = sentiment([
        "I love Python, it's amazing!",
        "This is terrible and I hate it"
    ])
    # [{'label': 'POSITIVE', 'score': 0.9998},
    #  {'label': 'NEGATIVE', 'score': 0.9994}]

Otros pipelines disponibles:
    pipeline("text-generation")          # Generar texto
    pipeline("question-answering")       # Responder preguntas sobre un contexto
    pipeline("summarization")            # Resumir textos largos
    pipeline("translation_en_to_es")     # Traducir
    pipeline("fill-mask")                # Completar texto con [MASK]
    pipeline("ner")                      # Reconocimiento de entidades nombradas
    pipeline("zero-shot-classification") # Clasificar sin entrenamiento

Modelos populares en HuggingFace:
- bert-base-uncased: Comprensión de texto (Google)
- gpt2: Generación de texto
- distilbert-base-uncased: BERT más ligero, casi igual de preciso
- sentence-transformers/...: Para similitud semántica de textos
- Helsinki-NLP/opus-mt-...: Modelos de traducción
""")

# Intentar usar HuggingFace si está disponible
try:
    from transformers import pipeline as hf_pipeline
    print("HuggingFace Transformers disponible. Ejecutando ejemplo...")

    # Análisis de sentimiento
    sentiment_analyzer = hf_pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    textos_test = [
        "Python is an amazing programming language!",
        "I hate bugs in my code, they are so frustrating"
    ]
    resultados = sentiment_analyzer(textos_test)
    for texto, res in zip(textos_test, resultados):
        print(f"  '{texto[:50]}' → {res['label']} ({res['score']:.3f})")

except ImportError:
    print("HuggingFace no disponible.")
    print("Instala con: pip install transformers torch")

print("\n" + "=" * 65)
print("Fin de NLP Básico — Continúa con 05_api_openai.py")
print("=" * 65)
