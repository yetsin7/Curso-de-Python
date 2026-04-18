# =============================================================================
# ARCHIVO: 03_modulo_propio.py
# TEMA: Crear y usar tus propios módulos
# =============================================================================
#
# El archivo mis_utilidades.py (en esta misma carpeta) es un módulo que
# creamos nosotros. Aquí aprendemos a importarlo y usarlo.
#
# Cuando ejecutes este archivo, Python buscará mis_utilidades.py en la
# misma carpeta. Si lo encuentra, puede importarlo.
# =============================================================================


# Importar el módulo completo
import mis_utilidades

# Usar las funciones del módulo con el prefijo
print(mis_utilidades.saludar("Carlos"))
print(mis_utilidades.calcular_iva(100))
print(mis_utilidades.calcular_precio_final(100))
print(mis_utilidades.AUTOR)
print(mis_utilidades.VERSION)


# Importar funciones específicas
from mis_utilidades import es_par, limitar, saludar

print(saludar("Ana"))         # ya no necesitas el prefijo mis_utilidades.
print(es_par(7))              # False
print(es_par(8))              # True
print(limitar(150, 0, 100))   # 100  (el valor excedía el máximo)
print(limitar(-5, 0, 100))    # 0    (el valor era menor al mínimo)
print(limitar(50, 0, 100))    # 50   (dentro del rango, no cambia)


# Importar con alias
import mis_utilidades as utils

print(utils.calcular_precio_final(200, tasa_iva=0.12))  # 224.0


# --- EL PATRÓN if __name__ == "__main__" ---
#
# Cuando Python importa un módulo, ejecuta TODO el código del archivo.
# Si mis_utilidades.py tuviera un print() al final, ese print se ejecutaría
# al importarlo, lo cual no queremos.
#
# La solución: envolver el código que "no debe ejecutarse al importar"
# dentro de:
#
#   if __name__ == "__main__":
#       código aquí
#
# __name__ es una variable especial:
#   - Es "__main__" cuando ejecutas el archivo directamente
#   - Es el nombre del módulo cuando lo importas desde otro archivo

print("\n--- Demostración de __name__ ---")
print(f"Este archivo se llama: {__name__}")   # __main__

# Si ejecutas mis_utilidades.py directamente:
#   __name__ == "__main__"   → True
# Si lo importas desde aquí:
#   __name__ == "mis_utilidades"   → True (no "__main__")

# Por eso en mis_utilidades.py no hay código fuera de las funciones.
# El patrón típico de un módulo bien hecho es:

# # --- en cualquier módulo bien escrito ---
# def mi_funcion():
#     pass
#
# if __name__ == "__main__":
#     # Este código solo corre al ejecutar el archivo directamente
#     # No se ejecuta al importar
#     print("Ejecutando pruebas del módulo...")
#     print(mi_funcion())
