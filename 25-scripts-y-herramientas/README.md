# Capítulo 25 — Scripts, Herramientas y CLI

## ¿Cuándo Crear Scripts vs Aplicaciones Completas?

| Situación | Herramienta |
|-----------|-------------|
| Tarea de un solo uso | Script `.py` simple |
| Tarea repetitiva manual | Script con argparse/click |
| Herramienta que otros usarán | Paquete con CLI y `pip install` |
| Interfaz de usuario web/móvil | Aplicación completa (Flask, FastAPI, React) |
| Automatización en servidor | Script + cron job / systemd |

La regla general: **empieza simple**. Un script de 50 líneas puede reemplazar horas de trabajo manual.

---

## CLI Tools — Por Qué Mejoran el Flujo de Trabajo

Las herramientas de línea de comandos (CLI) son la interfaz más eficiente para desarrolladores y sysadmins porque:

- **Componibles**: se encadenan con otros comandos via pipes (`|`)
- **Automatizables**: se integran en scripts y pipelines CI/CD
- **Reproducibles**: el mismo comando da el mismo resultado
- **Sin overhead**: sin interfaz gráfica = más rápido
- **Remotas**: funcionan via SSH en servidores

Herramientas Python que ya usas son CLI: `pip`, `python`, `pytest`, `black`, `git`.

---

## Scripts en DevOps, SysAdmin y Automatización

Python reemplaza a Bash para scripts complejos porque:
- Mejor manejo de errores y excepciones
- Librerías ricas (requests, boto3, paramiko)
- Más legible para scripts de más de 20 líneas
- Cross-platform (Windows + Linux + Mac)

Casos de uso reales:
- Renombrar 10,000 archivos según una regla
- Monitorear logs y enviar alertas
- Generar reportes periódicos
- Desplegar aplicaciones automáticamente
- Sincronizar datos entre servicios

---

## Publicar tu Herramienta en PyPI

PyPI (Python Package Index) es el repositorio oficial. Si publicas tu tool:
- Cualquiera puede instalarla con `pip install tu-herramienta`
- Aparece en el repositorio oficial con millones de paquetes
- Puedes versionarla y actualizar fácilmente

Ver `05_packaging.py` para los pasos completos.

---

## Librerías de Este Capítulo

```bash
pip install click rich
```

- **argparse**: módulo de la librería estándar, sin instalación
- **click**: CLI con decoradores, mucho más limpio que argparse
- **rich**: salida de terminal con colores, tablas, barras de progreso

---

## Archivos del Capítulo

| Archivo | Tema |
|---------|------|
| `01_argparse.py` | CLI con argparse (módulo estándar) |
| `02_click.py` | CLI con Click (librería moderna) |
| `03_rich.py` | Salida visual rica en terminal |
| `04_scripts_utiles.py` | Colección de scripts del mundo real |
| `05_packaging.py` | Empaquetar y publicar en PyPI |
