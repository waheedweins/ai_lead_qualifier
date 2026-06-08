from apify_client import ApifyClient
from src.app.core.settings import settings

class GoogleMapsScraper:
    def __init__(self):
        self.client = ApifyClient(settings.APIFY_TOKEN)

    def scrape(self, search_query: str, max_results: int = 50) -> list:
        run = self.client.actor("apify/google-maps-scraper").call(
            run_input={
                "searchStringsArray": [search_query],
                "maxCrawledPlaces": max_results
            }
        )
        dataset = self.client.dataset(run["defaultDatasetId"])
        return dataset.list_items().items
