# =============================================================================
# ARCHIVO: 01_if_elif_else.py
# TEMA: if / elif / else — tomar decisiones
# =============================================================================
#
# if significa "si". Permite ejecutar un bloque de código SOLO SI una
# condición es verdadera.
#
# Estructura básica:
#   if condición:
#       código a ejecutar si la condición es True
#
# El código dentro del if va indentado (con 4 espacios).
# El dos puntos : al final del if es OBLIGATORIO.
# =============================================================================


# --- IF SIMPLE ---

edad = 20

if edad >= 18:
    print("Eres mayor de edad")   # solo se imprime si edad >= 18 es True


# --- IF + ELSE ---
# else = "de lo contrario". Se ejecuta si la condición es False.

temperatura = 15

if temperatura >= 20:
    print("Hace calor, usa ropa liviana")
else:
    print("Hace frío, lleva abrigo")


# --- IF + ELIF + ELSE ---
# elif = "si no, si..." — permite agregar más condiciones.
# Se evalúan de arriba a abajo. La primera que sea True se ejecuta.

nota = 75

if nota >= 90:
    print("Excelente — Nota: A")
elif nota >= 80:
    print("Muy bien — Nota: B")
elif nota >= 70:
    print("Bien — Nota: C")
elif nota >= 60:
    print("Aprobado — Nota: D")
else:
    print("Reprobado — Nota: F")


# --- CONDICIONES CON OPERADORES LÓGICOS ---

usuario = "admin"
contrasena = "secreto123"

if usuario == "admin" and contrasena == "secreto123":
    print("Acceso concedido")
else:
    print("Credenciales incorrectas")


# --- IF ANIDADO (if dentro de if) ---
# Puedes poner un if dentro de otro. No abuses de esto (dificulta la lectura).

tiene_cuenta = True
saldo = 500

if tiene_cuenta:
    if saldo >= 100:
        print("Puedes realizar la transacción")
    else:
        print("Saldo insuficiente")
else:
    print("No tienes cuenta registrada")


# --- OPERADOR TERNARIO (if en una línea) ---
# Para condiciones simples con un resultado u otro, puedes usar una sola línea.
# Formato: valor_si_true if condición else valor_si_false

edad = 17
estado = "mayor de edad" if edad >= 18 else "menor de edad"
print(f"El usuario es {estado}")


# --- EJEMPLO COMPLETO: calculadora de descuento ---

print("\n--- Calculadora de descuento ---")
precio = float(input("Ingresa el precio del producto: $"))
es_cliente_vip = input("¿Eres cliente VIP? (s/n): ").lower() == "s"

if es_cliente_vip and precio >= 100:
    descuento = 0.20    # 20% de descuento
    motivo = "VIP + compra mayor a $100"
elif es_cliente_vip:
    descuento = 0.10    # 10% de descuento
    motivo = "cliente VIP"
elif precio >= 100:
    descuento = 0.05    # 5% de descuento
    motivo = "compra mayor a $100"
else:
    descuento = 0       # sin descuento
    motivo = "ninguno"

precio_final = precio * (1 - descuento)
print(f"Descuento aplicado: {descuento*100:.0f}% ({motivo})")
print(f"Precio final: ${precio_final:.2f}")
