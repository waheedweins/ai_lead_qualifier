from fastapi import APIRouter, BackgroundTasks, HTTPException
from src.app.workers.scraping_worker import run_scraping_job
import logging

logger = logging.getLogger("lead-engine")
router = APIRouter(prefix="/scrape", tags=["Scraping"])


@router.post("/")
def scrape(query: str, background_tasks: BackgroundTasks):
    """
    Enqueues a Google Maps scraping job to run in the background.
    Returns immediately so the HTTP request doesn't time out.
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    logger.info(f"Queueing scraping job for query: '{query}'")
    # run_scraping_job is a plain sync function — pass it directly, no anyio wrapper needed
    background_tasks.add_task(run_scraping_job, query)
    return {"status": "processing", "query": query}
