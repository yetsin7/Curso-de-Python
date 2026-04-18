# =============================================================================
# ARCHIVO: 03_encapsulamiento.py
# TEMA: Encapsulamiento — proteger los datos internos de una clase
# =============================================================================
#
# El encapsulamiento es el principio de proteger los datos internos de un
# objeto y controlar cómo se accede o modifica.
#
# Convenciones en Python:
#   nombre       → público: accesible desde cualquier lugar
#   _nombre      → "protegido": convención, no debería modificarse externamente
#   __nombre     → "privado": Python lo "oculta" para evitar acceso directo
# =============================================================================


# --- SIN ENCAPSULAMIENTO (problema) ---

class TemperaturaMala:
    """Sin encapsulamiento — cualquiera puede romper el estado."""

    def __init__(self):
        self.celsius = 20

# El problema:
temp = TemperaturaMala()
temp.celsius = -500   # nadie valida esto — es un valor imposible
print(temp.celsius)   # -500 → estado inválido


# --- CON ENCAPSULAMIENTO (solución) ---

class Temperatura:
    """Maneja una temperatura con validación de rango."""

    # Límites físicamente posibles (constantes de clase)
    MINIMO_CELSIUS = -273.15   # cero absoluto

    def __init__(self, celsius=20):
        self._celsius = None   # inicializar antes de usar el setter
        self.celsius = celsius  # usar el setter para validar

    @property
    def celsius(self):
        """Devuelve la temperatura en Celsius."""
        return self._celsius

    @celsius.setter
    def celsius(self, valor):
        """
        Establece la temperatura en Celsius.
        Lanza ValueError si el valor está por debajo del cero absoluto.
        """
        if valor < Temperatura.MINIMO_CELSIUS:
            raise ValueError(f"La temperatura no puede ser menor a {Temperatura.MINIMO_CELSIUS}°C")
        self._celsius = valor

    @property
    def fahrenheit(self):
        """Temperatura calculada en Fahrenheit (solo lectura)."""
        return self._celsius * 9/5 + 32

    @property
    def kelvin(self):
        """Temperatura calculada en Kelvin (solo lectura)."""
        return self._celsius + 273.15

    def __str__(self):
        return f"{self._celsius}°C / {self.fahrenheit:.1f}°F / {self.kelvin:.2f}K"


# Usar la clase
temp = Temperatura(25)
print(temp)           # 25°C / 77.0°F / 298.15K

temp.celsius = 100
print(temp.fahrenheit)  # 212.0  (agua hirviendo en °F)

# El setter valida automáticamente
try:
    temp.celsius = -300   # por debajo del cero absoluto
except ValueError as e:
    print(f"Error: {e}")

# Las propiedades de solo lectura no se pueden asignar
try:
    temp.fahrenheit = 100   # AttributeError
except AttributeError as e:
    print(f"Error: {e}")


# --- EJEMPLO PRÁCTICO: clase con atributos privados ---

class Usuario:
    """Representa un usuario del sistema con contraseña protegida."""

    def __init__(self, nombre, contrasena):
        self.nombre = nombre              # público
        self.__contrasena = contrasena    # "privado" — con doble guión bajo

    def verificar_contrasena(self, intento):
        """Verifica si la contraseña ingresada es correcta."""
        return intento == self.__contrasena

    def cambiar_contrasena(self, actual, nueva):
        """Cambia la contraseña si la actual es correcta."""
        if not self.verificar_contrasena(actual):
            print("Contraseña actual incorrecta")
            return False
        if len(nueva) < 8:
            print("La nueva contraseña debe tener al menos 8 caracteres")
            return False
        self.__contrasena = nueva
        print("Contraseña cambiada exitosamente")
        return True

    def __str__(self):
        return f"Usuario({self.nombre})"


user = Usuario("ana123", "mipass2024")
print(user)

# Verificar contraseña
print(user.verificar_contrasena("wrongpass"))   # False
print(user.verificar_contrasena("mipass2024"))  # True

# Cambiar contraseña
user.cambiar_contrasena("mipass2024", "nuevapass123")

# No se puede acceder directamente a __contrasena
# print(user.__contrasena)   # ❌ AttributeError

# Python la "renombra" internamente pero aun así no deberías accederla así:
# print(user._Usuario__contrasena)   # funciona pero es una mala práctica
