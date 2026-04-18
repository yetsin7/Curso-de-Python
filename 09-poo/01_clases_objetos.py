# =============================================================================
# ARCHIVO: 01_clases_objetos.py
# TEMA: Clases y objetos — el fundamento de la POO
# =============================================================================
#
# Clase  → el molde (se define UNA VEZ)
# Objeto → una instancia del molde (se pueden crear MUCHOS)
#
# Por convención, los nombres de clases usan PascalCase: MiClase, AutoDeCarrera
# (a diferencia de las funciones que usan snake_case)
# =============================================================================


# --- DEFINIR UNA CLASE BÁSICA ---

class Persona:
    """Representa a una persona con nombre y edad."""

    # __init__ es el constructor — se ejecuta al crear un nuevo objeto
    # 'self' representa al objeto en sí (como "yo" en español)
    def __init__(self, nombre, edad):
        # Atributos de instancia — cada objeto tiene los suyos
        self.nombre = nombre
        self.edad = edad

    def saludar(self):
        """Imprime un saludo presentando a la persona."""
        print(f"Hola, me llamo {self.nombre} y tengo {self.edad} años.")

    def cumpleanos(self):
        """Incrementa la edad de la persona en 1 año."""
        self.edad += 1
        print(f"¡Feliz cumpleaños {self.nombre}! Ahora tienes {self.edad} años.")

    def __str__(self):
        """Representación en texto del objeto (para print())."""
        return f"Persona({self.nombre}, {self.edad} años)"


# --- CREAR OBJETOS (instanciar la clase) ---

persona1 = Persona("Ana", 28)
persona2 = Persona("Carlos", 35)

# Acceder a atributos
print(persona1.nombre)   # Ana
print(persona2.edad)     # 35

# Llamar métodos
persona1.saludar()
persona2.saludar()

persona1.cumpleanos()

# __str__ se llama automáticamente con print()
print(persona1)   # Persona(Ana, 29 años)


# --- ATRIBUTOS DE CLASE vs. ATRIBUTOS DE INSTANCIA ---

class Contador:
    """Cuenta cuántos objetos se han creado de esta clase."""

    # Atributo de CLASE — compartido por TODOS los objetos
    total_creados = 0

    def __init__(self, nombre):
        # Atributo de INSTANCIA — único para cada objeto
        self.nombre = nombre
        Contador.total_creados += 1    # incrementa el contador de la clase

    def mostrar(self):
        print(f"Soy {self.nombre}. Total de contadores: {Contador.total_creados}")


c1 = Contador("A")
c2 = Contador("B")
c3 = Contador("C")

c1.mostrar()    # Soy A. Total de contadores: 3
c2.mostrar()    # Soy B. Total de contadores: 3


# --- EJEMPLO COMPLETO: clase Cuenta Bancaria ---

class CuentaBancaria:
    """Representa una cuenta bancaria simple."""

    def __init__(self, titular, saldo_inicial=0):
        """
        titular:       nombre del dueño de la cuenta
        saldo_inicial: saldo de apertura (0 por defecto)
        """
        self.titular = titular
        self.saldo = saldo_inicial
        self.historial = []   # lista de transacciones

    def depositar(self, monto):
        """Agrega dinero a la cuenta."""
        if monto <= 0:
            print("El monto del depósito debe ser positivo")
            return
        self.saldo += monto
        self.historial.append(f"Depósito: +${monto:.2f}")
        print(f"Depósito de ${monto:.2f} realizado. Saldo: ${self.saldo:.2f}")

    def retirar(self, monto):
        """Retira dinero de la cuenta si hay saldo suficiente."""
        if monto <= 0:
            print("El monto del retiro debe ser positivo")
            return
        if monto > self.saldo:
            print(f"Saldo insuficiente. Saldo actual: ${self.saldo:.2f}")
            return
        self.saldo -= monto
        self.historial.append(f"Retiro:   -${monto:.2f}")
        print(f"Retiro de ${monto:.2f} realizado. Saldo: ${self.saldo:.2f}")

    def ver_saldo(self):
        """Muestra el saldo actual."""
        print(f"Saldo de {self.titular}: ${self.saldo:.2f}")

    def ver_historial(self):
        """Muestra el historial de transacciones."""
        print(f"\nHistorial de {self.titular}:")
        if not self.historial:
            print("  Sin transacciones")
        else:
            for transaccion in self.historial:
                print(f"  {transaccion}")

    def __str__(self):
        return f"Cuenta de {self.titular} (saldo: ${self.saldo:.2f})"


# Usar la clase
cuenta_ana = CuentaBancaria("Ana García", saldo_inicial=500)
cuenta_carlos = CuentaBancaria("Carlos López")

print(cuenta_ana)
print(cuenta_carlos)

cuenta_ana.depositar(200)
cuenta_ana.retirar(100)
cuenta_ana.retirar(700)   # saldo insuficiente
cuenta_ana.ver_historial()

cuenta_carlos.depositar(1000)
cuenta_carlos.ver_saldo()
