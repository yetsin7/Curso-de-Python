# Capítulo 18 — Automatización de Tareas con Python

## ¿Qué tareas son automatizables con Python?

Si una tarea es **repetitiva, predecible y basada en reglas**, Python puede automatizarla. La automatización es una de las aplicaciones más prácticas e inmediatas de Python.

### Categorías de automatización

| Categoría | Ejemplos | Herramientas |
|-----------|----------|--------------|
| **Sistema de archivos** | Organizar carpetas, renombrar masivo, backups | `os`, `shutil`, `pathlib` |
| **Datos y reportes** | Procesar CSVs, generar Excel, consolidar datos | `csv`, `openpyxl`, `pandas` |
| **Email** | Enviar reportes, notificaciones, alertas | `smtplib`, `email.mime` |
| **Scheduling** | Tareas periódicas, recordatorios, limpieza | `schedule`, `APScheduler` |
| **GUI y escritorio** | Clic automático, capturas, teclas | `pyautogui` |
| **Procesos del sistema** | Ejecutar comandos, scripts, pipelines | `subprocess`, `os` |
| **Web** | Abrir URLs, descargar archivos | `webbrowser`, `requests` |

---

## ¿Por qué Python es el rey de la automatización?

1. **Legibilidad**: el código Python es casi lenguaje natural.
2. **Ecosistema**: hay una librería para prácticamente cualquier tarea.
3. **Multiplataforma**: funciona en Windows, macOS y Linux.
4. **Integración**: se conecta fácilmente con bases de datos, APIs, Office, etc.
5. **Comunidad**: millones de scripts y ejemplos disponibles.

---

## Categorías en detalle

### Archivos y Directorios
Python incluye de serie las herramientas más potentes para el sistema de archivos:

```python
import os         # operaciones del sistema operativo
import shutil     # copiar, mover, eliminar archivos/carpetas
from pathlib import Path  # API moderna y orientada a objetos para rutas
import glob       # buscar archivos por patrón (*.pdf, **/*.log)
```

### Datos: CSV y Excel
CSV es el formato universal de intercambio de datos. Excel domina en empresas.

```python
import csv                # lectura/escritura de CSV (incluido con Python)
import openpyxl           # leer y escribir archivos .xlsx (pip install openpyxl)
import pandas as pd       # el estándar para análisis de datos (pip install pandas)
```

### Email Automatizado
Python puede enviar emails directamente usando SMTP (el protocolo de correo).

```python
import smtplib            # cliente SMTP (incluido con Python)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
```

**Proveedores SMTP comunes:**

| Proveedor | Servidor SMTP | Puerto TLS |
|-----------|---------------|------------|
| Gmail | smtp.gmail.com | 587 |
| Outlook/Hotmail | smtp.office365.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |

> **Nota sobre Gmail**: Google requiere usar una "Contraseña de aplicación" en lugar de tu contraseña normal. Se genera en: Cuenta de Google → Seguridad → Verificación en 2 pasos → Contraseñas de aplicación.

### Scheduling — Tareas Periódicas
Para ejecutar código en horarios o intervalos fijos:

```bash
pip install schedule     # simple, para scripts básicos
pip install apscheduler  # más potente, para aplicaciones reales
```

### Automatización de GUI con PyAutoGUI
Controla el mouse y el teclado programáticamente:

```bash
pip install pyautogui
```

> **Precaución con PyAutoGUI**: puede mover el mouse y escribir en cualquier ventana. Mueve el mouse a la esquina superior izquierda para detenerlo (activa FailSafeException).

---

## Seguridad en automatización

### Variables de entorno para credenciales
**NUNCA** hardcodees contraseñas en el código fuente. Usa variables de entorno:

```bash
# Windows
set EMAIL_PASSWORD=mi_contraseña

# Linux/macOS
export EMAIL_PASSWORD=mi_contraseña
```

```python
import os
password = os.environ.get("EMAIL_PASSWORD")
```

### python-dotenv para desarrollo local
```bash
pip install python-dotenv
```

Crea un archivo `.env` (¡añádelo al `.gitignore`!):
```
EMAIL_ADDRESS=tu@email.com
EMAIL_PASSWORD=tu_password_de_app
```

```python
from dotenv import load_dotenv
load_dotenv()
password = os.environ.get("EMAIL_PASSWORD")
```

---

## Archivos del capítulo

| Archivo | Contenido |
|---------|-----------|
| `01_sistema_archivos.py` | `os`, `shutil`, `pathlib`, glob, operaciones completas |
| `02_automatizar_excel_csv.py` | CSV nativo, openpyxl para Excel, consolidar datos |
| `03_enviar_emails.py` | smtplib, HTML, adjuntos, variables de entorno |
| `04_scheduling.py` | `schedule`, threading, tareas periódicas en background |
| `05_automatizacion_web.py` | `pyautogui`, `webbrowser`, `subprocess` |
