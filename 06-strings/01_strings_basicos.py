# =============================================================================
# ARCHIVO: 01_strings_basicos.py
# TEMA: Strings básicos — crear, acceder y recorrer texto
# =============================================================================


# --- FORMAS DE CREAR STRINGS ---

simple = 'Hola'                         # comillas simples
doble = "Mundo"                         # comillas dobles (equivalente)
multilinea = """Este es un texto
que ocupa varias líneas
sin problema."""                         # triple comilla para multilínea

# Usar comillas dentro de strings:
frase1 = "Él dijo 'hola'"               # comillas simples dentro de dobles
frase2 = 'Ella dijo "adiós"'            # comillas dobles dentro de simples

print(simple)
print(multilinea)
print(frase1)


# --- CARACTERES ESPECIALES (secuencias de escape) ---
# El \ introduce un carácter especial

print("Línea 1\nLínea 2")      # \n = nueva línea
print("Col1\tCol2\tCol3")      # \t = tabulación
print("Dice: \"hola\"")        # \" = comilla doble literal
print("C:\\Users\\Python")     # \\ = barra invertida literal


# --- STRINGS SON INMUTABLES ---
# No puedes cambiar un carácter de un string. Debes crear uno nuevo.

texto = "Python"
# texto[0] = "J"   ← ❌ error: los strings no se modifican

# Para "modificar", crea uno nuevo:
nuevo = "J" + texto[1:]    # "J" + "ython" = "Jython"
print(nuevo)


# --- ACCEDER POR ÍNDICE ---

lenguaje = "Python"
print(lenguaje[0])     # P
print(lenguaje[-1])    # n
print(lenguaje[1:4])   # yth  (slicing)
print(lenguaje[::-1])  # nohtyP  (invertido)


# --- LONGITUD ---

print(len("Hola"))           # 4
print(len("   "))            # 3  (los espacios también cuentan)
print(len(""))               # 0  (string vacío)


# --- RECORRER UN STRING CON FOR ---

for letra in "Python":
    print(letra)

# Recorrer con índice
palabra = "hola"
for i, letra in enumerate(palabra):
    print(f"[{i}] = {letra}")


# --- VERIFICAR CONTENIDO ---

# in / not in
print("Py" in "Python")       # True
print("java" in "Python")     # False
print("java" not in "Python") # True

# startswith y endswith
archivo = "documento.pdf"
print(archivo.endswith(".pdf"))    # True
print(archivo.startswith("doc"))   # True


# --- COMPARAR STRINGS ---

# Comparación exacta (distingue mayúsculas)
print("Ana" == "Ana")    # True
print("Ana" == "ana")    # False

# Para comparar sin importar mayúsculas, usar .lower()
entrada = "PYTHON"
if entrada.lower() == "python":
    print("¡Correcto!")


# --- STRINGS COMO SECUENCIAS ---
# Al ser secuencias, comparten operaciones con listas

texto = "abcabc"
print(texto.count("a"))    # 2   → cuántas veces aparece "a"
print(texto.index("b"))    # 1   → primera posición de "b"
