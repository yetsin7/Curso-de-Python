# =============================================================================
# CAPÍTULO 24 — Inteligencia Artificial y Deep Learning
# Archivo: 01_redes_neuronales_conceptos.py
# Tema: Perceptrón y redes neuronales desde cero con NumPy
# =============================================================================
#
# Antes de usar Keras o PyTorch, es fundamental entender qué ocurre por dentro.
# Este archivo implementa una red neuronal desde cero usando solo NumPy.
#
# Objetivo: entender forward pass, backpropagation y gradient descent
# sin ninguna abstracción. Esto te permitirá usar frameworks con criterio.
# =============================================================================

try:
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Librería faltante: {e}")
    print("Instala con: pip install numpy matplotlib")
    exit(1)

import os
OUTPUT_DIR = "graficos_nn_conceptos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 65)
print("REDES NEURONALES — Implementación desde cero con NumPy")
print("=" * 65)

# =============================================================================
# SECCIÓN 1: El Perceptrón — La neurona artificial más simple
# =============================================================================
print("\n--- 1. Perceptrón Simple ---")

# Una sola neurona calcula:
#   output = activation_function(w·x + b)
# donde w = pesos, x = entrada, b = bias

class Perceptron:
    """
    Implementa un perceptrón simple: una sola neurona lineal.
    Aprende a clasificar datos linealmente separables.
    """

    def __init__(self, learning_rate=0.1, n_iterations=100):
        # Tasa de aprendizaje: cuánto ajustar los pesos en cada paso
        # Muy alta → inestable; Muy baja → lento
        self.lr = learning_rate
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = None

    def _step_function(self, x):
        """Función de activación escalón: output 0 o 1."""
        return np.where(x >= 0, 1, 0)

    def fit(self, X, y):
        """
        Entrena el perceptrón con la regla de Hebb/Perceptrón:
        w = w + lr * (y_real - y_pred) * x
        """
        n_samples, n_features = X.shape
        # Inicializar pesos en cero o aleatorio pequeño
        self.weights = np.zeros(n_features)
        self.bias = 0

        for _ in range(self.n_iterations):
            for x_i, y_i in zip(X, y):
                # Forward pass: calcular predicción
                z = np.dot(x_i, self.weights) + self.bias
                y_pred = self._step_function(z)

                # Calcular error y actualizar pesos
                error = y_i - y_pred
                self.weights += self.lr * error * x_i
                self.bias += self.lr * error

    def predict(self, X):
        """Predice etiquetas para nuevas entradas."""
        z = np.dot(X, self.weights) + self.bias
        return self._step_function(z)


# Problema: clasificar puntos que están arriba o abajo de una línea
np.random.seed(42)
X_and = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y_and = np.array([0, 0, 0, 1])  # AND lógico

perceptron = Perceptron(learning_rate=0.1, n_iterations=100)
perceptron.fit(X_and, y_and)

print(f"AND lógico — Perceptrón entrenado:")
for x, y_real in zip(X_and, y_and):
    pred = perceptron.predict(x.reshape(1, -1))[0]
    estado = "✓" if pred == y_real else "✗"
    print(f"  {x} → predicho: {pred}, real: {y_real} {estado}")

# =============================================================================
# SECCIÓN 2: Funciones de Activación — La no-linealidad que hace posible el DL
# =============================================================================
print("\n--- 2. Funciones de Activación ---")

# Sin funciones de activación no-lineales, una red de N capas equivale
# a una sola capa lineal. Las funciones de activación permiten aprender
# relaciones complejas y no lineales.

x = np.linspace(-5, 5, 200)

def sigmoid(x):
    """
    Comprime cualquier valor al rango (0, 1).
    Usada históricamente en capas ocultas y en la capa de salida para clasificación binaria.
    Problema: gradiente se desvanece para valores muy positivos o muy negativos.
    """
    return 1 / (1 + np.exp(-x))

def relu(x):
    """
    ReLU (Rectified Linear Unit): max(0, x).
    La más usada en capas ocultas de redes profundas.
    Ventajas: simple, rápida, no sufre tanto el problema del gradiente desvanecido.
    Problema: "neuronas muertas" (si la entrada siempre es negativa, el gradiente=0).
    """
    return np.maximum(0, x)

def tanh(x):
    """
    Tangente hiperbólica: rango (-1, 1), centrada en 0.
    Mejor que sigmoid porque el output centrado en 0 facilita el aprendizaje.
    """
    return np.tanh(x)

def leaky_relu(x, alpha=0.01):
    """
    Leaky ReLU: soluciona el problema de neuronas muertas de ReLU.
    Para x < 0: retorna alpha * x en vez de 0.
    """
    return np.where(x >= 0, x, alpha * x)

fig, axes = plt.subplots(2, 2, figsize=(11, 8))
fig.suptitle("Funciones de Activación en Deep Learning", fontsize=13)

funciones = [
    ("Sigmoid σ(x)", sigmoid(x), "Clasificación binaria (salida)"),
    ("ReLU max(0,x)", relu(x), "Capas ocultas — la más popular"),
    ("Tanh", tanh(x), "Capas ocultas — alternativa centrada"),
    ("Leaky ReLU", leaky_relu(x), "Soluciona neuronas muertas de ReLU")
]

for ax, (titulo, y_vals, descripcion) in zip(axes.flat, funciones):
    ax.plot(x, y_vals, linewidth=2.5, color="#1565C0")
    ax.axhline(0, color="black", linewidth=0.7, alpha=0.5)
    ax.axvline(0, color="black", linewidth=0.7, alpha=0.5)
    ax.set_title(titulo, fontweight="bold")
    ax.set_xlabel(descripcion, fontsize=9, color="gray")
    ax.grid(True, alpha=0.3)

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "funciones_activacion.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Gráfico guardado: {ruta}")

# =============================================================================
# SECCIÓN 3: Red Neuronal completa desde cero — 2 capas
# =============================================================================
print("\n--- 3. Red Neuronal 2 Capas con Backpropagation ---")

class NeuralNetwork:
    """
    Red neuronal con una capa oculta, implementada desde cero.
    Arquitectura: Entrada (2) → Oculta (4, ReLU) → Salida (1, Sigmoid)

    Este es el núcleo de TODO el deep learning:
    1. Forward pass: calcular predicción
    2. Calcular loss (error)
    3. Backpropagation: calcular gradientes (regla de la cadena)
    4. Gradient descent: actualizar pesos
    """

    def __init__(self, input_size, hidden_size, output_size, lr=0.01):
        # Xavier initialization: escala los pesos según el tamaño de las capas
        # Evita que los gradientes exploten o desaparezcan al inicio
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2.0 / input_size)
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(2.0 / hidden_size)
        self.b2 = np.zeros((1, output_size))
        self.lr = lr
        self.losses = []  # Historial de loss para graficar

    def _relu(self, z):
        """Activación ReLU para la capa oculta."""
        return np.maximum(0, z)

    def _relu_deriv(self, z):
        """Derivada de ReLU: 1 donde z>0, 0 donde z<=0."""
        return (z > 0).astype(float)

    def _sigmoid(self, z):
        """Activación Sigmoid para la capa de salida (clasificación binaria)."""
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))

    def forward(self, X):
        """
        Forward pass: propaga los datos de entrada hacia la salida.
        Guarda los valores intermedios para usarlos en backpropagation.
        """
        # Capa 1: lineal + ReLU
        self.Z1 = X @ self.W1 + self.b1
        self.A1 = self._relu(self.Z1)

        # Capa 2: lineal + Sigmoid
        self.Z2 = self.A1 @ self.W2 + self.b2
        self.A2 = self._sigmoid(self.Z2)

        return self.A2

    def compute_loss(self, y_pred, y_true):
        """
        Binary Cross-Entropy Loss: la función de costo estándar para clasificación binaria.
        Loss = -mean(y * log(ŷ) + (1-y) * log(1-ŷ))
        Penaliza más cuando la predicción está muy equivocada con alta confianza.
        """
        m = len(y_true)
        eps = 1e-15  # Evitar log(0)
        loss = -np.mean(
            y_true * np.log(y_pred + eps) + (1 - y_true) * np.log(1 - y_pred + eps)
        )
        return loss

    def backward(self, X, y_true):
        """
        Backpropagation: calcula los gradientes usando la regla de la cadena.
        Propaga el error desde la salida hacia la entrada para saber
        cuánto contribuyó cada peso al error.
        """
        m = len(y_true)

        # Gradiente de la capa de salida
        dA2 = self.A2 - y_true  # Derivada de BCE + Sigmoid combinadas
        dW2 = self.A1.T @ dA2 / m
        db2 = np.mean(dA2, axis=0, keepdims=True)

        # Gradiente de la capa oculta (regla de la cadena hacia atrás)
        dA1 = dA2 @ self.W2.T
        dZ1 = dA1 * self._relu_deriv(self.Z1)
        dW1 = X.T @ dZ1 / m
        db1 = np.mean(dZ1, axis=0, keepdims=True)

        # Actualizar pesos (gradient descent)
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1

    def train(self, X, y, epochs=1000, print_every=200):
        """Ciclo de entrenamiento completo."""
        y = y.reshape(-1, 1)
        for epoch in range(epochs):
            y_pred = self.forward(X)
            loss = self.compute_loss(y_pred, y)
            self.losses.append(loss)
            self.backward(X, y)

            if epoch % print_every == 0:
                acc = ((y_pred > 0.5).astype(int) == y).mean()
                print(f"  Epoch {epoch:4d} | Loss: {loss:.4f} | Accuracy: {acc:.3f}")

    def predict(self, X):
        """Predice clases binarias para nuevas entradas."""
        probs = self.forward(X)
        return (probs > 0.5).astype(int).flatten()


# Problema XOR — no es linealmente separable, requiere red con capa oculta
# El perceptrón simple NO puede resolver XOR
X_xor = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y_xor = np.array([0, 1, 1, 0])  # XOR lógico

print("\nEntrenando red neuronal para resolver XOR:")
np.random.seed(42)
nn = NeuralNetwork(input_size=2, hidden_size=4, output_size=1, lr=0.5)
nn.train(X_xor, y_xor, epochs=2000, print_every=500)

print("\nPredicciones finales en XOR:")
for x, y_real in zip(X_xor, y_xor):
    pred = nn.predict(x.reshape(1, -1))[0]
    prob = nn.forward(x.reshape(1, -1))[0, 0]
    estado = "✓" if pred == y_real else "✗"
    print(f"  {x} → pred: {pred} (prob: {prob:.3f}), real: {y_real} {estado}")

# Graficar la curva de aprendizaje
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(nn.losses, color="#1565C0", linewidth=2)
ax.set_title("Curva de Aprendizaje — Red Neuronal XOR")
ax.set_xlabel("Época")
ax.set_ylabel("Loss (Binary Cross-Entropy)")
ax.grid(True, alpha=0.3)
ruta = os.path.join(OUTPUT_DIR, "curva_aprendizaje.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"\nGráfico guardado: {ruta}")

print("\n" + "=" * 65)
print("Fin de Conceptos — Continúa con 02_keras_intro.py")
print("=" * 65)
