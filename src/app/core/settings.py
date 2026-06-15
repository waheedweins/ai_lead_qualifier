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

    # APIFY
    APIFY_API_TOKEN: str | None = None

    # EMAIL
    SENDGRID_API_KEY: str | None = None
    EMAIL_FROM: str | None = None

    # WHATSAPP
    WHATSAPP_TOKEN: str | None = None
    WHATSAPP_PHONE_ID: str | None = None

    # AWS
    AWS_REGION: str = "eu-north-1"
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
                    if hasattr(self, key) and not getattr(self, key):
                        setattr(self, key, value)

                logger.info("Secrets loaded successfully")

            except Exception as e:
                logger.exception(
                    f"Failed loading secrets: {str(e)}"
                )

        logger.info(
            f"DATABASE_URL present: {bool(self.DATABASE_URL)}"
        )
        logger.info(
            f"APIFY_API_TOKEN present: {bool(self.APIFY_API_TOKEN)}"
        )
        logger.info(
            f"SENDGRID_API_KEY present: {bool(self.SENDGRID_API_KEY)}"
        )
        logger.info(
            f"WHATSAPP_TOKEN present: {bool(self.WHATSAPP_TOKEN)}"
        )

        required_keys = [
            "DATABASE_URL",
            "APIFY_API_TOKEN",
        ]

        missing = [
            key for key in required_keys
            if not getattr(self, key)
        ]

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )


settings = Settings()
