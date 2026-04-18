"""
Capítulo 15 — Testing
Archivo: 01_unittest_basico.py

Tests básicos con unittest — TestCase, assertions, setUp/tearDown.

unittest es el framework de testing incluido en la librería estándar
de Python. Está inspirado en JUnit (Java) y xUnit.

Estructura básica:
  - Crea una clase que hereda de unittest.TestCase
  - Cada método que empieza con 'test_' es un test
  - Usa self.assert*() para verificar el comportamiento esperado

Cómo ejecutar:
    python 01_unittest_basico.py
    python -m unittest 01_unittest_basico.py
    python -m unittest -v 01_unittest_basico.py   (verbose)
"""

import unittest     # Framework de testing de la librería estándar
import sys          # Para verificar la versión de Python en algunos tests
import os           # Para tests de sistema de archivos

# Importamos el módulo que vamos a probar
# Si calculadora.py está en el mismo directorio, este import funciona
# directamente al ejecutar: python 01_unittest_basico.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calculadora


# ==============================================================
# CLASE 1: Tests básicos de operaciones matemáticas
# ==============================================================

class TestOperacionesBasicas(unittest.TestCase):
    """
    Tests para las operaciones matemáticas fundamentales.
    Cada método test_* es un test independiente.

    Convención de nomenclatura:
        test_[función]_[escenario]
        test_sumar_numeros_positivos
        test_dividir_por_cero
    """

    # --- Tests de sumar ---

    def test_sumar_enteros_positivos(self):
        """Verifica la suma de dos enteros positivos."""
        # assertEqual(obtenido, esperado)
        # Es convenio poner el resultado obtenido primero
        self.assertEqual(calculadora.sumar(2, 3), 5)

    def test_sumar_con_cero(self):
        """La suma con cero debe devolver el mismo número."""
        self.assertEqual(calculadora.sumar(5, 0), 5)
        self.assertEqual(calculadora.sumar(0, 5), 5)

    def test_sumar_negativos(self):
        """Suma de números negativos."""
        self.assertEqual(calculadora.sumar(-3, -2), -5)

    def test_sumar_positivo_y_negativo(self):
        """Suma de un positivo y un negativo."""
        self.assertEqual(calculadora.sumar(10, -3), 7)

    def test_sumar_flotantes(self):
        """
        Los flotantes tienen problemas de precisión en binario.
        0.1 + 0.2 en Python NO es exactamente 0.3.
        assertAlmostEqual verifica con tolerancia (por defecto 7 decimales).
        """
        # Esto fallaría: self.assertEqual(0.1 + 0.2, 0.3)
        self.assertAlmostEqual(calculadora.sumar(0.1, 0.2), 0.3, places=7)

    # --- Tests de restar ---

    def test_restar_resultado_positivo(self):
        self.assertEqual(calculadora.restar(10, 4), 6)

    def test_restar_resultado_negativo(self):
        self.assertEqual(calculadora.restar(3, 10), -7)

    def test_restar_mismo_numero(self):
        """Restar un número de sí mismo siempre da cero."""
        self.assertEqual(calculadora.restar(5, 5), 0)

    # --- Tests de multiplicar ---

    def test_multiplicar_positivos(self):
        self.assertEqual(calculadora.multiplicar(3, 4), 12)

    def test_multiplicar_por_cero(self):
        """Cualquier número multiplicado por cero es cero."""
        self.assertEqual(calculadora.multiplicar(100, 0), 0)

    def test_multiplicar_negativos(self):
        """Negativo × negativo = positivo."""
        self.assertEqual(calculadora.multiplicar(-3, -4), 12)

    def test_multiplicar_positivo_negativo(self):
        """Positivo × negativo = negativo."""
        self.assertEqual(calculadora.multiplicar(3, -4), -12)

    # --- Tests de dividir ---

    def test_dividir_division_exacta(self):
        self.assertEqual(calculadora.dividir(10, 2), 5.0)

    def test_dividir_resultado_decimal(self):
        self.assertAlmostEqual(calculadora.dividir(7, 2), 3.5)

    def test_dividir_por_cero_lanza_excepcion(self):
        """
        assertRaises verifica que una función lanza la excepción esperada.
        Si la función NO lanza la excepción, el test FALLA.
        Esto es importante: debemos probar los casos de error también.
        """
        self.assertRaises(ValueError, calculadora.dividir, 10, 0)

    def test_dividir_por_cero_mensaje_de_error(self):
        """
        Usando assertRaises como context manager para verificar
        también el mensaje de la excepción.
        """
        with self.assertRaises(ValueError) as contexto:
            calculadora.dividir(5, 0)
        # Verificamos que el mensaje contiene texto relevante
        self.assertIn("cero", str(contexto.exception).lower())


# ==============================================================
# CLASE 2: setUp y tearDown — preparación y limpieza
# ==============================================================

class TestConSetup(unittest.TestCase):
    """
    setUp y tearDown son métodos especiales de TestCase:

    setUp():    se ejecuta ANTES de cada test individual.
                Prepara el estado necesario para el test.

    tearDown(): se ejecuta DESPUÉS de cada test, SIEMPRE,
                incluso si el test falló o lanzó una excepción.
                Limpia recursos (archivos, conexiones, etc.).

    setUpClass():    se ejecuta UNA VEZ antes de todos los tests de la clase.
    tearDownClass(): se ejecuta UNA VEZ después de todos los tests.
    """

    def setUp(self):
        """
        Preparación que se repite antes de CADA test.
        Aquí preparamos datos de prueba reutilizables.
        """
        # Datos comunes que usan múltiples tests
        self.numeros_positivos = [1, 2, 3, 4, 5]
        self.numeros_mixtos = [-2, -1, 0, 1, 2]
        self.numero_primo = 17
        self.numero_no_primo = 15

    def tearDown(self):
        """
        Limpieza después de CADA test.
        En este caso no hay recursos que limpiar,
        pero es importante saber cuándo usarlo.
        """
        # En tests reales: cerrar conexiones a BD, borrar archivos temporales, etc.
        pass

    @classmethod
    def setUpClass(cls):
        """
        Se ejecuta UNA VEZ antes de todos los tests de esta clase.
        Útil para preparar recursos costosos (conexiones, datos grandes).
        """
        cls.mensaje_inicio = "Iniciando tests de TestConSetup"
        print(f"\n  [setUpClass] {cls.mensaje_inicio}")

    @classmethod
    def tearDownClass(cls):
        """Se ejecuta UNA VEZ al terminar todos los tests de la clase."""
        print("\n  [tearDownClass] Tests de TestConSetup terminados")

    def test_maximo_con_datos_setup(self):
        """Usa los datos preparados en setUp."""
        self.assertEqual(calculadora.maximo(self.numeros_positivos), 5)

    def test_promedio_numeros_positivos(self):
        resultado = calculadora.promedio(self.numeros_positivos)
        self.assertEqual(resultado, 3.0)

    def test_promedio_numeros_mixtos(self):
        resultado = calculadora.promedio(self.numeros_mixtos)
        self.assertEqual(resultado, 0.0)

    def test_es_primo_con_primo(self):
        self.assertTrue(calculadora.es_primo(self.numero_primo))

    def test_es_primo_con_no_primo(self):
        self.assertFalse(calculadora.es_primo(self.numero_no_primo))


# ==============================================================
# CLASE 3: Assertions especiales de unittest
# ==============================================================

class TestAssertions(unittest.TestCase):
    """
    unittest.TestCase tiene muchos métodos assert* especializados.
    Usar el assert correcto da mejores mensajes de error cuando falla.
    """

    def test_assert_equal(self):
        """assertEqual: verifica igualdad de valor."""
        self.assertEqual(2 + 2, 4)

    def test_assert_not_equal(self):
        """assertNotEqual: verifica que los valores son distintos."""
        self.assertNotEqual(2 + 2, 5)

    def test_assert_true(self):
        """assertTrue: verifica que el valor es truthy."""
        self.assertTrue(calculadora.es_primo(7))
        self.assertTrue([1, 2, 3])  # Lista no vacía es truthy

    def test_assert_false(self):
        """assertFalse: verifica que el valor es falsy."""
        self.assertFalse(calculadora.es_primo(4))
        self.assertFalse([])  # Lista vacía es falsy

    def test_assert_is_none(self):
        """assertIsNone: verifica que el valor es exactamente None."""
        resultado = None
        self.assertIsNone(resultado)

    def test_assert_is_not_none(self):
        self.assertIsNotNone(calculadora.sumar(1, 1))

    def test_assert_in(self):
        """assertIn: verifica que un elemento está en una colección."""
        primos = [2, 3, 5, 7, 11, 13]
        self.assertIn(7, primos)
        self.assertIn("p", "python")

    def test_assert_not_in(self):
        self.assertNotIn(4, [2, 3, 5, 7])

    def test_assert_is_instance(self):
        """assertIsInstance: verifica el tipo del objeto."""
        self.assertIsInstance(calculadora.sumar(1, 2), (int, float))
        self.assertIsInstance(calculadora.factorial(5), int)

    def test_assert_almost_equal(self):
        """assertAlmostEqual: para flotantes con tolerancia."""
        self.assertAlmostEqual(3.14159, 3.14160, places=4)

    def test_assert_greater(self):
        """assertGreater, assertLess, assertGreaterEqual, assertLessEqual."""
        self.assertGreater(calculadora.factorial(5), calculadora.factorial(4))
        self.assertLess(calculadora.promedio([1, 2]), calculadora.promedio([3, 4]))

    def test_assert_raises_con_context_manager(self):
        """assertRaises como context manager permite verificar el mensaje."""
        with self.assertRaises(ValueError) as cm:
            calculadora.factorial(-1)
        self.assertIn("negativo", str(cm.exception).lower())

    def test_assert_raises_tipo_error(self):
        """Verificar que se lanza TypeError con tipo incorrecto."""
        with self.assertRaises(TypeError):
            calculadora.factorial(3.14)  # float no permitido


# ==============================================================
# CLASE 4: subTest — múltiples casos en un solo test
# ==============================================================

class TestSubTest(unittest.TestCase):
    """
    subTest permite ejecutar el mismo test con múltiples valores
    sin que un fallo en uno detenga los demás.

    Sin subTest: si el primer valor falla, los demás no se ejecutan.
    Con subTest: todos los valores se prueban, y el reporte muestra
                 cuáles fallaron.
    """

    def test_factorial_multiples_valores(self):
        """
        Prueba factorial con múltiples entradas usando subTest.
        Todos los casos se ejecutan aunque alguno falle.
        """
        # Tabla de casos: (entrada, resultado_esperado)
        casos = [
            (0, 1),       # 0! = 1 por definición
            (1, 1),       # 1! = 1
            (2, 2),       # 2! = 2
            (3, 6),       # 3! = 6
            (4, 24),      # 4! = 24
            (5, 120),     # 5! = 120
            (10, 3628800),
        ]

        for n, esperado in casos:
            # with self.subTest crea un sub-test con contexto descriptivo
            # Si falla, el mensaje mostrará: "FAIL: test ... (n=5)"
            with self.subTest(n=n):
                self.assertEqual(calculadora.factorial(n), esperado)

    def test_es_primo_multiples_valores(self):
        """Verifica es_primo con una tabla de verdad de números primos."""
        # (número, es_primo_esperado)
        casos_primos = [
            (0, False), (1, False), (2, True),  (3, True),
            (4, False), (5, True),  (6, False),  (7, True),
            (8, False), (9, False), (10, False), (11, True),
            (12, False),(13, True), (17, True),  (25, False),
            (29, True), (97, True), (100, False),
        ]

        for n, esperado in casos_primos:
            with self.subTest(n=n, esperado=esperado):
                self.assertEqual(calculadora.es_primo(n), esperado)

    def test_sumar_propiedad_conmutativa(self):
        """a + b == b + a para cualquier par de números."""
        pares = [(1, 2), (0, 5), (-3, 7), (100, -50), (0.5, 1.5)]

        for a, b in pares:
            with self.subTest(a=a, b=b):
                self.assertEqual(
                    calculadora.sumar(a, b),
                    calculadora.sumar(b, a),
                    msg=f"La suma no es conmutativa para ({a}, {b})"
                )


# ==============================================================
# PUNTO DE ENTRADA — ejecuta todos los tests
# ==============================================================

if __name__ == "__main__":
    # unittest.main() descubre y ejecuta todos los tests en este módulo
    # verbosity=2 muestra el nombre de cada test y si pasó o falló
    unittest.main(verbosity=2)
