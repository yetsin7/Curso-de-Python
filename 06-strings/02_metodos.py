# =============================================================================
# ARCHIVO: 02_metodos.py
# TEMA: Métodos de strings — las herramientas más útiles para texto
# =============================================================================
#
# Un método es una función que "pertenece" a un tipo de dato.
# Se llama con: variable.metodo()
#
# IMPORTANTE: los strings son inmutables.
# Los métodos NO modifican el string original — devuelven UNO NUEVO.
# =============================================================================

texto = "  ¡Hola, Mundo en Python!  "


# --- MAYÚSCULAS Y MINÚSCULAS ---

print("python".upper())           # PYTHON
print("PYTHON".lower())           # python
print("hola mundo".capitalize())  # Hola mundo  (solo la primera letra)
print("hola mundo".title())       # Hola Mundo  (cada palabra capitalizada)
print("HoLa MuNdO".swapcase())    # hOlA mUnDo  (invierte mayúsculas/minúsculas)


# --- LIMPIAR ESPACIOS ---

sucio = "   hola mundo   "
print(sucio.strip())              # "hola mundo"   (elimina espacios de ambos lados)
print(sucio.lstrip())             # "hola mundo   " (solo lado izquierdo)
print(sucio.rstrip())             # "   hola mundo" (solo lado derecho)

# Útil para limpiar entrada del usuario:
nombre_usuario = input("Tu nombre: ").strip()


# --- BUSCAR Y REEMPLAZAR ---

frase = "El gato come gato"

# find() devuelve el índice de la primera ocurrencia, -1 si no existe
print(frase.find("gato"))      # 3
print(frase.find("perro"))     # -1  (no existe)

# rfind() busca desde el final
print(frase.rfind("gato"))     # 14  (última ocurrencia)

# replace() reemplaza todas las ocurrencias
nueva = frase.replace("gato", "perro")
print(nueva)                   # "El perro come perro"

# Reemplazar solo la primera ocurrencia
nueva2 = frase.replace("gato", "perro", 1)
print(nueva2)                  # "El perro come gato"


# --- DIVIDIR Y UNIR ---

# split() — divide un string en una lista usando un separador
csv = "Ana,Carlos,María,Pedro"
nombres = csv.split(",")
print(nombres)    # ['Ana', 'Carlos', 'María', 'Pedro']

ruta = "/usuarios/ana/documentos/archivo.txt"
partes = ruta.split("/")
print(partes)     # ['', 'usuarios', 'ana', 'documentos', 'archivo.txt']

# split() sin argumento divide por cualquier espacio en blanco
frase = "hola   mundo   python"
palabras = frase.split()
print(palabras)   # ['hola', 'mundo', 'python']

# join() — une una lista de strings con un separador
# Es el inverso de split()
separador = ", "
resultado = separador.join(nombres)
print(resultado)    # "Ana, Carlos, María, Pedro"

# Unir con otros separadores
print(" | ".join(["uno", "dos", "tres"]))    # uno | dos | tres
print("".join(["a", "b", "c"]))              # abc


# --- VERIFICAR CONTENIDO ---

print("123".isdigit())         # True   — solo contiene dígitos
print("abc".isalpha())         # True   — solo letras
print("abc123".isalnum())      # True   — solo letras o números
print("   ".isspace())         # True   — solo espacios
print("Hola Mundo".istitle())  # True   — formato título


# --- ALINEAR Y RELLENAR ---

# center, ljust, rjust — para formatear texto en tablas/reportes
titulo = "REPORTE"
print(titulo.center(40, "="))   # ================REPORTE================
print("Ana".ljust(20, "."))     # Ana.................
print("100".rjust(10))          #        100

# zfill() — rellena con ceros a la izquierda (útil para IDs, códigos)
codigo = "42"
print(codigo.zfill(5))    # 00042


# --- EJEMPLO PRÁCTICO: procesar datos de un CSV ---

linea_csv = " ANA GARCIA , ana@email.com , Buenos Aires , 28 "

# Limpiar y separar
partes = [campo.strip() for campo in linea_csv.split(",")]
print(partes)

nombre = partes[0].title()        # "Ana Garcia"
email  = partes[1].lower()        # "ana@email.com"
ciudad = partes[2]                # "Buenos Aires"
edad   = int(partes[3])           # 28

print(f"Nombre: {nombre}")
print(f"Email: {email}")
print(f"Ciudad: {ciudad}")
print(f"Edad: {edad}")
