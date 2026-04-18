# =============================================================================
# CAPÍTULO 19 — APIs REST y Requests
# Archivo 03: El módulo json en profundidad
# =============================================================================
# Por qué este archivo: JSON es el formato universal de las APIs REST.
# El módulo json de Python es el estándar para serializar/deserializar,
# pero tiene detalles importantes: tipos que no soporta por defecto,
# manejo de errores, validación, y formato de salida.
# =============================================================================

import json
import datetime
import math
from typing import Any


# =============================================================================
# SECCIÓN 1: encode (Python → JSON) y decode (JSON → Python)
# =============================================================================

def demo_encode_decode_basico() -> None:
    """
    Demuestra la conversión bidireccional entre Python y JSON.

    json.dumps  → Python object → string JSON  (encode / serializar)
    json.loads  → string JSON  → Python object (decode / deserializar)
    json.dump   → Python object → archivo JSON
    json.load   → archivo JSON → Python object
    """
    print("\n--- Encode / Decode básico ---")

    # Estructura Python con distintos tipos de datos
    datos_python = {
        "nombre": "Ana García",
        "edad": 28,
        "activa": True,
        "puntaje": 9.75,
        "notas": [8.5, 9.0, 10.0],
        "metadata": None,
        "config": {"tema": "oscuro", "idioma": "es"},
    }

    # json.dumps convierte el dict a una cadena JSON
    cadena_json = json.dumps(datos_python)
    print(f"  Tipo de cadena_json: {type(cadena_json)}")
    print(f"  JSON compacto: {cadena_json[:80]}...")

    # json.loads convierte la cadena JSON de vuelta a Python
    datos_recuperados = json.loads(cadena_json)
    print(f"  Tipo de datos_recuperados: {type(datos_recuperados)}")
    print(f"  Nombre recuperado: {datos_recuperados['nombre']}")

    # Tabla de equivalencias de tipos Python ↔ JSON
    print("\n  Equivalencias de tipos:")
    print("  Python dict      → JSON object  {}")
    print("  Python list      → JSON array   []")
    print("  Python str       → JSON string  \"\"")
    print("  Python int/float → JSON number")
    print("  Python True      → JSON true")
    print("  Python False     → JSON false")
    print("  Python None      → JSON null")


# =============================================================================
# SECCIÓN 2: Pretty print — JSON legible para humanos
# =============================================================================

def demo_pretty_print() -> None:
    """
    Genera JSON con formato legible (indentado y ordenado).

    Por qué: el JSON compacto es eficiente en red, pero difícil de leer.
    Durante desarrollo y logging, el JSON indentado es mucho más claro.

    indent=2 o indent=4 son las convenciones más comunes.
    sort_keys ordena las claves alfabéticamente — útil para comparar.
    ensure_ascii=False permite caracteres especiales como ñ, á, é...
    """
    print("\n--- Pretty print ---")

    datos = {
        "usuario": "Miguel Ángel",
        "ciudad": "Bogotá",
        "descripción": "Desarrollador Python",
        "habilidades": ["Python", "SQL", "Docker"],
        "experiencia": {"años": 5, "nivel": "senior"},
    }

    # Sin formato — difícil de leer
    compacto = json.dumps(datos)
    print(f"  Compacto ({len(compacto)} chars): {compacto[:70]}...")

    # Con indentación y sin escapar caracteres especiales
    bonito = json.dumps(datos, indent=2, ensure_ascii=False, sort_keys=True)
    print(f"\n  Formateado ({len(bonito)} chars):")
    # Mostramos solo las primeras líneas para no saturar la salida
    for linea in bonito.split("\n")[:10]:
        print(f"    {linea}")


# =============================================================================
# SECCIÓN 3: JSONEncoder personalizado para tipos no soportados
# =============================================================================

class DateTimeEncoder(json.JSONEncoder):
    """
    Encoder personalizado que serializa tipos que json no soporta por defecto.

    Por qué: json.dumps falla con datetime, Decimal, UUID, sets, etc.
    Extender JSONEncoder y sobreescribir default() resuelve esto elegantemente.

    La solución alternativa (menos limpia) sería convertir manualmente
    cada objeto antes de llamar a json.dumps.
    """

    def default(self, obj: Any) -> Any:
        """
        Se llama cuando json encuentra un tipo que no sabe serializar.

        Si reconocemos el tipo, lo convertimos a algo que json sí entienda.
        Si no, llamamos a super().default() que lanzará TypeError.

        Args:
            obj: El objeto que json no pudo serializar.

        Returns:
            Una representación serializable del objeto.
        """
        if isinstance(obj, datetime.datetime):
            # ISO 8601 es el estándar para fechas en APIs REST
            # Ejemplo: "2024-03-15T14:30:00"
            return obj.isoformat()

        if isinstance(obj, datetime.date):
            # Solo fecha sin hora
            return obj.isoformat()

        if isinstance(obj, set):
            # Los sets no tienen orden definido → los convertimos a lista ordenada
            return sorted(list(obj))

        if isinstance(obj, bytes):
            # Bytes los representamos como cadena hexadecimal
            return obj.hex()

        # Para tipos desconocidos, delegamos al comportamiento base
        # (que lanzará TypeError con un mensaje claro)
        return super().default(obj)


def demo_encoder_personalizado() -> None:
    """
    Demuestra el uso de DateTimeEncoder para tipos no serializables por defecto.
    """
    print("\n--- Encoder personalizado para tipos especiales ---")

    datos_complejos = {
        "timestamp": datetime.datetime(2024, 6, 15, 10, 30, 0),
        "fecha_nacimiento": datetime.date(1995, 3, 22),
        "etiquetas": {"python", "api", "rest"},  # set
        "hash_archivo": b"\xde\xad\xbe\xef",      # bytes
        "nombre": "Sofía",
    }

    # Sin encoder personalizado esto fallaría con TypeError
    try:
        json.dumps(datos_complejos)
    except TypeError as e:
        print(f"  Sin encoder personalizado → Error: {e}")

    # Con nuestro encoder personalizado funciona correctamente
    resultado = json.dumps(datos_complejos, cls=DateTimeEncoder, indent=2, ensure_ascii=False)
    print(f"\n  Con DateTimeEncoder:")
    for linea in resultado.split("\n"):
        print(f"    {linea}")


# =============================================================================
# SECCIÓN 4: Manejo robusto de errores de parsing
# =============================================================================

def parsear_json_seguro(texto: str) -> tuple[Any, str | None]:
    """
    Parsea JSON de forma segura, retornando el error en lugar de lanzarlo.

    Por qué: cuando recibes JSON de una API externa, puede estar malformado,
    incompleto, o ser texto de error (HTML) en lugar de JSON.
    Capturar el error permite dar feedback claro al usuario.

    Args:
        texto: La cadena que intentamos parsear como JSON.

    Returns:
        Tupla (datos_parseados, mensaje_error). Si hay error, datos=None.
    """
    if not texto or not texto.strip():
        return None, "El texto está vacío"

    try:
        datos = json.loads(texto)
        return datos, None

    except json.JSONDecodeError as e:
        # JSONDecodeError nos da la posición exacta del error
        mensaje = (
            f"JSON inválido en línea {e.lineno}, columna {e.colno}: {e.msg}\n"
            f"Fragmento problemático: ...{texto[max(0, e.pos-20):e.pos+20]}..."
        )
        return None, mensaje


def demo_manejo_errores_json() -> None:
    """
    Muestra distintos casos de JSON malformado y cómo manejarlos.
    """
    print("\n--- Manejo de errores de JSON ---")

    casos = [
        ('{"nombre": "Ana", "edad": 28}', "JSON válido"),
        ('{"nombre": "Ana", "edad": }', "Valor faltante"),
        ("{'nombre': 'Ana'}", "Comillas simples (Python, no JSON)"),
        ('<html><body>Error 500</body></html>', "HTML en lugar de JSON"),
        ("", "Cadena vacía"),
        ('{"truncado": true', "JSON incompleto"),
    ]

    for texto, descripcion in casos:
        datos, error = parsear_json_seguro(texto)
        if error:
            print(f"  [{descripcion}] → Error: {error[:80]}")
        else:
            print(f"  [{descripcion}] → OK: {datos}")


# =============================================================================
# SECCIÓN 5: Validación básica de esquema sin librerías externas
# =============================================================================

def validar_esquema(datos: dict, esquema: dict) -> list[str]:
    """
    Valida que un diccionario cumpla con un esquema básico definido.

    Por qué: antes de procesar datos de una API, conviene verificar que
    tienen la estructura esperada. jsonschema es la librería estándar para
    esto, pero aquí vemos cómo construir una validación básica manual
    para entender el concepto.

    El esquema es un dict donde las claves son campos y los valores son
    dicts con: required (bool), type (tipo Python), y min/max opcionales.

    Args:
        datos: El diccionario de datos a validar.
        esquema: La definición del esquema esperado.

    Returns:
        Lista de errores encontrados. Lista vacía si todo está bien.
    """
    errores = []

    for campo, reglas in esquema.items():
        es_requerido = reglas.get("required", True)
        tipo_esperado = reglas.get("type")

        # Verificar presencia del campo requerido
        if campo not in datos:
            if es_requerido:
                errores.append(f"Campo requerido faltante: '{campo}'")
            continue  # Si no está y no es requerido, no seguimos verificando

        valor = datos[campo]

        # Verificar tipo
        if tipo_esperado and not isinstance(valor, tipo_esperado):
            errores.append(
                f"'{campo}': se esperaba {tipo_esperado.__name__}, "
                f"se recibió {type(valor).__name__}"
            )
            continue

        # Verificar rango para números
        if isinstance(valor, (int, float)):
            minimo = reglas.get("min")
            maximo = reglas.get("max")
            if minimo is not None and valor < minimo:
                errores.append(f"'{campo}': {valor} es menor que el mínimo {minimo}")
            if maximo is not None and valor > maximo:
                errores.append(f"'{campo}': {valor} supera el máximo {maximo}")

        # Verificar longitud para strings
        if isinstance(valor, str):
            min_len = reglas.get("min_length")
            max_len = reglas.get("max_length")
            if min_len is not None and len(valor) < min_len:
                errores.append(f"'{campo}': texto muy corto (mínimo {min_len} chars)")
            if max_len is not None and len(valor) > max_len:
                errores.append(f"'{campo}': texto muy largo (máximo {max_len} chars)")

    return errores


def demo_validacion_esquema() -> None:
    """
    Demuestra la validación de esquema con datos válidos e inválidos.
    """
    print("\n--- Validación básica de esquema ---")

    # Definición del esquema esperado
    esquema_usuario = {
        "nombre": {"required": True, "type": str, "min_length": 2, "max_length": 100},
        "edad": {"required": True, "type": int, "min": 0, "max": 150},
        "email": {"required": True, "type": str, "min_length": 5},
        "bio": {"required": False, "type": str},
    }

    casos = [
        {
            "nombre": "Carlos",
            "edad": 35,
            "email": "carlos@ejemplo.com",
        },
        {
            "nombre": "X",            # Muy corto
            "edad": -5,               # Negativo
            "email": "no",            # Muy corto
        },
        {
            "edad": "treinta",        # Tipo incorrecto
            "email": "test@test.com", # Falta nombre
        },
    ]

    for i, datos in enumerate(casos, 1):
        errores = validar_esquema(datos, esquema_usuario)
        if errores:
            print(f"\n  Caso {i} — {len(errores)} error(es):")
            for e in errores:
                print(f"    • {e}")
        else:
            print(f"\n  Caso {i} — Válido ✓")


# =============================================================================
# SECCIÓN 6: Lectura y escritura de archivos JSON
# =============================================================================

def demo_archivos_json() -> None:
    """
    Demuestra cómo guardar y leer datos JSON en archivos.

    Por qué: muchos proyectos usan archivos JSON para configuración,
    caché local, o exportación de datos. json.dump y json.load
    son las funciones para trabajar con archivos.
    """
    import tempfile
    import os

    print("\n--- Archivos JSON ---")

    datos = {
        "version": "1.0",
        "creado": datetime.datetime.now().isoformat(),
        "usuarios": [
            {"id": 1, "nombre": "Lucía", "activa": True},
            {"id": 2, "nombre": "Pedro", "activa": False},
        ],
    }

    # Guardamos en un archivo temporal para la demostración
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",  # Siempre especificar UTF-8 para evitar problemas
    ) as f:
        ruta = f.name
        # json.dump escribe directamente al archivo (no devuelve string)
        json.dump(datos, f, indent=2, ensure_ascii=False)

    print(f"  Archivo guardado en: {ruta}")
    print(f"  Tamaño: {os.path.getsize(ruta)} bytes")

    # Leemos el archivo de vuelta
    with open(ruta, encoding="utf-8") as f:
        datos_leidos = json.load(f)

    print(f"  Versión leída: {datos_leidos['version']}")
    print(f"  Usuarios: {[u['nombre'] for u in datos_leidos['usuarios']]}")

    # Limpiamos el archivo temporal
    os.unlink(ruta)
    print("  Archivo temporal eliminado.")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("EL MÓDULO json EN PROFUNDIDAD")
    print("=" * 60)

    demo_encode_decode_basico()
    demo_pretty_print()
    demo_encoder_personalizado()
    demo_manejo_errores_json()
    demo_validacion_esquema()
    demo_archivos_json()

    print("\n" + "=" * 60)
    print("Fin — siguiente: 04_construir_cliente_api.py")
    print("=" * 60)
