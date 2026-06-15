import os
import logging
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from apify_client import ApifyClient

# 1. Initialize Standard Structured Logging
logger = logging.getLogger("lead-engine")
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

# Ensure tables exist in your RDS database instance
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Lead Generation API")

# Dependency utility to safely manage thread-local database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Background Ingestion Pipeline
def execute_apify_scraping_workflow(query: str):
    """
    Executes the real-time Google Maps scraping sequence by communicating 
    directly with the official Apify marketplace actor backend ecosystem.
    """
    # Uses the correct environment key matching your updated AWS Task Definition
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        logger.error("Failed to execute Apify scraping workflow: APIFY_API_TOKEN is missing from environment keys.")
        return

    client = ApifyClient(apify_token)
    run_input = {
        "searchStrings": [query],
        "maxCrawledPlacesPerSearch": 50,
        "language": "en",
        "exportPlaceUrls": False
    }
    
    try:
        logger.info(f"Launching Apify search automation query execution context: {query}")
        
        # FIXED: Points cleanly to the correct universal standard identifier for the scraper
        run = client.actor("apify/google-maps-scraper").call(run_input=run_input)
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
        logger.info(f"Apify call completed successfully. Extracted {len(dataset_items)} raw elements.")
        
        # Open an independent database context for the async background worker thread
        db: Session = SessionLocal()
        try:
            inserted_count = 0
            for item in dataset_items:
                title = item.get("title", "Unknown Business")
                phone = item.get("phone", None)
                address = item.get("address", None)
                email = item.get("email", "no-email@fallback.com")
                
                # Deduplication check: Avoid inserting duplicates if phone number exists
                if phone:
                    exists = db.query(Lead).filter(Lead.phone == phone).first()
                    if exists:
                        continue

                new_lead = Lead(
                    title=title,
                    phone=phone,
                    email=email,
                    address=address,
                    query=query
                )
                db.add(new_lead)
                inserted_count += 1
            
            db.commit()
            logger.info(f"Database Ingestion complete. Rows successfully committed: {inserted_count}")
        except Exception as db_err:
            db.rollback()
            logger.error(f"Database transaction failure during ingestion execution: {str(db_err)}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to execute Apify scraping workflow: {str(e)}")

# 5. Production API Routing Endpoints
@app.post("/scrape/")
async def trigger_scraping_pipeline(query: str, background_tasks: BackgroundTasks):
    logger.info(f"Initiating scraping task for query: {query}")
    background_tasks.add_task(execute_apify_scraping_workflow, query)
    return {"status": "processing", "message": "Scraping job successfully queued in background."}

@app.get("/leads/")
async def get_stored_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    leads = db.query(Lead).offset(skip).limit(limit).all()
    return leads
