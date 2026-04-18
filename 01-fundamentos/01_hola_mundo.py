# =============================================================================
# ARCHIVO: 01_hola_mundo.py
# TEMA: Tu primer programa en Python
# EJECUCION: python 01_hola_mundo.py
# =============================================================================
#
# Este archivo te presenta el primer contacto real con Python.
# Aqui no solo vas a ver un saludo en pantalla: tambien vas a empezar a entender
# como un programa recibe instrucciones, las ejecuta en orden y produce una
# salida visible en la consola.
#
# IDEA CLAVE:
# - Tu archivo .py es texto escrito por ti.
# - Python lee ese texto, lo interpreta y ejecuta las instrucciones.
# - La consola es la parte visible donde puedes observar el resultado.
# =============================================================================


# print() envia informacion a la salida estandar.
# En terminos simples: le pide a Python que muestre algo en la consola.
# La consola es una interfaz de texto que el sistema operativo pone a tu
# disposicion para comunicarte con los programas.
print("Hola, mundo!")

# Las comillas indican que esto es texto.
# En programacion, un texto se llama string o cadena de caracteres.
print("Bienvenido al Libro de Python")

# Python tambien puede mostrar numeros sin problema.
# Aqui no hay comillas porque queremos imprimir valores numericos reales,
# no texto que represente esos numeros.
print(42)
print(3.14)

# Cuando usas varias expresiones dentro de print(), Python las separa con
# espacios automaticamente para que la salida sea mas legible.
print("Mi numero favorito es", 7)

# Un print() vacio solo manda un salto de linea.
# Esto ayuda a separar visualmente bloques de informacion.
print()
print("Linea despues del espacio")

# Una variable es un nombre que apunta a un dato en memoria.
# No es una caja fisica, pero puedes imaginarla como una etiqueta que le pone
# nombre a un valor para poder reutilizarlo.
edad = 25

# Si quieres unir texto con numeros usando +, debes convertir el numero a texto.
# str() significa "string" y transforma el valor numerico en una cadena.
print("Tengo " + str(edad) + " anios")

# Las f-strings son una forma mas clara de insertar valores dentro de texto.
# Python reemplaza {nombre} por el valor real de la variable en el momento
# de ejecutar esta instruccion.
nombre = "Python"
print(f"Estoy aprendiendo {nombre}")

# Tambien puedes pedirle a Python que calcule algo antes de imprimirlo.
# Primero realiza la operacion y luego muestra el resultado.
print(f"En dos semanas hay {14} dias")


# =============================================================================
# QUE DEBERIAS ENTENDER AL TERMINAR
# - Un programa se ejecuta de arriba hacia abajo.
# - print() muestra resultados en la consola.
# - Las comillas representan texto.
# - Las variables guardan referencias a datos en memoria.
# - Python puede convertir datos para mostrarlos mejor.
#
# PRACTICA GUIADA
# 1. Cambia "Hola, mundo!" por un saludo con tu nombre.
# 2. Crea una variable llamada ciudad e imprimela.
# 3. Cambia edad por tu propia edad.
# 4. Intenta escribir: print("Tengo " + edad + " anios")
#    Lee el error con calma y explica por que ocurre.
# =============================================================================
