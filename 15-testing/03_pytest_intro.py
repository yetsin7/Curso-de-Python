"""
Capítulo 15 — Testing
Archivo: 03_pytest_intro.py

Introducción a pytest — el framework de testing estándar de la industria.

Este archivo detecta automáticamente si pytest está instalado:
  - Si pytest está instalado: los tests se ejecutan con pytest
  - Si pytest NO está instalado: se muestran instrucciones y los tests
    se ejecutan con unittest como fallback

Cómo instalar pytest:
    pip install pytest pytest-cov

Cómo ejecutar este archivo:
    python 03_pytest_intro.py    ← detecta automáticamente
    pytest 03_pytest_intro.py    ← si pytest está instalado
    pytest 03_pytest_intro.py -v ← verbose
"""

import sys
import os
import unittest

# Importamos el módulo de calculadora desde el mismo directorio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calculadora

# ==============================================================
# DETECCIÓN DE PYTEST
# ==============================================================

# Intentamos importar pytest de forma silenciosa
# Si no está instalado, usamos unittest como fallback
try:
    import pytest
    PYTEST_DISPONIBLE = True
except ImportError:
    PYTEST_DISPONIBLE = False

# Indicamos en la documentación del módulo si pytest está disponible
if PYTEST_DISPONIBLE:
    print("pytest detectado. Ejecuta: pytest 03_pytest_intro.py -v")
else:
    print("pytest no está instalado.")
    print("Para instalarlo: pip install pytest")
    print("Ejecutando con unittest como fallback...\n")


# ==============================================================
# SECCIÓN 1: Funciones de test básicas (estilo pytest)
# ==============================================================

def test_sumar_basico():
    """
    En pytest, las funciones que empiezan con test_ son tests.
    No necesitas heredar de ninguna clase.
    Usa assert directamente — pytest lo intercepta y da mensajes claros.
    """
    assert calculadora.sumar(2, 3) == 5


def test_sumar_con_negativos():
    """pytest da un mensaje de error muy descriptivo cuando assert falla."""
    assert calculadora.sumar(-5, 3) == -2


def test_restar():
    assert calculadora.restar(10, 4) == 6


def test_multiplicar_por_cero():
    assert calculadora.multiplicar(100, 0) == 0


def test_dividir_exacta():
    assert calculadora.dividir(10, 2) == 5.0


def test_dividir_por_cero_lanza_excepcion():
    """
    pytest.raises() verifica que se lanza una excepción.
    Requiere pytest instalado.
    """
    if PYTEST_DISPONIBLE:
        with pytest.raises(ValueError):
            calculadora.dividir(5, 0)
    else:
        # Fallback: verificamos con try/except
        try:
            calculadora.dividir(5, 0)
            assert False, "Debería haber lanzado ValueError"
        except ValueError:
            pass  # Correcto


def test_dividir_por_cero_mensaje():
    """Verifica el mensaje de la excepción."""
    if PYTEST_DISPONIBLE:
        with pytest.raises(ValueError, match="cero"):
            calculadora.dividir(1, 0)
    else:
        try:
            calculadora.dividir(1, 0)
        except ValueError as e:
            assert "cero" in str(e).lower()


def test_factorial_casos_base():
    assert calculadora.factorial(0) == 1
    assert calculadora.factorial(1) == 1


def test_factorial_valores_grandes():
    assert calculadora.factorial(10) == 3628800


def test_es_primo_numeros_primos():
    primos_conocidos = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    for n in primos_conocidos:
        assert calculadora.es_primo(n), f"{n} debería ser primo"


def test_es_primo_numeros_no_primos():
    no_primos = [0, 1, 4, 6, 8, 9, 10, 15, 25]
    for n in no_primos:
        assert not calculadora.es_primo(n), f"{n} no debería ser primo"


# ==============================================================
# SECCIÓN 2: Fixtures — estado compartido entre tests
# ==============================================================

if PYTEST_DISPONIBLE:

    @pytest.fixture
    def lista_numeros():
        """
        Un fixture es una función que prepara datos para los tests.
        Se declara con @pytest.fixture y se usa como parámetro del test.

        pytest inyecta el fixture automáticamente cuando el test
        declara un parámetro con el mismo nombre que el fixture.
        """
        return [1, 2, 3, 4, 5, 10, 15, 20]

    @pytest.fixture
    def numeros_negativos():
        """Fixture con números negativos para tests específicos."""
        return [-5, -3, -1, 0, 1, 3, 5]

    def test_maximo_con_fixture(lista_numeros):
        """
        pytest inyecta 'lista_numeros' automáticamente.
        El nombre del parámetro debe coincidir con el nombre del fixture.
        """
        assert calculadora.maximo(lista_numeros) == 20

    def test_promedio_con_fixture(lista_numeros):
        """Usa el mismo fixture que el test anterior."""
        resultado = calculadora.promedio(lista_numeros)
        assert resultado == sum(lista_numeros) / len(lista_numeros)

    def test_promedio_lista_vacia():
        """Test de error para lista vacía — no necesita fixture."""
        with pytest.raises(ValueError):
            calculadora.promedio([])

    @pytest.fixture
    def datos_calculadora():
        """
        Fixture que devuelve múltiples valores como diccionario.
        Útil cuando varios tests necesitan el mismo conjunto de datos.
        """
        return {
            "a": 10,
            "b": 3,
            "suma_esperada": 13,
            "resta_esperada": 7,
            "mult_esperada": 30,
            "div_esperada": 10 / 3,
        }

    def test_operaciones_con_fixture_dict(datos_calculadora):
        """Usa el fixture de diccionario."""
        d = datos_calculadora
        assert calculadora.sumar(d["a"], d["b"]) == d["suma_esperada"]
        assert calculadora.restar(d["a"], d["b"]) == d["resta_esperada"]
        assert calculadora.multiplicar(d["a"], d["b"]) == d["mult_esperada"]


# ==============================================================
# SECCIÓN 3: parametrize — múltiples casos de prueba
# ==============================================================

if PYTEST_DISPONIBLE:

    @pytest.mark.parametrize("a, b, esperado", [
        (2, 3, 5),        # Enteros positivos
        (0, 5, 5),        # Con cero
        (-3, -2, -5),     # Negativos
        (10, -3, 7),      # Positivo + negativo
        (0.5, 0.5, 1.0),  # Flotantes
    ])
    def test_sumar_parametrizado(a, b, esperado):
        """
        @pytest.mark.parametrize ejecuta el test una vez por cada
        tupla de parámetros. Si alguno falla, muestra exactamente cuál.

        Esto reemplaza el patrón de loop con subTest de unittest,
        pero con sintaxis más limpia y mejor output.
        """
        assert calculadora.sumar(a, b) == esperado

    @pytest.mark.parametrize("n, esperado", [
        (0, 1),
        (1, 1),
        (2, 2),
        (3, 6),
        (4, 24),
        (5, 120),
        (10, 3628800),
    ])
    def test_factorial_parametrizado(n, esperado):
        """Factorial con tabla de valores esperados."""
        assert calculadora.factorial(n) == esperado

    @pytest.mark.parametrize("n, es_primo_esperado", [
        (0, False),
        (1, False),
        (2, True),
        (3, True),
        (7, True),
        (9, False),
        (97, True),
        (100, False),
    ])
    def test_es_primo_parametrizado(n, es_primo_esperado):
        assert calculadora.es_primo(n) == es_primo_esperado

    @pytest.mark.parametrize("a, b", [
        (10, 0),
        (0, 0),
        (-5, 0),
        (1000000, 0),
    ])
    def test_dividir_por_cero_parametrizado(a, b):
        """Todos estos casos deben lanzar ValueError."""
        with pytest.raises(ValueError):
            calculadora.dividir(a, b)


# ==============================================================
# SECCIÓN 4: Markers — categorizar tests
# ==============================================================

if PYTEST_DISPONIBLE:

    @pytest.mark.slow
    def test_primos_grandes():
        """
        Marker 'slow': marca el test como lento.
        Se puede excluir con: pytest -m "not slow"
        Se puede correr solo con: pytest -m slow

        Para que los markers personalizados no generen warnings,
        deben registrarse en pytest.ini o pyproject.toml:

        [pytest]
        markers =
            slow: tests que toman más tiempo de lo normal
        """
        # Verificamos varios números primos grandes
        primos_grandes = [9973, 9001, 7919, 6271]
        for p in primos_grandes:
            assert calculadora.es_primo(p), f"{p} debería ser primo"

    @pytest.mark.skipif(
        sys.version_info < (3, 10),
        reason="Requiere Python 3.10+"
    )
    def test_solo_python_310():
        """
        skipif: omite el test si la condición es True.
        Útil para tests de features específicas de versiones de Python.
        """
        # El operador | de unions de tipos requiere Python 3.10+
        def mi_funcion(x: int | float) -> int | float:
            return x
        assert mi_funcion(5) == 5

    @pytest.mark.skip(reason="Ejemplo de test temporalmente desactivado")
    def test_desactivado():
        """Este test siempre será omitido."""
        assert False, "Este test no debería ejecutarse"

    def test_con_expected_failure():
        """
        xfail: marca un test como "se espera que falle".
        Útil cuando hay un bug conocido que aún no se ha corregido.
        El test pasa si falla (xfail) y lanza alerta si pasa (xpass).
        """
        # Ejemplo: la suma de flotantes no es exactamente precisa
        # pytest.xfail("Imprecisión conocida de flotantes")
        resultado = calculadora.sumar(0.1, 0.2)
        # Esto es True porque Python representa 0.1+0.2 ≈ 0.30000000000000004
        assert resultado != 0.3  # La imprecisión existe, pero no es un bug


# ==============================================================
# SECCIÓN 5: conftest.py — fixtures compartidas entre archivos
# ==============================================================

"""
NOTA EDUCATIVA — conftest.py (no implementado en este archivo):

En proyectos reales, los fixtures compartidos se ponen en conftest.py.
pytest lo descubre automáticamente sin necesidad de importarlo.

Ejemplo de conftest.py:

    # conftest.py
    import pytest
    from calculadora import sumar, dividir

    @pytest.fixture(scope="session")
    def calculadora_configurada():
        '''
        scope="session": el fixture se crea una vez para toda la sesión.
        scope="module": una vez por módulo.
        scope="class":  una vez por clase.
        scope="function": una vez por test (por defecto).
        '''
        return {"max_decimales": 10, "modo": "estricto"}

    @pytest.fixture
    def datos_prueba():
        return {"numeros": [1, 2, 3, 4, 5]}
"""


# ==============================================================
# FALLBACK: Tests con unittest cuando pytest no está disponible
# ==============================================================

class TestCalculadoraFallback(unittest.TestCase):
    """
    Tests con unittest que se ejecutan cuando pytest no está instalado.
    Cubren los mismos casos que las funciones test_ de pytest.
    """

    def test_sumar(self):
        self.assertEqual(calculadora.sumar(2, 3), 5)
        self.assertEqual(calculadora.sumar(-5, 3), -2)

    def test_dividir(self):
        self.assertEqual(calculadora.dividir(10, 2), 5.0)

    def test_dividir_por_cero(self):
        with self.assertRaises(ValueError):
            calculadora.dividir(5, 0)

    def test_factorial(self):
        casos = [(0, 1), (1, 1), (3, 6), (5, 120), (10, 3628800)]
        for n, esperado in casos:
            with self.subTest(n=n):
                self.assertEqual(calculadora.factorial(n), esperado)

    def test_es_primo(self):
        self.assertTrue(calculadora.es_primo(17))
        self.assertFalse(calculadora.es_primo(15))
        self.assertFalse(calculadora.es_primo(1))

    def test_maximo(self):
        self.assertEqual(calculadora.maximo([3, 1, 9, 2, 5]), 9)
        with self.assertRaises(ValueError):
            calculadora.maximo([])

    def test_promedio(self):
        self.assertEqual(calculadora.promedio([1, 2, 3, 4, 5]), 3.0)


# ==============================================================
# PUNTO DE ENTRADA
# ==============================================================

if __name__ == "__main__":
    if PYTEST_DISPONIBLE:
        print("=" * 60)
        print("pytest está instalado.")
        print("Ejecuta: pytest 03_pytest_intro.py -v")
        print("         pytest 03_pytest_intro.py -v --tb=short")
        print("         pytest 03_pytest_intro.py -v -m 'not slow'")
        print("=" * 60)
        # Ejecutamos pytest programáticamente para la demo
        sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
    else:
        print("=" * 60)
        print("pytest no encontrado. Ejecutando con unittest...")
        print("Para instalar pytest: pip install pytest")
        print("=" * 60)
        # Ejecutamos solo los tests del fallback con unittest
        unittest.main(
            defaultTest="TestCalculadoraFallback",
            verbosity=2,
            exit=True
        )
