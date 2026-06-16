import os
import logging
from apify_client import ApifyClient
from sqlalchemy.orm import Session

# Initialize structured logging for this specific module path
logger = logging.getLogger("lead-engine.scrapers.google_maps")
logger.setLevel(logging.INFO)

def execute_apify_scraping_workflow(query: str, session_factory):
    """
    Executes the real-time Google Maps scraping sequence by communicating 
    directly with the official Apify marketplace actor backend ecosystem.
    """
    # Absolute path import from root 'src' to match your repository layout
    from src.app.main import Lead

    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        logger.error("Failed to execute Apify scraping workflow: APIFY_API_TOKEN is missing from environment keys.")
        return

    client = ApifyClient(apify_token)
    
    # Standard minimal payload layout recognized across all versions
    run_input = {
        "searchStrings": [query],
        "maxCrawledPlacesPerSearch": 10,  # Lowered limit to ensure fast, testing-friendly execution
        "language": "en"
    }
    
    try:
        logger.info(f"Launching Apify search automation query execution context: {query}")
        
        # AMENDED: Swapped to the explicit unique identifier string to bypass name lookup errors entirely
        run = client.actor("compass~google-maps-scraper").call(run_input=run_input)
        
        # Fetch data dictionary items array matrix from the completed dataset loop run
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
        logger.info(f"Apify call completed successfully. Extracted {len(dataset_items)} raw elements.")
        
        # Open an independent database context for the async background worker thread
        db: Session = session_factory()
        try:
            inserted_count = 0
            for item in dataset_items:
                # Robust fallback checking for variable schema maps
                title = item.get("title") or item.get("name")
                if not title or title == "Unknown Business":
                    continue
                    
                phone = item.get("phone") or item.get("internationalPhone") or None
                address = item.get("address") or item.get("locatedIn") or None
                email = item.get("email") or "no-email@fallback.com"

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
