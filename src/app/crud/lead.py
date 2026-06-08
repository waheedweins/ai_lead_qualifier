from sqlalchemy.orm import Session
from src.app.models.lead import Lead
from src.app.schemas.lead import LeadCreate

def get_lead_by_email(db: Session, email: str):
    return db.query(Lead).filter(Lead.email == email).first()

def get_leads(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Lead).offset(skip).limit(limit).all()

def create_lead(db: Session, lead: LeadCreate):
    db_lead = Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        source=lead.source
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead
