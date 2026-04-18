# Capítulo 14 — Python Avanzado

## ¿Por qué estos temas son "avanzados"?

Los temas de este capítulo no son difíciles en el sentido de ser imposibles de entender. Son "avanzados" porque:

1. **Requieren entender bien los fundamentos primero** — si no dominas funciones, clases y módulos, estos conceptos se ven sin contexto.
2. **Aparecen en código profesional real** — cuando leas código de librerías como `requests`, `FastAPI`, `pandas` o `SQLAlchemy`, encontrarás todo esto.
3. **Desbloquean patrones de diseño importantes** — type hints permiten herramientas como mypy; context managers permiten gestión limpia de recursos; dataclasses reducen drásticamente el boilerplate.

---

## Cuándo necesitarás cada tema

| Tema | Lo necesitas cuando... |
|---|---|
| Type hints | Tu proyecto crece y quieres detectar bugs antes de ejecutar |
| Context managers | Trabajas con archivos, conexiones, locks, timers |
| Dataclasses | Creas muchas clases que principalmente almacenan datos |
| Iteradores avanzados | Procesas secuencias grandes o trabajas con combinaciones |
| Programación funcional | Quieres código más expresivo y reutilizable |

---

## Cómo estos conceptos aparecen en código real

### Type hints — FastAPI los usa para definir toda su API

```python
# FastAPI usa type hints para generar documentación automática,
# validar datos de entrada y generar clientes TypeScript
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    age: int

@app.post("/users/")
async def create_user(user: User) -> dict:
    return {"id": 1, **user.dict()}
```

### Context managers — SQLAlchemy los usa para transacciones

```python
# SQLAlchemy usa context managers para garantizar que las
# transacciones se confirmen o se reviertan correctamente
with Session() as session:
    user = session.get(User, 1)
    user.name = "Nuevo nombre"
    # Al salir del with, la sesión se cierra automáticamente
```

### Dataclasses — reemplaza el boilerplate de clases de datos

```python
# Sin dataclass: 15 líneas para una clase simple
class PointOld:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

# Con dataclass: 4 líneas, mismo resultado
@dataclass
class Point:
    x: float
    y: float
```

### Itertools — procesamiento eficiente de datos

```python
# pandas usa conceptos similares internamente para groupby
from itertools import groupby

ventas = [("enero", 100), ("enero", 200), ("febrero", 150)]
for mes, grupo in groupby(ventas, key=lambda x: x[0]):
    total = sum(v for _, v in grupo)
    print(f"{mes}: {total}")
```

---

## Herramientas que complementan este capítulo

### mypy — verificador de tipos estático

```bash
pip install mypy
mypy mi_archivo.py
```

mypy analiza tu código sin ejecutarlo y detecta errores de tipos. Cuando dices `def suma(a: int, b: int) -> int`, mypy verifica que siempre llamas a `suma` con enteros.

### pyright / pylance — en VS Code

VS Code usa Pylance (basado en pyright) para mostrar errores de tipos en tiempo real. Solo necesitas agregar type hints a tu código y VS Code los usa automáticamente.

---

## Archivos de este capítulo

| Archivo | Concepto central |
|---|---|
| `01_type_hints.py` | Anotaciones de tipos: básico → avanzado |
| `02_context_managers.py` | `with`, `__enter__`/`__exit__`, `contextlib` |
| `03_dataclasses.py` | `@dataclass`, `field()`, frozen, herencia |
| `04_iteradores_avanzados.py` | `__iter__`, `__next__`, `itertools` completo |
| `05_programacion_funcional.py` | `functools`, closures, currying, `operator` |

---

## Consejo de aprendizaje

No intentes memorizar la sintaxis. Entiende **el problema que resuelve cada concepto** y, cuando lo necesites en un proyecto real, sabrás exactamente cuál buscar.

Los mejores programadores Python no memorizan la API de `itertools` de memoria — saben que existe, saben qué problema resuelve, y consultan la documentación cuando la usan.
