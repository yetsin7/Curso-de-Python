# =============================================================================
# ARCHIVO: 02_herencia.py
# TEMA: Herencia — reutilizar y extender clases
# =============================================================================
#
# La herencia permite crear una clase nueva basada en una existente.
# La clase nueva (hija) hereda todos los atributos y métodos de la clase
# padre, y puede agregar o modificar lo que necesite.
#
# Ventaja: reutilizar código. Si cambias algo en la clase padre,
# automáticamente se aplica a todas las clases hijas.
# =============================================================================


# --- CLASE BASE (PADRE) ---

class Animal:
    """Clase base que representa cualquier animal."""

    def __init__(self, nombre, edad):
        """
        nombre: nombre del animal
        edad:   edad en años
        """
        self.nombre = nombre
        self.edad = edad
        self.energia = 100

    def comer(self, alimento):
        """Alimenta al animal y le da energía."""
        self.energia += 20
        print(f"{self.nombre} come {alimento}. Energía: {self.energia}")

    def dormir(self):
        """El animal descansa y recupera energía."""
        self.energia += 30
        print(f"{self.nombre} duerme. Energía: {self.energia}")

    def hacer_sonido(self):
        """El animal hace un sonido genérico."""
        print(f"{self.nombre} hace un sonido")

    def __str__(self):
        return f"{type(self).__name__}(nombre={self.nombre}, edad={self.edad})"


# --- CLASES HIJAS ---

class Perro(Animal):   # ← Perro hereda de Animal
    """Clase que representa un perro. Extiende Animal."""

    def __init__(self, nombre, edad, raza):
        # super() llama al __init__ del padre para no repetir código
        super().__init__(nombre, edad)
        self.raza = raza   # atributo propio de Perro

    def hacer_sonido(self):
        """Sobreescribe el método del padre — el perro ladra."""
        print(f"{self.nombre} dice: ¡Guau guau!")

    def buscar_pelota(self):
        """Método exclusivo de Perro — Animals no tienen esto."""
        self.energia -= 10
        print(f"{self.nombre} busca la pelota. Energía: {self.energia}")


class Gato(Animal):
    """Clase que representa un gato. Extiende Animal."""

    def __init__(self, nombre, edad, es_domestico=True):
        super().__init__(nombre, edad)
        self.es_domestico = es_domestico

    def hacer_sonido(self):
        """El gato maúlla."""
        print(f"{self.nombre} dice: ¡Miau!")

    def ronronear(self):
        """Método exclusivo de Gato."""
        print(f"{self.nombre} ronronea contentamente... 💤")


class Pajaro(Animal):
    """Clase que representa un pájaro. Extiende Animal."""

    def __init__(self, nombre, edad, puede_volar=True):
        super().__init__(nombre, edad)
        self.puede_volar = puede_volar

    def hacer_sonido(self):
        """El pájaro canta."""
        print(f"{self.nombre} canta: ¡Pío pío!")

    def volar(self):
        """El pájaro vuela si puede."""
        if self.puede_volar:
            print(f"{self.nombre} está volando 🕊️")
        else:
            print(f"{self.nombre} no puede volar")


# --- USAR LAS CLASES ---

rex = Perro("Rex", 3, "Labrador")
michi = Gato("Michi", 5)
tweety = Pajaro("Tweety", 2)

# Métodos heredados de Animal
rex.comer("croquetas")
michi.dormir()

# Métodos sobreescritos (polimorfismo básico)
rex.hacer_sonido()      # Guau guau
michi.hacer_sonido()    # Miau
tweety.hacer_sonido()   # Pío pío

# Métodos propios de cada clase
rex.buscar_pelota()
michi.ronronear()
tweety.volar()

print(rex)
print(michi)


# --- isinstance() — verificar si un objeto es de cierto tipo ---

print(isinstance(rex, Perro))     # True
print(isinstance(rex, Animal))    # True  ← también es Animal (por herencia)
print(isinstance(rex, Gato))      # False

# issubclass() — verificar si una clase hereda de otra
print(issubclass(Perro, Animal))  # True
print(issubclass(Gato, Perro))    # False


# --- HERENCIA MULTINIVEL ---

class AnimalDomestico(Animal):
    """Animal que vive con humanos."""

    def __init__(self, nombre, edad, dueño):
        super().__init__(nombre, edad)
        self.dueño = dueño

    def presentar_dueño(self):
        """Presenta al dueño del animal."""
        print(f"Mi dueño es {self.dueño}")


class PerroGuia(AnimalDomestico):
    """Perro guía entrenado para asistir a personas."""

    def __init__(self, nombre, edad, dueño, habilidad):
        super().__init__(nombre, edad, dueño)
        self.habilidad = habilidad

    def asistir(self):
        """El perro guía asiste a su dueño."""
        print(f"{self.nombre} asiste a {self.dueño}: {self.habilidad}")


guia = PerroGuia("Lassie", 4, "Don Roberto", "guiar al cruzar la calle")
guia.comer("pienso")          # heredado de Animal
guia.presentar_dueño()         # heredado de AnimalDomestico
guia.asistir()                 # propio de PerroGuia
