# =============================================================================
# CAPÍTULO 11 - NIVEL INTERMEDIO
# Archivo: 04_comprehensions_avanzadas.py
# Descripción: Técnicas avanzadas de comprehensions: anidadas, condicionales
#              complejas, walrus operator, comparación de memoria y
#              transformación de JSON anidado.
# =============================================================================

import sys
import time


# =============================================================================
# SECCIÓN 1: NESTED COMPREHENSIONS PARA MATRICES
# Crear, transponer y operar con matrices usando list comprehensions.
# =============================================================================

def demo_matrices():
    """
    Demuestra el uso de comprehensions anidadas para crear y
    transformar matrices (listas de listas).
    """
    print("\n" + "=" * 55)
    print("1. NESTED COMPREHENSIONS - Matrices")
    print("=" * 55)

    # Crear matriz identidad 4x4
    identidad = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
    print("\nMatriz identidad 4x4:")
    for fila in identidad:
        print(f"  {fila}")

    # Tabla de multiplicar como matriz 5x5
    tabla = [[i * j for j in range(1, 6)] for i in range(1, 6)]
    print("\nTabla de multiplicar 5x5:")
    for fila in tabla:
        print(f"  {[str(x).rjust(3) for x in fila]}")

    # Transponer una matriz (filas se convierten en columnas)
    # ANTES: [[1,2,3], [4,5,6]] → DESPUÉS: [[1,4], [2,5], [3,6]]
    original = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    transpuesta = [[fila[i] for fila in original] for i in range(len(original[0]))]
    print(f"\nOriginal:   {original}")
    print(f"Transpuesta: {transpuesta}")

    # Aplanar matriz en lista usando comprehension anidada
    aplanada = [elemento for fila in original for elemento in fila]
    print(f"Aplanada:   {aplanada}")


# =============================================================================
# SECCIÓN 2: CONDITIONAL EXPRESSIONS COMPLEJAS
# Comprehensions con múltiples condiciones y lógica anidada.
# =============================================================================

def demo_condicionales_complejas():
    """
    Muestra cómo usar condiciones complejas dentro de comprehensions,
    incluyendo expresiones ternarias anidadas y filtros múltiples.
    """
    print("\n" + "=" * 55)
    print("2. CONDITIONAL EXPRESSIONS COMPLEJAS")
    print("=" * 55)

    numeros = list(range(-10, 11))

    # Clasificar cada número con expresión ternaria anidada
    clasificados = [
        "cero" if n == 0 else ("positivo" if n > 0 else "negativo")
        for n in numeros
    ]
    print(f"\nClasificación de {numeros}:")
    # Mostrar solo los cambios para no saturar
    for n, c in zip(numeros, clasificados):
        if n in [-1, 0, 1]:
            print(f"  {n:3d} → {c}")

    # Filtro múltiple: múltiplos de 2 Y de 3 entre 1-50
    multiplos_6 = [n for n in range(1, 51) if n % 2 == 0 if n % 3 == 0]
    print(f"\nMúltiplos de 6 (entre 1-50): {multiplos_6}")

    # Comprehension con condición en el valor Y el filtro
    datos = [1, -2, None, 3, -4, None, 5, -6, 7, None]
    procesados = [
        abs(x) * 2 if x is not None and x < 0 else x
        for x in datos
        if x is not None
    ]
    print(f"\nDatos:     {datos}")
    print(f"Procesados: {procesados}")

    # Dict comprehension con condición compleja
    estudiantes = {"Ana": 95, "Luis": 42, "María": 78, "Pedro": 55, "Sofía": 88}
    aprobados = {
        nombre: ("Sobresaliente" if nota >= 90 else "Aprobado")
        for nombre, nota in estudiantes.items()
        if nota >= 60
    }
    print(f"\nEstudiantes aprobados: {aprobados}")


# =============================================================================
# SECCIÓN 3: WALRUS OPERATOR (:=) EN COMPREHENSIONS
# El walrus operator asigna y evalúa en la misma expresión.
# Disponible desde Python 3.8.
# =============================================================================

def demo_walrus_operator():
    """
    Demuestra el operador morsa (:=) en comprehensions.
    Evita calcular el mismo valor dos veces (una para filtrar, otra para usar).
    """
    print("\n" + "=" * 55)
    print("3. WALRUS OPERATOR (:=) EN COMPREHENSIONS")
    print("=" * 55)

    # Problema clásico: calcular algo costoso y usarlo en la misma comprehension
    datos = list(range(1, 21))

    # SIN walrus: la raíz cuadrada se calcula DOS veces
    sin_walrus = [x**0.5 for x in datos if x**0.5 > 3]

    # CON walrus: calcular una vez, reutilizar el resultado
    con_walrus = [raiz for x in datos if (raiz := x**0.5) > 3]

    print(f"\nResultados (√x > 3): {[round(r, 2) for r in con_walrus]}")
    print("El walrus evita calcular la raíz dos veces.")

    # Caso real: procesar texto y filtrar líneas largas
    lineas = [
        "Python es increíble",
        "Hola",
        "Las comprehensions son una característica poderosa",
        "OK",
        "El walrus operator mejora la eficiencia",
    ]

    # Filtrar y reutilizar la longitud (calculada una sola vez)
    lineas_largas = [
        f"{longitud} chars: '{linea}'"
        for linea in lineas
        if (longitud := len(linea)) > 15
    ]

    print(f"\nLíneas con más de 15 caracteres:")
    for linea in lineas_largas:
        print(f"  {linea}")


# =============================================================================
# SECCIÓN 4: COMPARACIÓN DE MEMORIA — LIST vs GENERATOR
# Los generators no almacenan todos los elementos en memoria a la vez.
# =============================================================================

def demo_memoria_list_vs_generator():
    """
    Compara el uso de memoria y tiempo entre una list comprehension
    y un generator expression para el mismo conjunto de datos.
    El generator es ideal cuando no se necesitan todos los valores a la vez.
    """
    print("\n" + "=" * 55)
    print("4. MEMORIA: LIST COMPREHENSION vs GENERATOR")
    print("=" * 55)

    N = 1_000_000  # Un millón de elementos

    # --- Lista: almacena TODO en memoria de inmediato ---
    t1 = time.perf_counter()
    lista = [x * x for x in range(N)]
    t2 = time.perf_counter()
    lista_memoria = sys.getsizeof(lista)  # Tamaño en bytes

    # --- Generator: calcula cada valor bajo demanda ---
    t3 = time.perf_counter()
    generador = (x * x for x in range(N))  # ¡No calcula nada todavía!
    t4 = time.perf_counter()
    gen_memoria = sys.getsizeof(generador)  # Solo almacena el estado

    print(f"\nN = {N:,} elementos (x² para cada x)")
    print(f"\n  List comprehension:")
    print(f"    Tiempo de creación: {(t2-t1)*1000:.2f} ms")
    print(f"    Memoria usada:      {lista_memoria:,} bytes ({lista_memoria/1024/1024:.1f} MB)")

    print(f"\n  Generator expression:")
    print(f"    Tiempo de creación: {(t4-t3)*1000:.4f} ms (prácticamente 0)")
    print(f"    Memoria usada:      {gen_memoria} bytes (solo el estado)")

    print(f"\n  → El generator usa {lista_memoria // gen_memoria:,}x menos memoria.")
    print("  → Usa generators cuando procesas grandes volúmenes uno a uno.")

    # Consumir el generator (suma de todos los cuadrados)
    total = sum(x * x for x in range(100))
    print(f"\n  Suma de x² (0..99) con generator: {total}")


# =============================================================================
# SECCIÓN 5: TRANSFORMAR JSON ANIDADO CON COMPREHENSIONS
# Extraer, filtrar y reformatear datos de estructuras JSON complejas.
# =============================================================================

def demo_json_anidado():
    """
    Demuestra cómo usar comprehensions para transformar datos JSON anidados,
    un caso muy común al consumir APIs REST.
    """
    print("\n" + "=" * 55)
    print("5. COMPREHENSIONS PARA TRANSFORMAR JSON ANIDADO")
    print("=" * 55)

    # JSON simulado de una API de tienda
    productos_json = [
        {"id": 1, "nombre": "Laptop Pro", "precio": 1299.99,
         "categorias": ["tecnología", "computadoras"],
         "stock": {"disponible": 15, "reservado": 3}},
        {"id": 2, "nombre": "Auriculares BT", "precio": 89.50,
         "categorias": ["tecnología", "audio"],
         "stock": {"disponible": 0, "reservado": 2}},
        {"id": 3, "nombre": "Silla Ergonómica", "precio": 450.00,
         "categorias": ["muebles", "oficina"],
         "stock": {"disponible": 8, "reservado": 0}},
        {"id": 4, "nombre": "Monitor 4K", "precio": 699.99,
         "categorias": ["tecnología", "monitores"],
         "stock": {"disponible": 5, "reservado": 1}},
    ]

    # 1. Extraer solo nombre y precio de productos en stock
    en_stock = [
        {"nombre": p["nombre"], "precio": p["precio"]}
        for p in productos_json
        if p["stock"]["disponible"] > 0
    ]
    print(f"\nProductos en stock: {en_stock}")

    # 2. Diccionario id → nombre para lookup rápido
    id_nombre = {p["id"]: p["nombre"] for p in productos_json}
    print(f"\nMapa id→nombre: {id_nombre}")

    # 3. Aplanar todas las categorías únicas
    todas_categorias = list({
        categoria
        for p in productos_json
        for categoria in p["categorias"]
    })
    print(f"\nCategorías únicas: {sorted(todas_categorias)}")

    # 4. Agrupar productos por primera categoría
    por_categoria = {
        categoria: [p["nombre"] for p in productos_json if categoria in p["categorias"]]
        for categoria in todas_categorias
    }
    print("\nProductos por categoría:")
    for cat, prods in sorted(por_categoria.items()):
        print(f"  {cat}: {prods}")

    # 5. Aplicar descuento del 10% a productos de tecnología
    con_descuento = [
        {**p, "precio": round(p["precio"] * 0.9, 2), "descuento": "10%"}
        if "tecnología" in p["categorias"]
        else p
        for p in productos_json
    ]
    print("\nPrecios con descuento en tecnología:")
    for p in con_descuento:
        descuento = p.get("descuento", "sin descuento")
        print(f"  {p['nombre']:<20} ${p['precio']:>8.2f}  [{descuento}]")


# =============================================================================
# SECCIÓN 6: RESUMEN DE SINTAXIS DE COMPREHENSIONS
# =============================================================================

def resumen_sintaxis():
    """
    Repaso rápido de la sintaxis de todos los tipos de comprehensions en Python.
    """
    print("\n" + "=" * 55)
    print("6. RESUMEN DE SINTAXIS")
    print("=" * 55)

    # List comprehension: [expresion for item in iterable if condicion]
    cuadrados = [x**2 for x in range(10) if x % 2 == 0]
    print(f"\nList:  [x**2 for x in range(10) if x%2==0] → {cuadrados}")

    # Dict comprehension: {clave: valor for item in iterable if condicion}
    cuadrados_dict = {x: x**2 for x in range(5)}
    print(f"Dict:  {{x: x**2 for x in range(5)}} → {cuadrados_dict}")

    # Set comprehension: {expresion for item in iterable}
    letras = {letra.lower() for letra in "Python es Genial" if letra.isalpha()}
    print(f"Set:   {{letra for letra in 'Python es Genial'}} → {sorted(letras)}")

    # Generator expression: (expresion for item in iterable)
    gen = (x**2 for x in range(5))
    print(f"Gen:   (x**2 for x in range(5)) → {list(gen)}")


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

def main():
    """Ejecuta todas las demostraciones de comprehensions avanzadas."""
    print("=" * 55)
    print("   COMPREHENSIONS AVANZADAS - CAPÍTULO 11")
    print("=" * 55)

    demo_matrices()
    demo_condicionales_complejas()
    demo_walrus_operator()
    demo_memoria_list_vs_generator()
    demo_json_anidado()
    resumen_sintaxis()

    print("\n" + "=" * 55)
    print("   Fin de demostraciones.")
    print("=" * 55)


if __name__ == "__main__":
    main()
