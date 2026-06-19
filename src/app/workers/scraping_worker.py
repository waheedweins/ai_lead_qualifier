import logging
from src.app.core.logging import logger
from src.app.core.database import SessionLocal
from src.app.scrapers.google_maps import GoogleMapsScraper
from src.app.scrapers.lead_ingestor import ingest_leads


def run_scraping_job(query: str) -> int:
    """
    Synchronous scraping job — safe to call from FastAPI BackgroundTasks.
    Scrapes Google Maps via Apify and ingests results into the database.
    Returns the number of new leads inserted.
    """
    logger.info(f"Scraping job started for query: '{query}'")

    db = SessionLocal()
    try:
        scraper = GoogleMapsScraper()
        data = scraper.scrape(search_query=query)
        logger.info(f"Apify returned {len(data)} raw items for '{query}'")

        inserted = ingest_leads(db=db, scraped_data=data)
        logger.info(f"Scraping job complete. {inserted} new leads inserted for '{query}'")
        return inserted

    except Exception as e:
        logger.error(f"Scraping job crashed for query '{query}': {e}", exc_info=True)
        raise
    finally:
        db.close()
