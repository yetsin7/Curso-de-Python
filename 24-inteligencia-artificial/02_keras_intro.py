# =============================================================================
# CAPÍTULO 24 — Inteligencia Artificial y Deep Learning
# Archivo: 02_keras_intro.py
# Tema: Introducción a Keras/TensorFlow
# =============================================================================
#
# Keras es la API de alto nivel de TensorFlow. Abstrae todo el código
# de bajo nivel (backprop, gradientes) que implementamos en el archivo anterior.
# Con Keras, construir una red neuronal es tan simple como apilar capas.
#
# Si TensorFlow no está instalado, este archivo muestra los conceptos
# con comentarios detallados y código de referencia.
# =============================================================================

import os
import numpy as np

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    from tensorflow.keras.datasets import mnist
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    TF_DISPONIBLE = True
    print(f"TensorFlow {tf.__version__} disponible")
except ImportError:
    TF_DISPONIBLE = False
    print("TensorFlow no está instalado.")
    print("Instala con: pip install tensorflow")
    print("\nMostrando código de referencia (no ejecutable sin TF)...\n")

OUTPUT_DIR = "graficos_keras"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 65)
print("KERAS/TENSORFLOW — Redes Neuronales con API de Alto Nivel")
print("=" * 65)

# =============================================================================
# CÓDIGO DE REFERENCIA — Se explica aunque TF no esté instalado
# =============================================================================

print("""
CONCEPTO: El Modelo Sequential de Keras
========================================

En Keras, la forma más simple de construir una red es con Sequential:
las capas se apilan en orden, la salida de una es la entrada de la siguiente.

Ejemplo: Clasificador de imágenes MNIST (dígitos escritos a mano)

    model = keras.Sequential([
        # Capa de aplanado: convierte la imagen 28x28 en un vector de 784
        layers.Flatten(input_shape=(28, 28)),

        # Primera capa densa (fully connected): 128 neuronas, activación ReLU
        # Dense(128) significa 784 * 128 + 128 = 100,480 parámetros
        layers.Dense(128, activation='relu'),

        # Dropout: desactiva aleatoriamente el 20% de neuronas durante entrenamiento
        # Es una técnica de regularización que previene el overfitting
        layers.Dropout(0.2),

        # Capa de salida: 10 neuronas (una por dígito 0-9), softmax
        # Softmax convierte los outputs en probabilidades que suman 1
        layers.Dense(10, activation='softmax')
    ])

COMPILAR: elegir optimizador, función de pérdida y métricas
    model.compile(
        optimizer='adam',          # Algoritmo de gradient descent adaptativo
        loss='sparse_categorical_crossentropy',  # Para clasificación multiclase
        metrics=['accuracy']
    )

ENTRENAR: fit() hace forward + backward pass automáticamente
    history = model.fit(
        X_train, y_train,
        epochs=10,              # Cuántas veces pasar por todo el dataset
        batch_size=32,          # Cuántos ejemplos procesar antes de actualizar pesos
        validation_split=0.1    # 10% de datos de entrenamiento como validación
    )

EVALUAR:
    test_loss, test_acc = model.evaluate(X_test, y_test)

PREDECIR:
    predicciones = model.predict(X_nuevos)  # Devuelve probabilidades
    clases = np.argmax(predicciones, axis=1)  # La clase con mayor probabilidad
""")

# =============================================================================
# CÓDIGO EJECUTABLE — Solo si TensorFlow está disponible
# =============================================================================

if TF_DISPONIBLE:
    print("--- Entrenando modelo real en MNIST ---\n")

    # Cargar MNIST: 70,000 imágenes de dígitos escritos a mano
    # 60,000 para entrenamiento, 10,000 para test
    (X_train, y_train), (X_test, y_test) = mnist.load_data()

    # Normalizar píxeles al rango [0, 1]
    # Los valores originales son enteros 0-255
    # La normalización acelera el entrenamiento y mejora la convergencia
    X_train = X_train.astype("float32") / 255.0
    X_test = X_test.astype("float32") / 255.0

    print(f"X_train shape: {X_train.shape}")  # (60000, 28, 28)
    print(f"y_train shape: {y_train.shape}")  # (60000,)

    # Definir el modelo
    model = keras.Sequential([
        layers.Flatten(input_shape=(28, 28)),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.2),
        layers.Dense(64, activation="relu"),
        layers.Dense(10, activation="softmax")
    ], name="clasificador_mnist")

    # Resumen de la arquitectura
    model.summary()

    # Compilar el modelo
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    # Entrenar
    print("\nEntrenando...\n")
    history = model.fit(
        X_train, y_train,
        epochs=5,
        batch_size=128,
        validation_split=0.1,
        verbose=1
    )

    # Evaluar en test
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nResultados en Test:")
    print(f"  Loss:     {test_loss:.4f}")
    print(f"  Accuracy: {test_acc:.4f}")

    # Predicciones de ejemplo
    muestra = X_test[:5]
    probs = model.predict(muestra, verbose=0)
    clases_pred = np.argmax(probs, axis=1)

    print(f"\nPredicciones de ejemplo:")
    for i, (pred, real) in enumerate(zip(clases_pred, y_test[:5])):
        conf = probs[i, pred]
        estado = "✓" if pred == real else "✗"
        print(f"  Imagen {i}: predicho={pred}, real={real}, confianza={conf:.3f} {estado}")

    # Graficar curvas de entrenamiento
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Entrenamiento MNIST con Keras", fontsize=13)

    epochs = range(1, len(history.history["accuracy"]) + 1)

    axes[0].plot(epochs, history.history["accuracy"], "bo-", label="Train")
    axes[0].plot(epochs, history.history["val_accuracy"], "ro-", label="Validación")
    axes[0].set_title("Accuracy por Época")
    axes[0].set_xlabel("Época")
    axes[0].set_ylabel("Accuracy")
    axes[0].legend()

    axes[1].plot(epochs, history.history["loss"], "bo-", label="Train")
    axes[1].plot(epochs, history.history["val_loss"], "ro-", label="Validación")
    axes[1].set_title("Loss por Época")
    axes[1].set_xlabel("Época")
    axes[1].set_ylabel("Loss")
    axes[1].legend()

    plt.tight_layout()
    ruta = os.path.join(OUTPUT_DIR, "entrenamiento_mnist.png")
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nGráfico guardado: {ruta}")

    # Visualizar algunas predicciones
    fig, axes = plt.subplots(2, 5, figsize=(12, 5))
    fig.suptitle("Predicciones en MNIST", fontsize=13)

    indices = np.random.choice(len(X_test), 10, replace=False)
    for ax, idx in zip(axes.flat, indices):
        img = X_test[idx]
        real = y_test[idx]
        pred = np.argmax(model.predict(img.reshape(1, 28, 28), verbose=0))
        color = "green" if pred == real else "red"
        ax.imshow(img, cmap="gray")
        ax.set_title(f"Pred:{pred} Real:{real}", color=color, fontsize=9)
        ax.axis("off")

    plt.tight_layout()
    ruta2 = os.path.join(OUTPUT_DIR, "predicciones_mnist.png")
    fig.savefig(ruta2, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Gráfico guardado: {ruta2}")

else:
    print("\nPara ejecutar este código, instala TensorFlow:")
    print("  pip install tensorflow")
    print("\nAlternativa ligera para CPU:")
    print("  pip install tensorflow-cpu")

print("""
CONCEPTOS CLAVE DE KERAS:
=========================
- Sequential: red de capas apiladas, flujo lineal
- Dense: capa fully-connected (todas las neuronas conectadas con todas)
- Dropout: regularización, previene overfitting
- activation: función de activación por capa
- optimizer='adam': gradiente adaptativo, el más popular
- epochs: vueltas completas por el dataset
- batch_size: ejemplos por actualización de pesos
- history: objeto con las métricas por época para graficar
""")

print("\n" + "=" * 65)
print("Fin de Keras Intro — Continúa con 03_keras_avanzado.py")
print("=" * 65)
