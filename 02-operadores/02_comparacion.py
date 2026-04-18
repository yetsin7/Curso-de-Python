# =============================================================================
# ARCHIVO: 02_comparacion.py
# TEMA: Operadores de comparación — comparar valores
# =============================================================================
#
# Los operadores de comparación comparan dos valores y devuelven True o False.
# Son la base de las condiciones: "si esto es verdad, haz esto".
#
# IMPORTANTE: no confundas = con ==
#   =  → asignación: guarda un valor en una variable  (edad = 18)
#   == → comparación: pregunta si dos cosas son iguales (edad == 18)
# =============================================================================

a = 10
b = 5

# Igual a
print(a == b)       # False  (10 no es igual a 5)
print(a == 10)      # True

# Diferente de
print(a != b)       # True   (10 sí es diferente de 5)
print(a != 10)      # False

# Mayor que
print(a > b)        # True   (10 > 5)

# Menor que
print(a < b)        # False  (10 no es < 5)

# Mayor o igual que
print(a >= 10)      # True   (10 >= 10, son iguales)
print(a >= 11)      # False

# Menor o igual que
print(b <= 5)       # True   (5 <= 5)
print(b <= 4)       # False


# --- LOS RESULTADOS SON bool (True o False) ---
# Puedes guardar el resultado de una comparación en una variable
es_mayor = a > b
print(es_mayor)         # True
print(type(es_mayor))   # <class 'bool'>


# --- COMPARAR STRINGS (TEXTO) ---
# También puedes comparar texto
nombre1 = "Ana"
nombre2 = "Pedro"
nombre3 = "Ana"

print(nombre1 == nombre3)    # True   (mismo texto)
print(nombre1 == nombre2)    # False
print(nombre1 != nombre2)    # True

# Python distingue mayúsculas al comparar texto
print("ana" == "Ana")        # False   (diferente capitalización)
print("hola" == "hola")      # True


# --- EJEMPLO PRÁCTICO ---
edad = 17
es_mayor_de_edad = edad >= 18
print(f"¿Es mayor de edad? {es_mayor_de_edad}")     # False

nota = 60
aprobado = nota >= 51
print(f"¿Aprobó con {nota}? {aprobado}")            # True


# --- COMPARAR TIPOS DISTINTOS ---
# Python puede comparar int y float sin problema
print(5 == 5.0)      # True   (mismo valor numérico)
print(5 == "5")      # False  (un número no es igual a un texto)


# =============================================================================
# CONCEPTO CLAVE: Las comparaciones devuelven True o False.
# Esos True/False son los que usarás en el próximo capítulo con if/else.
# =============================================================================
