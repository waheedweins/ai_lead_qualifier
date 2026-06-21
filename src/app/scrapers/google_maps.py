import logging
from apify_client import ApifyClient
from src.app.core.settings import settings

logger = logging.getLogger("lead-engine.scrapers.google_maps")

class GoogleMapsScraper:
    """
    Wraps the Apify Google Maps scraper using the friendly name.
    """

    def __init__(self):
        # Initialization does not crash the app
        self.token = settings.APIFY_API_TOKEN
        self.client = ApifyClient(self.token) if self.token else None
        
        # Friendly name as requested
        self.actor_name = "compass/crawler-google-places"
        # Alphanumeric fallback in case name resolution fails
        self.actor_id_fallback = "nwua9Gu5YrADL7ZDj"

    def scrape(self, search_query: str, max_results: int = 20) -> list[dict]:
        if not self.client:
            raise RuntimeError("Scraper not initialized: API token missing.")

        run_input = {
            "searchStringsArray": [search_query],
            "maxCrawledPlacesPerSearch": max_results,
            "language": "en",
        }

        logger.info(f"Launching Apify actor: {self.actor_name} for query: '{search_query}'")
        
        try:
            # Try calling via friendly name
            run = self.client.actor(self.actor_name).call(run_input=run_input)
        except Exception as name_error:
            logger.warning(f"Friendly name failed, attempting fallback to ID: {name_error}")
            # Fallback to the permanent ID if the name fails
            run = self.client.actor(self.actor_id_fallback).call(run_input=run_input)
            
        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            logger.error("No dataset ID returned from Apify.")
            return []

        items = self.client.dataset(dataset_id).list_items().items
        logger.info(f"Apify returned {len(items)} items for '{search_query}'")
        return items

def execute_apify_scraping_workflow(query: str, session_factory) -> None:
    from src.app.scrapers.lead_ingestor import ingest_leads

    scraper = GoogleMapsScraper()
    items = scraper.scrape(search_query=query)

    if not items:
        return

    db = session_factory()
    try:
        inserted = ingest_leads(db=db, scraped_data=items)
        logger.info(f"Workflow: inserted {inserted} leads for query '{query}'")
    except Exception as e:
        db.rollback()
        logger.error(f"Ingestion failed: {e}")
        raise
    finally:
        db.close()
