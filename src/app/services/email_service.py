from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from src.app.core.settings import settings

class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)

    def send_email(self, recipient: str, subject: str, content: str) -> int:
        message = Mail(
            from_email=settings.EMAIL_FROM,
            to_emails=recipient,
            subject=subject,
            plain_text_content=content
        )
        response = self.client.send(message)
        return response.status_code
