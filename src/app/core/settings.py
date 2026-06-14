%%writefile src/app/core/settings.py
import json
import logging
import boto3
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("lead-engine")


class Settings(BaseSettings):
    APP_NAME: str = "AI Lead Engine"
    DEBUG: bool = False
    ENV: str = "production"

    DATABASE_URL: str | None = None
    APIFY_TOKEN: str | None = None
    SENDGRID_API_KEY: str | None = None
    EMAIL_FROM: str | None = None
    WHATSAPP_TOKEN: str | None = None
    WHATSAPP_PHONE_ID: str | None = None

    AWS_REGION: str = "us-east-1"
    AWS_SECRET_NAME: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    def __init__(self, **values):
        super().__init__(**values)

        if self.AWS_SECRET_NAME:
            try:
                logger.info(
                    f"Loading secrets from AWS Secrets Manager: {self.AWS_SECRET_NAME}"
                )

                client = boto3.client(
                    "secretsmanager",
                    region_name=self.AWS_REGION
                )

                response = client.get_secret_value(
                    SecretId=self.AWS_SECRET_NAME
                )

                secret_dict = json.loads(
                    response["SecretString"]
                )

                for key, value in secret_dict.items():
                    if hasattr(self, key) and getattr(self, key) is None:
                        setattr(self, key, value)

            except Exception as e:
                logger.error(
                    f"Secrets Manager load failed: {str(e)}"
                )

        logger.info("Configuration loaded")

        logger.info(
            f"DATABASE_URL present: {bool(self.DATABASE_URL)}"
        )
        logger.info(
            f"APIFY_TOKEN present: {bool(self.APIFY_TOKEN)}"
        )
        logger.info(
            f"SENDGRID_API_KEY present: {bool(self.SENDGRID_API_KEY)}"
        )
        logger.info(
            f"WHATSAPP_TOKEN present: {bool(self.WHATSAPP_TOKEN)}"
        )


settings = Settings()
