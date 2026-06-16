import os
import logging
from apify_client import ApifyClient
from sqlalchemy.orm import Session

logger = logging.getLogger("lead-engine.scrapers.google_maps")
logger.setLevel(logging.INFO)

def execute_apify_scraping_workflow(query: str, session_factory):
    """
    Executes real-time Google Maps scraping sequence via Apify.
    """
    from src.app.main import Lead  # Safe cross-import now that model exists

    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        logger.error("Failed to execute Apify scraping workflow: APIFY_API_TOKEN is missing from environment keys.")
        return

    client = ApifyClient(apify_token)
    run_input = {
        "searchStrings": [query],
        "maxCrawledPlacesPerSearch": 10,
        "language": "en"
    }
    
    try:
        logger.info(f"Launching Apify search automation query execution context: {query}")
        run = client.actor("compass~google-maps-scraper").call(run_input=run_input)
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
        logger.info(f"Apify call completed successfully. Extracted {len(dataset_items)} raw elements.")
        
        db: Session = session_factory()
        try:
            inserted_count = 0
            for item in dataset_items:
                title = item.get("title") or item.get("name")
                if not title or title == "Unknown Business":
                    continue
                    
                phone = item.get("phone") or item.get("internationalPhone") or None
                address = item.get("address") or item.get("locatedIn") or None
                email = item.get("email") or "no-email@fallback.com"

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
            logger.info("Database worker execution context session safely released back to core connection pool.")
            
    except Exception as e:
        logger.error(f"Failed to execute Apify scraping workflow processing stack: {str(e)}")
