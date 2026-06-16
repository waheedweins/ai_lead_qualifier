%%writefile src/app/main.py
import logging
from fastapi import FastAPI, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

# Internal absolute imports matching your repository schema
from src.app.database import SessionLocal, engine, Base
from src.app.scrapers.google_maps import execute_apify_scraping_workflow

# Explicitly alias or verify your SQLAlchemy model matches what the scraper looks for
try:
    from src.app.database import Lead
except ImportError:
    # Fallback definition if your database file names it LeadModel instead of Lead
    from src.app.database import LeadModel as Lead

# Initialize database schema components
Base.metadata.create_all(bind=engine)

# Setup logger
logger = logging.getLogger("lead-engine.main")
logger.setLevel(logging.INFO)

app = FastAPI(
    title="AI Lead Generation API",
    version="0.1.0",
    description="Production-grade asynchronous real-time lead generation engine."
)

# SQLAlchemy DB Dependency context provider
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schema Definitions
class LeadResponse(BaseModel):
    id: int
    title: str
    phone: str = None
    email: str = None
    address: str = None
    query: str

    class Config:
        from_attributes = True

@app.get("/health", status_code=200)
def health_check():
    """
    Lightweight health probe endpoint for AWS ALB target group validation.
    """
    return {"status": "healthy"}

@app.post("/scrape/", status_code=200)
def trigger_scraping_pipeline(query: str, background_tasks: BackgroundTasks):
    """
    Non-blocking endpoint that offloads execution directly to background workers.
    """
    logger.info(f"Received scrape request query parameter: '{query}'. Handing off to background worker pool.")
    
    background_tasks.add_task(
        execute_apify_scraping_workflow,
        query=query,
        session_factory=SessionLocal
    )
    
    return {
        "status": "processing",
        "query": query,
        "message": "Scraping pipeline job successfully queued in background thread pool."
    }

@app.get("/leads/", response_model=List[LeadResponse])
def get_historical_leads(db: Session = Depends(get_db)):
    """
    Retrieves all collected lead profile models committed to the datastore.
    """
    leads = db.query(Lead).all()
    return leads
