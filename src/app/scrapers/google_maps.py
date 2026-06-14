%%writefile src/app/scrapers/google_maps.py
from apify_client import ApifyClient
from src.app.core.settings import settings

class GoogleMapsScraper:
    def __init__(self):
        self.client = ApifyClient(settings.APIFY_TOKEN)

    def scrape(self, search_query: str, max_results: int = 50) -> list:
        # Fixed actor execution payload using valid Apify key structures
        run = self.client.actor("apify/google-maps-scraper").call(
            run_input={
                "searchStrings": [search_query],
                "maxResults": max_results
            }
        )
        dataset = self.client.dataset(run["defaultDatasetId"])
        return dataset.list_items().items
