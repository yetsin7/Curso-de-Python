# Capítulo 04 — Funciones

Una función es un bloque de código con nombre que puedes reutilizar.
En lugar de escribir el mismo código 10 veces, lo escribes una vez como función
y lo llamas 10 veces.

---

## ¿Por qué usar funciones?

Imagina que tienes que calcular el área de un rectángulo en 5 partes distintas
de tu programa. Sin funciones:

```python
# Parte 1
area1 = 5 * 3

# Parte 2
area2 = 8 * 4

# Parte 3
area3 = 2 * 7
```

Con función:
```python
def area_rectangulo(ancho, alto):
    return ancho * alto

area1 = area_rectangulo(5, 3)
area2 = area_rectangulo(8, 4)
area3 = area_rectangulo(2, 7)
```

**Ventajas:**
- Si hay un error, lo corriges en un solo lugar
- El código es más fácil de leer y entender
- Puedes reutilizarla en cualquier parte del programa

---

## Conceptos clave

- **`def`** — palabra clave para definir una función
- **parámetros** — los datos que la función recibe (su entrada)
- **`return`** — devuelve un resultado al código que llamó la función
- **argumento** — el valor real que pasas al llamar la función
- **función lambda** — función anónima de una línea para usos simples

---

## Archivos de este capítulo

| Archivo | Qué aprenderás |
|---|---|
| `01_funciones_basicas.py` | Definir y llamar funciones |
| `02_parametros.py` | Parámetros, argumentos y valores por defecto |
| `03_retorno.py` | return — devolver resultados |
| `04_lambda.py` | Funciones anónimas de una línea |

---

> ✅ Cuando termines, pasa a `05-estructuras-de-datos/`
