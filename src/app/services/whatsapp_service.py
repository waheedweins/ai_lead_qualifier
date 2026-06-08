import requests
from src.app.core.settings import settings

class WhatsAppService:
    def __init__(self):
        self.token = settings.WHATSAPP_TOKEN
        self.phone_id = settings.WHATSAPP_PHONE_ID
        self.url = f"https://graph.facebook.com/v20.0/{self.phone_id}/messages"

    def send_message(self, phone: str, message: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message}
        }
        response = requests.post(self.url, headers=headers, json=payload)
        return response.json()
