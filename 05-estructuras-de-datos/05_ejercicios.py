# =============================================================================
# CAPÍTULO 05 - ESTRUCTURAS DE DATOS
# Archivo: 05_ejercicios.py
# Descripción: 8 ejercicios avanzados que dominan listas, diccionarios,
#              conjuntos, Counter y técnicas de procesamiento de datos.
# =============================================================================

from collections import Counter, defaultdict


# =============================================================================
# EJERCICIO 1: Agenda de contactos (CRUD completo con menú)
# Estructura: diccionario de diccionarios {'nombre': {'tel': ..., 'email': ...}}
# =============================================================================
def ejercicio_agenda():
    """
    Agenda de contactos interactiva con operaciones CRUD:
    Crear, Leer, Actualizar y Eliminar contactos.
    Los datos se guardan en memoria (dict de dicts).
    """
    print("\n--- EJERCICIO 1: Agenda de Contactos ---")

    # Diccionario principal: nombre → datos del contacto
    contacts: dict = {}

    def add_contact():
        """Agrega un nuevo contacto a la agenda."""
        name = input("Nombre: ").strip()
        if name in contacts:
            print(f"El contacto '{name}' ya existe.")
            return
        phone = input("Teléfono: ").strip()
        email = input("Email: ").strip()
        contacts[name] = {"telefono": phone, "email": email}
        print(f"Contacto '{name}' agregado.")

    def list_contacts():
        """Muestra todos los contactos almacenados."""
        if not contacts:
            print("La agenda está vacía.")
            return
        print(f"\n{'Nombre':<20} {'Teléfono':<15} {'Email'}")
        print("-" * 55)
        for name, data in sorted(contacts.items()):
            print(f"{name:<20} {data['telefono']:<15} {data['email']}")

    def search_contact():
        """Busca y muestra un contacto por nombre."""
        name = input("Nombre a buscar: ").strip()
        if name in contacts:
            print(f"\n{name}: {contacts[name]}")
        else:
            print(f"Contacto '{name}' no encontrado.")

    def delete_contact():
        """Elimina un contacto de la agenda."""
        name = input("Nombre a eliminar: ").strip()
        if name in contacts:
            del contacts[name]
            print(f"Contacto '{name}' eliminado.")
        else:
            print(f"'{name}' no existe en la agenda.")

    # Menú principal de la agenda
    while True:
        print("\n[1] Agregar | [2] Listar | [3] Buscar | [4] Eliminar | [0] Volver")
        option = input("Opción: ").strip()
        if option == "1":
            add_contact()
        elif option == "2":
            list_contacts()
        elif option == "3":
            search_contact()
        elif option == "4":
            delete_contact()
        elif option == "0":
            break
        else:
            print("Opción inválida.")


# =============================================================================
# EJERCICIO 2: Sistema de calificaciones con estadísticas
# Almacena notas de estudiantes y calcula estadísticas descriptivas.
# =============================================================================
def ejercicio_calificaciones():
    """
    Registra calificaciones de estudiantes y calcula:
    promedio, nota mínima, nota máxima, mediana y clasificación.
    """
    print("\n--- EJERCICIO 2: Sistema de Calificaciones ---")

    # Lista de calificaciones de ejemplo
    grades = [87, 92, 78, 95, 63, 88, 74, 91, 85, 70, 96, 55, 82, 79, 93]

    print(f"Calificaciones: {grades}")
    print(f"\nEstadísticas:")
    print(f"  Total de notas: {len(grades)}")
    print(f"  Promedio:       {sum(grades) / len(grades):.2f}")
    print(f"  Nota mínima:    {min(grades)}")
    print(f"  Nota máxima:    {max(grades)}")

    # Calcular mediana sin importar statistics
    sorted_grades = sorted(grades)
    mid = len(sorted_grades) // 2
    if len(sorted_grades) % 2 == 0:
        median = (sorted_grades[mid - 1] + sorted_grades[mid]) / 2
    else:
        median = sorted_grades[mid]
    print(f"  Mediana:        {median}")

    # Distribución por rango
    print("\nDistribución:")
    ranges = {"Sobresaliente (90-100)": 0, "Notable (80-89)": 0,
              "Aprobado (60-79)": 0, "Reprobado (0-59)": 0}
    for g in grades:
        if g >= 90:
            ranges["Sobresaliente (90-100)"] += 1
        elif g >= 80:
            ranges["Notable (80-89)"] += 1
        elif g >= 60:
            ranges["Aprobado (60-79)"] += 1
        else:
            ranges["Reprobado (0-59)"] += 1

    for category, count in ranges.items():
        bar = "█" * count
        print(f"  {category:<28}: {count:2d} {bar}")


# =============================================================================
# EJERCICIO 3: Frecuencia de palabras en un texto
# Usa Counter para encontrar las palabras más usadas.
# =============================================================================
def ejercicio_frecuencia_palabras():
    """
    Analiza la frecuencia de palabras en un texto usando collections.Counter.
    Muestra las N palabras más comunes con un gráfico de barras ASCII.
    """
    print("\n--- EJERCICIO 3: Frecuencia de Palabras ---")
    import re

    text = """Python es un lenguaje de programación poderoso y fácil de aprender.
    Python es usado en ciencia de datos, web, automatización e inteligencia artificial.
    Muchos expertos consideran que Python es el mejor lenguaje para empezar a programar.
    La comunidad de Python es enorme y hay muchos recursos para aprender Python."""

    print(f"Texto de análisis (fragmento): '{text[:80]}...'")

    # Limpiar y dividir en palabras (ignorar puntuación y mayúsculas)
    words = re.findall(r'\b[a-záéíóúüñ]+\b', text.lower())
    # Excluir palabras muy comunes (stop words básicas)
    stop_words = {"es", "un", "de", "y", "en", "el", "la", "los", "las",
                  "a", "que", "para", "con", "por", "se", "al", "lo"}
    filtered = [w for w in words if w not in stop_words]

    word_count = Counter(filtered)
    top_10 = word_count.most_common(10)

    print(f"\nTop 10 palabras más frecuentes:")
    max_count = top_10[0][1] if top_10 else 1
    for word, count in top_10:
        bar_length = int(count / max_count * 20)
        bar = "█" * bar_length
        print(f"  {word:<15} {count:2d} {bar}")


# =============================================================================
# EJERCICIO 4: Eliminar duplicados manteniendo el orden de aparición
# Los sets no conservan orden; aquí combinamos set + lista para lograrlo.
# =============================================================================
def eliminar_duplicados_ordenados(lst: list) -> list:
    """
    Elimina los elementos duplicados de una lista manteniendo
    el orden de primera aparición de cada elemento.

    Args:
        lst: Lista con posibles duplicados.

    Returns:
        Nueva lista sin duplicados, en el orden original de aparición.
    """
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def ejercicio_eliminar_duplicados():
    """
    Demuestra la eliminación de duplicados preservando el orden.
    Compara la solución con set() vs la solución correcta.
    """
    print("\n--- EJERCICIO 4: Eliminar Duplicados (con orden) ---")

    numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2]
    words = ["banana", "manzana", "pera", "banana", "uva", "manzana", "kiwi"]

    print(f"Lista original: {numbers}")
    print(f"Con set() (sin orden): {sorted(list(set(numbers)))}")
    print(f"Con orden preservado:  {eliminar_duplicados_ordenados(numbers)}")

    print(f"\nFrutas originales: {words}")
    print(f"Sin duplicados:    {eliminar_duplicados_ordenados(words)}")


# =============================================================================
# EJERCICIO 5: Merge de dos diccionarios sumando valores comunes
# Cuando ambos diccionarios tienen la misma clave, se suman los valores.
# =============================================================================
def merge_sum_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Combina dos diccionarios. Si una clave existe en ambos,
    suma los valores en lugar de sobreescribir.

    Args:
        dict1: Primer diccionario.
        dict2: Segundo diccionario.

    Returns:
        Nuevo diccionario con todas las claves y valores sumados.
    """
    result = dict(dict1)  # Copiar el primero
    for key, value in dict2.items():
        if key in result:
            result[key] += value  # Sumar si ya existe
        else:
            result[key] = value   # Agregar si es nuevo
    return result


def ejercicio_merge_diccionarios():
    """
    Combina inventarios de dos tiendas sumando las cantidades.
    """
    print("\n--- EJERCICIO 5: Merge de Diccionarios (suma de valores) ---")

    store_a = {"manzanas": 50, "peras": 30, "uvas": 20, "mangos": 15}
    store_b = {"peras": 25, "uvas": 40, "kiwis": 35, "mangos": 10}

    merged = merge_sum_dicts(store_a, store_b)

    print(f"Tienda A: {store_a}")
    print(f"Tienda B: {store_b}")
    print(f"Inventario combinado: {merged}")

    # Alternativa elegante con Counter
    combined_counter = Counter(store_a) + Counter(store_b)
    print(f"Con Counter:          {dict(combined_counter)}")


# =============================================================================
# EJERCICIO 6: Encontrar los N elementos más comunes
# Generalización del Counter para cualquier colección.
# =============================================================================
def ejercicio_mas_comunes():
    """
    Encuentra los N elementos más frecuentes en una lista.
    Útil para análisis de datos, logs, votaciones, etc.
    """
    print("\n--- EJERCICIO 6: N Elementos Más Comunes ---")

    votes = ["Python", "Java", "Python", "C++", "Python", "JavaScript",
             "Java", "Python", "Go", "JavaScript", "Java", "Rust",
             "Python", "Go", "JavaScript", "Python", "C++"]

    n = 3
    counter = Counter(votes)
    top_n = counter.most_common(n)

    print(f"Votos registrados: {len(votes)}")
    print(f"\nTop {n} más votados:")
    for rank, (language, count) in enumerate(top_n, 1):
        percentage = count / len(votes) * 100
        print(f"  #{rank} {language:<15} {count} votos ({percentage:.1f}%)")


# =============================================================================
# EJERCICIO 7: Flatten de lista anidada arbitrariamente profunda
# Aplana una lista con cualquier nivel de anidamiento.
# =============================================================================
def flatten(nested: list) -> list:
    """
    Aplana una lista anidada a cualquier profundidad de forma recursiva.
    Maneja listas dentro de listas dentro de listas, etc.

    Args:
        nested: Lista que puede contener otras listas como elementos.

    Returns:
        Lista plana con todos los elementos en el mismo nivel.

    Ejemplo:
        flatten([1, [2, [3, [4]]], 5]) → [1, 2, 3, 4, 5]
    """
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))  # Recursión para sub-listas
        else:
            result.append(item)
    return result


def ejercicio_flatten():
    """
    Demuestra el aplanamiento de listas anidadas a diferentes profundidades.
    """
    print("\n--- EJERCICIO 7: Flatten de Lista Anidada ---")

    examples = [
        [1, 2, 3, 4, 5],
        [1, [2, 3], [4, 5]],
        [1, [2, [3, [4, [5]]]]],
        [[1, 2], [3, [4, 5]], [6, [7, [8, 9]]], 10],
    ]

    for lst in examples:
        print(f"  Original: {str(lst):<40} → Plano: {flatten(lst)}")


# =============================================================================
# EJERCICIO 8: Agrupar anagramas de una lista de palabras
# Dos palabras son anagramas si tienen las mismas letras en diferente orden.
# =============================================================================
def agrupar_anagramas(words: list) -> list:
    """
    Agrupa palabras que son anagramas entre sí.
    Estrategia: ordenar las letras de cada palabra como clave.

    Args:
        words: Lista de strings a agrupar.

    Returns:
        Lista de listas, donde cada sublista contiene anagramas.

    Ejemplo:
        agrupar_anagramas(["eat","tea","tan","ate","nat","bat"])
        → [["eat","tea","ate"], ["tan","nat"], ["bat"]]
    """
    groups: dict = defaultdict(list)
    for word in words:
        # La clave es la versión con letras ordenadas alfabéticamente
        key = "".join(sorted(word.lower()))
        groups[key].append(word)
    # Retornar solo los grupos (sin las claves)
    return [group for group in groups.values()]


def ejercicio_anagramas():
    """
    Demuestra la agrupación de anagramas usando defaultdict.
    """
    print("\n--- EJERCICIO 8: Agrupar Anagramas ---")

    words = ["eat", "tea", "tan", "ate", "nat", "bat",
             "amor", "roma", "mora", "armo", "python", "listen", "silent", "enlist"]

    groups = agrupar_anagramas(words)

    print(f"Palabras: {words}")
    print(f"\nGrupos de anagramas:")
    for group in sorted(groups, key=len, reverse=True):
        if len(group) > 1:
            print(f"  {group}")
        else:
            print(f"  {group} (sin anagrama)")


# =============================================================================
# MENÚ PRINCIPAL
# =============================================================================
def main():
    """Menú principal para acceder a cada ejercicio del capítulo."""
    exercises = {
        "1": ("Agenda de contactos (CRUD)", ejercicio_agenda),
        "2": ("Sistema de calificaciones", ejercicio_calificaciones),
        "3": ("Frecuencia de palabras", ejercicio_frecuencia_palabras),
        "4": ("Eliminar duplicados con orden", ejercicio_eliminar_duplicados),
        "5": ("Merge de diccionarios (suma)", ejercicio_merge_diccionarios),
        "6": ("N elementos más comunes", ejercicio_mas_comunes),
        "7": ("Flatten de lista anidada", ejercicio_flatten),
        "8": ("Agrupar anagramas", ejercicio_anagramas),
        "0": ("Salir", None),
    }

    print("=" * 55)
    print("   EJERCICIOS - CAPÍTULO 05: ESTRUCTURAS DE DATOS")
    print("=" * 55)

    while True:
        print("\nElige un ejercicio:")
        for key, (name, _) in exercises.items():
            print(f"  [{key}] {name}")

        choice = input("\nOpción: ").strip()

        if choice == "0":
            print("¡Hasta luego!")
            break
        elif choice in exercises:
            _, func = exercises[choice]
            func()
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
