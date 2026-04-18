"""
Análisis de la Biblia RV60 con Pandas y visualizaciones con Matplotlib.
Aprende a cargar datos SQL en DataFrames, groupby, y generar gráficas.
Ejecutar: python 05_biblia_con_pandas.py
Requiere: pip install pandas matplotlib
"""

import sqlite3
import os
import re

# --- Ruta relativa a la BD ---
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')

# Carpeta donde se guardarán las imágenes generadas
OUTPUT_DIR = os.path.dirname(__file__)

LINEA = '=' * 60


def limpiar_texto(texto):
    """
    Elimina marcas Strong del texto del versículo.
    Retorna cadena limpia sin etiquetas <S>NNNN</S>.
    """
    limpio = re.sub(r'<S>\d+</S>', '', texto)
    return re.sub(r' {2,}', ' ', limpio).strip()


def conectar():
    """
    Abre y devuelve la conexión SQLite a la Biblia RV60.
    """
    ruta = os.path.abspath(DB_PATH)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f'No se encontró la BD en: {ruta}')
    return sqlite3.connect(ruta)


def cargar_dataframe(conn, pd):
    """
    Carga la tabla verses junto con info de libros en un DataFrame de Pandas.
    Limpia el texto, agrega columna 'testament' y 'word_count'.

    Parámetros:
        conn -- conexión SQLite activa
        pd   -- módulo pandas ya importado

    Retorna: DataFrame con columnas limpias y enriquecidas.
    """
    # Carga los datos con JOIN
    df = pd.read_sql_query('''
        SELECT v.book_number,
               b.short_name  AS book_short,
               b.long_name   AS book_name,
               v.chapter,
               v.verse,
               v.text
        FROM verses v
        JOIN books b ON v.book_number = b.book_number
        ORDER BY v.book_number, v.chapter, v.verse
    ''', conn)

    # Limpia las marcas Strong de toda la columna text
    df['text'] = df['text'].apply(limpiar_texto)

    # Agrega columna de testamento (AT o NT)
    df['testament'] = df['book_number'].apply(
        lambda n: 'AT' if n <= 390 else 'NT'
    )

    # Agrega conteo de palabras por versículo
    df['word_count'] = df['text'].str.split().str.len()

    return df


def analisis_basico(df):
    """
    Muestra estadísticas generales del DataFrame:
    forma, distribución por testamento, promedio de palabras.
    """
    print(f'\n{LINEA}')
    print('  ANÁLISIS BÁSICO DEL DATAFRAME')
    print(LINEA)
    print(f'  Filas (versículos) : {len(df):,}')
    print(f'  Columnas           : {list(df.columns)}')
    print(f'\n  Versículos por testamento:')
    print(df['testament'].value_counts().to_string(header=False))
    print(f'\n  Promedio de palabras por versículo:')
    print(f'  Total: {df["word_count"].mean():.1f}')
    print(f'  AT   : {df[df["testament"]=="AT"]["word_count"].mean():.1f}')
    print(f'  NT   : {df[df["testament"]=="NT"]["word_count"].mean():.1f}')


def groupby_por_libro(df):
    """
    Agrupa por libro y muestra los 10 libros con más versículos y
    el promedio de palabras por versículo de cada libro.
    """
    print(f'\n{LINEA}')
    print('  GROUPBY POR LIBRO (top 10 por versículos)')
    print(LINEA)

    resumen = df.groupby('book_name').agg(
        versiculos=('verse', 'count'),
        capitulos=('chapter', 'nunique'),
        palabras_promedio=('word_count', 'mean')
    ).sort_values('versiculos', ascending=False)

    print(resumen.head(10).to_string())


def groupby_por_testamento(df):
    """
    Compara AT y NT en número de libros, versículos, capítulos y palabras totales.
    """
    print(f'\n{LINEA}')
    print('  GROUPBY POR TESTAMENTO')
    print(LINEA)

    resumen = df.groupby('testament').agg(
        libros=('book_number', 'nunique'),
        capitulos=('chapter', lambda x: len(set(zip(df.loc[x.index, 'book_number'], x)))),
        versiculos=('verse', 'count'),
        total_palabras=('word_count', 'sum'),
        palabras_promedio=('word_count', 'mean')
    )
    print(resumen.to_string())


def grafico_top_libros(df, plt):
    """
    Genera y guarda un gráfico de barras con los 10 libros
    que tienen más versículos. Guarda la imagen como PNG.

    Parámetros:
        df  -- DataFrame con los datos
        plt -- módulo matplotlib.pyplot ya importado
    """
    resumen = df.groupby('book_name')['verse'].count().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    colores = ['#2196F3' if df[df['book_name'] == libro]['testament'].iloc[0] == 'AT'
               else '#FF5722' for libro in resumen.index]

    resumen.plot(kind='bar', ax=ax, color=colores, edgecolor='white')
    ax.set_title('Top 10 Libros por Cantidad de Versículos\n(Azul = AT, Rojo = NT)',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Libro', fontsize=11)
    ax.set_ylabel('Número de Versículos', fontsize=11)
    ax.tick_params(axis='x', rotation=30)
    ax.grid(axis='y', alpha=0.3)

    # Añade el número sobre cada barra
    for bar, valor in zip(ax.patches, resumen.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 5,
                str(int(valor)),
                ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    ruta = os.path.join(OUTPUT_DIR, 'top10_libros.png')
    plt.savefig(ruta, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'\n  Gráfico guardado: {ruta}')


def mapa_calor_salmos(df, plt, sns):
    """
    Genera un mapa de calor mostrando la cantidad de versículos
    por capítulo en el libro de Salmos.

    Parámetros:
        df  -- DataFrame completo
        plt -- matplotlib.pyplot
        sns -- seaborn (puede ser None si no está instalado)
    """
    salmos = df[df['book_name'] == 'Salmos'].copy()

    # Cuenta versículos por capítulo
    conteo = salmos.groupby('chapter')['verse'].count().reset_index()
    conteo.columns = ['Capítulo', 'Versículos']

    fig, ax = plt.subplots(figsize=(18, 4))

    # Organiza en filas de 30 capítulos para que sea legible
    caps = conteo['Versículos'].values
    cols_por_fila = 30
    filas = [caps[i:i+cols_por_fila] for i in range(0, len(caps), cols_por_fila)]

    # Rellena la última fila para que sea rectangular
    max_cols = max(len(f) for f in filas)
    import numpy as np
    matriz = np.zeros((len(filas), max_cols))
    for i, fila in enumerate(filas):
        matriz[i, :len(fila)] = fila

    im = ax.imshow(matriz, cmap='YlOrRd', aspect='auto')
    plt.colorbar(im, ax=ax, label='Versículos')
    ax.set_title('Mapa de Calor: Versículos por Capítulo — Salmos',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Capítulo (dentro de cada fila)')
    ax.set_ylabel('Grupo de capítulos')

    plt.tight_layout()
    ruta = os.path.join(OUTPUT_DIR, 'mapa_calor_salmos.png')
    plt.savefig(ruta, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  Mapa de calor guardado: {ruta}')


def main():
    """
    Punto de entrada: intenta importar pandas y matplotlib,
    muestra instrucciones si no están instalados, y ejecuta los análisis.
    """
    print(f'\n{"#" * 60}')
    print('  ANÁLISIS CON PANDAS — BIBLIA RV60')
    print(f'{"#" * 60}')

    # Verifica pandas
    try:
        import pandas as pd
    except ImportError:
        print('\n  [!] pandas no está instalado.')
        print('      Instálalo con: pip install pandas')
        print('      Luego vuelve a ejecutar este script.\n')
        return

    # Verifica matplotlib
    try:
        import matplotlib
        matplotlib.use('Agg')  # Sin interfaz gráfica (guarda en archivo)
        import matplotlib.pyplot as plt
        tiene_matplotlib = True
    except ImportError:
        print('\n  [!] matplotlib no está instalado.')
        print('      Instálalo con: pip install matplotlib')
        print('      Los análisis de texto se ejecutarán igual, sin gráficas.\n')
        plt = None
        tiene_matplotlib = False

    # Seaborn es opcional
    try:
        import seaborn as sns
    except ImportError:
        sns = None

    try:
        conn = conectar()
        print('\n  Cargando datos en DataFrame...')
        df = cargar_dataframe(conn, pd)
        print(f'  Datos cargados: {len(df):,} versículos.')

        analisis_basico(df)
        groupby_por_libro(df)
        groupby_por_testamento(df)

        if tiene_matplotlib:
            print(f'\n  Generando gráficos...')
            grafico_top_libros(df, plt)
            mapa_calor_salmos(df, plt, sns)
        else:
            print('\n  [!] Sin matplotlib, se omiten los gráficos.')

        conn.close()
        print(f'\n{LINEA}')
        print('  Análisis completado.')
        print(LINEA)

    except FileNotFoundError as e:
        print(f'\n[ERROR] {e}')
    except sqlite3.Error as e:
        print(f'\n[ERROR SQLite] {e}')
    except Exception as e:
        print(f'\n[ERROR] {e}')
        raise


if __name__ == '__main__':
    main()
