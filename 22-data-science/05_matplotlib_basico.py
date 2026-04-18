# =============================================================================
# CAPÍTULO 22 — Data Science con Python
# Archivo: 05_matplotlib_basico.py
# Tema: Matplotlib — Visualización de datos desde la base
# =============================================================================
#
# Matplotlib es la librería de visualización fundamental de Python.
# Todas las demás librerías (Seaborn, Pandas plotting, etc.) están construidas
# sobre Matplotlib. Entender su modelo de figuras y ejes te da control total.
#
# IMPORTANTE: Este script usa savefig() en vez de show() para ser compatible
# con todos los entornos (servidores sin pantalla, CI/CD, notebooks).
# Para ver los gráficos interactivamente en tu máquina, cambia savefig() por
# plt.show() al final de cada sección, o ejecuta en Jupyter Notebook.
# =============================================================================

try:
    import matplotlib
    matplotlib.use("Agg")  # Backend sin pantalla — necesario para savefig sin display
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError as e:
    print(f"Librería faltante: {e}")
    print("Instala con: pip install matplotlib numpy")
    exit(1)

import os

# Directorio donde se guardarán los gráficos
OUTPUT_DIR = "graficos_matplotlib"
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Gráficos se guardarán en: {OUTPUT_DIR}/")

# Estilo general — hace los gráficos más bonitos por defecto
plt.style.use("seaborn-v0_8-whitegrid")

# =============================================================================
# SECCIÓN 1: Figura y Ejes — El modelo de Matplotlib
# =============================================================================
print("\n--- 1. Modelo Figure / Axes ---")

# En Matplotlib:
# - Figure: el "lienzo" completo (la ventana o imagen)
# - Axes: cada gráfico dentro de la figura (puede haber varios)
# - Artist: cualquier elemento visual (líneas, texto, etc.)

# Crear figura con múltiples subplots (2 filas, 2 columnas)
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))
fig.suptitle("Galería de Tipos de Gráficos", fontsize=16, fontweight="bold", y=1.02)

# Datos para los ejemplos
x = np.linspace(0, 2 * np.pi, 100)  # 100 puntos de 0 a 2π

# --- Subplot 1: Gráfico de línea ---
ax1 = axes[0, 0]
ax1.plot(x, np.sin(x), color="blue", linewidth=2, label="sin(x)")
ax1.plot(x, np.cos(x), color="red", linewidth=2, linestyle="--", label="cos(x)")
ax1.set_title("Gráfico de Línea")
ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.legend()
ax1.set_xlim(0, 2 * np.pi)

# --- Subplot 2: Scatter plot ---
np.random.seed(42)
x_scatter = np.random.randn(100)
y_scatter = 2 * x_scatter + np.random.randn(100)
colores_scatter = x_scatter  # Mapear valor a color

ax2 = axes[0, 1]
scatter = ax2.scatter(x_scatter, y_scatter, c=colores_scatter,
                      cmap="viridis", alpha=0.7, s=50)
fig.colorbar(scatter, ax=ax2)
ax2.set_title("Scatter Plot")
ax2.set_xlabel("Variable X")
ax2.set_ylabel("Variable Y")

# --- Subplot 3: Histograma ---
datos_hist = np.random.normal(0, 1, 1000)

ax3 = axes[1, 0]
ax3.hist(datos_hist, bins=30, color="steelblue", edgecolor="white", alpha=0.8)
ax3.axvline(datos_hist.mean(), color="red", linewidth=2, label=f"Media: {datos_hist.mean():.2f}")
ax3.set_title("Histograma")
ax3.set_xlabel("Valor")
ax3.set_ylabel("Frecuencia")
ax3.legend()

# --- Subplot 4: Gráfico de barras ---
categorias = ["Ventas", "Marketing", "IT", "RRHH"]
valores = [420, 180, 350, 120]
colores_bar = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0"]

ax4 = axes[1, 1]
barras = ax4.bar(categorias, valores, color=colores_bar, edgecolor="white")
# Agregar etiquetas de valor encima de cada barra
for barra, val in zip(barras, valores):
    ax4.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 5,
             str(val), ha="center", va="bottom", fontweight="bold")
ax4.set_title("Gráfico de Barras")
ax4.set_ylabel("Presupuesto (miles €)")

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "01_galeria_graficos.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Guardado: {ruta}")

# =============================================================================
# SECCIÓN 2: Line Plot — Evolución temporal
# =============================================================================
print("\n--- 2. Line Plot detallado ---")

# Datos: ventas mensuales de 3 productos durante un año
meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
np.random.seed(1)
laptop = np.random.randint(80, 200, 12)
tablet = np.random.randint(50, 150, 12)
monitor = np.random.randint(30, 100, 12)

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(meses, laptop, marker="o", linewidth=2.5, markersize=8,
        color="#2196F3", label="Laptop")
ax.plot(meses, tablet, marker="s", linewidth=2.5, markersize=8,
        color="#4CAF50", label="Tablet")
ax.plot(meses, monitor, marker="^", linewidth=2.5, markersize=8,
        color="#FF9800", label="Monitor")

# Área sombreada para rango de verano (Jun-Ago)
ax.axvspan(5, 7, alpha=0.1, color="yellow", label="Temporada alta")

ax.set_title("Ventas Mensuales por Producto — 2024", fontsize=14, fontweight="bold")
ax.set_xlabel("Mes", fontsize=12)
ax.set_ylabel("Unidades Vendidas", fontsize=12)
ax.legend(loc="upper left")
ax.set_ylim(0, 220)
ax.grid(True, alpha=0.4)

ruta = os.path.join(OUTPUT_DIR, "02_line_plot.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Guardado: {ruta}")

# =============================================================================
# SECCIÓN 3: Histograma — Distribuciones
# =============================================================================
print("\n--- 3. Histogramas ---")

np.random.seed(7)
grupo_a = np.random.normal(65, 10, 500)   # Grupo A: media=65, std=10
grupo_b = np.random.normal(75, 8, 500)    # Grupo B: media=75, std=8

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Histograma simple
axes[0].hist(grupo_a, bins=25, color="#2196F3", alpha=0.7, edgecolor="white", label="Grupo A")
axes[0].hist(grupo_b, bins=25, color="#FF5722", alpha=0.7, edgecolor="white", label="Grupo B")
axes[0].axvline(grupo_a.mean(), color="#1565C0", linewidth=2, linestyle="--")
axes[0].axvline(grupo_b.mean(), color="#BF360C", linewidth=2, linestyle="--")
axes[0].set_title("Distribución de Calificaciones")
axes[0].set_xlabel("Calificación")
axes[0].set_ylabel("Frecuencia")
axes[0].legend()

# Histograma normalizado (densidad de probabilidad)
axes[1].hist(grupo_a, bins=25, density=True, color="#2196F3", alpha=0.6, label="Grupo A")
axes[1].hist(grupo_b, bins=25, density=True, color="#FF5722", alpha=0.6, label="Grupo B")
axes[1].set_title("Distribución Normalizada (Densidad)")
axes[1].set_xlabel("Calificación")
axes[1].set_ylabel("Densidad de Probabilidad")
axes[1].legend()

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "03_histogramas.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Guardado: {ruta}")

# =============================================================================
# SECCIÓN 4: Pie chart y gráfico de barras horizontal
# =============================================================================
print("\n--- 4. Pie chart y barras horizontales ---")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Pie chart — bueno solo para pocas categorías (máximo 5-6)
etiquetas = ["Producto A", "Producto B", "Producto C", "Producto D"]
tamaños = [38, 27, 22, 13]
colores_pie = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0"]
explotar = [0.05, 0, 0, 0]  # Resaltar el primero

axes[0].pie(tamaños, labels=etiquetas, colors=colores_pie,
            autopct="%1.1f%%", explode=explotar, startangle=90)
axes[0].set_title("Participación de Mercado")

# Barras horizontales — mejor para muchas categorías con etiquetas largas
paises = ["España", "México", "Argentina", "Colombia", "Chile", "Peru"]
ventas_paises = [820, 1240, 650, 480, 390, 310]

colores_grad = plt.cm.Blues(np.linspace(0.4, 0.9, len(paises)))
barras_h = axes[1].barh(paises, ventas_paises, color=colores_grad)

for barra, val in zip(barras_h, ventas_paises):
    axes[1].text(val + 10, barra.get_y() + barra.get_height()/2,
                 f"${val:,}", va="center", fontsize=9)

axes[1].set_title("Ventas por País (miles USD)")
axes[1].set_xlabel("Ventas (miles USD)")
axes[1].set_xlim(0, 1450)

plt.tight_layout()
ruta = os.path.join(OUTPUT_DIR, "04_pie_y_barras.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Guardado: {ruta}")

# =============================================================================
# SECCIÓN 5: Customización avanzada
# =============================================================================
print("\n--- 5. Customización ---")

fig, ax = plt.subplots(figsize=(10, 6))

x = np.linspace(0, 10, 300)
y1 = np.sin(x) * np.exp(-x * 0.1)

ax.plot(x, y1, color="#1A237E", linewidth=3, label="Señal amortiguada")
ax.fill_between(x, y1, alpha=0.15, color="#1A237E")

# Anotación: flecha apuntando al máximo
idx_max = np.argmax(y1)
ax.annotate(f"Máximo\n({x[idx_max]:.1f}, {y1[idx_max]:.2f})",
            xy=(x[idx_max], y1[idx_max]),
            xytext=(x[idx_max] + 1.5, y1[idx_max] + 0.15),
            arrowprops=dict(arrowstyle="->", color="red", lw=2),
            fontsize=10, color="red", fontweight="bold")

ax.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
ax.set_title("Señal Amortiguada — sin(x)·e^(-0.1x)", fontsize=14, fontweight="bold")
ax.set_xlabel("Tiempo (s)", fontsize=12)
ax.set_ylabel("Amplitud", fontsize=12)
ax.legend(fontsize=11)
ax.set_facecolor("#FAFAFA")

ruta = os.path.join(OUTPUT_DIR, "05_customizacion.png")
fig.savefig(ruta, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Guardado: {ruta}")

print(f"\nTodos los gráficos guardados en '{OUTPUT_DIR}/'")
print("Para verlos interactivamente, reemplaza savefig() con plt.show()")
print("\n" + "=" * 60)
print("Fin de Matplotlib — Continúa con 06_seaborn_y_visualizacion.py")
print("=" * 60)
