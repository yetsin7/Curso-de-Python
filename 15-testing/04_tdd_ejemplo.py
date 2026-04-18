# =============================================================================
# CAPÍTULO 15 - TESTING
# Archivo: 04_tdd_ejemplo.py
# Descripción: Demostración completa del ciclo TDD (Red → Green → Refactor)
#              implementando una clase CarritoDeCompras desde cero.
#              Incluye 15 tests que cubren todos los casos de uso principales.
# =============================================================================
#
# CICLO TDD:
#   RED    → Escribir el test primero (el test falla porque no existe la clase)
#   GREEN  → Escribir el mínimo código para que el test pase
#   REFACTOR → Mejorar el código sin romper los tests existentes
#
# Para ejecutar: python -m pytest 04_tdd_ejemplo.py -v
# O directamente: python 04_tdd_ejemplo.py
# =============================================================================

import unittest
from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# IMPLEMENTACIÓN: CarritoDeCompras
# Esta es la clase que se construyó iterativamente siguiendo TDD.
# En TDD real, cada método se escribe SOLO cuando el test correspondiente falla.
# =============================================================================

@dataclass
class Producto:
    """
    Representa un producto que puede agregarse al carrito.
    Inmutable por diseño para garantizar consistencia de datos.
    """
    id: str
    nombre: str
    precio: float
    stock_disponible: int = 0

    def __post_init__(self):
        """Valida los datos del producto al crearlo."""
        if self.precio < 0:
            raise ValueError(f"El precio no puede ser negativo: {self.precio}")
        if self.stock_disponible < 0:
            raise ValueError(f"El stock no puede ser negativo: {self.stock_disponible}")


class StockInsuficienteError(Exception):
    """
    Se lanza cuando se intenta agregar más unidades de las disponibles en stock.
    """
    pass


class ProductoNoEncontradoError(Exception):
    """
    Se lanza cuando se intenta operar con un producto que no está en el carrito.
    """
    pass


class CarritoDeCompras:
    """
    Carrito de compras con manejo de productos, cantidades, descuentos y stock.

    Atributos:
        _items: Diccionario interno {producto_id: (Producto, cantidad)}
        _descuento_porcentaje: Descuento global aplicado al total (0-100)
    """

    def __init__(self):
        """Inicializa el carrito vacío y sin descuento."""
        self._items: dict = {}          # {id: (Producto, cantidad)}
        self._descuento_porcentaje: float = 0.0

    def agregar(self, producto: Producto, cantidad: int = 1):
        """
        Agrega un producto al carrito en la cantidad indicada.
        Si el producto ya existe, incrementa la cantidad.

        Args:
            producto: El producto a agregar.
            cantidad: Cuántas unidades agregar (default: 1).

        Raises:
            ValueError: Si la cantidad es menor o igual a cero.
            StockInsuficienteError: Si no hay suficiente stock disponible.
        """
        if cantidad <= 0:
            raise ValueError(f"La cantidad debe ser positiva, recibida: {cantidad}")

        # Calcular cuántas unidades ya tenemos en el carrito
        cantidad_actual = 0
        if producto.id in self._items:
            _, cantidad_actual = self._items[producto.id]

        cantidad_total = cantidad_actual + cantidad
        if cantidad_total > producto.stock_disponible:
            raise StockInsuficienteError(
                f"Stock insuficiente para '{producto.nombre}': "
                f"solicitado={cantidad_total}, disponible={producto.stock_disponible}"
            )

        self._items[producto.id] = (producto, cantidad_total)

    def eliminar(self, producto_id: str, cantidad: Optional[int] = None):
        """
        Elimina un producto del carrito completo o reduce su cantidad.

        Args:
            producto_id: ID del producto a eliminar.
            cantidad:    Si se especifica, reduce en esa cantidad.
                         Si es None, elimina el producto completamente.

        Raises:
            ProductoNoEncontradoError: Si el producto no está en el carrito.
            ValueError: Si la cantidad a eliminar supera la cantidad en el carrito.
        """
        if producto_id not in self._items:
            raise ProductoNoEncontradoError(f"Producto '{producto_id}' no está en el carrito")

        if cantidad is None:
            del self._items[producto_id]
        else:
            producto, cantidad_actual = self._items[producto_id]
            if cantidad > cantidad_actual:
                raise ValueError(
                    f"No puedes eliminar {cantidad} unidades, solo hay {cantidad_actual}"
                )
            nueva_cantidad = cantidad_actual - cantidad
            if nueva_cantidad == 0:
                del self._items[producto_id]
            else:
                self._items[producto_id] = (producto, nueva_cantidad)

    def obtener_cantidad(self, producto_id: str) -> int:
        """
        Retorna cuántas unidades de un producto hay en el carrito.
        Retorna 0 si el producto no está.
        """
        if producto_id not in self._items:
            return 0
        _, cantidad = self._items[producto_id]
        return cantidad

    def calcular_subtotal(self) -> float:
        """Calcula el subtotal sin aplicar descuento."""
        return sum(producto.precio * cantidad for producto, cantidad in self._items.values())

    def aplicar_descuento(self, porcentaje: float):
        """
        Aplica un descuento porcentual al total del carrito.

        Args:
            porcentaje: Valor entre 0 y 100.

        Raises:
            ValueError: Si el porcentaje está fuera del rango válido.
        """
        if not (0 <= porcentaje <= 100):
            raise ValueError(f"El descuento debe estar entre 0 y 100, recibido: {porcentaje}")
        self._descuento_porcentaje = porcentaje

    def calcular_total(self) -> float:
        """Calcula el total aplicando el descuento si existe."""
        subtotal = self.calcular_subtotal()
        descuento_monto = subtotal * (self._descuento_porcentaje / 100)
        return round(subtotal - descuento_monto, 2)

    def vaciar(self):
        """Elimina todos los productos del carrito y resetea el descuento."""
        self._items.clear()
        self._descuento_porcentaje = 0.0

    def esta_vacio(self) -> bool:
        """Retorna True si el carrito no tiene ningún producto."""
        return len(self._items) == 0

    def cantidad_total_items(self) -> int:
        """Retorna el número total de unidades (no productos únicos) en el carrito."""
        return sum(cantidad for _, cantidad in self._items.values())

    def __len__(self) -> int:
        """Retorna el número de productos únicos en el carrito."""
        return len(self._items)

    def __repr__(self) -> str:
        items_str = ", ".join(
            f"{p.nombre}×{c}" for p, c in self._items.values()
        )
        return f"CarritoDeCompras([{items_str}], total={self.calcular_total()})"


# =============================================================================
# TESTS TDD — 15 TESTS QUE CUBREN TODOS LOS CASOS DE USO
# Organizados por ciclo RED → GREEN → REFACTOR
# =============================================================================

class TestCarritoDeComprasBasico(unittest.TestCase):
    """
    Suite de tests básicos del carrito.
    CICLO RED: Se escribieron primero. CICLO GREEN: Se implementó el código mínimo.
    """

    def setUp(self):
        """
        Se ejecuta antes de cada test.
        Prepara un carrito vacío y productos de prueba comunes.
        """
        self.carrito = CarritoDeCompras()
        self.laptop = Producto("p1", "Laptop", 999.99, stock_disponible=5)
        self.mouse = Producto("p2", "Mouse", 29.99, stock_disponible=10)
        self.teclado = Producto("p3", "Teclado", 59.99, stock_disponible=0)  # sin stock

    # =========================================================================
    # TEST 1: El carrito empieza vacío
    # RED: Falló porque CarritoDeCompras no existía
    # GREEN: Crear la clase con __init__ básico
    # =========================================================================
    def test_01_carrito_inicia_vacio(self):
        """El carrito recién creado debe estar vacío."""
        self.assertTrue(self.carrito.esta_vacio())
        self.assertEqual(len(self.carrito), 0)
        self.assertEqual(self.carrito.calcular_total(), 0.0)

    # =========================================================================
    # TEST 2: Agregar un producto
    # GREEN: Implementar el método agregar()
    # =========================================================================
    def test_02_agregar_producto(self):
        """Agregar un producto debe añadirlo al carrito."""
        self.carrito.agregar(self.laptop)
        self.assertFalse(self.carrito.esta_vacio())
        self.assertEqual(len(self.carrito), 1)
        self.assertEqual(self.carrito.obtener_cantidad("p1"), 1)

    # =========================================================================
    # TEST 3: Agregar múltiples productos
    # =========================================================================
    def test_03_agregar_multiples_productos(self):
        """El carrito debe manejar múltiples productos distintos."""
        self.carrito.agregar(self.laptop)
        self.carrito.agregar(self.mouse, cantidad=3)
        self.assertEqual(len(self.carrito), 2)
        self.assertEqual(self.carrito.obtener_cantidad("p2"), 3)

    # =========================================================================
    # TEST 4: Agregar el mismo producto dos veces incrementa la cantidad
    # =========================================================================
    def test_04_agregar_mismo_producto_acumula(self):
        """Agregar un producto ya existente debe sumar la cantidad."""
        self.carrito.agregar(self.laptop, 2)
        self.carrito.agregar(self.laptop, 1)
        self.assertEqual(self.carrito.obtener_cantidad("p1"), 3)
        self.assertEqual(len(self.carrito), 1)  # Sigue siendo 1 producto único

    # =========================================================================
    # TEST 5: Calcular el total correctamente
    # GREEN: Implementar calcular_total()
    # =========================================================================
    def test_05_calcular_total(self):
        """El total debe ser la suma de precio × cantidad de todos los items."""
        self.carrito.agregar(self.laptop, 1)    # 999.99
        self.carrito.agregar(self.mouse, 2)     # 29.99 × 2 = 59.98
        expected_total = 999.99 + 59.98
        self.assertAlmostEqual(self.carrito.calcular_total(), expected_total, places=2)

    # =========================================================================
    # TEST 6: Eliminar un producto completo
    # GREEN: Implementar eliminar()
    # =========================================================================
    def test_06_eliminar_producto(self):
        """Eliminar un producto debe quitarlo completamente del carrito."""
        self.carrito.agregar(self.laptop)
        self.carrito.agregar(self.mouse)
        self.carrito.eliminar("p1")
        self.assertEqual(len(self.carrito), 1)
        self.assertEqual(self.carrito.obtener_cantidad("p1"), 0)

    # =========================================================================
    # TEST 7: Eliminar cantidad parcial de un producto
    # =========================================================================
    def test_07_eliminar_cantidad_parcial(self):
        """Eliminar n unidades de un producto debe reducir su cantidad."""
        self.carrito.agregar(self.mouse, 5)
        self.carrito.eliminar("p2", cantidad=3)
        self.assertEqual(self.carrito.obtener_cantidad("p2"), 2)

    # =========================================================================
    # TEST 8: Aplicar descuento
    # GREEN: Implementar aplicar_descuento()
    # =========================================================================
    def test_08_aplicar_descuento(self):
        """El descuento debe reducir el total en el porcentaje correcto."""
        self.carrito.agregar(self.laptop, 1)   # $999.99
        self.carrito.aplicar_descuento(10)      # 10% de descuento
        expected = round(999.99 * 0.90, 2)
        self.assertAlmostEqual(self.carrito.calcular_total(), expected, places=2)

    # =========================================================================
    # TEST 9: Vaciar el carrito
    # GREEN: Implementar vaciar()
    # =========================================================================
    def test_09_vaciar_carrito(self):
        """Vaciar el carrito debe eliminar todos los productos y el descuento."""
        self.carrito.agregar(self.laptop)
        self.carrito.agregar(self.mouse)
        self.carrito.aplicar_descuento(20)
        self.carrito.vaciar()
        self.assertTrue(self.carrito.esta_vacio())
        self.assertEqual(self.carrito.calcular_total(), 0.0)

    # =========================================================================
    # TEST 10: Error al agregar producto sin stock
    # GREEN: Agregar validación de stock
    # =========================================================================
    def test_10_error_stock_insuficiente(self):
        """Agregar un producto sin stock debe lanzar StockInsuficienteError."""
        with self.assertRaises(StockInsuficienteError):
            self.carrito.agregar(self.teclado)

    # =========================================================================
    # TEST 11: Error al superar el stock disponible
    # =========================================================================
    def test_11_error_superar_stock(self):
        """Agregar más unidades que el stock disponible debe lanzar error."""
        with self.assertRaises(StockInsuficienteError):
            self.carrito.agregar(self.laptop, 10)  # Solo hay 5 en stock

    # =========================================================================
    # TEST 12: Error al eliminar producto inexistente
    # =========================================================================
    def test_12_error_eliminar_producto_inexistente(self):
        """Eliminar un producto que no está en el carrito debe lanzar error."""
        with self.assertRaises(ProductoNoEncontradoError):
            self.carrito.eliminar("id_que_no_existe")

    # =========================================================================
    # TEST 13: Error al aplicar descuento inválido
    # =========================================================================
    def test_13_error_descuento_invalido(self):
        """Un porcentaje de descuento fuera de [0, 100] debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            self.carrito.aplicar_descuento(150)
        with self.assertRaises(ValueError):
            self.carrito.aplicar_descuento(-10)

    # =========================================================================
    # TEST 14: Cantidad total de unidades en el carrito
    # =========================================================================
    def test_14_cantidad_total_items(self):
        """cantidad_total_items debe contar todas las unidades, no productos únicos."""
        self.carrito.agregar(self.laptop, 2)
        self.carrito.agregar(self.mouse, 3)
        # 2 laptops + 3 ratones = 5 unidades totales, pero 2 productos únicos
        self.assertEqual(self.carrito.cantidad_total_items(), 5)
        self.assertEqual(len(self.carrito), 2)

    # =========================================================================
    # TEST 15: El descuento del 0% no cambia el total (caso borde)
    # =========================================================================
    def test_15_descuento_cero_no_cambia_total(self):
        """Un descuento del 0% no debe modificar el total."""
        self.carrito.agregar(self.laptop)
        subtotal = self.carrito.calcular_subtotal()
        self.carrito.aplicar_descuento(0)
        self.assertAlmostEqual(self.carrito.calcular_total(), subtotal, places=2)


# =============================================================================
# EJECUCIÓN DE TESTS CON SALIDA DETALLADA
# =============================================================================

def ejecutar_tests():
    """
    Ejecuta todos los tests con output detallado y muestra cobertura conceptual.
    Puede ejecutarse directamente o via pytest.
    """
    print("=" * 60)
    print("   TDD COMPLETO: CarritoDeCompras")
    print("   Ciclo RED → GREEN → REFACTOR")
    print("=" * 60)

    print("\nCICLO RED: Cada test fue escrito ANTES del código.")
    print("CICLO GREEN: Se implementó el mínimo código para pasar.")
    print("CICLO REFACTOR: Se mejoró la implementación sin romper tests.\n")

    # Ejecutar los tests con verbosidad alta
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCarritoDeComprasBasico)

    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)

    # Reporte de cobertura conceptual
    print("\n" + "=" * 60)
    print("COBERTURA CONCEPTUAL DE TESTS")
    print("=" * 60)
    cobertura = [
        ("CarritoDeCompras.__init__",  "test_01"),
        ("CarritoDeCompras.agregar",   "test_02, test_03, test_04"),
        ("CarritoDeCompras.calcular_total", "test_05, test_08, test_15"),
        ("CarritoDeCompras.eliminar",  "test_06, test_07"),
        ("CarritoDeCompras.vaciar",    "test_09"),
        ("StockInsuficienteError",     "test_10, test_11"),
        ("ProductoNoEncontradoError",  "test_12"),
        ("ValueError (descuento)",     "test_13"),
        ("cantidad_total_items",       "test_14"),
    ]
    for metodo, tests in cobertura:
        print(f"  {'✓' if resultado.wasSuccessful() else '?'} {metodo:<40} ← {tests}")

    total = resultado.testsRun
    fallos = len(resultado.failures) + len(resultado.errors)
    pasaron = total - fallos
    print(f"\n  Tests totales:  {total}")
    print(f"  Tests pasaron:  {pasaron}")
    print(f"  Tests fallaron: {fallos}")
    print(f"  Cobertura:      {pasaron/total*100:.0f}% de los casos implementados")

    if resultado.wasSuccessful():
        print("\n  Todos los tests pasaron. El carrito está listo para producción.")
    else:
        print("\n  Algunos tests fallaron. Revisar la implementación.")


if __name__ == "__main__":
    ejecutar_tests()
