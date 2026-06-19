import logging
import requests
from src.app.core.settings import settings

logger = logging.getLogger("lead-engine.whatsapp-service")


class WhatsAppService:
    def __init__(self):
        if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_ID:
            raise RuntimeError("WHATSAPP_TOKEN or WHATSAPP_PHONE_ID is not configured.")
        self.token = settings.WHATSAPP_TOKEN
        self.phone_id = settings.WHATSAPP_PHONE_ID
        self.url = f"https://graph.facebook.com/v20.0/{self.phone_id}/messages"

    def send_message(self, phone: str, message: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message},
        }
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"WhatsApp message sent to {phone}")
            return response.json()
        except Exception as e:
            logger.error(f"WhatsApp send failed to {phone}: {e}")
            raise
