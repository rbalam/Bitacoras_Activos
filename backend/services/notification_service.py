import os
import asyncio
import logging
import resend
from twilio.rest import Client
from typing import Optional

logger = logging.getLogger(__name__)

resend.api_key = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")

twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
twilio_whatsapp_from = os.environ.get("TWILIO_WHATSAPP_FROM", "")

twilio_client = None
if twilio_account_sid and twilio_auth_token:
    try:
        twilio_client = Client(twilio_account_sid, twilio_auth_token)
    except Exception as e:
        logger.warning(f"No se pudo inicializar Twilio: {e}")

async def send_email(recipient_email: str, subject: str, html_content: str) -> bool:
    """Enviar email usando Resend"""
    if not resend.api_key or resend.api_key == "":
        logger.warning("RESEND_API_KEY no configurada, saltando envío de email")
        return False
    
    try:
        params = {
            "from": SENDER_EMAIL,
            "to": [recipient_email],
            "subject": subject,
            "html": html_content
        }
        
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email enviado a {recipient_email} - ID: {email.get('id')}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar email: {str(e)}")
        return False

async def send_whatsapp(phone_number: str, message: str) -> bool:
    """Enviar mensaje de WhatsApp usando Twilio"""
    if not twilio_client or not twilio_whatsapp_from:
        logger.warning("Twilio no configurado, saltando envío de WhatsApp")
        return False
    
    try:
        # Asegurar formato correcto del número
        if not phone_number.startswith("whatsapp:"):
            phone_number = f"whatsapp:{phone_number}"
        
        message_obj = await asyncio.to_thread(
            twilio_client.messages.create,
            body=message,
            from_=twilio_whatsapp_from,
            to=phone_number
        )
        logger.info(f"WhatsApp enviado a {phone_number} - SID: {message_obj.sid}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar WhatsApp: {str(e)}")
        return False

async def send_alert_notification(alert_type: str, recipient_email: str, recipient_phone: Optional[str], alert_data: dict) -> dict:
    """Enviar notificación de alerta por email y WhatsApp"""
    results = {"email": False, "whatsapp": False}
    
    # Construir contenido
    subject = f"AssetGuard Pro - {alert_data.get('titulo', 'Alerta')} "
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #0F172A;">{alert_data.get('titulo', 'Alerta')}</h2>
            <p><strong>Prioridad:</strong> {alert_data.get('prioridad', 'Media').upper()}</p>
            <p><strong>Mensaje:</strong></p>
            <p>{alert_data.get('mensaje', '')}</p>
            <hr style="margin: 20px 0;">
            <p style="color: #64748B; font-size: 12px;">Este es un mensaje automático de AssetGuard Pro</p>
        </body>
    </html>
    """
    
    whatsapp_message = f"*AssetGuard Pro - {alert_data.get('titulo', 'Alerta')}*\n\n{alert_data.get('mensaje', '')}\n\nPrioridad: {alert_data.get('prioridad', 'Media').upper()}"
    
    # Enviar email
    results["email"] = await send_email(recipient_email, subject, html_content)
    
    # Enviar WhatsApp si hay número
    if recipient_phone:
        results["whatsapp"] = await send_whatsapp(recipient_phone, whatsapp_message)
    
    return results
