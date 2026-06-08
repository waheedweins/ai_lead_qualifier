from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.schemas.lead import LeadCreate, LeadResponse
from src.app.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["Leads"])

@router.post("/", response_model=LeadResponse)
def add_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    service = LeadService(db)
    return service.create(lead)

@router.get("/", response_model=list[LeadResponse])
def list_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = LeadService(db)
    return service.list_all(skip=skip, limit=limit)
