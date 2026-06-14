from src.app.database import SessionLocal  # Import your raw session maker factory
from src.app.scrapers.google_maps import GoogleMapsScraper
from src.app.crud import create_lead  # Import your lead saving function
from src.app.schemas import LeadCreate

def run_scraping_job(query: str):
    # 1. Initialize the scraper module
    scraper = GoogleMapsScraper()
    
    # 2. Open a fresh, isolated database session context for the background thread
    db = SessionLocal() 
    
    try:
        print(f"Background worker fetching leads for: {query}")
        raw_data = scraper.scrape(search_query=query)
        
        # 3. Iterate and parse the payload items array
        for item in raw_data:
            lead_payload = LeadCreate(
                name=item.get("title", "Unknown Business"),
                email=item.get("email", "No Email Provided"),
                phone=item.get("phone", "No Phone Provided"),
                source="Google Maps Scraper",
                status="new",
                ai_score=0
            )
            # Pass the dedicated worker database session explicitly
            create_lead(db=db, lead=lead_payload)
            
        print(f"Successfully saved {len(raw_data)} automated leads into the database!")
        
    except Exception as e:
        print(f"Background database storage failed: {e}")
        raise e
    finally:
        # 4. Always close the pool connection when the worker job concludes
        db.close()
