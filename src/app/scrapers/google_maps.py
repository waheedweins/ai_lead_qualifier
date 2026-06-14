import os
from apify_client import ApifyClient
from src.app.core.logging import logger

class GoogleMapsScraper:
    def __init__(self):
        # Retrieve the API token from the environment variables
        self.token = os.getenv("APIFY_TOKEN")
        if not self.token:
            logger.error("APIFY_TOKEN variable is completely missing from runtime environment configurations.")
            raise ValueError("Missing APIFY_TOKEN configuration environment value.")
        self.client = ApifyClient(self.token)

    def scrape(self, search_query: str) -> list:
        logger.info(f"Launching Apify search automation query execution context: {search_query}")
        try:
            # Call the Google Maps Scraper Actor on Apify
            run_input = {
                "searchStrings": [search_query],
                "maxCrawledPlacesPerSearch": 10,
                "language": "en",
            }
            run = self.client.actor("compass/google-maps-scraper").call(run_input=run_input)
            
            # Fetch the results from the dataset
            dataset_items = list(self.client.dataset(run["defaultDatasetId"]).list_items().items)
            logger.info(f"Successfully pulled {len(dataset_items)} raw data records out of Apify execution context.")
            return dataset_items
        except Exception as e:
            logger.error(f"Failed to execute Apify scraping workflow: {str(e)}")
            return []
