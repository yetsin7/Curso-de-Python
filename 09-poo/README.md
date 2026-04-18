# Capítulo 09 — Programación Orientada a Objetos (POO)

La Programación Orientada a Objetos (POO) es una forma de organizar el código
modelando el mundo real en **objetos**. Es el paradigma más usado en
el desarrollo de software profesional.

---

## ¿Qué es un objeto?

Un objeto es una entidad que tiene:
- **Atributos** — características (datos que describe al objeto)
- **Métodos** — comportamientos (acciones que puede hacer)

Por ejemplo, un **Auto** tiene:
- Atributos: color, marca, velocidad actual, está encendido
- Métodos: encender(), acelerar(), frenar(), apagar()

---

## ¿Qué es una clase?

Una clase es el **molde** o **plano** para crear objetos.
Del mismo molde puedes crear muchos objetos distintos.

```
Clase: Auto (molde)
   ↓
Objeto 1: mi_auto = Auto(color="rojo", marca="Toyota")
Objeto 2: tu_auto = Auto(color="azul", marca="Ford")
```

---

## Los 4 pilares de la POO

| Pilar | Qué significa |
|---|---|
| **Encapsulamiento** | Los datos internos están protegidos; se accede a través de métodos |
| **Herencia** | Una clase puede heredar atributos y métodos de otra |
| **Polimorfismo** | Distintas clases pueden tener métodos con el mismo nombre pero diferente comportamiento |
| **Abstracción** | Ocultar detalles complejos, exponer solo lo necesario |

---

## Archivos de este capítulo

| Archivo | Qué aprenderás |
|---|---|
| `01_clases_objetos.py` | Definir clases, crear objetos, atributos y métodos |
| `02_herencia.py` | Reutilizar clases con herencia |
| `03_encapsulamiento.py` | Proteger datos internos |
| `04_polimorfismo.py` | Mismo método, distinto comportamiento |

---

> ✅ Cuando termines, pasa a `10-archivos/`
