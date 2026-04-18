# Capítulo 07 — Manejo de Errores

Los errores son parte normal de la programación. La diferencia entre un
programador principiante y uno experimentado no es que el experimentado
no comete errores — es que sabe manejarlos con gracia.

---

## Tipos de errores en Python

### Errores de sintaxis (SyntaxError)
El código está mal escrito y Python no lo puede leer.
```python
print("hola"    # falta el paréntesis de cierre
```

### Errores en tiempo de ejecución (Exceptions)
El código está bien escrito pero algo falla cuando corre.
```python
int("hola")           # ValueError
lista[99]             # IndexError
1 / 0                 # ZeroDivisionError
```

---

## ¿Qué es una excepción?

Una excepción es un objeto que Python crea cuando algo sale mal en tiempo de
ejecución. Si no la "atrapes", el programa se detiene con un mensaje de error.
Si la atrapes con `try/except`, puedes decidir qué hacer.

---

## Archivos de este capítulo

| Archivo | Qué aprenderás |
|---|---|
| `01_try_except.py` | Capturar y manejar errores con try/except |
| `02_tipos_de_errores.py` | Los errores más comunes y cuándo ocurren |

---

> ✅ Cuando termines, pasa a `08-modulos/`
