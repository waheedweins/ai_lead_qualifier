import json
import logging
import boto3
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

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

    def model_post_init(self, __context) -> None:
        """Load secrets from AWS Secrets Manager after base env vars are loaded."""
        if self.AWS_SECRET_NAME:
            try:
                logger.info(f"Loading secrets from AWS Secrets Manager: {self.AWS_SECRET_NAME}")
                client = boto3.client("secretsmanager", region_name=self.AWS_REGION)
                response = client.get_secret_value(SecretId=self.AWS_SECRET_NAME)
                secret_dict = json.loads(response["SecretString"])

                for key, value in secret_dict.items():
                    if hasattr(self, key) and not getattr(self, key):
                        # Use object.__setattr__ because pydantic models are frozen after init
                        object.__setattr__(self, key, value)

                logger.info("Secrets loaded from AWS Secrets Manager successfully.")
            except Exception as e:
                logger.exception(f"Failed to load secrets from AWS Secrets Manager: {e}")

        # Log presence (never log values)
        logger.info(f"DATABASE_URL present: {bool(self.DATABASE_URL)}")
        logger.info(f"APIFY_API_TOKEN present: {bool(self.APIFY_API_TOKEN)}")
        logger.info(f"SENDGRID_API_KEY present: {bool(self.SENDGRID_API_KEY)}")
        logger.info(f"WHATSAPP_TOKEN present: {bool(self.WHATSAPP_TOKEN)}")

        # Validate required keys
        required_keys = ["DATABASE_URL", "APIFY_API_TOKEN"]
        missing = [k for k in required_keys if not getattr(self, k)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


@lru_cache()
def get_settings() -> Settings:
    """
    Cached singleton — avoids re-instantiating Settings (and re-calling Secrets Manager)
    on every module import. Use get_settings() everywhere instead of bare `settings`.
    """
    return Settings()


# Module-level alias for backwards compatibility with existing imports
settings = get_settings()
