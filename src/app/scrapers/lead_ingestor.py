import logging
from sqlalchemy.orm import Session
from src.app.services.lead_service import LeadService
from src.app.schemas.lead import LeadCreate
from src.app.crud.lead import get_lead_by_phone, get_lead_by_email

logger = logging.getLogger("lead-engine.scrapers.ingestor")

def extract_string_or_list_first(item: dict, keys: list) -> str:
    """Safely extracts a value whether Apify returns it as a string or an array list."""
    for key in keys:
        val = item.get(key)
        if not val:
            continue
        if isinstance(val, list) and len(val) > 0:
            return str(val).strip()
        elif isinstance(val, str):
            return val.strip()
    return ""

def ingest_leads(db: Session, scraped_data: list) -> int:
    service = LeadService(db)
    inserted = 0
    
    logger.info(f"Ingestor checking {len(scraped_data)} raw records against extraction matrices.")
    
    for idx, item in enumerate(scraped_data):
        # 1. Adaptively resolve the Business Name
        business_name = item.get("title") or item.get("name") or f"Solar Lead {idx}"
        
        # 2. Extract Phone (checking all possible Apify fields/lists)
        phone = extract_string_or_list_first(item, ["phone", "phoneNumber", "internationalPhoneNumber", "phoneLocal", "phones"])
        
        # 3. Extract Email (checking all possible string/list variants)
        email = extract_string_or_list_first(item, ["email", "emails", "emailAddress"])
        
        # 4. Resolve fallback address and categorization metadata
        address = item.get("address") or item.get("fullAddress") or item.get("addressString") or "Chichawatni, Pakistan"
        category = item.get("categoryName") or item.get("subCategory") or "Solar Installation"

        # Safe fallback: If everything is missing, create a placeholder string so the database can log it
        if not phone and not email:
            # Let's create a placeholder email using the title to ensure it doesn't get rejected!
            clean_name = "".join(e for e in business_name if e.isalnum()).lower()
            email = f"contact_{clean_name}_{idx}@placeholder-solar.com"
            logger.info(f"Generated generic contact route for missing fields: {email}")

        # Check duplicates by phone channel
        if phone and get_lead_by_phone(db, phone):
            logger.info(f"Skipping duplicate phone: {phone}")
            continue
            
        # Create fallback email if phone exists but email doesn't
        if not email and phone:
            clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
            email = f"no_email_{clean_phone}@placeholder.com"
                
        # Check duplicates by email channel
        if get_lead_by_email(db, email):
            logger.info(f"Skipping duplicate email: {email}")
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
            logger.info(f"Successfully committed lead #{inserted}: {business_name}")
        except Exception as save_err:
            logger.error(f"Failed to commit lead structure for '{business_name}': {save_err}")
            continue
            
    logger.info(f"Ingestion lifecycle completed. Total records saved: {inserted}")
    return inserted
