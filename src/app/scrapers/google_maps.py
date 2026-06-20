import logging
from apify_client import ApifyClient
from src.app.core.settings import settings

logger = logging.getLogger("lead-engine.scrapers.google_maps")

class GoogleMapsScraper:
    """
    Wraps the Apify Google Maps scraper actor.
    """

    def __init__(self):
        # Initialization does not crash the app if token is missing
        if not settings.APIFY_API_TOKEN:
            logger.error("APIFY_API_TOKEN is not set.")
            self.client = None
        else:
            self.client = ApifyClient(settings.APIFY_API_TOKEN)

    def scrape(self, search_query: str, max_results: int = 20) -> list[dict]:
        if not self.client:
            raise RuntimeError("Scraper not initialized: API token missing.")

        run_input = {
            "searchStringsArray": [search_query],
            "maxCrawledPlacesPerSearch": max_results,
            "language": "en",
        }

        logger.info(f"Launching Apify actor for query: '{search_query}'")
        try:
            # Using the identifier from your Apify console
            # If this fails, it now logs the error instead of crashing the server
            run = self.client.actor("compass/crawler-google-places").call(run_input=run_input)
            
            dataset_id = run.get("defaultDatasetId")
            items = self.client.dataset(dataset_id).list_items().items
            
            logger.info(f"Apify returned {len(items)} raw items for '{search_query}'")
            return items
            
        except Exception as e:
            logger.error(f"Apify scraping failed for query '{search_query}': {e}")
            # Re-raise only if you want the API endpoint to return 500
            raise

def execute_apify_scraping_workflow(query: str, session_factory) -> None:
    from src.app.scrapers.lead_ingestor import ingest_leads

    scraper = GoogleMapsScraper()
    items = scraper.scrape(search_query=query)

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
