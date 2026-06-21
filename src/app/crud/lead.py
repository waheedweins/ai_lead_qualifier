from sqlalchemy.orm import Session
from src.app.models.lead import Lead
from src.app.schemas.lead import LeadCreate

def create_lead(db: Session, lead: LeadCreate) -> Lead:
    """
    Creates a new lead record using the provided schema.
    """
    db_lead = Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        source=lead.source,
        title=lead.title,
        address=lead.address
    )
    db.add(db_lead)
    db.commit()      # Persists the data to the database
    db.refresh(db_lead)  # Updates the object with the generated ID and created_at
    return db_lead
