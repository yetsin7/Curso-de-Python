# Capítulo 28 — Logging, Configuración y Buenas Prácticas

## ¿Por qué `print()` no es suficiente en producción?

```python
# ❌ Desarrollo amateur
print("Usuario logueado")
print("ERROR: algo falló")
print(f"DEBUG: valor = {x}")

# ✅ Producción profesional
logger.info("Usuario logueado", extra={"user_id": 123})
logger.error("Pago fallido", exc_info=True, extra={"order_id": 456})
logger.debug("Valor intermedio calculado", extra={"value": x})
```

### Los problemas de `print()`:

| Problema | Impacto |
|---|---|
| Sin niveles de severidad | No puedes filtrar "solo errores" en producción |
| Sin timestamps | No sabes cuándo ocurrió algo |
| Sin contexto | No sabes en qué módulo/función ocurrió |
| Sin destino configurable | No puedes enviar logs a un archivo, servicio externo, etc. |
| No puede silenciarse | Siempre sale por stdout sin opción de desactivar |
| Sin rotación | Los logs crecen infinitamente llenando el disco |

---

## Los 5 niveles de log

Los niveles son jerárquicos. Si configuras el logger en nivel `WARNING`, ignorará `DEBUG` e `INFO` automáticamente.

```
CRITICAL (50) ← Más severo: la app no puede continuar
ERROR    (40) ← Error grave: una operación falló
WARNING  (30) ← Advertencia: algo inesperado pero recuperable
INFO     (20) ← Información general: flujo normal del programa
DEBUG    (10) ← Más detalle: información de diagnóstico
NOTSET   (0)  ← Procesa todos los mensajes
```

### Guía práctica de cuándo usar cada nivel:

**DEBUG**: Información para desarrolladores. ¿Qué valor tiene esta variable? ¿Se ejecutó este branch?
```python
logger.debug(f"Calculando precio con descuento={descuento}")
```

**INFO**: Eventos normales del negocio. ¿Qué está haciendo el sistema?
```python
logger.info(f"Pedido #{order_id} creado exitosamente por usuario #{user_id}")
```

**WARNING**: Algo inusual pero no crítico. El sistema puede continuar.
```python
logger.warning(f"Tasa de caché bajo el umbral: {cache_hit_rate:.1%}")
```

**ERROR**: Algo falló. Una función no pudo completarse.
```python
logger.error(f"Pago fallido para pedido #{order_id}", exc_info=True)
```

**CRITICAL**: El sistema está en estado irrecuperable.
```python
logger.critical("Base de datos principal no disponible — apagando servicio")
```

---

## Configuración de aplicaciones

Una aplicación profesional **no debe tener valores hardcodeados**. Los secretos, URLs, credenciales y configuración específica del entorno deben vivir fuera del código.

### Jerarquía de configuración (de mayor a menor prioridad):

```
1. Variables de entorno del OS
2. Argumentos de línea de comandos
3. Archivo .env (solo desarrollo)
4. Archivo de configuración (YAML/TOML/INI)
5. Valores por defecto en el código
```

### Opciones de formato para archivos de configuración:

| Formato | Librería | Cuándo usarlo |
|---|---|---|
| `.env` | `python-dotenv` | Secretos locales de desarrollo |
| `.ini` / `.cfg` | `configparser` (stdlib) | Apps simples, sin anidamiento |
| `.yaml` | `pyyaml` | Configuración compleja, legible |
| `.toml` | `tomllib` (Python 3.11+) | Proyectos modernos (pyproject.toml) |
| Python tipado | `pydantic-settings` | APIs, FastAPI, validación automática |

### Reglas de oro para seguridad en configuración:

1. **NUNCA** commitear `.env` al repositorio → agregarlo a `.gitignore`
2. **NUNCA** poner secretos en el código fuente
3. **NUNCA** loguear contraseñas, tokens o datos sensibles
4. **Usar variables de entorno** para producción (no archivos .env)
5. **Validar la configuración al inicio** — falla rápido si falta algo crítico
6. **Rotar secretos** periódicamente (API keys, contraseñas de BD)

---

## Principios de código limpio en Python

### PEP 8 — La guía de estilo oficial de Python

PEP 8 no es opcional en código profesional. Define:
- Indentación: 4 espacios (no tabs)
- Longitud máxima de línea: 88 caracteres (Black) o 79 (PEP 8 puro)
- Espacios alrededor de operadores
- Nombres: `snake_case` para variables/funciones, `PascalCase` para clases

### Principios SOLID en Python

| Principio | Significa | Beneficio |
|---|---|---|
| **S**ingle Responsibility | Cada clase hace UNA cosa | Fácil de entender y testear |
| **O**pen/Closed | Abierto a extensión, cerrado a modificación | No rompes código existente |
| **L**iskov Substitution | Las subclases son intercambiables | Polimorfismo correcto |
| **I**nterface Segregation | Interfaces pequeñas y específicas | No forzas métodos innecesarios |
| **D**ependency Inversion | Depende de abstracciones, no implementaciones | Código desacoplado y testeable |

---

## Archivos de este capítulo

1. **`01_logging_basico.py`** — Módulo `logging`: handlers, formatters, rotación, múltiples módulos
2. **`02_logging_avanzado.py`** — Logs estructurados JSON, dictConfig, integración con excepciones
3. **`03_configuracion_app.py`** — python-dotenv, configparser, pydantic-settings, por entornos
4. **`04_buenas_practicas.py`** — PEP 8, SOLID, code smells, type hints, refactoring

---

## Recursos adicionales

- [logging — documentación oficial](https://docs.python.org/3/library/logging.html)
- [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [PEP 8 — Style Guide](https://peps.python.org/pep-0008/)
- [black — The uncompromising formatter](https://black.readthedocs.io/)
