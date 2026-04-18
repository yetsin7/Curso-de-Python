# Capítulo 19 — APIs REST y Requests

## ¿Qué es una API REST?

Una **API REST** (Representational State Transfer) es una interfaz que permite que dos sistemas se comuniquen a través de HTTP. Es el estándar más usado en la web para exponer y consumir datos entre aplicaciones.

- El **servidor** expone recursos a través de URLs (endpoints).
- El **cliente** envía peticiones HTTP a esos endpoints.
- La respuesta suele llegar en formato **JSON**.

Ejemplo real: cuando una app del clima consulta la temperatura, hace una petición GET a la API de un servicio meteorológico y recibe un JSON con los datos.

---

## Métodos HTTP

| Método   | Uso                                         | Ejemplo                          |
|----------|---------------------------------------------|----------------------------------|
| `GET`    | Obtener datos (sin modificar nada)          | Leer lista de usuarios           |
| `POST`   | Crear un nuevo recurso                      | Registrar un usuario             |
| `PUT`    | Reemplazar un recurso completo              | Actualizar todos los campos      |
| `PATCH`  | Modificar parcialmente un recurso           | Cambiar solo el email            |
| `DELETE` | Eliminar un recurso                         | Borrar un usuario                |

---

## Status Codes más importantes

| Código | Significado                          | Cuándo ocurre                              |
|--------|--------------------------------------|--------------------------------------------|
| `200`  | OK                                   | Petición exitosa (GET, PUT, PATCH)         |
| `201`  | Created                              | Recurso creado correctamente (POST)        |
| `204`  | No Content                           | Eliminación exitosa (DELETE)               |
| `400`  | Bad Request                          | Datos enviados incorrectos o malformados   |
| `401`  | Unauthorized                         | No autenticado (falta token/credenciales)  |
| `403`  | Forbidden                            | Autenticado pero sin permisos              |
| `404`  | Not Found                            | El recurso no existe                       |
| `422`  | Unprocessable Entity                 | Validación fallida (FastAPI lo usa mucho)  |
| `429`  | Too Many Requests                    | Rate limit alcanzado                       |
| `500`  | Internal Server Error                | Error en el servidor                       |

---

## JSON como formato estándar

**JSON** (JavaScript Object Notation) es el formato universal de intercambio de datos en APIs REST.

```json
{
  "id": 1,
  "nombre": "Ana García",
  "activo": true,
  "roles": ["admin", "editor"],
  "direccion": {
    "ciudad": "Madrid",
    "pais": "España"
  }
}
```

Python tiene el módulo `json` integrado para codificar/decodificar JSON. La librería `requests` lo hace automáticamente con `.json()`.

---

## Autenticación en APIs

### API Key
La forma más simple. Se envía una clave única en el header o como parámetro de URL.

```
GET /api/data?api_key=tu_clave_aqui
# o en header:
X-API-Key: tu_clave_aqui
```

### Bearer Token
Token de sesión enviado en el header `Authorization`. Muy común en APIs modernas.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Basic Auth
Credenciales (usuario:contraseña) codificadas en Base64. Solo seguro con HTTPS.

```
Authorization: Basic dXN1YXJpbzpjb250cmFzZW5h
```

### OAuth2
Protocolo estándar para autorización delegada (ej: "Iniciar sesión con Google"). 
Flujo típico:
1. El usuario da permiso en una página del proveedor.
2. El proveedor entrega un `code` temporal.
3. Tu app intercambia ese `code` por un `access_token`.
4. Usas ese token para hacer peticiones.

---

## Cómo explorar una API con su documentación

Antes de escribir código, siempre lee la documentación de la API:

1. **Busca la base URL** (ej: `https://api.github.com`)
2. **Identifica los endpoints** disponibles (`/users`, `/repos`, etc.)
3. **Verifica qué autenticación requiere** (API Key, Bearer, etc.)
4. **Revisa los ejemplos de request/response** en JSON
5. **Anota los rate limits** (cuántas peticiones por minuto/hora)
6. **Usa herramientas como Postman o HTTPie** para probar antes de codificar

---

## Librería `requests`

La librería más popular de Python para hacer peticiones HTTP:

```bash
pip install requests
```

Ventajas sobre `urllib` nativo:
- Sintaxis mucho más limpia y legible
- Manejo automático de cookies, redirecciones, codificación
- Soporte nativo para JSON, archivos, autenticación
- Sessions para reutilizar conexiones y headers

---

## APIs públicas usadas en este capítulo

| API | URL | Autenticación | Para qué se usa |
|-----|-----|---------------|-----------------|
| GitHub API | `api.github.com` | Opcional | Repositorios, usuarios |
| HTTPBin | `httpbin.org` | No | Probar peticiones HTTP |
| JSONPlaceholder | `jsonplaceholder.typicode.com` | No | CRUD falso para pruebas |
| Open-Meteo | `api.open-meteo.com` | No | Clima en tiempo real |
| REST Countries | `restcountries.com` | No | Datos de países |

---

## Archivos del capítulo

| Archivo | Tema |
|---------|------|
| `01_http_conceptos.py` | urllib nativo: GET, POST, headers, errores HTTP |
| `02_requests_avanzado.py` | requests: sessions, auth, retry, timeout, APIs reales |
| `03_trabajar_con_json.py` | json module: encode/decode, custom objects, validación |
| `04_construir_cliente_api.py` | Cliente orientado a objetos con retry, logging, rate limiting |
| `05_autenticacion.py` | Patrones de autenticación: API Key, Bearer, Basic, OAuth2 |
