# Capítulo 24 — Inteligencia Artificial y Deep Learning

## IA vs ML vs Deep Learning

Estos tres términos se usan intercambiablemente pero no son lo mismo:

```
Inteligencia Artificial (IA)
└── Machine Learning (ML)
    └── Deep Learning (DL)
```

- **IA**: Cualquier sistema que imita comportamiento inteligente humano (reglas, búsqueda, planificación)
- **ML**: Subcampo de IA donde el sistema aprende de datos (ver Capítulo 23)
- **Deep Learning**: Subcampo de ML que usa redes neuronales profundas (muchas capas)

---

## Redes Neuronales — Conceptos Fundamentales

Una red neuronal está inspirada (vagamente) en el cerebro humano:

```
Capa de Entrada → Capas Ocultas → Capa de Salida

[X1]   →   [○○○○]   →   [○○]   →   [ŷ]
[X2]   →   [○○○○]   →   [○○]
[X3]   →   [○○○○]
```

**Cada neurona:**
1. Recibe valores de entrada
2. Los multiplica por sus pesos (`weights`)
3. Suma los resultados
4. Aplica una **función de activación** (introduce no-linealidad)
5. Pasa el resultado a la siguiente capa

**Entrenamiento:**
- **Forward pass**: datos entran, se calcula la predicción
- **Loss function**: mide qué tan mala es la predicción
- **Backpropagation**: calcula el gradiente del error respecto a cada peso
- **Gradient descent**: actualiza los pesos para reducir el error

---

## TensorFlow/Keras vs PyTorch

| Aspecto | TensorFlow/Keras | PyTorch |
|---------|-----------------|---------|
| Facilidad de uso | Alta (Keras) | Media-Alta |
| Ecosistema producción | Muy maduro (TFLite, TF Serving) | Creciente (TorchServe) |
| Investigación | Menos dominante | Dominante |
| Curva de aprendizaje | Suave (Keras) | Moderada |
| Instalación | `pip install tensorflow` | `pip install torch` |

**¿Cuándo usar cuál?**
- Aplicación producción + mobile: TensorFlow/Keras
- Investigación y experimentación: PyTorch
- Principiante: Keras (sintaxis más limpia)

---

## La Revolución de los Transformers

En 2017, el paper "Attention is All You Need" introdujo la arquitectura **Transformer**. Esta arquitectura revolucionó el NLP y luego toda la IA:

- **BERT** (Google, 2018): comprensión de texto bidireccional
- **GPT-2/3/4** (OpenAI): generación de texto
- **ChatGPT** (2022): interfaz conversacional sobre GPT
- **Claude** (Anthropic): alternativa segura y útil a ChatGPT
- **Llama** (Meta): modelos open-source
- **Gemini** (Google): multimodal (texto + imágenes)

Los transformers usan **mecanismo de atención** para entender el contexto de cada palabra en relación a todas las demás.

---

## APIs de IA — Cómo Integrarlas

En vez de entrenar tus propios modelos (costoso, requiere GPU, datos masivos), puedes usar modelos de clase mundial via API:

```bash
pip install openai          # API de OpenAI (ChatGPT, GPT-4)
pip install anthropic       # API de Anthropic (Claude)
# Google Gemini — usar google-generativeai
```

**Variables de entorno para API keys:**
```bash
# Nunca hardcodear API keys en el código
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Instalación

```bash
# Para TensorFlow/Keras
pip install tensorflow numpy matplotlib

# Para PyTorch
pip install torch torchvision

# Para NLP
pip install nltk scikit-learn

# Para APIs de IA
pip install openai anthropic langchain
```

---

## Archivos del Capítulo

| Archivo | Tema |
|---------|------|
| `01_redes_neuronales_conceptos.py` | Perceptrón desde cero con NumPy |
| `02_keras_intro.py` | Keras: modelo Sequential, entrenamiento |
| `03_keras_avanzado.py` | Functional API, callbacks, regularización |
| `04_nlp_basico.py` | Tokenización, TF-IDF, HuggingFace |
| `05_api_openai.py` | Integrar APIs de IA (OpenAI/Anthropic) |
| `06_langchain_intro.py` | LangChain: chains, memoria, agentes |
