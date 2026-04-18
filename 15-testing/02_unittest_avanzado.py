"""
Capítulo 15 — Testing
Archivo: 02_unittest_avanzado.py

unittest.mock — mocking de dependencias externas.

¿Por qué hacer mock?
    Los tests deben ser:
    - RÁPIDOS (no depender de red, BD, sistema de archivos lentos)
    - DETERMINISTAS (mismo resultado siempre, sin datos variables)
    - AISLADOS (un test no afecta a otro)

    Cuando tu código llama a una API externa, base de datos, o
    servicio de terceros, no puedes controlarlo en los tests.
    Los mocks reemplazan esas dependencias con objetos falsos
    que tú controlas.

Cómo ejecutar:
    python 02_unittest_avanzado.py
    python -m unittest 02_unittest_avanzado.py -v
"""

import unittest
from unittest.mock import (
    MagicMock,    # Mock con comportamiento mágico pre-configurado
    patch,        # Context manager/decorador para reemplazar objetos
    call,         # Para verificar llamadas específicas
    ANY,          # Comodín para assertions: "cualquier valor"
    PropertyMock, # Para mockear propiedades (@property)
)
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calculadora


# ==============================================================
# MÓDULOS A MOCKEAR — código con dependencias externas
# ==============================================================

class ServicioClima:
    """
    Servicio que llama a una API externa de clima.
    En los tests NO queremos hacer llamadas reales a internet.
    Mockearemos este servicio para que devuelva datos controlados.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.clima-ejemplo.com"

    def obtener_temperatura(self, ciudad: str) -> float:
        """
        Hace una petición HTTP a la API de clima.
        En tests reales: se mockea para no necesitar conexión.
        """
        import urllib.request
        url = f"{self.base_url}/temperatura?ciudad={ciudad}&key={self.api_key}"
        with urllib.request.urlopen(url) as response:
            datos = json.loads(response.read())
        return datos["temperatura"]

    def obtener_pronostico(self, ciudad: str, dias: int = 3) -> list[dict]:
        """Devuelve el pronóstico para los próximos N días."""
        import urllib.request
        url = f"{self.base_url}/pronostico?ciudad={ciudad}&dias={dias}"
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())


class RepositorioUsuarios:
    """
    Repositorio que interactúa con una base de datos.
    En tests NO queremos modificar datos reales.
    """

    def __init__(self, conexion):
        """
        conexion: objeto de conexión a BD (SQLite, PostgreSQL, etc.)
        En tests, 'conexion' será un MagicMock.
        """
        self.conexion = conexion

    def buscar_por_id(self, user_id: int) -> dict | None:
        """Consulta un usuario por ID."""
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        return cursor.fetchone()

    def guardar(self, usuario: dict) -> bool:
        """Guarda un usuario en la base de datos."""
        cursor = self.conexion.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, email) VALUES (?, ?)",
            (usuario["nombre"], usuario["email"])
        )
        self.conexion.commit()
        return True

    def contar_usuarios(self) -> int:
        """Cuenta el total de usuarios."""
        cursor = self.conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        resultado = cursor.fetchone()
        return resultado[0]


class ServicioNotificaciones:
    """
    Servicio de envío de emails/SMS.
    En tests NO queremos enviar emails reales.
    """

    def enviar_email(self, destinatario: str, asunto: str, cuerpo: str) -> bool:
        """
        Envía un email real (en producción).
        En tests, mockearemos este método.
        """
        # Simulamos el envío (en producción llamaría a smtplib, SendGrid, etc.)
        print(f"  [EMAIL REAL] Para: {destinatario}, Asunto: {asunto}")
        return True

    def enviar_sms(self, telefono: str, mensaje: str) -> bool:
        print(f"  [SMS REAL] Para: {telefono}: {mensaje}")
        return True


class ProcesadorPedidos:
    """
    Clase que usa múltiples servicios externos.
    Para testearla, mockearemos todos sus servicios.
    """

    def __init__(self, repo_usuarios, notificaciones, calcs=None):
        self.repo = repo_usuarios
        self.notif = notificaciones
        # calcs permite inyectar el módulo calculadora para testing
        self.calc = calcs or calculadora

    def procesar_compra(self, user_id: int, items: list[dict]) -> dict:
        """
        Procesa una compra:
        1. Busca el usuario
        2. Calcula el total
        3. Envía confirmación por email
        """
        usuario = self.repo.buscar_por_id(user_id)
        if usuario is None:
            raise ValueError(f"Usuario {user_id} no encontrado")

        total = sum(
            self.calc.multiplicar(item["precio"], item["cantidad"])
            for item in items
        )

        enviado = self.notif.enviar_email(
            destinatario=usuario["email"],
            asunto="Confirmación de compra",
            cuerpo=f"Total: ${total}"
        )

        return {
            "usuario": usuario["nombre"],
            "total": total,
            "email_enviado": enviado
        }


# ==============================================================
# TESTS CON MOCKING
# ==============================================================

class TestMagicMock(unittest.TestCase):
    """Tests básicos con MagicMock."""

    def test_magic_mock_basico(self):
        """
        MagicMock crea un objeto falso que acepta cualquier llamada
        y devuelve otro MagicMock por defecto.
        """
        mock = MagicMock()

        # Podemos llamarlo como función
        mock(1, 2, 3)
        mock.llamar_con(nombre="test")

        # Verificar que fue llamado
        mock.assert_called()

        # Verificar la última llamada
        mock.assert_called_with(1, 2, 3)

    def test_configurar_valor_de_retorno(self):
        """
        return_value configura qué devuelve el mock cuando es llamado.
        """
        mock_funcion = MagicMock(return_value=42)

        resultado = mock_funcion("cualquier argumento")
        self.assertEqual(resultado, 42)

        resultado2 = mock_funcion()
        self.assertEqual(resultado2, 42)

    def test_configurar_side_effect_excepcion(self):
        """
        side_effect permite que el mock lance una excepción.
        Útil para testear cómo tu código maneja errores de APIs.
        """
        mock = MagicMock()
        mock.side_effect = ConnectionError("Sin conexión a internet")

        with self.assertRaises(ConnectionError):
            mock()

    def test_configurar_side_effect_secuencia(self):
        """
        Si side_effect es una lista, el mock devuelve cada elemento
        en orden en llamadas sucesivas.
        """
        mock = MagicMock()
        mock.side_effect = [10, 20, 30, StopIteration]

        self.assertEqual(mock(), 10)
        self.assertEqual(mock(), 20)
        self.assertEqual(mock(), 30)
        with self.assertRaises(StopIteration):
            mock()

    def test_verificar_numero_de_llamadas(self):
        """Verificar cuántas veces fue llamado un mock."""
        mock = MagicMock()

        mock("a")
        mock("b")
        mock("c")

        self.assertEqual(mock.call_count, 3)

        # call_args_list guarda el historial de todas las llamadas
        self.assertEqual(mock.call_args_list, [
            call("a"),
            call("b"),
            call("c"),
        ])


class TestPatch(unittest.TestCase):
    """
    patch() reemplaza temporalmente un objeto por un Mock.
    Al salir del bloque with (o al terminar el test decorado),
    el objeto ORIGINAL es restaurado automáticamente.

    patch(target): target es la ruta completa al objeto a mockear
    en formato 'modulo.Clase.metodo' o 'modulo.funcion'
    """

    def test_mockear_servicio_clima_con_patch(self):
        """
        Mockeamos ServicioClima.obtener_temperatura para que no
        haga llamadas HTTP reales durante el test.
        """
        servicio = ServicioClima("mi-api-key")

        # patch como context manager
        with patch.object(servicio, "obtener_temperatura", return_value=22.5):
            temp = servicio.obtener_temperatura("Madrid")
            self.assertEqual(temp, 22.5)

        # Fuera del bloque with, el método original está restaurado
        # (pero no lo llamamos porque haría HTTP real)

    def test_mockear_metodo_en_clase_completa(self):
        """
        Cuando usas patch.object con la CLASE (no la instancia),
        todas las instancias tienen el método mockeado.
        """
        with patch.object(ServicioClima, "obtener_temperatura", return_value=15.0):
            servicio1 = ServicioClima("key1")
            servicio2 = ServicioClima("key2")
            # Ambas instancias usan el mock
            self.assertEqual(servicio1.obtener_temperatura("Lima"), 15.0)
            self.assertEqual(servicio2.obtener_temperatura("Paris"), 15.0)


class TestRepositorioConMock(unittest.TestCase):
    """
    Tests del repositorio usando una conexión a BD mockeada.
    No necesitamos una BD real para estos tests.
    """

    def setUp(self):
        """Crea una conexión de BD mockeada para cada test."""
        # MagicMock simula la conexión a la base de datos
        self.mock_conexion = MagicMock()
        self.repo = RepositorioUsuarios(self.mock_conexion)

    def test_buscar_usuario_existente(self):
        """
        Configuramos el mock para simular un usuario en la BD.
        El cursor mockeado devuelve datos controlados.
        """
        # Configuramos la cadena de llamadas:
        # conexion.cursor() → cursor_mock
        # cursor_mock.execute(...) → nada
        # cursor_mock.fetchone() → datos del usuario
        mock_cursor = self.mock_conexion.cursor.return_value
        mock_cursor.fetchone.return_value = {
            "id": 1,
            "nombre": "Ana García",
            "email": "ana@ejemplo.com"
        }

        resultado = self.repo.buscar_por_id(1)

        # Verificamos que se llamó a execute con los parámetros correctos
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM usuarios WHERE id = ?",
            (1,)
        )

        # Verificamos el resultado
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["nombre"], "Ana García")

    def test_buscar_usuario_no_existente(self):
        """Cuando el usuario no existe, fetchone devuelve None."""
        mock_cursor = self.mock_conexion.cursor.return_value
        mock_cursor.fetchone.return_value = None

        resultado = self.repo.buscar_por_id(999)
        self.assertIsNone(resultado)

    def test_guardar_usuario(self):
        """Verifica que guardar llama a execute y commit."""
        usuario = {"nombre": "Luis", "email": "luis@ejemplo.com"}

        resultado = self.repo.guardar(usuario)

        # Verificamos que se hizo commit (la transacción se confirmó)
        self.mock_conexion.commit.assert_called_once()
        self.assertTrue(resultado)

    def test_contar_usuarios(self):
        """Verifica el conteo de usuarios."""
        mock_cursor = self.mock_conexion.cursor.return_value
        mock_cursor.fetchone.return_value = (42,)  # 42 usuarios en la BD

        total = self.repo.contar_usuarios()
        self.assertEqual(total, 42)


class TestProcesadorPedidos(unittest.TestCase):
    """
    Tests de integración del procesador de pedidos.
    Mockeamos TODAS las dependencias externas para testear
    solo la lógica del procesador.
    """

    def setUp(self):
        """Preparamos los mocks de todas las dependencias."""
        self.mock_repo = MagicMock()
        self.mock_notif = MagicMock()
        self.procesador = ProcesadorPedidos(
            self.mock_repo,
            self.mock_notif,
        )

    def test_procesar_compra_exitosa(self):
        """Test del flujo exitoso de procesamiento de compra."""
        # Configuramos: el usuario existe en la BD mockeada
        self.mock_repo.buscar_por_id.return_value = {
            "id": 1,
            "nombre": "María",
            "email": "maria@ejemplo.com"
        }
        # El servicio de email devuelve True (éxito)
        self.mock_notif.enviar_email.return_value = True

        items = [
            {"precio": 10.0, "cantidad": 2},   # 20.0
            {"precio": 5.0,  "cantidad": 3},   # 15.0
        ]

        resultado = self.procesador.procesar_compra(user_id=1, items=items)

        # Verificamos el resultado
        self.assertEqual(resultado["usuario"], "María")
        self.assertEqual(resultado["total"], 35.0)
        self.assertTrue(resultado["email_enviado"])

        # Verificamos que se llamaron los servicios correctamente
        self.mock_repo.buscar_por_id.assert_called_once_with(1)
        self.mock_notif.enviar_email.assert_called_once_with(
            destinatario="maria@ejemplo.com",
            asunto="Confirmación de compra",
            cuerpo="Total: $35.0"
        )

    def test_procesar_compra_usuario_no_encontrado(self):
        """Si el usuario no existe, debe lanzar ValueError."""
        self.mock_repo.buscar_por_id.return_value = None

        with self.assertRaises(ValueError) as ctx:
            self.procesador.procesar_compra(user_id=999, items=[])

        self.assertIn("999", str(ctx.exception))

        # Verificamos que NO se intentó enviar email
        self.mock_notif.enviar_email.assert_not_called()

    def test_procesar_compra_falla_email(self):
        """Si el email falla, el resultado refleja el error."""
        self.mock_repo.buscar_por_id.return_value = {
            "id": 2, "nombre": "Carlos", "email": "carlos@ejemplo.com"
        }
        # Simulamos fallo en el envío de email
        self.mock_notif.enviar_email.return_value = False

        items = [{"precio": 20.0, "cantidad": 1}]
        resultado = self.procesador.procesar_compra(user_id=2, items=items)

        self.assertFalse(resultado["email_enviado"])


class TestNotificacionesConPatch(unittest.TestCase):
    """
    Uso de @patch como decorador de test.
    El mock se pasa como parámetro al método de test.
    """

    @patch.object(ServicioNotificaciones, "enviar_email", return_value=True)
    def test_enviar_email_mockeado(self, mock_enviar):
        """
        @patch como decorador inyecta el mock como argumento.
        El nombre del parámetro es convención: mock_<nombre>.
        """
        notif = ServicioNotificaciones()
        resultado = notif.enviar_email("test@test.com", "Asunto", "Cuerpo")

        self.assertTrue(resultado)
        mock_enviar.assert_called_once()

    @patch.object(ServicioNotificaciones, "enviar_sms")
    @patch.object(ServicioNotificaciones, "enviar_email")
    def test_multiples_patch(self, mock_email, mock_sms):
        """
        Múltiples @patch: se pasan en orden INVERSO a la declaración.
        El más cercano al método es el primero en los parámetros.
        """
        mock_email.return_value = True
        mock_sms.return_value = True

        notif = ServicioNotificaciones()
        email_ok = notif.enviar_email("a@b.com", "tema", "texto")
        sms_ok = notif.enviar_sms("+34600000000", "mensaje")

        self.assertTrue(email_ok)
        self.assertTrue(sms_ok)

        # ANY verifica que fue llamado con algún argumento (sin importar cuál)
        mock_email.assert_called_once_with("a@b.com", "tema", "texto")
        mock_sms.assert_called_with(ANY, ANY)


# ==============================================================
# PUNTO DE ENTRADA
# ==============================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
