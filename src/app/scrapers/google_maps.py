import os
from apify_client import ApifyClient
from src.app.core.logging import logger


class GoogleMapsScraper:

    def __init__(self):
        self.token = os.getenv("APIFY_TOKEN")

        logger.info(
            f"APIFY_TOKEN exists: {bool(self.token)}"
        )

        if self.token:
            logger.info(
                f"APIFY_TOKEN length: {len(self.token)}"
            )

        if not self.token:
            raise ValueError(
                "APIFY_TOKEN missing from runtime environment."
            )

        self.client = ApifyClient(self.token)

    def scrape(self, search_query: str) -> list:

        try:
            logger.info(
                f"Starting Apify scrape: {search_query}"
            )

            run_input = {
                "searchStrings": [search_query],
                "maxCrawledPlacesPerSearch": 10,
                "language": "en"
            }

            run = self.client.actor(
                "apify/google-maps-scraper"
            ).call(
                run_input=run_input
            )

            logger.info(
                f"Actor run id: {run.get('id')}"
            )

            dataset_items = list(
                self.client.dataset(
                    run["defaultDatasetId"]
                ).list_items().items
            )

            logger.info(
                f"Returned records: {len(dataset_items)}"
            )

            return dataset_items

        except Exception as e:
            logger.exception(
                f"Apify execution failed: {str(e)}"
            )
            raise
