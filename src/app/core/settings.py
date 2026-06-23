import json
import logging
import boto3
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

logger = logging.getLogger("lead-engine")

def fetch_aws_secrets_synchronously() -> dict:
    """
    Forces a synchronous fetch of AWS secrets before Pydantic initializes fields.
    This prevents eager module imports from crashing on undefined variables.
    """
    # Hardcoded or env-fallback configurations for bootstrap loading
    secret_name = "production/LeadQualifier" # Ensure this matches your actual AWS Secret Name exactly
    region_name = "eu-north-1"
    
    try:
        # Create a localized client immediately to fetch configuration parameters
        client = boto3.client("secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except Exception as e:
        # Fallback to empty dictionary if running locally without AWS credentials
        logger.warning(f"Bootstrap AWS Secrets fetch skipped or failed: {e}")
        return {}

# Pre-fetch secrets cleanly at the global initialization boundary
AWS_SECRETS = fetch_aws_secrets_synchronously()

class Settings(BaseSettings):
    APP_NAME: str = "AI Lead Engine"
    DEBUG: bool = False
    ENV: str = "production"
    
    # Values populate from AWS Secrets pre-fetch, falling back to environment variables
    DATABASE_URL: str | None = AWS_SECRETS.get("DATABASE_URL")
    APIFY_API_TOKEN: str | None = AWS_SECRETS.get("APIFY_API_TOKEN")
    
    # INTEGRATIONS
    SENDGRID_API_KEY: str | None = AWS_SECRETS.get("SENDGRID_API_KEY")
    EMAIL_FROM: str | None = AWS_SECRETS.get("EMAIL_FROM")
    WHATSAPP_TOKEN: str | None = AWS_SECRETS.get("WHATSAPP_TOKEN")
    WHATSAPP_PHONE_ID: str | None = AWS_SECRETS.get("WHATSAPP_PHONE_ID")
    
    AWS_REGION: str = "eu-north-1"
    AWS_SECRET_NAME: str | None = "production/LeadQualifier"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    def model_post_init(self, __context) -> None:
        """Fallback validation step to guarantee the application baseline is met."""
        if not self.DATABASE_URL:
            # Check environment variables directly if secrets manager didn't find it
            import os
            self.DATABASE_URL = os.getenv("DATABASE_URL")
            
        logger.info(f"DATABASE_URL present: {bool(self.DATABASE_URL)}")
        logger.info(f"APIFY_API_TOKEN present: {bool(self.APIFY_API_TOKEN)}")
        
        if not self.DATABASE_URL:
            raise ValueError("CRITICAL: DATABASE_URL is missing. Engine cannot start.")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
