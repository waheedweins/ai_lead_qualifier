import sys
from src.app.core.logging import logger
from src.app.core.database import SessionLocal
from src.app.scrapers.google_maps import GoogleMapsScraper
from src.app.scrapers.lead_ingestor import ingest_leads

def run_scraping_job(query: str) -> int:
    # Explicitly flush stdout so Docker logs show everything in real-time
    print(f"DEBUG WORKER: Initiating scraping task for query: {query}", flush=True)
    
    db = SessionLocal()
    try:
        scraper = GoogleMapsScraper()
        print("DEBUG WORKER: Calling Apify Actor...", flush=True)
        data = scraper.scrape(search_query=query)
        print(f"DEBUG WORKER: Apify call complete. Found {len(data)} items.", flush=True)

        inserted = ingest_leads(db=db, scraped_data=data)
        print(f"DEBUG WORKER: Ingestion complete. Rows committed: {inserted}", flush=True)
        return inserted
    except Exception as e:
        print(f"CRITICAL WORKER CRASH: {str(e)}", file=sys.stderr, flush=True)
        logger.error(f"Scraping background pipeline execution crash: {str(e)}")
        raise e
    finally:
        db.close()
