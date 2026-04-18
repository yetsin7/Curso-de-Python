# Capítulo 15 — Testing

## ¿Por qué el testing es fundamental?

El código sin tests es código que no puedes modificar con confianza. Cada vez que cambias algo, tienes que verificar manualmente que nada se rompió. Esto no escala.

Con tests puedes:

- **Refactorizar sin miedo** — los tests te dicen inmediatamente si algo se rompió
- **Documentar el comportamiento esperado** — los tests son la especificación ejecutable del código
- **Detectar regresiones** — si alguien agrega código que rompe algo existente, el test falla
- **Diseñar mejor** — el código fácil de testear suele ser código bien diseñado (bajo acoplamiento)
- **Desplegar con confianza** — si todos los tests pasan, el despliegue es seguro

---

## unittest vs pytest

Python tiene dos ecosistemas principales de testing:

### unittest — incluido en la librería estándar

```python
import unittest

class TestMiCodigo(unittest.TestCase):
    def test_suma(self):
        self.assertEqual(2 + 2, 4)

if __name__ == "__main__":
    unittest.main()
```

**Cuándo usar unittest:**
- No puedes instalar dependencias externas
- El proyecto ya usa unittest y no vale la pena migrar
- Quieres algo incluido en Python sin instalación extra

### pytest — el estándar de la industria

```python
def test_suma():
    assert 2 + 2 == 4
```

**Cuándo usar pytest:**
- Proyectos nuevos (recomendado por defecto)
- Quieres fixtures potentes, parametrize, markers
- Quieres plugins (cobertura, mocking, async, etc.)
- El output es más legible y los errores más informativos

| Aspecto | unittest | pytest |
|---|---|---|
| Incluido en Python | Sí | No (pip install pytest) |
| Verbosidad | Alta | Baja |
- Fixtures | Manual (setUp/tearDown) | Poderosas y reutilizables |
| Parametrización | Subtest (limitado) | @pytest.mark.parametrize |
| Plugins | Pocos | Más de 1000 |
| Output de errores | Básico | Muy detallado |

---

## TDD — Test-Driven Development

TDD invierte el orden habitual de desarrollo:

```
Ciclo normal:     Escribe código → (a veces) escribe tests
Ciclo TDD:        Escribe test → (falla) → escribe código → (pasa) → refactoriza
```

### El ciclo Red-Green-Refactor

```
1. RED    → Escribe un test que describe el comportamiento esperado.
            El test DEBE fallar (el código aún no existe).

2. GREEN  → Escribe el código mínimo para que el test pase.
            No te preocupes por el diseño todavía.

3. REFACTOR → Mejora el código sin cambiar el comportamiento.
              Los tests garantizan que no rompiste nada.
```

### Por qué TDD importa

- Fuerza a pensar en la **interfaz** antes que en la implementación
- Los tests actúan como **especificación ejecutable**
- Nunca escribes código que no necesitas (YAGNI)
- El diseño emerge naturalmente del proceso

---

## Cómo ejecutar los tests

### Con unittest

```bash
# Ejecutar un archivo de tests directamente
python 01_unittest_basico.py

# Ejecutar con el runner de unittest (más detalle)
python -m unittest 01_unittest_basico.py

# Descubrir y ejecutar todos los tests en el directorio
python -m unittest discover -s . -p "*.py"

# Modo verbose (muestra el nombre de cada test)
python -m unittest -v 01_unittest_basico.py
```

### Con pytest

```bash
# Instalar pytest
pip install pytest pytest-cov

# Ejecutar todos los tests
pytest

# Ejecutar un archivo específico
pytest 03_pytest_intro.py

# Modo verbose
pytest -v

# Mostrar output de print() durante los tests
pytest -s

# Cobertura de código
pytest --cov=calculadora --cov-report=term-missing

# Ejecutar solo tests con un marker específico
pytest -m "not slow"
```

### En VS Code

1. Abre la paleta de comandos: `Ctrl+Shift+P`
2. Escribe "Python: Configure Tests"
3. Selecciona "unittest" o "pytest"
4. Selecciona el directorio de tests (`.` para el actual)
5. La extensión de Python mostrará los tests en el panel izquierdo
6. Puedes ejecutar y depurar tests individuales con un clic

---

## Conceptos clave

### Assertions (afirmaciones)

Un test verifica que el código se comporta como se espera usando assertions:

```python
# unittest
self.assertEqual(resultado, esperado)
self.assertRaises(ValueError, funcion, argumento)
self.assertTrue(condicion)
self.assertIsNone(valor)

# pytest
assert resultado == esperado
with pytest.raises(ValueError):
    funcion(argumento)
```

### Fixtures (accesorios)

Datos o estados que los tests necesitan. Se crean en `setUp` (unittest) o con `@pytest.fixture` (pytest).

### Mocking (simulación)

Reemplaza dependencias reales (bases de datos, APIs, archivos) con objetos falsos controlables. Permite testear en aislamiento.

### Cobertura de código (coverage)

Mide qué porcentaje de tu código es ejecutado por los tests. 100% de cobertura no garantiza que los tests sean buenos, pero 30% de cobertura garantiza que hay mucho sin probar.

---

## Archivos de este capítulo

| Archivo | Qué aprenderás |
|---|---|
| `calculadora.py` | Módulo bajo prueba — funciones matemáticas |
| `01_unittest_basico.py` | TestCase, assertions, setUp/tearDown, subTest |
| `02_unittest_avanzado.py` | Mock, patch, MagicMock, side_effect |
| `03_pytest_intro.py` | fixtures, parametrize, markers, fallback a unittest |
