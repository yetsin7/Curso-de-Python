# =============================================================================
# ARCHIVO: 04_comentarios.py
# TEMA: Comentarios — notas dentro del código
# =============================================================================
#
# Un COMENTARIO es texto dentro del código que Python ignora completamente.
# No se ejecuta, no afecta el programa. Solo sirve para que los humanos
# (tú, o alguien que lea tu código después) entiendan qué hace cada parte.
#
# Los comentarios son una de las habilidades más importantes de un buen
# programador. Código sin comentarios es difícil de entender y mantener.
# =============================================================================


# --- COMENTARIO DE UNA LÍNEA ---
# Para escribir un comentario de una línea, pon # al inicio.
# Todo lo que esté después del # en esa línea es ignorado por Python.

# Esto es un comentario. Python no lo ejecuta.
print("Esto sí se ejecuta")   # Esto también es un comentario (al final de línea)


# --- COMENTARIO DE MÚLTIPLES LÍNEAS ---
# No existe un símbolo especial para comentarios multilínea en Python.
# La convención es poner # en cada línea:

# Este es un bloque de comentarios largo
# que ocupa varias líneas.
# Python ignora todas estas líneas.

# Alternativa: usar triple comilla """ o '''
# Técnicamente esto es un string que no se asigna a nada,
# pero se usa a veces como comentario largo (docstring):
"""
Esto es un texto entre triple comilla.
Python lo procesa como un string pero como no se guarda en ninguna variable
ni se usa para nada, funciona como comentario.
Se usa principalmente para documentar funciones y clases (lo verás más adelante).
"""


# --- ¿CUÁNDO COMENTAR? ---

# ✅ Comenta el PORQUÉ, no el QUÉ.
# El código en sí ya dice QUÉ hace. El comentario agrega el PORQUÉ.

# ❌ Mal comentario (dice lo mismo que el código, es inútil):
x = x + 1  if (x := 5) else x  # suma 1 a x (esto lo veo yo solo)

# ✅ Buen comentario (explica por qué se hace esto):
intentos = 0
intentos_maximos = 3  # límite de intentos antes de bloquear la cuenta

# ✅ Otro buen comentario (explica algo no obvio):
precio = precio * 1.19  # se agrega el 19% de IVA según ley vigente


# --- COMENTAR CÓDIGO TEMPORALMENTE ---
# También puedes "desactivar" líneas de código poniéndoles # al inicio.
# Esto es útil para probar cosas sin borrar código.

print("Esta línea está activa")
# print("Esta línea está desactivada temporalmente")
print("Esta también está activa")


# =============================================================================
# HÁBITO: Desde ahora, escribe al menos un comentario por cada bloque
# de código que crees. Con el tiempo se vuelve natural.
# =============================================================================
