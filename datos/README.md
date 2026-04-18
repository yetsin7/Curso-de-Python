# Carpeta `datos/` — Recursos del Libro de Python

Esta carpeta contiene la base de datos local de este curso. Este repositorio ya
no depende de un monorepo compartido: aquí vive su propia copia de
`biblia_rv60.sqlite3`.

Ruta relativa desde cualquier capítulo de este libro:

```python
import os
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')
```

Puedes personalizar esta base más adelante sin afectar a los demás cursos.
