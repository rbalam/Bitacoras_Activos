import asyncio
import logging
import resend
from twilio.rest import Client
from typing import Optional

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, config_service):
        self.config_service = config_service
        self._twilio_client = None
    
    async def _get_twilio_client(self):
        """Get or create Twilio client with current config"""
        config = await self.config_service.get_twilio_config()
        account_sid = config.get("account_sid")
        auth_token = config.get("auth_token")
        
        if not account_sid or not auth_token:
            return None
        
        try:
            return Client(account_sid, auth_token)
        except Exception as e:
            logger.error(f"Error al crear cliente Twilio: {e}")
            return None
    
    async def send_email(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """Enviar email usando Resend"""
        config = await self.config_service.get_resend_config()
        api_key = config.get("api_key")
        sender_email = config.get("sender_email") or "onboarding@resend.dev"
        
        if not api_key or api_key == "":
            logger.warning("RESEND_API_KEY no configurada, saltando envío de email")
            return False
        
        try:
            # Set API key dynamically
            resend.api_key = api_key
            
            params = {
                "from": sender_email,
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

    async def send_whatsapp(self, phone_number: str, message: str) -> bool:
        """Enviar mensaje de WhatsApp usando Twilio"""
        twilio_client = await self._get_twilio_client()
        config = await self.config_service.get_twilio_config()
        whatsapp_from = config.get("whatsapp_from")
        
        if not twilio_client or not whatsapp_from:
            logger.warning("Twilio no configurado, saltando envío de WhatsApp")
            return False
        
        try:
            # Asegurar formato correcto del número
            if not phone_number.startswith("whatsapp:"):
                phone_number = f"whatsapp:{phone_number}"
            
            if not whatsapp_from.startswith("whatsapp:"):
                whatsapp_from = f"whatsapp:{whatsapp_from}"
            
            message_obj = await asyncio.to_thread(
                twilio_client.messages.create,
                body=message,
                from_=whatsapp_from,
                to=phone_number
            )
            logger.info(f"WhatsApp enviado a {phone_number} - SID: {message_obj.sid}")
            return True
        except Exception as e:
            logger.error(f"Error al enviar WhatsApp: {str(e)}")
            return False

    async def send_alert_notification(self, alert_type: str, recipient_email: str, recipient_phone: Optional[str], alert_data: dict) -> dict:
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
        results["email"] = await self.send_email(recipient_email, subject, html_content)
        
        # Enviar WhatsApp si hay número
        if recipient_phone:
            results["whatsapp"] = await self.send_whatsapp(recipient_phone, whatsapp_message)
        
        return results
