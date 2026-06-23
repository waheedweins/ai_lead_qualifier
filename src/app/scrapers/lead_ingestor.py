import logging
from sqlalchemy.orm import Session
from src.app.services.lead_service import LeadService
from src.app.schemas.lead import LeadCreate
from src.app.crud.lead import get_lead_by_phone, get_lead_by_email

logger = logging.getLogger("lead-engine.scrapers.ingestor")

def ingest_leads(db: Session, scraped_data: list) -> int:
    service = LeadService(db)
    inserted = 0
    
    logger.info(f"Ingestor received {len(scraped_data)} raw records to process.")
    
    for idx, item in enumerate(scraped_data):
        # Normalize incoming payload data fields
        business_name = item.get("title") or item.get("name") or f"Unknown Business {idx}"
        phone = str(item.get("phone") or item.get("phoneNumber") or item.get("internationalPhoneNumber") or "").strip()
        email = str(item.get("email") or "").strip()
        address = item.get("address") or item.get("fullAddress") or item.get("locatedIn")
        category = item.get("categoryName") or item.get("subCategory") or "Solar Services"

        # Fallback tracking if both contact channels are blank
        if not phone and not email:
            logger.warning(f"Skipping '{business_name}': Missing both phone and email details.")
            continue
            
        # Check duplicates by phone
        if phone and get_lead_by_phone(db, phone):
            logger.info(f"Skipping '{business_name}': Duplicate phone number identified ({phone}).")
            continue
            
        # Create fallback email if missing but phone exists
        if not email:
            clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
            if clean_phone:
                email = f"no_email_{clean_phone}@placeholder.com"
            else:
                continue
                
        # Check duplicates by email
        if get_lead_by_email(db, email):
            logger.info(f"Skipping '{business_name}': Duplicate email identifier identified ({email}).")
            continue

        try:
            lead = LeadCreate(
                name=business_name, 
                email=email, 
                phone=phone if phone else None, 
                source="google_maps", 
                title=category, 
                address=address
            )
            service.create(lead)
            inserted += 1
            logger.info(f"Successfully saved lead #{inserted}: {business_name}")
        except Exception as save_err:
            logger.error(f"Failed to write record structure for '{business_name}': {save_err}")
            continue
            
    logger.info(f"Ingestion lifecycle completed. Total records saved: {inserted}")
    return inserted
