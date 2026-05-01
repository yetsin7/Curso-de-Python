# =============================================================================
# ARCHIVO: mis_utilidades.py
# DESCRIPCIÓN: Módulo de utilidades creado por nosotros.
#              Este archivo es importado por 03_modulo_propio.py.
# =============================================================================
#
# Cualquier archivo .py puede ser importado como módulo.
# Simplemente guárdalo en la misma carpeta y usa: import mis_utilidades
# =============================================================================


def saludar(nombre):
    """Devuelve un saludo personalizado."""
    return f"¡Hola, {nombre}! Bienvenido."


def calcular_iva(precio, tasa=0.19):
    """
    Calcula el IVA de un precio.

    precio: precio base del producto (float)
    tasa:   tasa de IVA como decimal (por defecto 0.19 = 19%)
    Retorna: monto del IVA
    """
    return precio * tasa


def calcular_precio_final(precio, tasa_iva=0.19):
    """
    Calcula el precio total incluyendo el IVA.

    precio:   precio base
    tasa_iva: tasa como decimal (por defecto 19%)
    Retorna:  precio final con IVA incluido
    """
    return precio * (1 + tasa_iva)


def es_par(numero):
    """Retorna True si el número es par, False si es impar."""
    return numero % 2 == 0


def limitar(valor, minimo, maximo):
    """
    Limita un valor dentro de un rango [minimo, maximo].

    Si el valor es menor que mínimo, devuelve mínimo.
    Si el valor es mayor que máximo, devuelve máximo.
    En caso contrario, devuelve el valor tal como está.
    """
    return max(minimo, min(valor, maximo))


# Variable del módulo (accesible con mis_utilidades.AUTOR)
AUTOR = "Curso de Python"
VERSION = "1.0"
