# =============================================================================
# ARCHIVO: 04_polimorfismo.py
# TEMA: Polimorfismo — mismo método, distinto comportamiento
# =============================================================================
#
# Polimorfismo = "muchas formas"
#
# Significa que objetos de distintas clases pueden responder al mismo
# mensaje (método) de forma diferente, cada uno según su propia naturaleza.
#
# Ya lo viste en herencia: rex.hacer_sonido() y michi.hacer_sonido()
# llaman al mismo método pero producen resultados distintos.
# Eso es polimorfismo.
# =============================================================================


# --- POLIMORFISMO A TRAVÉS DE HERENCIA ---

class Figura:
    """Clase base para figuras geométricas."""

    def __init__(self, color="negro"):
        self.color = color

    def area(self):
        """Devuelve el área de la figura. Las subclases deben sobreescribir esto."""
        raise NotImplementedError("Cada figura debe implementar area()")

    def perimetro(self):
        """Devuelve el perímetro de la figura."""
        raise NotImplementedError("Cada figura debe implementar perimetro()")

    def describir(self):
        """Descripción general, reutilizada por todas las figuras."""
        print(f"{type(self).__name__} de color {self.color}:")
        print(f"  Área:      {self.area():.2f}")
        print(f"  Perímetro: {self.perimetro():.2f}")


class Circulo(Figura):
    """Figura circular definida por su radio."""

    def __init__(self, radio, color="negro"):
        super().__init__(color)
        self.radio = radio

    def area(self):
        """Área = π * r²"""
        import math
        return math.pi * self.radio ** 2

    def perimetro(self):
        """Perímetro = 2 * π * r"""
        import math
        return 2 * math.pi * self.radio


class Rectangulo(Figura):
    """Figura rectangular definida por ancho y alto."""

    def __init__(self, ancho, alto, color="negro"):
        super().__init__(color)
        self.ancho = ancho
        self.alto = alto

    def area(self):
        """Área = ancho × alto"""
        return self.ancho * self.alto

    def perimetro(self):
        """Perímetro = 2 × (ancho + alto)"""
        return 2 * (self.ancho + self.alto)


class Triangulo(Figura):
    """Triángulo rectángulo definido por base y altura."""

    def __init__(self, base, altura, hipotenusa=None, color="negro"):
        super().__init__(color)
        self.base = base
        self.altura = altura
        # Si no se da la hipotenusa, la calcula con Pitágoras
        import math
        self.hipotenusa = hipotenusa or math.sqrt(base**2 + altura**2)

    def area(self):
        """Área = (base × altura) / 2"""
        return (self.base * self.altura) / 2

    def perimetro(self):
        """Perímetro = base + altura + hipotenusa"""
        return self.base + self.altura + self.hipotenusa


# --- POLIMORFISMO EN ACCIÓN ---
# La función recibe cualquier Figura — no le importa el tipo exacto.

def mostrar_info(figura):
    """Muestra la información de cualquier figura geométrica."""
    figura.describir()

figuras = [
    Circulo(5, "rojo"),
    Rectangulo(4, 6, "azul"),
    Triangulo(3, 4),
]

for figura in figuras:
    mostrar_info(figura)   # llama a area() y perimetro() polimórficamente
    print()


# --- POLIMORFISMO SIN HERENCIA (Duck Typing) ---
# En Python no necesitas heredar para el polimorfismo.
# Si un objeto tiene el método que se necesita, funciona.
# "Si camina como un pato y suena como un pato, es un pato."

class Impresora:
    """Representa una impresora física."""
    def imprimir(self, contenido):
        print(f"[IMPRESORA] Imprimiendo: {contenido}")

class PDF:
    """Representa un exportador de PDF."""
    def imprimir(self, contenido):
        print(f"[PDF] Guardando como PDF: {contenido}")

class CorreoElectronico:
    """Representa el envío por correo."""
    def imprimir(self, contenido):
        print(f"[EMAIL] Enviando por correo: {contenido}")

def procesar_documento(dispositivo, texto):
    """Procesa un documento usando cualquier 'dispositivo de salida'."""
    # No importa el tipo — solo necesita tener .imprimir()
    dispositivo.imprimir(texto)

procesar_documento(Impresora(), "Reporte mensual")
procesar_documento(PDF(), "Reporte mensual")
procesar_documento(CorreoElectronico(), "Reporte mensual")


# --- RESUMEN ---
# El polimorfismo hace tu código más flexible y extensible:
# - Puedes agregar nuevas figuras sin cambiar mostrar_info()
# - Puedes agregar nuevos dispositivos sin cambiar procesar_documento()
# - El código que "consume" objetos no necesita saber su tipo exacto
