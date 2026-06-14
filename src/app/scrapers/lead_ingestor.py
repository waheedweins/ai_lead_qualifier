%%writefile src/app/scrapers/lead_ingestor.py
from sqlalchemy.orm import Session
from src.app.services.lead_service import LeadService
from src.app.schemas.lead import LeadCreate
from src.app.crud.lead import get_lead_by_phone, get_lead_by_email

def ingest_leads(db: Session, scraped_data: list) -> int:
    service = LeadService(db)
    inserted = 0
    
    for item in scraped_data:
        # 1. Extract flexible keys from modern Apify payload structures
        business_name = item.get("title") or item.get("name") or "Unknown Business"
        phone = item.get("phone") or item.get("phoneNumber") or "No Phone Provided"
        email = item.get("email")
        
        # Clean string formats
        phone = str(phone).strip()
        
        # 2. Advanced Deduplication Check before parsing schemas
        if phone and phone != "No Phone Provided":
            if get_lead_by_phone(db, phone):
                print(f"⚠️ Skipping Duplicate Record (Phone already exists): {business_name}")
                continue

        # 3. Handle Missing Emails to dodge the strict Database Column unique=True constraint
        if not email:
            if phone and phone != "No Phone Provided":
                email = f"no_email_{phone.replace('+', '').replace(' ', '')}@placeholder.com"
            else:
                continue # Skip if it has neither phone nor email to prevent dead rows

        if get_lead_by_email(db, email):
            print(f"⚠️ Skipping Duplicate Record (Email already exists): {business_name}")
            continue

        # 4. Construct valid Pydantic Payload
        lead = LeadCreate(
            name=business_name,
            email=email,
            phone=phone,
            source="google_maps"
        )
        
        service.create(lead)
        inserted += 1
        
    return inserted
