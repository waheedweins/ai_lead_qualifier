from sqlalchemy.orm import Session
from src.app.crud.lead import create_lead, get_leads, get_lead_by_email
from src.app.schemas.lead import LeadCreate
from src.app.services.ai_service import AIService

class LeadService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIService()

    def create(self, lead: LeadCreate):
        existing = get_lead_by_email(self.db, email=lead.email)
        if existing:
            return existing
        return create_lead(db=self.db, lead=lead)

    def list_all(self, skip: int = 0, limit: int = 100):
        return get_leads(self.db, skip=skip, limit=limit)

    def score_lead(self, lead_dict: dict) -> dict:
        return self.ai.score_lead(lead_dict)
