# =============================================================================
# CAPÍTULO 24 — Inteligencia Artificial y Deep Learning
# Archivo: 05_api_openai.py
# Tema: Integrar APIs de IA (OpenAI / Anthropic)
# =============================================================================
#
# En vez de entrenar tu propio LLM (se necesitan millones de dólares y GPUs),
# usas modelos de clase mundial via API REST. Este archivo muestra cómo
# integrar OpenAI (GPT-4) y Anthropic (Claude) en tus aplicaciones.
#
# SEGURIDAD: Las API keys son secretos. NUNCA las hardcodees en el código.
# Siempre usar variables de entorno: os.environ.get("OPENAI_API_KEY")
# =============================================================================

import os
import json

print("=" * 65)
print("APIs de IA — OpenAI y Anthropic (Claude)")
print("=" * 65)

# =============================================================================
# SECCIÓN 1: Configuración y seguridad de API Keys
# =============================================================================
print("""
--- 1. Configuración segura de API Keys ---

NUNCA hagas esto:
    api_key = "sk-abc123..."  # ¡PELIGROSO! Se sube a GitHub y te roban la key

SIEMPRE hazlo así:
    # En tu terminal (Linux/Mac):
    export OPENAI_API_KEY="sk-..."
    export ANTHROPIC_API_KEY="sk-ant-..."

    # En Windows PowerShell:
    $env:OPENAI_API_KEY = "sk-..."

    # En un archivo .env (y agregar .env al .gitignore):
    OPENAI_API_KEY=sk-...
    ANTHROPIC_API_KEY=sk-ant-...

    # Leer en Python:
    import os
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY no está configurada")

Cómo obtener API keys:
    OpenAI:    https://platform.openai.com/api-keys
    Anthropic: https://console.anthropic.com/
""")

# Leer keys del entorno (no fallamos si no están — explicamos cómo configurarlas)
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")

# =============================================================================
# SECCIÓN 2: Conceptos de los LLMs antes de ver el código
# =============================================================================
print("""
--- 2. Conceptos Clave de los LLMs vía API ---

TOKENS:
  Los LLMs no trabajan con palabras sino con tokens (fragmentos de texto).
  Aproximadamente: 1 token ≈ 4 caracteres ≈ 0.75 palabras
  Costo = tokens_entrada + tokens_salida × precio_por_token

MENSAJES:
  La API de chat usa un historial de mensajes con roles:
  - "system":    Instrucciones de comportamiento del modelo (el "personaje")
  - "user":      Lo que el usuario pregunta/dice
  - "assistant": La respuesta del modelo (para historial de conversación)

TEMPERATURE (0.0 - 2.0):
  - 0.0: Determinista, siempre la respuesta más probable. Ideal para código/datos.
  - 0.7: Balance entre creatividad y coherencia. Ideal para conversación.
  - 1.5+: Muy creativo y aleatorio. Para brainstorming.

MAX_TOKENS:
  Límite máximo de tokens en la respuesta del modelo.

MODELOS OPENAI (2024):
  - gpt-4o:          El más capaz (caro)
  - gpt-4o-mini:     Rápido, económico, muy bueno para la mayoría de tareas
  - gpt-3.5-turbo:   El más barato, bueno para tareas simples

MODELOS ANTHROPIC (2024):
  - claude-3-5-sonnet-20241022: Mejor balance velocidad/capacidad
  - claude-3-5-haiku-20241022:  Más rápido y barato
  - claude-3-opus-20240229:     El más capaz (caro)
""")

# =============================================================================
# SECCIÓN 3: OpenAI — Código completo
# =============================================================================
print("--- 3. OpenAI API ---")

try:
    from openai import OpenAI
    OPENAI_DISPONIBLE = True
except ImportError:
    OPENAI_DISPONIBLE = False
    print("OpenAI SDK no instalado. Ejecuta: pip install openai\n")

# Mostrar el código aunque no esté instalado
CODIGO_OPENAI = '''
# ============================================================
# EJEMPLO 1: Chat simple
# ============================================================
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

respuesta = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Eres un asistente experto en Python."},
        {"role": "user", "content": "¿Cuál es la diferencia entre list y tuple?"}
    ],
    temperature=0.7,
    max_tokens=300
)

texto = respuesta.choices[0].message.content
print(texto)

# Información de uso (para calcular costos)
print(f"Tokens usados: {respuesta.usage.total_tokens}")


# ============================================================
# EJEMPLO 2: Chatbot con memoria (historial)
# ============================================================
historial = [
    {"role": "system", "content": "Eres un tutor amable de programación."}
]

def chat(mensaje_usuario):
    historial.append({"role": "user", "content": mensaje_usuario})
    respuesta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=historial
    )
    respuesta_texto = respuesta.choices[0].message.content
    historial.append({"role": "assistant", "content": respuesta_texto})
    return respuesta_texto

# Conversación de ejemplo:
print(chat("Explícame qué es una lista en Python"))
print(chat("¿Y cuál es la diferencia con un diccionario?"))


# ============================================================
# EJEMPLO 3: Extracción de información estructurada (JSON)
# ============================================================
# Los LLMs pueden extraer datos estructurados de texto no estructurado
texto_cv = """
    Juan García, 32 años, Madrid.
    Trabaja como Senior Developer en TechCorp desde 2018.
    Skills: Python, JavaScript, React, Docker.
    Email: juan@example.com
"""

respuesta_json = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Extrae información del CV en formato JSON."},
        {"role": "user", "content": f"CV:\\n{texto_cv}"}
    ],
    response_format={"type": "json_object"}  # Fuerza respuesta JSON válida
)

datos = json.loads(respuesta_json.choices[0].message.content)
print(json.dumps(datos, indent=2, ensure_ascii=False))
'''

print(f"Código de referencia para OpenAI:")
print(CODIGO_OPENAI)

# Ejecutar solo si la key está configurada
if OPENAI_DISPONIBLE and OPENAI_KEY:
    print("\nEjecutando ejemplo real con OpenAI...\n")
    try:
        client = OpenAI(api_key=OPENAI_KEY)
        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente de Python. Responde en español."},
                {"role": "user", "content": "En una sola oración: ¿qué es una lambda en Python?"}
            ],
            max_tokens=100,
            temperature=0.5
        )
        print(f"Respuesta: {respuesta.choices[0].message.content}")
        print(f"Tokens: {respuesta.usage.total_tokens}")
    except Exception as e:
        print(f"Error al llamar a OpenAI: {e}")
else:
    if not OPENAI_KEY:
        print("Para ejecutar: export OPENAI_API_KEY='tu-key-aqui'")

# =============================================================================
# SECCIÓN 4: Anthropic (Claude) — Código completo
# =============================================================================
print("\n--- 4. Anthropic (Claude) API ---")

try:
    import anthropic as anthropic_sdk
    ANTHROPIC_DISPONIBLE = True
except ImportError:
    ANTHROPIC_DISPONIBLE = False
    print("Anthropic SDK no instalado. Ejecuta: pip install anthropic\n")

CODIGO_ANTHROPIC = '''
# ============================================================
# EJEMPLO: Usar Claude de Anthropic
# ============================================================
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

mensaje = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=300,
    system="Eres un experto en Python que explica conceptos claramente.",
    messages=[
        {"role": "user", "content": "¿Qué son los decoradores en Python?"}
    ]
)

print(mensaje.content[0].text)
print(f"Tokens entrada: {mensaje.usage.input_tokens}")
print(f"Tokens salida:  {mensaje.usage.output_tokens}")

# Diferencias principales con OpenAI SDK:
# - "system" es un parámetro separado (no un mensaje con role="system")
# - La respuesta está en mensaje.content[0].text
# - Los tokens se llaman input_tokens y output_tokens
'''

print(f"Código de referencia para Anthropic:")
print(CODIGO_ANTHROPIC)

if ANTHROPIC_DISPONIBLE and ANTHROPIC_KEY:
    print("\nEjecutando ejemplo real con Anthropic...\n")
    try:
        client_ant = anthropic_sdk.Anthropic(api_key=ANTHROPIC_KEY)
        mensaje = client_ant.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            system="Responde siempre en español en máximo 2 oraciones.",
            messages=[{"role": "user", "content": "¿Qué es NumPy en Python?"}]
        )
        print(f"Respuesta Claude: {mensaje.content[0].text}")
        print(f"Tokens: entrada={mensaje.usage.input_tokens}, salida={mensaje.usage.output_tokens}")
    except Exception as e:
        print(f"Error al llamar a Anthropic: {e}")
else:
    if not ANTHROPIC_KEY:
        print("Para ejecutar: export ANTHROPIC_API_KEY='sk-ant-...'")

# =============================================================================
# SECCIÓN 5: Buenas prácticas para producción
# =============================================================================
print("""
--- 5. Buenas Prácticas en Producción ---

1. MANEJO DE ERRORES:
   Las APIs pueden fallar por rate limits, errores de red o keys inválidas.
   Siempre envuelve las llamadas en try/except.

2. RATE LIMITING:
   Implementa exponential backoff para reintentar con espera progresiva:
   1s, 2s, 4s, 8s...

3. COSTOS:
   Monitorea el uso. Un bug de bucle infinito puede generar cargos masivos.
   Siempre establece max_tokens para limitar el costo por llamada.

4. CACHÉ:
   Para preguntas repetidas, guarda las respuestas en caché para ahorrar.

5. PROMPT ENGINEERING:
   - System prompt: define el rol y restricciones del modelo
   - Few-shot examples: muestra ejemplos de input/output esperado
   - Chain of thought: pide "piensa paso a paso" para razonamiento complejo

6. SEGURIDAD:
   - Nunca pases input del usuario sin sanitizar (prompt injection)
   - Valida que la respuesta tenga el formato esperado
   - No uses el LLM para ejecutar código dinámicamente sin sandboxing
""")

print("\n" + "=" * 65)
print("Fin de APIs de IA — Continúa con 06_langchain_intro.py")
print("=" * 65)
