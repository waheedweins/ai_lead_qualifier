import os
import logging
from fastapi import FastAPI, BackgroundTasks, Depends
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# Corrected path import matching your src/app layout
from app.scrapers.google_maps import execute_apify_scraping_workflow

# 1. Initialize Standard Structured Logging
logger = logging.getLogger("lead-engine.main")
logger.setLevel(logging.INFO)

# 2. Database Infrastructure Connection Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password123@database-1.c5ckwgukooe0.eu-north-1.rds.amazonaws.com:5432/postgres")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Database Schema Mapping
class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    query = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Lead Generation API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Production API Routing Endpoints
@app.post("/scrape/")
async def trigger_scraping_pipeline(query: str, background_tasks: BackgroundTasks):
    logger.info(f"Initiating scraping task for query: {query}")
    # Pass SessionLocal directly so the modular file can safely spin up its own thread pool context
    background_tasks.add_task(execute_apify_scraping_workflow, query, SessionLocal)
    return {"status": "processing", "message": "Scraping job successfully queued in background."}

@app.get("/leads/")
async def get_stored_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    leads = db.query(Lead).offset(skip).limit(limit).all()
    return leads
