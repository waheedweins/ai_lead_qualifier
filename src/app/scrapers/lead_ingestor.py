from sqlalchemy.orm import Session
from src.app.services.lead_service import LeadService
from src.app.schemas.lead import LeadCreate

def ingest_leads(db: Session, scraped_data: list) -> int:
    service = LeadService(db)
    inserted = 0
    for item in scraped_data:
        email = item.get("email")
        if not email:
            continue
        lead = LeadCreate(
            name=item.get("title"),
            email=email,
            phone=item.get("phone"),
            source="google_maps"
        )
        service.create(lead)
        inserted += 1
    return inserted
