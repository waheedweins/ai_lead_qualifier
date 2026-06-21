from sqlalchemy.orm import Session
from src.app.models.lead import Lead
from src.app.schemas.lead import LeadCreate

def create_lead(db: Session, lead: LeadCreate) -> Lead:
    db_lead = Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        source=lead.source,
        title=lead.title,
        address=lead.address
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead
