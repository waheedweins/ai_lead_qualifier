import json
import logging
import os
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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def __init__(self, **values):
        super().__init__(**values)
        
        # Scenario 1: Fallback to AWS Secrets Manager if secret name is provided
        if self.AWS_SECRET_NAME and not self.DATABASE_URL:
            try:
                logger.info(f"Fetching secrets from AWS Secrets Manager: {self.AWS_SECRET_NAME}")
                client = boto3.client("secretsmanager", region_name=self.AWS_REGION)
                response = client.get_secret_value(SecretId=self.AWS_SECRET_NAME)
                secret_dict = json.loads(response["SecretString"])
                
                for key, val in secret_dict.items():
                    if hasattr(self, key) and getattr(self, key) is None:
                        setattr(self, key, val)
            except Exception as e:
                logger.error(f"Failed to fetch secrets from AWS Secrets Manager: {str(e)}")

        # FIX: Validation Guard moved to the absolute end after AWS resolution
        critical_keys = ["DATABASE_URL", "APIFY_TOKEN", "SENDGRID_API_KEY", "WHATSAPP_TOKEN"]
        for missing_key in critical_keys:
            if not getattr(self, missing_key):
                raise ValueError(f"❌ Configuration Error: Missing required environment variable '{missing_key}'")

settings = Settings()
