# =============================================================================
# ARCHIVO: 03_decoradores.py
# TEMA: Decoradores — agregar comportamiento a funciones
# =============================================================================
#
# Un decorador es una función que toma otra función como argumento,
# le "agrega" algo, y devuelve la función modificada.
#
# Son posibles porque en Python las funciones son objetos que pueden
# pasarse como argumentos, guardarse en variables y devolverse.
#
# Se usan mucho en frameworks: @app.route en Flask, @login_required en Django.
# =============================================================================


# --- FUNCIONES COMO OBJETOS (base para entender decoradores) ---

def saludar():
    """Función simple que saluda."""
    print("¡Hola!")

# Las funciones se pueden asignar a variables
mi_funcion = saludar
mi_funcion()    # ¡Hola!

# Las funciones se pueden pasar como argumentos
def ejecutar(funcion):
    """Recibe una función y la ejecuta."""
    print("Antes de ejecutar")
    funcion()
    print("Después de ejecutar")

ejecutar(saludar)


# --- CREAR UN DECORADOR BÁSICO ---

def cronometrar(funcion):
    """
    Decorador que mide cuánto tarda en ejecutarse una función.
    Recibe la función original, devuelve una función mejorada.
    """
    import time

    def wrapper(*args, **kwargs):
        """Envuelve la función original con medición de tiempo."""
        inicio = time.time()
        resultado = funcion(*args, **kwargs)   # llama a la función original
        fin = time.time()
        print(f"  ⏱ {funcion.__name__}() tardó {fin - inicio:.4f} segundos")
        return resultado

    return wrapper


# FORMA LARGA de aplicar un decorador:
def calcular_suma(n):
    """Suma los números del 0 al n."""
    return sum(range(n + 1))

calcular_suma = cronometrar(calcular_suma)   # aplicar decorador manualmente


# FORMA CORTA con @ (syntactic sugar — hace lo mismo que arriba):
@cronometrar
def calcular_producto(numeros):
    """Multiplica todos los números de una lista."""
    resultado = 1
    for n in numeros:
        resultado *= n
    return resultado

print(calcular_suma(1000000))
print(calcular_producto([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))


# --- DECORADOR DE LOGGING ---

def registrar(funcion):
    """Decorador que registra cada llamada a la función."""
    def wrapper(*args, **kwargs):
        print(f"[LOG] Llamando a {funcion.__name__}(args={args}, kwargs={kwargs})")
        resultado = funcion(*args, **kwargs)
        print(f"[LOG] {funcion.__name__} devolvió: {resultado}")
        return resultado
    return wrapper

@registrar
def sumar(a, b):
    """Suma dos números."""
    return a + b

@registrar
def multiplicar(a, b):
    """Multiplica dos números."""
    return a * b

sumar(3, 4)
multiplicar(5, 6)


# --- DECORADOR CON PARÁMETROS ---

def repetir(veces):
    """
    Decorador que ejecuta la función 'veces' veces.
    Los decoradores con parámetros requieren una capa extra.
    """
    def decorador(funcion):
        def wrapper(*args, **kwargs):
            for _ in range(veces):
                funcion(*args, **kwargs)
        return wrapper
    return decorador

@repetir(3)
def decir_hola():
    """Saluda."""
    print("¡Hola!")

decir_hola()   # imprime ¡Hola! tres veces


# --- FUNCTOOLS.WRAPS — buena práctica ---
# Sin wraps, el nombre y docstring de la función original se pierden.

from functools import wraps

def mi_decorador(funcion):
    """Decorador correctamente implementado con @wraps."""
    @wraps(funcion)   # preserva el nombre y docstring de la función original
    def wrapper(*args, **kwargs):
        return funcion(*args, **kwargs)
    return wrapper

@mi_decorador
def funcion_importante():
    """Esta es la docstring de la función importante."""
    pass

print(funcion_importante.__name__)   # funcion_importante (correcto)
print(funcion_importante.__doc__)    # Esta es la docstring...


# --- DECORADORES PREDEFINIDOS DE PYTHON ---

class MiClase:
    """Ejemplo de decoradores estándar de Python."""

    clase_variable = "compartida"

    def __init__(self, valor):
        self.valor = valor

    @property
    def valor_doble(self):
        """Propiedad: accede como atributo pero ejecuta una función."""
        return self.valor * 2

    @staticmethod
    def metodo_estatico():
        """No recibe self — no necesita una instancia para llamarse."""
        print("Soy un método estático")

    @classmethod
    def metodo_de_clase(cls):
        """Recibe la clase, no la instancia. Accede a clase_variable."""
        print(f"Variable de clase: {cls.clase_variable}")

obj = MiClase(5)
print(obj.valor_doble)         # 10 (sin paréntesis, gracias a @property)
MiClase.metodo_estatico()      # sin crear instancia
MiClase.metodo_de_clase()
