# Capítulo 11 — Nivel Intermedio

¡Felicitaciones! Si llegaste hasta aquí, ya sabes lo esencial de Python.
Este capítulo te introduce a técnicas que usarás en código Python real y
profesional. No son imprescindibles para empezar, pero separan a quienes
"conocen Python" de quienes lo dominan.

---

## ¿Qué aprenderás?

### Comprensiones de listas
Una forma concisa y pythónica de crear listas, diccionarios y conjuntos
en una sola línea. Código más limpio y generalmente más rápido.

```python
# Sin comprensión:
cuadrados = []
for i in range(10):
    cuadrados.append(i ** 2)

# Con comprensión:
cuadrados = [i ** 2 for i in range(10)]
```

### Generadores
Como las comprensiones, pero más eficientes en memoria.
En lugar de crear toda la lista, producen valores uno a la vez.
Ideales para procesar archivos grandes o secuencias infinitas.

### Decoradores
Funciones que "envuelven" otras funciones para agregar comportamiento.
Muy usados en frameworks como Flask y Django.

---

## Archivos de este capítulo

| Archivo | Qué aprenderás |
|---|---|
| `01_comprensiones.py` | List comprehensions, dict comprehensions |
| `02_generadores.py` | yield, generators, iteradores |
| `03_decoradores.py` | Decoradores de funciones |

---

> ✅ Cuando termines, pasa a `12-proyecto-final/` — ¡la recta final!
