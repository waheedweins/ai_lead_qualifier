from sqlalchemy.orm import Session
from src.app.crud.lead import create_lead, get_leads, get_lead_by_email
from src.app.schemas.lead import LeadCreate
from src.app.services.ai_service import AIService
import logging

logger = logging.getLogger("lead-engine.lead-service")

class LeadService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIService()

    def create(self, lead: LeadCreate):
        # 1. Deduplication check
        existing = get_lead_by_email(self.db, email=lead.email)
        if existing:
            return existing
        
        # 2. Save core data to DB first (Ensures data is never lost)
        new_lead = create_lead(db=self.db, lead=lead)
        
        # 3. Score lead without blocking the save operation
        try:
            lead_dict = new_lead.__dict__.copy()
            # Remove SQLAlchemy internal state keys before passing to AI
            lead_dict.pop('_sa_instance_state', None)
            
            score_result = self.ai.score_lead(lead_dict)
            
            # Update score if scoring was successful
            new_lead.ai_score = score_result.get("score", 0)
            self.db.commit()
            self.db.refresh(new_lead)
        except Exception as e:
            logger.warning(f"Lead {new_lead.id} was saved, but AI scoring hit an error: {e}")
            
        return new_lead

    def list_all(self, skip: int = 0, limit: int = 100):
        return get_leads(self.db, skip=skip, limit=limit)
