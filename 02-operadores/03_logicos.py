# =============================================================================
# ARCHIVO: 03_logicos.py
# TEMA: Operadores lógicos — combinar condiciones
# =============================================================================
#
# Los operadores lógicos combinan dos o más comparaciones en una sola.
# Hay tres: and, or, not
#
#   and → "y"       → ambas condiciones deben ser True
#   or  → "o"       → al menos una condición debe ser True
#   not → "no"      → invierte: True pasa a False y viceversa
# =============================================================================


# --- AND: ambas condiciones deben ser verdaderas ---

edad = 20
tiene_carnet = True

# Para entrar al evento: debe ser mayor de 18 Y tener carnet
puede_entrar = edad >= 18 and tiene_carnet
print(f"¿Puede entrar? {puede_entrar}")      # True

# Tabla de verdad del AND:
print(True and True)    # True    (ambas verdaderas → verdadero)
print(True and False)   # False   (una falsa → falso)
print(False and True)   # False
print(False and False)  # False


# --- OR: al menos una condición debe ser verdadera ---

es_admin = False
es_dueno = True

# Puede acceder si es admin O si es dueño
puede_acceder = es_admin or es_dueno
print(f"¿Puede acceder? {puede_acceder}")    # True

# Tabla de verdad del OR:
print(True or True)     # True
print(True or False)    # True    (al menos una verdadera → verdadero)
print(False or True)    # True
print(False or False)   # False   (ninguna verdadera → falso)


# --- NOT: invierte el valor booleano ---

esta_lloviendo = False
print(not esta_lloviendo)    # True   (no está lloviendo → verdadero)

esta_activo = True
print(not esta_activo)       # False  (no está activo → falso)


# --- COMBINANDO OPERADORES ---
# Puedes combinar and, or, not. Usa paréntesis para claridad.

edad = 25
tiene_membresia = False
es_invitado = True

# Puede entrar si tiene membresía, O si es invitado (y además es mayor de edad)
puede_entrar = (edad >= 18) and (tiene_membresia or es_invitado)
print(f"¿Puede entrar? {puede_entrar}")     # True


# --- EJEMPLO PRÁCTICO: sistema de login ---

usuario = "admin"
contraseña = "1234"
cuenta_activa = True

# El login es correcto si: usuario Y contraseña son correctos, Y la cuenta está activa
usuario_correcto = usuario == "admin"
contrasena_correcta = contraseña == "1234"

login_exitoso = usuario_correcto and contrasena_correcta and cuenta_activa
print(f"¿Login exitoso? {login_exitoso}")   # True


# --- SHORT-CIRCUIT (evaluación de cortocircuito) ---
# Python es inteligente: con 'and', si el primero es False, no evalúa el segundo.
# Con 'or', si el primero es True, no evalúa el segundo.
# Esto es eficiente y se usa mucho en código real.

x = 5
# False and ... → Python no evalúa lo que sigue
resultado = (x > 10) and (x / 0 > 1)   # no da error porque no llega al x/0
print(resultado)   # False
