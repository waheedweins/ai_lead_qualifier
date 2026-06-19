from sqlalchemy.orm import Session
from src.app.models.lead import Lead
from src.app.schemas.lead import LeadCreate


def get_lead_by_email(db: Session, email: str):
    if not email or email in ["No Email", "No Email Provided"]:
        return None
    return db.query(Lead).filter(Lead.email == email).first()


def get_lead_by_phone(db: Session, phone: str):
    """Finds existing leads by phone to prevent duplicate Maps records."""
    if not phone or phone in ["No Phone", "No Phone Provided"]:
        return None
    return db.query(Lead).filter(Lead.phone == phone).first()


def get_leads(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Lead).offset(skip).limit(limit).all()


def create_lead(db: Session, lead: LeadCreate) -> Lead:
    db_lead = Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        source=lead.source,
        status="new",
        ai_score=0,
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead
