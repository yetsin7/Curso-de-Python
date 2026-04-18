# =============================================================================
# 03_enviar_emails.py — Enviar emails con Python (smtplib)
# =============================================================================
# Python puede enviar emails directamente sin depender de servicios externos,
# usando smtplib (incluido con Python) y el protocolo SMTP.
#
# Módulos (todos incluidos con Python):
#   smtplib        — cliente SMTP para enviar emails
#   email.mime     — construir emails con texto, HTML y adjuntos
#   ssl            — conexión segura TLS/SSL
#   os             — leer credenciales desde variables de entorno
#
# Instalación opcional:
#   pip install python-dotenv   — para cargar variables desde archivo .env
#
# IMPORTANTE ANTES DE USAR:
#   1. Nunca hardcodees contraseñas en el código.
#   2. Para Gmail: activa la verificación en 2 pasos y crea una
#      "Contraseña de aplicación" en:
#      https://myaccount.google.com/apppasswords
#   3. Configura las variables de entorno:
#      Windows:  set EMAIL_ADDRESS=tu@gmail.com
#                set EMAIL_PASSWORD=tu_contraseña_de_app
#      Linux/Mac: export EMAIL_ADDRESS=tu@gmail.com
#                 export EMAIL_PASSWORD=tu_contraseña_de_app
# =============================================================================

import smtplib
import ssl
import os
import tempfile
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Intentar cargar python-dotenv si está disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


# =============================================================================
# CONFIGURACIÓN SMTP — Ajusta según tu proveedor de email
# =============================================================================

# Servidores SMTP de los proveedores más comunes
SMTP_CONFIGS = {
    "gmail": {
        "host": "smtp.gmail.com",
        "port": 587,
        "description": "Gmail — requiere Contraseña de Aplicación"
    },
    "outlook": {
        "host": "smtp.office365.com",
        "port": 587,
        "description": "Outlook / Hotmail / Microsoft 365"
    },
    "yahoo": {
        "host": "smtp.mail.yahoo.com",
        "port": 587,
        "description": "Yahoo Mail"
    },
}

# Las credenciales se leen SIEMPRE desde variables de entorno
# Nunca se hardcodean en el código fuente
EMAIL_ADDRESS  = os.environ.get("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
SMTP_HOST      = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT      = int(os.environ.get("SMTP_PORT", "587"))


# =============================================================================
# CONSTRUCCIÓN DE EMAILS
# =============================================================================

def create_simple_text_email(from_addr, to_addr, subject, body):
    """
    Crea un email de solo texto plano.

    El texto plano es el formato más compatible: funciona en todos
    los clientes de correo, incluso los más antiguos o en terminales.

    Parámetros:
        from_addr (str): dirección del remitente
        to_addr (str): dirección del destinatario (o lista de direcciones)
        subject (str): asunto del email
        body (str): cuerpo del email en texto plano

    Retorna:
        MIMEText: objeto de email listo para enviar
    """
    # MIMEText con subtype "plain" crea un email de texto simple
    message = MIMEText(body, "plain", "utf-8")
    message["From"]    = from_addr
    message["To"]      = to_addr if isinstance(to_addr, str) else ", ".join(to_addr)
    message["Subject"] = subject
    message["Date"]    = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    return message


def create_html_email(from_addr, to_addr, subject, text_body, html_body):
    """
    Crea un email con contenido HTML y fallback de texto plano.

    Los emails HTML permiten formato rico: colores, fuentes, tablas, imágenes.
    Siempre se incluye la versión de texto como fallback para clientes
    que no soporten HTML (lectores de pantalla, terminales, etc.).

    Parámetros:
        from_addr (str): dirección del remitente
        to_addr (str): dirección del destinatario
        subject (str): asunto del email
        text_body (str): versión texto plano (fallback)
        html_body (str): versión HTML con formato

    Retorna:
        MIMEMultipart: objeto de email multipart listo para enviar
    """
    # MIMEMultipart("alternative") indica que hay múltiples versiones del mismo contenido
    message = MIMEMultipart("alternative")
    message["From"]    = from_addr
    message["To"]      = to_addr
    message["Subject"] = subject

    # El orden importa: el cliente usa la última versión que entiende
    # Por convención: texto primero, HTML después
    part_text = MIMEText(text_body, "plain", "utf-8")
    part_html = MIMEText(html_body, "html",  "utf-8")

    message.attach(part_text)
    message.attach(part_html)

    return message


def create_email_with_attachment(from_addr, to_addr, subject, body, attachment_paths):
    """
    Crea un email con archivos adjuntos.

    MIMEMultipart("mixed") permite combinar texto con archivos adjuntos.
    Los adjuntos se codifican en Base64 para transmitirse como texto ASCII.

    Parámetros:
        from_addr (str): dirección del remitente
        to_addr (str): dirección del destinatario
        subject (str): asunto del email
        body (str): cuerpo del email (texto plano)
        attachment_paths (list): lista de rutas de archivos a adjuntar

    Retorna:
        MIMEMultipart: objeto de email con adjuntos
    """
    # MIMEMultipart("mixed") para combinar cuerpo + adjuntos
    message = MIMEMultipart("mixed")
    message["From"]    = from_addr
    message["To"]      = to_addr
    message["Subject"] = subject

    # Añadir el cuerpo del email como texto
    message.attach(MIMEText(body, "plain", "utf-8"))

    # Adjuntar cada archivo
    for file_path in attachment_paths:
        file_path = Path(file_path)

        if not file_path.exists():
            print(f"  Advertencia: archivo no encontrado: {file_path}")
            continue

        # Leer el archivo en modo binario
        with open(file_path, "rb") as attachment:
            # MIMEBase es la clase genérica para cualquier tipo de archivo
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Codificar en Base64 para transmisión como texto
        encoders.encode_base64(part)

        # Añadir header Content-Disposition con el nombre del archivo
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={file_path.name}"
        )

        message.attach(part)
        print(f"  Adjunto añadido: {file_path.name} ({file_path.stat().st_size} bytes)")

    return message


# =============================================================================
# ENVÍO DE EMAILS
# =============================================================================

def send_email(message, from_addr, to_addrs, smtp_host, smtp_port, password):
    """
    Envía un email usando SMTP con TLS (STARTTLS).

    STARTTLS inicia la conexión sin cifrar y luego la actualiza a TLS seguro.
    Es el método estándar en el puerto 587.
    (Diferente de SSL/SMTPS que usa el puerto 465 y cifra desde el inicio)

    Parámetros:
        message: objeto email MIME ya construido
        from_addr (str): dirección del remitente (para SMTP AUTH)
        to_addrs (str | list): destinatario(s)
        smtp_host (str): servidor SMTP
        smtp_port (int): puerto SMTP (generalmente 587 para TLS)
        password (str): contraseña de la cuenta o contraseña de app

    Retorna:
        bool: True si se envió correctamente, False si hubo error
    """
    # Contexto SSL seguro con verificación de certificados
    context = ssl.create_default_context()

    if isinstance(to_addrs, str):
        to_addrs = [to_addrs]

    try:
        # Conectar al servidor SMTP
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:

            # Enviar saludo EHLO (Extended Hello) al servidor
            server.ehlo()

            # Actualizar la conexión a TLS seguro
            server.starttls(context=context)

            # Autenticarse con las credenciales
            server.login(from_addr, password)

            # Enviar el email
            server.sendmail(from_addr, to_addrs, message.as_string())

        print(f"  Email enviado exitosamente a: {', '.join(to_addrs)}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("  Error: Credenciales incorrectas.")
        print("  Para Gmail, usa una Contraseña de Aplicación (no tu contraseña normal).")
        print("  Generarla en: https://myaccount.google.com/apppasswords")
        return False

    except smtplib.SMTPRecipientsRefused as e:
        print(f"  Error: Destinatario rechazado: {e}")
        return False

    except smtplib.SMTPConnectError:
        print(f"  Error: No se pudo conectar a {smtp_host}:{smtp_port}")
        return False

    except smtplib.SMTPException as e:
        print(f"  Error SMTP: {e}")
        return False

    except Exception as e:
        print(f"  Error inesperado: {e}")
        return False


# =============================================================================
# PLANTILLAS DE EMAIL HTML
# =============================================================================

def get_report_html(report_data):
    """
    Genera el HTML de un email de reporte con tabla de datos.

    Parámetros:
        report_data (list[dict]): datos para mostrar en la tabla

    Retorna:
        str: HTML del email formateado
    """
    # Construir filas de la tabla
    table_rows = ""
    for i, row in enumerate(report_data):
        bg_color = "#f0f4f8" if i % 2 == 0 else "#ffffff"
        table_rows += f"""
            <tr style="background-color: {bg_color};">
                <td style="padding: 8px 12px;">{row.get('vendedor', '')}</td>
                <td style="padding: 8px 12px; text-align: center;">{row.get('ventas', '')}</td>
                <td style="padding: 8px 12px; text-align: right;">${row.get('total', '')}</td>
            </tr>
        """

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; }}
            .header {{ background-color: #2E4057; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
            .content {{ background-color: #fff; padding: 20px; border: 1px solid #ddd; }}
            .footer {{ background-color: #f5f5f5; padding: 12px; text-align: center;
                       font-size: 12px; color: #999; border-radius: 0 0 8px 8px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
            th {{ background-color: #2E4057; color: white; padding: 10px 12px; text-align: left; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2 style="margin:0;">Reporte de Ventas Mensual</h2>
                <p style="margin:4px 0 0;">Generado automáticamente por Python</p>
            </div>
            <div class="content">
                <p>Hola,</p>
                <p>Adjunto encontrarás el reporte de ventas del período actual.</p>
                <table>
                    <thead>
                        <tr>
                            <th>Vendedor</th>
                            <th>Num. Ventas</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                <p>Este email fue enviado automáticamente. No responder a este mensaje.</p>
            </div>
            <div class="footer">
                Generado el {fecha} · Sistema de Reportes Automáticos
            </div>
        </div>
    </body>
    </html>
    """


# =============================================================================
# DEMOSTRACIÓN (SIN ENVIAR REALMENTE)
# =============================================================================

def demo_construir_emails():
    """
    Construye y muestra los emails sin enviarlos realmente.

    Si las variables de entorno no están configuradas, solo muestra
    la estructura de los emails para fines educativos.
    """
    print("\n--- Construyendo emails (modo demo) ---")

    from_addr = EMAIL_ADDRESS or "remitente@example.com"
    to_addr   = "destinatario@example.com"

    # 1. Email de texto simple
    msg_text = create_simple_text_email(
        from_addr=from_addr,
        to_addr=to_addr,
        subject="Prueba de email automático",
        body=(
            "Hola,\n\n"
            "Este es un email enviado automáticamente con Python usando smtplib.\n\n"
            "Características:\n"
            "  - Texto plano, compatible con todos los clientes\n"
            "  - Enviado con SMTP + TLS\n"
            "  - Credenciales desde variables de entorno\n\n"
            "Saludos,\n"
            "El sistema automático"
        )
    )
    print(f"\n  Email de texto:")
    print(f"    From: {msg_text['From']}")
    print(f"    To:   {msg_text['To']}")
    print(f"    Subject: {msg_text['Subject']}")
    print(f"    Tamaño del mensaje: {len(msg_text.as_string())} bytes")

    # 2. Email HTML
    report_data = [
        {"vendedor": "Ana García",  "ventas": 5, "total": "4,299.94"},
        {"vendedor": "Carlos López","ventas": 4, "total": "3,399.97"},
        {"vendedor": "María Torres","ventas": 4, "total": "5,398.94"},
    ]
    html_body = get_report_html(report_data)
    text_body = "Reporte de ventas mensual. Ver versión HTML para tabla completa."

    msg_html = create_html_email(
        from_addr=from_addr,
        to_addr=to_addr,
        subject="[Automático] Reporte de Ventas Mensual",
        text_body=text_body,
        html_body=html_body,
    )
    print(f"\n  Email HTML:")
    print(f"    Subject: {msg_html['Subject']}")
    print(f"    Partes: {len(msg_html.get_payload())}")
    print(f"    Tamaño HTML: {len(html_body)} chars")

    # 3. Email con adjunto (usando un archivo temporal)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write("vendedor,total\nAna,4299.94\nCarlos,3399.97\n")
        tmp_path = tmp.name

    msg_adjunto = create_email_with_attachment(
        from_addr=from_addr,
        to_addr=to_addr,
        subject="Reporte con adjunto",
        body="Adjunto encontrarás el reporte en CSV.",
        attachment_paths=[tmp_path],
    )
    print(f"\n  Email con adjunto:")
    print(f"    Subject: {msg_adjunto['Subject']}")
    print(f"    Partes MIME: {len(msg_adjunto.get_payload())}")

    # Limpiar archivo temporal
    os.unlink(tmp_path)

    return msg_text, msg_html, msg_adjunto


def check_credentials():
    """
    Verifica si las credenciales están configuradas en las variables de entorno.

    Retorna:
        bool: True si las credenciales están disponibles
    """
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("\n--- Credenciales no configuradas ---")
        print("  Para enviar emails reales, configura:")
        print()
        print("  Windows (PowerShell):")
        print('    $env:EMAIL_ADDRESS = "tu@gmail.com"')
        print('    $env:EMAIL_PASSWORD = "tu_contraseña_de_app"')
        print()
        print("  Linux / macOS:")
        print('    export EMAIL_ADDRESS="tu@gmail.com"')
        print('    export EMAIL_PASSWORD="tu_contraseña_de_app"')
        print()
        print("  Con archivo .env (pip install python-dotenv):")
        print("    Crea un archivo .env:")
        print("      EMAIL_ADDRESS=tu@gmail.com")
        print("      EMAIL_PASSWORD=tu_contraseña_de_app")
        print()

        if not DOTENV_AVAILABLE:
            print("  Para usar .env instala: pip install python-dotenv")

        return False

    print(f"  Email configurado: {EMAIL_ADDRESS}")
    print(f"  Servidor SMTP: {SMTP_HOST}:{SMTP_PORT}")
    return True


def send_real_email_example():
    """
    Ejemplo de envío real de email si las credenciales están disponibles.
    Solo se ejecuta si EMAIL_ADDRESS y EMAIL_PASSWORD están configurados.
    """
    if not check_credentials():
        return

    print("\n--- Enviando email real ---")

    # Email de prueba simple
    message = create_simple_text_email(
        from_addr=EMAIL_ADDRESS,
        to_addr=EMAIL_ADDRESS,   # enviamos a nosotros mismos como prueba
        subject="[Test] Email automático desde Python",
        body=(
            f"Email de prueba enviado con Python smtplib.\n"
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            "Si recibes este email, la configuración funciona correctamente."
        )
    )

    send_email(
        message=message,
        from_addr=EMAIL_ADDRESS,
        to_addrs=EMAIL_ADDRESS,
        smtp_host=SMTP_HOST,
        smtp_port=SMTP_PORT,
        password=EMAIL_PASSWORD,
    )


# =============================================================================
# INFORMACIÓN SOBRE CONFIGURACIÓN
# =============================================================================

def show_smtp_providers():
    """Muestra información sobre los proveedores SMTP disponibles."""
    print("\n--- Proveedores SMTP configurables ---")
    for name, config in SMTP_CONFIGS.items():
        print(f"\n  {name.upper()}:")
        print(f"    Host: {config['host']}")
        print(f"    Puerto TLS: {config['port']}")
        print(f"    Nota: {config['description']}")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal del módulo de envío de emails."""

    print("=" * 60)
    print("  DEMO: Enviar Emails con Python (smtplib)")
    print("=" * 60)

    show_smtp_providers()

    print("\n" + "=" * 60)
    print("  Construyendo emails (no se envían — solo demo)")
    print("=" * 60)

    demo_construir_emails()

    print("\n" + "=" * 60)
    print("  Verificar credenciales para envío real")
    print("=" * 60)

    # Intentar envío real solo si hay credenciales configuradas
    send_real_email_example()

    print("\n" + "=" * 60)
    print("  Demo completado.")
    print("=" * 60)


if __name__ == "__main__":
    main()
