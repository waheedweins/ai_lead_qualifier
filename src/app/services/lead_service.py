from sqlalchemy.orm import Session
from src.app.crud.lead import create_lead, get_lead_by_email, get_leads
from src.app.schemas.lead import LeadCreate
from src.app.services.ai_service import AIService
import logging

logger = logging.getLogger("lead-engine.lead-service")

class LeadService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIService()

    def list_all(self, skip: int = 0, limit: int = 100):
        """
        Fetches a paginated list of leads.
        """
        return get_leads(self.db, skip=skip, limit=limit)

    def create(self, lead: LeadCreate):
        """
        Creates a new lead and performs AI scoring.
        """
        existing = get_lead_by_email(self.db, email=lead.email)
        if existing:
            return existing
        
        new_lead = create_lead(db=self.db, lead=lead)
        
        try:
            # Prepare data for AI scoring
            lead_dict = new_lead.__dict__.copy()
            lead_dict.pop('_sa_instance_state', None)
            
            # Non-blocking AI scoring
            score_result = self.ai.score_lead(lead_dict)
            new_lead.ai_score = score_result.get("score", 0)
            
            self.db.commit()
            self.db.refresh(new_lead)
        except Exception as e:
            logger.warning(f"Lead {new_lead.id} saved, but AI scoring failed: {e}")
            
        return new_lead
