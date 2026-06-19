%%writefile src/app/crud/lead.py
from sqlalchemy.orm import Session
from src.app.models.lead import Lead
from src.app.schemas.lead import LeadCreate

def get_lead_by_email(db: Session, email: str):
    """
    Safely look up a lead by email, bypassing placeholder data checks.
    """
    if not email or email in ["No Email", "No Email Provided"]:
        return None
    return db.query(Lead).filter(Lead.email == email).first()

def get_lead_by_phone(db: Session, phone: str):
    """
    Finds existing leads by phone to prevent duplicate Maps records.
    """
    if not phone or phone in ["No Phone", "No Phone Provided"]:
        return None
    return db.query(Lead).filter(Lead.phone == phone).first()

def get_leads(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves historical lead records with built-in pagination constraints.
    """
    return db.query(Lead).offset(skip).limit(limit).all()

def create_lead(db: Session, lead: LeadCreate) -> Lead:
    """
    Builds and commits a database lead instance using the correct model attributes.
    """
    db_lead = Lead(
        title=lead.title,      # ✅ Fixed: Matches model property
        phone=lead.phone,      # ✅ Fixed: Matches model property
        email=lead.email,      # ✅ Fixed: Matches model property
        address=lead.address,  # ✅ Fixed: Matches model property
        query=lead.query       # ✅ Fixed: Matches model property
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead
