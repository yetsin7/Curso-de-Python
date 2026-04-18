# Capítulo 03 — Control de Flujo

Por defecto, Python ejecuta el código de arriba hacia abajo, línea por línea.
El control de flujo te permite **cambiar ese orden**: tomar decisiones,
repetir acciones, o saltar partes del código.

---

## ¿Qué es el flujo de un programa?

Imagina que estás cocinando. Las instrucciones son:
1. Hervir agua
2. **Si** tienes sal, agregar sal (si no, continuar)
3. Agregar pasta
4. **Repetir** cada minuto: revisar si está lista
5. Cuando esté lista, apagar el fuego

Los pasos en negrita son control de flujo: decisiones y repeticiones.

---

## Herramientas de control de flujo

| Herramienta | Para qué sirve |
|---|---|
| `if / elif / else` | Tomar decisiones según una condición |
| `for` | Repetir algo una cantidad conocida de veces |
| `while` | Repetir algo mientras una condición sea verdadera |
| `break` | Salir de un bucle antes de que termine |
| `continue` | Saltar la iteración actual y seguir con la siguiente |

---

## La indentación es OBLIGATORIA en Python

Python usa la **indentación** (espacios al inicio de la línea) para saber
qué código pertenece a qué bloque. Otros lenguajes usan llaves `{}`.
En Python, los espacios tienen significado. Si no indentas bien, el programa da error.

```python
if edad >= 18:
    print("Mayor de edad")   # ← esta línea pertenece al if
    print("Puede votar")     # ← esta también
print("Siempre se ejecuta")  # ← esta NO pertenece al if
```

El estándar es usar **4 espacios** por nivel de indentación.
VS Code lo hace automáticamente cuando presionas Enter después de un `:`.

---

## Archivos de este capítulo

| Archivo | Qué aprenderás |
|---|---|
| `01_if_elif_else.py` | Tomar decisiones con condiciones |
| `02_bucle_for.py` | Repetir con for y range() |
| `03_bucle_while.py` | Repetir mientras una condición sea verdadera |
| `04_break_continue.py` | Controlar bucles con break y continue |

---

> ✅ Cuando termines, pasa a `04-funciones/`
