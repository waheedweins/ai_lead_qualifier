from sqlalchemy.orm import Session
from src.app.services.lead_service import LeadService
from src.app.schemas.lead import LeadCreate
from src.app.crud.lead import get_lead_by_phone, get_lead_by_email

def ingest_leads(db: Session, scraped_data: list) -> int:
    service = LeadService(db)
    inserted = 0
    for item in scraped_data:
        business_name = item.get("title") or item.get("name") or "Unknown"
        phone = str(item.get("phone") or item.get("phoneNumber") or "").strip()
        email = str(item.get("email") or "").strip()
        address = item.get("address") or item.get("fullAddress")

        if not phone and not email: continue
        if phone and get_lead_by_phone(db, phone): continue
        if not email:
            if phone: email = f"no_email_{phone.replace('+', '')}@placeholder.com"
            else: continue
        if get_lead_by_email(db, email): continue

        try:
            lead = LeadCreate(name=business_name, email=email, phone=phone, source="google_maps", title=item.get("categoryName"), address=address)
            service.create(lead)
            inserted += 1
        except Exception: continue
    return inserted
