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
        category = item.get("categoryName") or item.get("title") or "General"
        # Extract address safely
        address = item.get("address") or item.get("fullAddress") or None

        phone = str(phone).strip()
        email = str(email).strip()

        # Deduplication
        if phone and phone not in ("No Phone Provided", ""):
            if get_lead_by_phone(db, phone):
                continue

        if not email:
            if phone and phone not in ("No Phone Provided", ""):
                email = f"no_email_{phone.replace('+', '').replace(' ', '')}@placeholder.com"
            else:
                continue

        if get_lead_by_email(db, email):
            continue

        try:
            lead = LeadCreate(
                name=business_name,
                email=email,
                phone=phone or None,
                source="google_maps",
                title=category,
                address=address # Now matches the schema
            )
            service.create(lead)
            inserted += 1
        except Exception as e:
            logger.error(f"Failed to create lead schema for {business_name}: {e}")

    logger.info(f"Ingestion complete: {inserted} new leads inserted.")
    return inserted
