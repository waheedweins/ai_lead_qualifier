import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from src.app.core.settings import settings

logger = logging.getLogger("lead-engine.email-service")


class EmailService:
    def __init__(self):
        if not settings.SENDGRID_API_KEY:
            raise RuntimeError("SENDGRID_API_KEY is not configured.")
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)

    def send_email(self, recipient: str, subject: str, content: str) -> int:
        if not settings.EMAIL_FROM:
            raise RuntimeError("EMAIL_FROM is not configured.")
        message = Mail(
            from_email=settings.EMAIL_FROM,
            to_emails=recipient,
            subject=subject,
            plain_text_content=content,
        )
        try:
            response = self.client.send(message)
            logger.info(f"Email sent to {recipient}: HTTP {response.status_code}")
            return response.status_code
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            raise
