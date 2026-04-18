# =============================================================================
# CAPÍTULO 24 — Inteligencia Artificial y Deep Learning
# Archivo: 03_keras_avanzado.py
# Tema: Keras avanzado — Functional API, callbacks, regularización
# =============================================================================
#
# La API Sequential es suficiente para redes simples. Para arquitecturas
# más complejas (múltiples entradas/salidas, skip connections, etc.),
# se usa la Functional API que trata las capas como funciones.
#
# También cubrimos callbacks (controlar el entrenamiento dinámicamente)
# y técnicas de regularización para modelos más robustos.
# =============================================================================

import numpy as np
import os

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, callbacks, regularizers
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    TF_DISPONIBLE = True
    print(f"TensorFlow {tf.__version__} disponible")
except ImportError:
    TF_DISPONIBLE = False
    print("TensorFlow no disponible. Mostrando código de referencia.")
    print("Instala con: pip install tensorflow\n")

OUTPUT_DIR = "graficos_keras_avanzado"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 65)
print("KERAS AVANZADO — Functional API, Callbacks y Regularización")
print("=" * 65)

# =============================================================================
# CONCEPTO 1: Functional API — Para arquitecturas complejas
# =============================================================================
print("""
--- 1. Functional API ---

La API Functional trata las capas como funciones que se llaman con tensores:

    # Entrada
    inputs = keras.Input(shape=(784,))

    # Capas (llamadas como funciones)
    x = layers.Dense(128, activation='relu')(inputs)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(64, activation='relu')(x)

    # Salida
    outputs = layers.Dense(10, activation='softmax')(x)

    # Crear el modelo especificando entrada y salida
    model = keras.Model(inputs=inputs, outputs=outputs)

Ventajas sobre Sequential:
- Permite múltiples entradas: model = keras.Model(inputs=[input1, input2], ...)
- Permite múltiples salidas
- Permite conexiones residuales (skip connections) como ResNet
- Más explícito: se ve el flujo de datos claramente
""")

# =============================================================================
# CONCEPTO 2: Callbacks — Control dinámico del entrenamiento
# =============================================================================
print("""
--- 2. Callbacks ---

Los callbacks son funciones que se ejecutan en puntos específicos del
entrenamiento (inicio de época, fin de lote, etc.).

Los más importantes:

1. EarlyStopping — Detiene el entrenamiento cuando deja de mejorar
   Evita overfitting y ahorra tiempo de cómputo.

    callback_early = callbacks.EarlyStopping(
        monitor='val_loss',    # Qué métrica monitorear
        patience=5,            # Cuántas épocas tolerar sin mejora
        restore_best_weights=True  # Restaurar los mejores pesos al parar
    )

2. ModelCheckpoint — Guarda el mejor modelo durante el entrenamiento
   Si el entrenamiento falla a la mitad, no pierdes el progreso.

    callback_checkpoint = callbacks.ModelCheckpoint(
        filepath='mejor_modelo.keras',
        monitor='val_accuracy',
        save_best_only=True     # Solo guarda si mejora
    )

3. ReduceLROnPlateau — Reduce la learning rate cuando el entrenamiento estanca
   A veces un learning rate más pequeño permite salir de un mínimo local.

    callback_lr = callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,    # Multiplica lr * factor cuando no hay mejora
        patience=3,
        min_lr=1e-6
    )

Usar callbacks en fit():
    model.fit(
        X_train, y_train,
        callbacks=[callback_early, callback_checkpoint, callback_lr],
        epochs=100  # EarlyStopping parará antes si es necesario
    )
""")

# =============================================================================
# CONCEPTO 3: Regularización — Prevenir overfitting
# =============================================================================
print("""
--- 3. Técnicas de Regularización ---

El overfitting ocurre cuando el modelo memoriza el entrenamiento pero
no generaliza. Las técnicas de regularización lo previenen:

1. DROPOUT
   Desactiva aleatoriamente un % de neuronas en cada forward pass.
   Fuerza a la red a no depender de ninguna neurona individual.

    layers.Dropout(rate=0.3)  # 30% de neuronas apagadas durante entrenamiento

2. BATCH NORMALIZATION
   Normaliza las activaciones de cada capa (media≈0, varianza≈1).
   - Acelera el entrenamiento (permite learning rates más altas)
   - Actúa como regularizador
   - Reducce la sensibilidad a la inicialización

    layers.BatchNormalization()

3. L1/L2 REGULARIZATION (Weight Decay)
   Penaliza pesos grandes en la función de costo.
   L2 (Ridge): empuja todos los pesos hacia 0
   L1 (Lasso): puede llevar algunos pesos exactamente a 0

    layers.Dense(128, kernel_regularizer=regularizers.l2(0.01))

Ejemplo con todas las técnicas juntas:

    inputs = keras.Input(shape=(20,))

    x = layers.Dense(128)(inputs)
    x = layers.BatchNormalization()(x)  # Normalizar antes de activar
    x = layers.Activation('relu')(x)
    x = layers.Dropout(0.3)(x)

    x = layers.Dense(64, kernel_regularizer=regularizers.l2(0.001))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Dropout(0.2)(x)

    outputs = layers.Dense(1, activation='sigmoid')(x)
    model = keras.Model(inputs, outputs)
""")

# =============================================================================
# CONCEPTO 4: Learning Rate Scheduling
# =============================================================================
print("""
--- 4. Learning Rate Scheduling ---

El learning rate es el hiperparámetro más importante. Una estrategia común:
- Empezar con lr alta para moverse rápido
- Reducirla a medida que el entrenamiento converge para afinar

Opciones en Keras:

# Decaimiento exponencial
lr_schedule = keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=0.001,
    decay_steps=1000,
    decay_rate=0.9
)
optimizer = keras.optimizers.Adam(learning_rate=lr_schedule)

# Cosine annealing (reinicia la lr cíclicamente)
lr_cosine = keras.optimizers.schedules.CosineDecay(
    initial_learning_rate=0.001,
    decay_steps=10000
)
""")

# =============================================================================
# EJEMPLO EJECUTABLE — Si TF está disponible
# =============================================================================
if TF_DISPONIBLE:
    print("\n--- Ejemplo ejecutable: Clasificación con todas las técnicas ---\n")

    # Dataset sintético
    np.random.seed(42)
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    X, y = make_classification(n_samples=2000, n_features=20, n_informative=10,
                                n_classes=3, random_state=42)
    X = X.astype("float32")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.15)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train).astype("float32")
    X_val = scaler.transform(X_val).astype("float32")
    X_test = scaler.transform(X_test).astype("float32")

    # Modelo con Functional API + todas las técnicas de regularización
    inputs = keras.Input(shape=(20,), name="entrada")

    x = layers.Dense(128)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Dropout(0.3)(x)

    x = layers.Dense(64, kernel_regularizer=regularizers.l2(0.001))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Dropout(0.2)(x)

    outputs = layers.Dense(3, activation="softmax", name="salida")(x)
    model = keras.Model(inputs, outputs, name="modelo_avanzado")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    model.summary()

    # Callbacks
    ruta_checkpoint = os.path.join(OUTPUT_DIR, "mejor_modelo.keras")
    mis_callbacks = [
        callbacks.EarlyStopping(monitor="val_loss", patience=10,
                                restore_best_weights=True, verbose=1),
        callbacks.ModelCheckpoint(filepath=ruta_checkpoint, monitor="val_accuracy",
                                  save_best_only=True, verbose=0),
        callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5,
                                    patience=5, min_lr=1e-6, verbose=1)
    ]

    print("\nEntrenando con callbacks...\n")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=60,
        batch_size=64,
        callbacks=mis_callbacks,
        verbose=1
    )

    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nResultados en Test: Loss={test_loss:.4f}, Accuracy={test_acc:.4f}")
    print(f"Épocas reales entrenadas: {len(history.history['accuracy'])}")

    # Graficar
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Entrenamiento con Callbacks y Regularización", fontsize=13)

    n_epochs = len(history.history["accuracy"])
    ep = range(1, n_epochs + 1)

    axes[0].plot(ep, history.history["accuracy"], label="Train")
    axes[0].plot(ep, history.history["val_accuracy"], label="Validación")
    axes[0].set_title("Accuracy")
    axes[0].set_xlabel("Época")
    axes[0].legend()

    axes[1].plot(ep, history.history["loss"], label="Train")
    axes[1].plot(ep, history.history["val_loss"], label="Validación")
    axes[1].set_title("Loss")
    axes[1].set_xlabel("Época")
    axes[1].legend()

    plt.tight_layout()
    ruta = os.path.join(OUTPUT_DIR, "entrenamiento_avanzado.png")
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Gráfico guardado: {ruta}")

print("\n" + "=" * 65)
print("Fin de Keras Avanzado — Continúa con 04_nlp_basico.py")
print("=" * 65)
