import logging
from sqlalchemy.orm import Session
from src.app.services.lead_service import LeadService
from src.app.schemas.lead import LeadCreate
from src.app.crud.lead import get_lead_by_phone, get_lead_by_email

logger = logging.getLogger("lead-engine.scrapers.lead_ingestor")


def ingest_leads(db: Session, scraped_data: list) -> int:
    service = LeadService(db)
    inserted = 0

    for item in scraped_data:
        business_name = item.get("title") or item.get("name") or "Unknown Business"
        phone = item.get("phone") or item.get("phoneNumber") or ""
        email = item.get("email") or ""

        phone = str(phone).strip()
        email = str(email).strip()

        # Deduplication by phone
        if phone and phone not in ("No Phone Provided", ""):
            if get_lead_by_phone(db, phone):
                logger.debug(f"Skipping duplicate (phone): {business_name}")
                continue

        # Generate placeholder email for phone-only leads
        if not email:
            if phone and phone not in ("No Phone Provided", ""):
                email = f"no_email_{phone.replace('+', '').replace(' ', '')}@placeholder.com"
            else:
                logger.debug(f"Skipping lead with no email and no phone: {business_name}")
                continue  # Skip if neither contact method is available

        # Deduplication by email
        if get_lead_by_email(db, email):
            logger.debug(f"Skipping duplicate (email): {business_name}")
            continue

        lead = LeadCreate(
            name=business_name,
            email=email,
            phone=phone or None,
            source="google_maps",
        )
        service.create(lead)
        inserted += 1

    logger.info(f"Ingestion complete: {inserted} new leads inserted.")
    return inserted
