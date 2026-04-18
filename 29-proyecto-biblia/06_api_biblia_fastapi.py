"""
Mini API REST de la Biblia RV60 con FastAPI.
Si FastAPI no está instalado, usa http.server como fallback.
Aprende a construir endpoints, respuestas JSON y manejar parámetros de ruta.
Ejecutar: python 06_api_biblia_fastapi.py
Requiere: pip install fastapi uvicorn
"""

import sqlite3
import os
import re
import json
import random
from urllib.parse import urlparse, parse_qs

# --- Ruta relativa a la BD ---
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'biblia_rv60.sqlite3')

PORT = 8000


# ──────────────────────────────────────────────────────────────
#  LÓGICA DE DATOS COMPARTIDA (usada tanto por FastAPI como por http.server)
# ──────────────────────────────────────────────────────────────

def limpiar_texto(texto):
    """
    Elimina marcas Strong del texto bíblico.
    Retorna el texto limpio sin etiquetas <S>NNNN</S>.
    """
    limpio = re.sub(r'<S>\d+</S>', '', texto)
    return re.sub(r' {2,}', ' ', limpio).strip()


def get_conn():
    """
    Abre y retorna una conexión nueva a la BD de la Biblia.
    Cada petición abre y cierra su propia conexión (thread-safe).
    """
    ruta = os.path.abspath(DB_PATH)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f'BD no encontrada en: {ruta}')
    conn = sqlite3.connect(ruta)
    conn.row_factory = sqlite3.Row  # Permite acceder por nombre de columna
    return conn


def db_get_libros():
    """
    Devuelve la lista de los 66 libros con book_number, short_name, long_name.
    """
    conn = get_conn()
    filas = conn.execute(
        'SELECT book_number, short_name, long_name FROM books ORDER BY book_number'
    ).fetchall()
    conn.close()
    return [{'book_number': r[0], 'short_name': r[1], 'long_name': r[2]} for r in filas]


def db_get_libro(book_number):
    """
    Devuelve la información de un libro por su book_number.
    Incluye el total de capítulos y versículos.
    Retorna None si no existe.
    """
    conn = get_conn()
    fila = conn.execute(
        'SELECT book_number, short_name, long_name, book_color FROM books WHERE book_number = ?',
        (book_number,)
    ).fetchone()
    if not fila:
        conn.close()
        return None
    caps = conn.execute(
        'SELECT COUNT(DISTINCT chapter) FROM verses WHERE book_number = ?',
        (book_number,)
    ).fetchone()[0]
    vers = conn.execute(
        'SELECT COUNT(*) FROM verses WHERE book_number = ?',
        (book_number,)
    ).fetchone()[0]
    conn.close()
    return {
        'book_number': fila[0],
        'short_name':  fila[1],
        'long_name':   fila[2],
        'book_color':  fila[3],
        'chapters':    caps,
        'verses_total': vers
    }


def db_get_versiculo(book_number, chapter, verse):
    """
    Devuelve un versículo específico con texto limpio.
    Retorna None si no existe.
    """
    conn = get_conn()
    fila = conn.execute(
        '''SELECT b.long_name, b.short_name, v.chapter, v.verse, v.text
           FROM verses v JOIN books b ON v.book_number = b.book_number
           WHERE v.book_number=? AND v.chapter=? AND v.verse=?''',
        (book_number, chapter, verse)
    ).fetchone()
    conn.close()
    if not fila:
        return None
    return {
        'book_name': fila[0], 'short_name': fila[1],
        'chapter': fila[2], 'verse': fila[3],
        'text': limpiar_texto(fila[4]),
        'reference': f'{fila[1]} {fila[2]}:{fila[3]}'
    }


def db_get_capitulo(book_number, chapter):
    """
    Devuelve todos los versículos de un capítulo completo con texto limpio.
    Retorna lista vacía si el capítulo no existe.
    """
    conn = get_conn()
    filas = conn.execute(
        '''SELECT b.long_name, b.short_name, v.verse, v.text
           FROM verses v JOIN books b ON v.book_number = b.book_number
           WHERE v.book_number=? AND v.chapter=? ORDER BY v.verse''',
        (book_number, chapter)
    ).fetchall()
    conn.close()
    return [
        {'book_name': f[0], 'short_name': f[1],
         'chapter': chapter, 'verse': f[2],
         'text': limpiar_texto(f[3]),
         'reference': f'{f[1]} {chapter}:{f[2]}'}
        for f in filas
    ]


def db_buscar(query, limite=20):
    """
    Busca versículos que contengan 'query' en su texto usando LIKE.
    Devuelve lista de dicts con texto limpio.
    """
    conn = get_conn()
    conn.execute("PRAGMA case_sensitive_like = OFF")
    filas = conn.execute(
        '''SELECT b.long_name, b.short_name, v.chapter, v.verse, v.text
           FROM verses v JOIN books b ON v.book_number = b.book_number
           WHERE v.text LIKE ?
           ORDER BY v.book_number, v.chapter, v.verse LIMIT ?''',
        (f'%{query}%', limite)
    ).fetchall()
    conn.close()
    return [
        {'book_name': f[0], 'short_name': f[1],
         'chapter': f[2], 'verse': f[3],
         'text': limpiar_texto(f[4]),
         'reference': f'{f[1]} {f[2]}:{f[3]}'}
        for f in filas
    ]


def db_aleatorio():
    """
    Devuelve un versículo elegido al azar de toda la Biblia.
    """
    conn = get_conn()
    ids = conn.execute('SELECT book_number, chapter, verse FROM verses').fetchall()
    conn.close()
    bnum, cap, ver = random.choice(ids)
    return db_get_versiculo(bnum, cap, ver)


# ──────────────────────────────────────────────────────────────
#  VERSIÓN FASTAPI
# ──────────────────────────────────────────────────────────────

def crear_app_fastapi():
    """
    Crea y configura la aplicación FastAPI con todos los endpoints.
    Retorna la instancia de la app lista para ejecutar con uvicorn.
    """
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.responses import JSONResponse

    app = FastAPI(
        title='API Biblia Reina-Valera 1960',
        description='API REST para leer y buscar versículos de la Biblia RV60.',
        version='1.0.0'
    )

    @app.get('/libros', summary='Lista todos los libros')
    def get_libros():
        """Devuelve la lista de los 66 libros de la Biblia."""
        return db_get_libros()

    @app.get('/libros/{book_number}', summary='Info de un libro')
    def get_libro(book_number: int):
        """Devuelve información de un libro por su book_number."""
        libro = db_get_libro(book_number)
        if not libro:
            raise HTTPException(status_code=404, detail='Libro no encontrado')
        return libro

    @app.get('/versiculos/{book_number}/{capitulo}/{versiculo}',
             summary='Un versículo específico')
    def get_versiculo(book_number: int, capitulo: int, versiculo: int):
        """Devuelve un versículo con texto limpio (sin marcas Strong)."""
        v = db_get_versiculo(book_number, capitulo, versiculo)
        if not v:
            raise HTTPException(status_code=404, detail='Versículo no encontrado')
        return v

    @app.get('/capitulo/{book_number}/{capitulo}', summary='Capítulo completo')
    def get_capitulo(book_number: int, capitulo: int):
        """Devuelve todos los versículos de un capítulo."""
        vers = db_get_capitulo(book_number, capitulo)
        if not vers:
            raise HTTPException(status_code=404, detail='Capítulo no encontrado')
        return {'book_number': book_number, 'chapter': capitulo,
                'total_verses': len(vers), 'verses': vers}

    @app.get('/buscar', summary='Buscar en la Biblia')
    def buscar(q: str = Query(..., description='Texto a buscar'),
               limit: int = Query(20, ge=1, le=100)):
        """Busca versículos que contengan el texto indicado."""
        if len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail='La búsqueda debe tener al menos 2 caracteres')
        resultados = db_buscar(q, limite=limit)
        return {'query': q, 'total': len(resultados), 'results': resultados}

    @app.get('/aleatorio', summary='Versículo aleatorio')
    def aleatorio():
        """Devuelve un versículo elegido al azar."""
        return db_aleatorio()

    return app


# ──────────────────────────────────────────────────────────────
#  FALLBACK CON http.server
# ──────────────────────────────────────────────────────────────

def crear_servidor_fallback():
    """
    Servidor HTTP minimal usando la biblioteca estándar http.server.
    Implementa los mismos endpoints que la versión FastAPI.
    """
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class BibliaHandler(BaseHTTPRequestHandler):
        """
        Manejador de peticiones HTTP que implementa los endpoints de la API bíblica
        usando solo la biblioteca estándar de Python.
        """

        def log_message(self, format, *args):
            """Sobrescribe el log para formato más legible."""
            print(f'  [{self.command}] {self.path}  →  {args[1]}')

        def send_json(self, status, data):
            """
            Envía una respuesta JSON con el código de estado indicado.
            Parámetros:
                status -- código HTTP (200, 404, etc.)
                data   -- dict o lista Python a serializar como JSON
            """
            body = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            """
            Maneja peticiones GET enrutando según el path.
            Rutas disponibles:
              /libros
              /libros/{book_number}
              /versiculos/{book_number}/{cap}/{ver}
              /capitulo/{book_number}/{cap}
              /buscar?q=texto
              /aleatorio
            """
            parsed = urlparse(self.path)
            path   = parsed.path.rstrip('/')
            partes = [p for p in path.split('/') if p]

            try:
                # GET /libros
                if partes == ['libros']:
                    self.send_json(200, db_get_libros())

                # GET /libros/{book_number}
                elif len(partes) == 2 and partes[0] == 'libros':
                    libro = db_get_libro(int(partes[1]))
                    if libro:
                        self.send_json(200, libro)
                    else:
                        self.send_json(404, {'error': 'Libro no encontrado'})

                # GET /versiculos/{book_number}/{cap}/{ver}
                elif len(partes) == 4 and partes[0] == 'versiculos':
                    v = db_get_versiculo(int(partes[1]), int(partes[2]), int(partes[3]))
                    if v:
                        self.send_json(200, v)
                    else:
                        self.send_json(404, {'error': 'Versículo no encontrado'})

                # GET /capitulo/{book_number}/{cap}
                elif len(partes) == 3 and partes[0] == 'capitulo':
                    vers = db_get_capitulo(int(partes[1]), int(partes[2]))
                    if vers:
                        self.send_json(200, {
                            'book_number': int(partes[1]),
                            'chapter': int(partes[2]),
                            'total_verses': len(vers),
                            'verses': vers
                        })
                    else:
                        self.send_json(404, {'error': 'Capítulo no encontrado'})

                # GET /buscar?q=texto
                elif len(partes) == 1 and partes[0] == 'buscar':
                    params = parse_qs(parsed.query)
                    q = params.get('q', [''])[0].strip()
                    if len(q) < 2:
                        self.send_json(400, {'error': 'Mínimo 2 caracteres'})
                    else:
                        resultados = db_buscar(q, limite=20)
                        self.send_json(200, {
                            'query': q,
                            'total': len(resultados),
                            'results': resultados
                        })

                # GET /aleatorio
                elif partes == ['aleatorio']:
                    self.send_json(200, db_aleatorio())

                else:
                    self.send_json(404, {
                        'error': 'Ruta no encontrada',
                        'rutas_disponibles': [
                            '/libros',
                            '/libros/{book_number}',
                            '/versiculos/{book_number}/{capitulo}/{versiculo}',
                            '/capitulo/{book_number}/{capitulo}',
                            '/buscar?q=texto',
                            '/aleatorio'
                        ]
                    })

            except (ValueError, IndexError):
                self.send_json(400, {'error': 'Parámetros inválidos'})
            except Exception as e:
                self.send_json(500, {'error': str(e)})

    return HTTPServer(('0.0.0.0', PORT), BibliaHandler)


# ──────────────────────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ──────────────────────────────────────────────────────────────

def main():
    """
    Intenta iniciar con FastAPI + uvicorn.
    Si no están instalados, usa el servidor fallback de http.server.
    """
    print(f'\n{"#" * 60}')
    print('  API REST — BIBLIA REINA-VALERA 1960')
    print(f'{"#" * 60}')

    # Verificar que la BD existe antes de arrancar
    ruta_bd = os.path.abspath(DB_PATH)
    if not os.path.exists(ruta_bd):
        print(f'\n[ERROR] Base de datos no encontrada en:\n  {ruta_bd}')
        return

    try:
        import uvicorn
        import fastapi  # noqa: F401

        print('\n  Usando FastAPI + uvicorn')
        print(f'  Servidor en: http://localhost:{PORT}')
        print(f'  Documentación: http://localhost:{PORT}/docs')
        print('\n  Endpoints disponibles:')
        print(f'    GET http://localhost:{PORT}/libros')
        print(f'    GET http://localhost:{PORT}/libros/430')
        print(f'    GET http://localhost:{PORT}/versiculos/430/3/16')
        print(f'    GET http://localhost:{PORT}/capitulo/430/3')
        print(f'    GET http://localhost:{PORT}/buscar?q=amor')
        print(f'    GET http://localhost:{PORT}/aleatorio')
        print('\n  Presiona Ctrl+C para detener.\n')

        app = crear_app_fastapi()
        uvicorn.run(app, host='0.0.0.0', port=PORT, log_level='warning')

    except ImportError:
        print('\n  FastAPI o uvicorn no están instalados.')
        print('  Para instalarlos: pip install fastapi uvicorn')
        print('\n  Usando servidor fallback (http.server)...')
        print(f'  Servidor en: http://localhost:{PORT}')
        print('\n  Endpoints disponibles:')
        print(f'    GET http://localhost:{PORT}/libros')
        print(f'    GET http://localhost:{PORT}/libros/430')
        print(f'    GET http://localhost:{PORT}/versiculos/430/3/16')
        print(f'    GET http://localhost:{PORT}/capitulo/430/3')
        print(f'    GET http://localhost:{PORT}/buscar?q=amor')
        print(f'    GET http://localhost:{PORT}/aleatorio')
        print('\n  Presiona Ctrl+C para detener.\n')

        servidor = crear_servidor_fallback()
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print('\n\n  Servidor detenido.\n')


if __name__ == '__main__':
    main()
