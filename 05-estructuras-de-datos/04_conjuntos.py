# =============================================================================
# ARCHIVO: 04_conjuntos.py
# TEMA: Conjuntos (sets) — colecciones sin duplicados
# =============================================================================
#
# Un conjunto (set) es una colección de elementos ÚNICOS y SIN ORDEN.
# - No puede tener elementos repetidos
# - No tiene índices (no puedes acceder por posición)
# - Se define con llaves {} o con set()
#
# Úsalo cuando:
#   - Necesitas eliminar duplicados de una lista
#   - Necesitas verificar pertenencia muy rápidamente
#   - Necesitas operaciones matemáticas de conjuntos (unión, intersección, etc.)
# =============================================================================


# --- CREAR CONJUNTOS ---

colores = {"rojo", "azul", "verde"}
numeros = {1, 2, 3, 4, 5}
vacio = set()    # ← IMPORTANTE: {} crea diccionario vacío, NO set vacío

print(colores)
print(type(colores))    # <class 'set'>

# Los duplicados se eliminan automáticamente
con_duplicados = {1, 2, 2, 3, 3, 3, 4}
print(con_duplicados)    # {1, 2, 3, 4}  — los duplicados desaparecen


# --- ELIMINAR DUPLICADOS DE UNA LISTA ---
# El uso más común de los conjuntos.

votos = ["si", "no", "si", "si", "no", "si", "no", "no"]
opciones_unicas = set(votos)
print(opciones_unicas)    # {'si', 'no'}

# Convertir una lista con duplicados a lista sin duplicados:
lista_con_dupes = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
sin_duplicados = list(set(lista_con_dupes))
print(sin_duplicados)    # los elementos únicos (en orden arbitrario)


# --- AGREGAR Y ELIMINAR ---

permisos = {"leer", "escribir"}

permisos.add("ejecutar")       # agregar un elemento
print(permisos)

permisos.discard("escribir")   # eliminar (no da error si no existe)
print(permisos)

permisos.remove("leer")        # eliminar (da KeyError si no existe)
print(permisos)


# --- VERIFICAR PERTENENCIA ---
# Esto es más rápido en sets que en listas.

roles_admin = {"admin", "superadmin", "moderador"}

if "admin" in roles_admin:
    print("Tiene privilegios de administrador")


# --- OPERACIONES DE CONJUNTOS (matemáticas) ---

matematica = {"Ana", "Carlos", "María", "Pedro"}
programacion = {"Carlos", "Pedro", "Lucía", "Juan"}

# UNIÓN — todos los estudiantes (en al menos una de las dos materias)
union = matematica | programacion
# o: matematica.union(programacion)
print("Unión:", union)

# INTERSECCIÓN — estudiantes en AMBAS materias al mismo tiempo
interseccion = matematica & programacion
# o: matematica.intersection(programacion)
print("Intersección:", interseccion)   # Carlos, Pedro

# DIFERENCIA — en matemática pero NO en programación
solo_matematica = matematica - programacion
# o: matematica.difference(programacion)
print("Solo matemática:", solo_matematica)  # Ana, María

# DIFERENCIA SIMÉTRICA — en una u otra, pero NO en ambas
solo_una = matematica ^ programacion
# o: matematica.symmetric_difference(programacion)
print("En solo una materia:", solo_una)


# --- SUBCONJUNTO Y SUPERCONJUNTO ---

todos_permisos = {"leer", "escribir", "ejecutar", "admin"}
permisos_usuario = {"leer", "escribir"}

# ¿Es permisos_usuario un subconjunto de todos_permisos?
print(permisos_usuario.issubset(todos_permisos))      # True
print(permisos_usuario <= todos_permisos)              # True (misma cosa)

# ¿Es todos_permisos un superconjunto de permisos_usuario?
print(todos_permisos.issuperset(permisos_usuario))    # True


# --- EJEMPLO PRÁCTICO: encontrar elementos comunes ---

tags_post1 = {"python", "programacion", "tutorial", "beginner"}
tags_post2 = {"python", "avanzado", "decoradores", "programacion"}
tags_post3 = {"javascript", "web", "frontend", "tutorial"}

# ¿Qué posts comparten tags con el post1?
comunes_1_2 = tags_post1 & tags_post2
comunes_1_3 = tags_post1 & tags_post3

print(f"\nTags comunes post1 y post2: {comunes_1_2}")  # python, programacion
print(f"Tags comunes post1 y post3: {comunes_1_3}")    # tutorial

# Tags únicos en todo el blog
todos_los_tags = tags_post1 | tags_post2 | tags_post3
print(f"Todos los tags únicos: {todos_los_tags}")
