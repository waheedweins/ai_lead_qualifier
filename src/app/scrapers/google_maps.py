import logging
from apify_client import ApifyClient
from src.app.core.settings import settings

logger = logging.getLogger("lead-engine.scrapers.google_maps")


class GoogleMapsScraper:
    """
    Wraps the Apify Google Maps scraper actor.
    Returns a list of raw dicts — ingestion/deduplication is handled by lead_ingestor.
    """

    def __init__(self):
        if not settings.APIFY_API_TOKEN:
            raise RuntimeError("APIFY_API_TOKEN is not set. Cannot initialise scraper.")
        self.client = ApifyClient(settings.APIFY_API_TOKEN)

    def scrape(self, search_query: str, max_results: int = 20) -> list[dict]:
        run_input = {
            "searchStringsArray": [search_query],
            "maxCrawledPlacesPerSearch": max_results,
            "language": "en",
        }

        logger.info(f"Launching Apify actor for query: '{search_query}'")
        try:
            run = self.client.actor("compass/crawler-google-places").call(run_input=run_input)

            dataset_id = (run or {}).get("defaultDatasetId")
            if not dataset_id:
                raise RuntimeError(f"Apify actor returned no dataset ID. Run result: {run}")

            items = self.client.dataset(dataset_id).list_items().items
            logger.info(f"Apify returned {len(items)} raw items for '{search_query}'")
            return items
        except Exception as e:
            logger.error(f"Apify scraping failed for query '{search_query}': {e}")
            raise


def execute_apify_scraping_workflow(query: str, session_factory) -> None:
    """Legacy entry point — delegates to GoogleMapsScraper + lead_ingestor."""
    from src.app.scrapers.lead_ingestor import ingest_leads

    scraper = GoogleMapsScraper()
    items = scraper.scrape(search_query=query)

    db = session_factory()
    try:
        inserted = ingest_leads(db=db, scraped_data=items)
        logger.info(f"Legacy workflow: inserted {inserted} leads for query '{query}'")
    except Exception as e:
        db.rollback()
        logger.error(f"Ingestion failed in legacy workflow: {e}")
        raise
    finally:
        db.close()
