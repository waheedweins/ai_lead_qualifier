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
    # FIXED: Absolute path import from root 'src' to match your repository layout
    from src.app.main import Lead

    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        logger.error("Failed to execute Apify scraping workflow: APIFY_API_TOKEN is missing from environment keys.")
        return

    client = ApifyClient(apify_token)
    
    # Flawless Input Configuration for universal Google Maps Scraper Actors
    run_input = {
        "searchStrings": [query],
        "maxCrawledPlacesPerSearch": 30,
        "language": "en",
        "exportPlaceUrls": False,
        "includeWebsites": True,
        "skipClosedPlaces": False
    }
    
    try:
        logger.info(f"Launching Apify search automation query execution context: {query}")
        
        # Call the universal standard Google Maps Scraper actor on the Apify platform
        run = client.actor("apify/google-maps-scraper").call(run_input=run_input)
        
        # Fetch data dictionary items array matrix from the completed dataset loop run
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
        logger.info(f"Apify call completed successfully. Extracted {len(dataset_items)} raw elements.")
        
        # Open an independent database context for the async background worker thread
        db: Session = session_factory()
        try:
            inserted_count = 0
            for item in dataset_items:
                # Fallback lookups to support multiple Apify schema variations cleanly
                title = item.get("title") or item.get("name") or "Unknown Business"
                phone = item.get("phone") or item.get("internationalPhone") or None
                address = item.get("address") or item.get("locatedIn") or None
                email = item.get("email") or "no-email@fallback.com"
                
                # Sanitize empty records
                if title == "Unknown Business" and not phone:
                    continue

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
