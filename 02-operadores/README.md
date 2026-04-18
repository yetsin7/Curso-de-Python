# Capítulo 02 — Operadores

Los operadores son herramientas para transformar datos. Gracias a ellos un
programa puede calcular, comparar, decidir y actualizar valores.

---

## ¿Que aprenderas?

Al terminar este capitulo deberias entender:

- como Python hace calculos;
- como compara valores;
- como combina condiciones;
- como actualiza una variable sin reescribir toda la expresion.

---

## ¿Que ocurre dentro del programa?

Cuando Python evalua una expresion con operadores:

- toma los valores involucrados;
- aplica reglas de precedencia;
- calcula un resultado;
- lo imprime, lo guarda o lo usa dentro de una condicion.

Por ejemplo, en `a + b`, Python toma ambos datos, hace la suma y genera un valor
nuevo que puede seguir viviendo en memoria.

---

## Tipos de operadores en Python

| Tipo | Ejemplos | Para que sirve |
|---|---|---|
| **Aritmeticos** | `+`, `-`, `*`, `/`, `**`, `//`, `%` | Hacer calculos |
| **Comparacion** | `==`, `!=`, `>`, `<`, `>=`, `<=` | Comparar valores |
| **Logicos** | `and`, `or`, `not` | Combinar condiciones |
| **Asignacion** | `=`, `+=`, `-=`, `*=` | Actualizar variables |

---

## ¿Por que este capitulo es importante?

Porque en el siguiente capitulo aprenderas a tomar decisiones con `if`.

```python
if edad >= 18 and tiene_documento:
    print("Puede entrar")
```

En esa sola linea ya aparecen comparacion y logica trabajando juntas.

---

## Archivos de este capítulo

| Archivo | Que aprenderas |
|---|---|
| `01_aritmeticos.py` | Calculos y orden de operaciones |
| `02_comparacion.py` | Comparar valores y obtener `True` o `False` |
| `03_logicos.py` | Combinar condiciones |
| `04_asignacion.py` | Actualizar una variable con mas claridad |

---

## Errores comunes

- confundir `=` con `==`;
- olvidar que `/` y `//` no hacen lo mismo;
- usar `and` y `or` sin pensar el resultado esperado;
- no usar parentesis cuando una expresion se vuelve dificil de leer.

---

## Practica guiada

1. Ejecuta los ejemplos y escribe el resultado esperado antes de correrlos.
2. Cambia valores para provocar resultados distintos.
3. Prueba divisibilidad con `%`.
4. Escribe dos condiciones propias usando `and` y `or`.
5. Explica la diferencia entre comparar y asignar.

> ✅ Cuando termines, pasa a `03-control-de-flujo/`.
