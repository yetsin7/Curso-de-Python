# =============================================================================
# CAPÍTULO 24 — Inteligencia Artificial y Deep Learning
# Archivo: 06_langchain_intro.py
# Tema: LangChain — Framework para aplicaciones con LLMs
# =============================================================================
#
# LangChain es un framework que simplifica la construcción de aplicaciones
# complejas con LLMs. Resuelve problemas comunes como:
# - Gestión del historial de conversación (memoria)
# - Encadenar múltiples llamadas al LLM (chains)
# - Conectar LLMs con herramientas externas (agentes)
# - Parsear y validar respuestas
# - Cargar documentos y bases de conocimiento (RAG)
#
# Instalación: pip install langchain langchain-openai langchain-anthropic
# =============================================================================

import os
import json

print("=" * 65)
print("LANGCHAIN — Framework para aplicaciones con LLMs")
print("=" * 65)

# Detectar qué está instalado
LANGCHAIN_OK = False
OPENAI_OK = False
ANTHROPIC_OK = False

try:
    import langchain
    LANGCHAIN_OK = True
except ImportError:
    pass

try:
    from openai import OpenAI
    OPENAI_OK = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    pass

try:
    import anthropic
    ANTHROPIC_OK = bool(os.environ.get("ANTHROPIC_API_KEY"))
except ImportError:
    pass

if not LANGCHAIN_OK:
    print("LangChain no está instalado.")
    print("Instala con: pip install langchain langchain-openai langchain-anthropic\n")

# =============================================================================
# SECCIÓN 1: Conceptos de LangChain
# =============================================================================
print("""
--- 1. Conceptos Principales de LangChain ---

COMPONENTS (Componentes fundamentales):

1. LLMs / Chat Models:
   Wrapper que normaliza la interfaz de distintos proveedores
   (OpenAI, Anthropic, Google, etc. con la misma API)

2. Prompt Templates:
   Plantillas reutilizables con variables que se llenan dinámicamente
   En vez de construir strings manualmente, usas templates formales

3. Chains:
   Secuencias de pasos: prompt → LLM → parser → siguiente paso
   Permiten componer flujos complejos de manera organizada

4. Memory:
   Almacena el historial de conversación para que el LLM tenga contexto
   Sin memoria: cada mensaje es independiente
   Con memoria: el LLM "recuerda" mensajes anteriores

5. Agents:
   LLMs que pueden usar HERRAMIENTAS (buscar en web, ejecutar código,
   consultar bases de datos) para responder preguntas complejas
   El LLM decide qué herramienta usar y cuándo

6. RAG (Retrieval-Augmented Generation):
   Conectar el LLM con una base de conocimiento propia
   El LLM puede responder sobre documentos que no estaban en su training
""")

# =============================================================================
# SECCIÓN 2: Código de referencia — Prompt Templates
# =============================================================================
print("--- 2. Prompt Templates ---")
print('''
# Sin LangChain (manual, propenso a errores):
nombre = "Juan"
tema = "Python"
prompt = f"Explícale a {nombre} qué es {tema} en 3 pasos simples."

# Con LangChain (organizado, reutilizable):
from langchain.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "Eres un tutor de {materia} para principiantes."),
    ("user", "Explícame {concepto} en {n_pasos} pasos simples.")
])

# Formatear el template con variables específicas
prompt_formateado = template.format_messages(
    materia="programación",
    concepto="las listas en Python",
    n_pasos=3
)
# Resultado: lista de HumanMessage y SystemMessage listos para enviar
''')

# =============================================================================
# SECCIÓN 3: Código de referencia — Chains LCEL
# =============================================================================
print("--- 3. Chains con LCEL (LangChain Expression Language) ---")
print('''
# LCEL usa el operador | (pipe) para encadenar componentes
# Es como Unix pipes pero para LLMs

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser

# Definir componentes
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
parser = StrOutputParser()  # Extrae el string del mensaje

# Template simple
prompt = ChatPromptTemplate.from_template(
    "Resume en 2 oraciones el siguiente texto:\\n{texto}"
)

# Chain: prompt → llm → parser
chain = prompt | llm | parser

# Ejecutar la chain
resultado = chain.invoke({"texto": "Python es un lenguaje..."})
print(resultado)

# Chain con múltiples pasos:
from langchain.prompts import PromptTemplate

# Paso 1: Generar preguntas sobre un tema
template_preguntas = PromptTemplate.from_template(
    "Genera 3 preguntas sobre {tema}"
)

# Paso 2: Responder cada pregunta
template_respuestas = PromptTemplate.from_template(
    "Responde brevemente estas preguntas:\\n{preguntas}"
)

# Encadenar: el output del primero se pasa como input al segundo
chain_doble = (
    template_preguntas
    | llm
    | parser
    | (lambda texto: {"preguntas": texto})
    | template_respuestas
    | llm
    | parser
)
''')

# =============================================================================
# SECCIÓN 4: Memoria — Chatbot que recuerda la conversación
# =============================================================================
print("--- 4. Memoria de Conversación ---")
print('''
# La memoria permite que el chatbot recuerde mensajes anteriores

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

llm = ChatOpenAI(model="gpt-4o-mini")

# ConversationBufferMemory guarda TODA la conversación
# Para conversaciones largas: usa ConversationSummaryMemory
# (resume automáticamente para no consumir demasiados tokens)
memory = ConversationBufferMemory()

chain = ConversationChain(llm=llm, memory=memory, verbose=False)

# Primera vuelta
resp1 = chain.predict(input="Hola, me llamo Carlos y soy desarrollador Python")
print(resp1)

# Segunda vuelta — el LLM "sabe" tu nombre porque está en la memoria
resp2 = chain.predict(input="¿Recuerdas cómo me llamo?")
print(resp2)  # Debería decir "Carlos"

# Ver el historial en memoria
print(memory.chat_memory.messages)
''')

# =============================================================================
# SECCIÓN 5: Implementación pura sin LangChain — chatbot con memoria manual
# =============================================================================
print("--- 5. Chatbot con Memoria (Implementación Propia) ---")
print("(Funciona sin LangChain — usa solo el SDK de OpenAI/Anthropic)")

class ChatbotConMemoria:
    """
    Chatbot simple con historial de conversación implementado sin LangChain.
    Útil para entender los fundamentos antes de usar abstracciones.
    """

    def __init__(self, nombre_bot="Asistente", system_prompt=None):
        # Historial de mensajes: el LLM ve toda esta lista en cada llamada
        self.historial = []
        self.nombre_bot = nombre_bot

        # Mensaje del sistema: define el comportamiento del bot
        if system_prompt:
            self.sistema = system_prompt
        else:
            self.sistema = f"Eres {nombre_bot}, un asistente útil y amable."

    def agregar_contexto(self, informacion):
        """Inyecta información en el contexto antes de que el usuario pregunte."""
        self.historial.append({
            "role": "user",
            "content": f"[Contexto del sistema]: {informacion}"
        })
        self.historial.append({
            "role": "assistant",
            "content": "Entendido, tomaré esto en cuenta."
        })

    def chat(self, mensaje_usuario):
        """
        Envía un mensaje y devuelve la respuesta.
        Si no hay API disponible, simula una respuesta para demostración.
        """
        self.historial.append({
            "role": "user",
            "content": mensaje_usuario
        })

        # Intentar llamar a la API si está disponible
        if OPENAI_OK:
            try:
                from openai import OpenAI
                client = OpenAI()
                respuesta = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": self.sistema}] + self.historial,
                    max_tokens=200,
                    temperature=0.7
                )
                texto = respuesta.choices[0].message.content
            except Exception as e:
                texto = f"[Error API: {e}]"
        elif ANTHROPIC_OK:
            try:
                import anthropic as ant
                client = ant.Anthropic()
                resp = client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=200,
                    system=self.sistema,
                    messages=self.historial
                )
                texto = resp.content[0].text
            except Exception as e:
                texto = f"[Error API: {e}]"
        else:
            # Simulación sin API para demostración del concepto
            respuestas_simuladas = {
                "hola": "¡Hola! Soy tu asistente de Python. ¿En qué puedo ayudarte?",
                "python": "Python es un lenguaje de alto nivel, interpretado y de propósito general.",
                "default": f"[Simulado] Recibí: '{mensaje_usuario[:30]}...' (configura una API key para respuestas reales)"
            }
            texto_lower = mensaje_usuario.lower()
            if "hola" in texto_lower:
                texto = respuestas_simuladas["hola"]
            elif "python" in texto_lower:
                texto = respuestas_simuladas["python"]
            else:
                texto = respuestas_simuladas["default"]

        self.historial.append({"role": "assistant", "content": texto})
        return texto

    def get_historial_resumido(self):
        """Devuelve un resumen del historial para debugging."""
        return [
            f"{msg['role'].upper()}: {msg['content'][:50]}..."
            for msg in self.historial
        ]


# Demostración del chatbot
print("\nDemostración del chatbot con memoria:\n")

bot = ChatbotConMemoria(
    nombre_bot="PythonBot",
    system_prompt="Eres un asistente experto en Python. Responde siempre en español y de forma concisa."
)

# Simular una conversación
conversacion = [
    "Hola, me llamo María y estoy aprendiendo Python",
    "¿Qué es una lista en Python?",
    "¿Y un diccionario?"
]

for turno, mensaje in enumerate(conversacion, 1):
    print(f"[Turno {turno}] Usuario: {mensaje}")
    respuesta = bot.chat(mensaje)
    print(f"           Bot: {respuesta}")
    print()

print(f"Historial guardado ({len(bot.historial)} mensajes):")
for entrada in bot.get_historial_resumido():
    print(f"  {entrada}")

# =============================================================================
# SECCIÓN 6: RAG — Recuperación y Generación Aumentada
# =============================================================================
print("""
--- 6. RAG — Retrieval-Augmented Generation ---

RAG permite al LLM responder preguntas sobre TUS documentos:
PDFs, sitios web, bases de datos, código fuente, etc.

Flujo de RAG:
    1. INDEXACIÓN (una vez):
       Cargar documentos → dividir en chunks → crear embeddings → guardar en vectorDB

    2. CONSULTA (cada pregunta):
       Pregunta → embedding → buscar chunks similares → pasar al LLM con contexto

Instalación:
    pip install langchain langchain-openai faiss-cpu pypdf

Ejemplo básico:

    from langchain.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain.vectorstores import FAISS
    from langchain.chains import RetrievalQA

    # 1. Cargar el documento
    loader = PyPDFLoader("mi_documento.pdf")
    docs = loader.load()

    # 2. Dividir en chunks (fragmentos pequeños)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    # 3. Crear embeddings y guardar en vectorDB
    embeddings = OpenAIEmbeddings()
    vectordb = FAISS.from_documents(chunks, embeddings)

    # 4. Crear chain de pregunta-respuesta
    llm = ChatOpenAI(model="gpt-4o-mini")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(search_kwargs={"k": 3})
    )

    # 5. Hacer preguntas sobre el documento
    respuesta = qa_chain.invoke("¿Qué dice el documento sobre las ventas?")
    print(respuesta["result"])
""")

print("\n" + "=" * 65)
print("Fin del Capítulo 24 — ¡Pasa al Capítulo 25: Scripts y CLI!")
print("=" * 65)
