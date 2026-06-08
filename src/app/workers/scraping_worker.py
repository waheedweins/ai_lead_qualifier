from src.app.core.logging import logger
from src.app.core.database import SessionLocal
from src.app.scrapers.google_maps import GoogleMapsScraper
from src.app.scrapers.lead_ingestor import ingest_leads

def run_scraping_job(query: str) -> int:
    # Explicitly bound session lifecycle inside the target worker thread
    db = SessionLocal()
    try:
        logger.info(f"Starting scraping task context for query: {query}")
        scraper = GoogleMapsScraper()
        data = scraper.scrape(search_query=query)
        
        inserted = ingest_leads(db=db, scraped_data=data)
        logger.info(f"Ingestion successful. Rows committed: {inserted}")
        return inserted
    except Exception as e:
        logger.error(f"Scraping background pipeline execution crash: {str(e)}")
        raise e
    finally:
        db.close()
