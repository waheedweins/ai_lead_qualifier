import os
from apify_client import ApifyClient

from src.app.core.logging import logger


class GoogleMapsScraper:
    """
    Google Maps scraper powered by Apify.
    """

    def __init__(self):
        self.token = os.getenv("APIFY_API_TOKEN")

        logger.info(
            f"APIFY_API_TOKEN present: {bool(self.token)}"
        )

        if not self.token:
            logger.error(
                "APIFY_API_TOKEN variable is missing from runtime environment."
            )

            raise ValueError(
                "Missing APIFY_API_TOKEN configuration environment value."
            )

        self.client = ApifyClient(self.token)

    def scrape(
        self,
        search_query: str,
        max_results: int = 10,
    ) -> list:

        try:
            logger.info(
                f"Starting Apify Google Maps scrape for query: {search_query}"
            )

            run_input = {
                "searchStrings": [search_query],
                "maxCrawledPlacesPerSearch": max_results,
                "language": "en",
            }

            run = self.client.actor(
                "apify/google-maps-scraper"
            ).call(
                run_input=run_input
            )

            logger.info(
                f"Apify actor completed successfully. Run ID: {run.get('id')}"
            )

            dataset_items = list(
                self.client.dataset(
                    run["defaultDatasetId"]
                ).list_items().items
            )

            logger.info(
                f"Retrieved {len(dataset_items)} records from Apify."
            )

            return dataset_items

        except Exception as e:
            logger.exception(
                f"Apify scraping failed: {str(e)}"
            )
            raise
